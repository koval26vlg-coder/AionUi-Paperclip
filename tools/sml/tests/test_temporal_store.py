"""Unit-тесты TemporalStore (задачи 3.1–3.7)."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path

import pytest

from tools.sml.errors import ConflictError, NotFoundError
from tools.sml.temporal_store import make_new_record, open_store


@pytest.fixture
def store(tmp_path: Path):
    s = open_store(tmp_path / "sml.db")
    try:
        yield s
    finally:
        s.close()


# --- CRUD ---


def test_insert_and_read_roundtrip(store) -> None:
    rec = make_new_record(type="fact", content="пример факта", author_agent="kiro")
    store.insert(rec)
    loaded = store.read_by_id(rec.id)
    assert loaded is not None
    assert loaded.content == "пример факта"
    assert loaded.is_current is True
    assert loaded.type.value == "fact"


def test_insert_duplicate_id_raises_conflict(store) -> None:
    rec = make_new_record(type="fact", content="x", author_agent="kiro")
    store.insert(rec)
    with pytest.raises(ConflictError):
        store.insert(rec)


def test_read_missing_returns_none(store) -> None:
    assert store.read_by_id("00000000-0000-7000-8000-000000000000") is None


def test_update_fields_writes_history(store) -> None:
    rec = make_new_record(type="decision", content="v1", author_agent="kiro")
    store.insert(rec)
    time.sleep(0.005)  # гарантируем различимую миллисекундную метку
    updated = store.update_fields(rec.id, content="v2")
    assert updated.content == "v2"
    # У записи 2 истории: v1 и v2.
    rows = store._conn.execute(
        "SELECT snapshot, valid_to FROM records_history WHERE id = ? ORDER BY valid_from",
        (rec.id,),
    ).fetchall()
    assert len(rows) == 2
    # У первого интервала valid_to заполнен, у второго — NULL
    assert rows[0]["valid_to"] is not None
    assert rows[1]["valid_to"] is None


def test_update_fields_unknown_id(store) -> None:
    with pytest.raises(NotFoundError):
        store.update_fields("00000000-0000-7000-8000-000000000000", content="x")


def test_delete_soft(store) -> None:
    rec = make_new_record(type="fact", content="to-delete", author_agent="kiro")
    store.insert(rec)
    store.delete(rec.id)
    # Публичный read возвращает None после soft-delete
    assert store.read_by_id(rec.id) is None
    # Но записи в records_history сохраняются (Req 4.6, Req 10 аудит)
    rows = store._conn.execute(
        "SELECT COUNT(*) AS c FROM records_history WHERE id = ?", (rec.id,)
    ).fetchone()
    assert rows["c"] >= 1


# --- Supersede ---


def test_supersede_happy_path(store) -> None:
    old = make_new_record(type="decision", content="old", author_agent="kiro")
    new = make_new_record(type="decision", content="new", author_agent="kiro")
    store.insert(old)
    store.insert(new)

    updated_ids = store.supersede(new.id, [old.id])
    assert updated_ids == [old.id]

    old_again = store.read_by_id(old.id)
    new_again = store.read_by_id(new.id)
    assert old_again.is_current is False
    assert old_again.superseded_by_id == new.id
    assert new_again.is_current is True
    assert new_again.supersedes_id == old.id


def test_supersede_unknown_new_id(store) -> None:
    old = make_new_record(type="decision", content="old", author_agent="kiro")
    store.insert(old)
    bogus = "00000000-0000-7000-8000-000000000000"
    with pytest.raises(NotFoundError):
        store.supersede(bogus, [old.id])
    # Состояние старой записи не изменилось
    refreshed = store.read_by_id(old.id)
    assert refreshed.is_current is True
    assert refreshed.superseded_by_id is None


def test_supersede_unknown_old_id(store) -> None:
    new = make_new_record(type="decision", content="new", author_agent="kiro")
    store.insert(new)
    bogus = "00000000-0000-7000-8000-000000000000"
    with pytest.raises(NotFoundError):
        store.supersede(new.id, [bogus])
    # new должен остаться is_current=True, без supersedes_id
    refreshed = store.read_by_id(new.id)
    assert refreshed.is_current is True
    assert refreshed.supersedes_id is None


def test_supersede_atomicity_mid_list(store) -> None:
    """P5: если один из old_ids уже суперседирован, ни одна запись не меняется."""
    a = make_new_record(type="decision", content="a", author_agent="kiro")
    b = make_new_record(type="decision", content="b", author_agent="kiro")
    mid = make_new_record(type="decision", content="mid", author_agent="kiro")
    c = make_new_record(type="decision", content="c", author_agent="kiro")
    for r in (a, b, mid, c):
        store.insert(r)
    # Сначала легитимно суперседируем b с помощью mid
    store.supersede(mid.id, [b.id])
    # Теперь пытаемся суперседировать [a, b, c] через c.
    # b уже суперседирован → весь вызов должен откатиться.
    with pytest.raises(ConflictError):
        store.supersede(c.id, [a.id, b.id])

    # a и c не должны измениться
    a_again = store.read_by_id(a.id)
    c_again = store.read_by_id(c.id)
    assert a_again.is_current is True
    assert a_again.superseded_by_id is None
    assert c_again.is_current is True
    assert c_again.supersedes_id is None
    # b остаётся в том состоянии, в какое его привёл первый supersede
    b_again = store.read_by_id(b.id)
    assert b_again.is_current is False
    assert b_again.superseded_by_id == mid.id


def test_supersede_self_rejected(store) -> None:
    r = make_new_record(type="decision", content="self", author_agent="kiro")
    store.insert(r)
    with pytest.raises(ConflictError):
        store.supersede(r.id, [r.id])


# --- Temporal_Query ---


def test_query_at_returns_current_state(store) -> None:
    old = make_new_record(type="decision", content="old", author_agent="kiro")
    new = make_new_record(type="decision", content="new", author_agent="kiro")
    store.insert(old)
    time.sleep(0.005)
    store.insert(new)
    time.sleep(0.005)
    # Зафиксируем метку времени ДО supersede
    before_supersede = store._conn.execute(
        "SELECT MAX(valid_from) AS t FROM records_history"
    ).fetchone()["t"]
    time.sleep(0.005)
    store.supersede(new.id, [old.id])

    # В момент before_supersede old должен быть ещё current
    records = store.query_at(before_supersede, only_current_at=True, limit=10)
    ids = {r.id for r in records}
    assert old.id in ids

    # После супер old уже не current → при only_current_at=True исключается
    now = store._conn.execute("SELECT MAX(updated_at) AS t FROM records").fetchone()["t"]
    records_now = store.query_at(now, only_current_at=True, limit=10)
    current_ids = {r.id for r in records_now}
    assert new.id in current_ids
    assert old.id not in current_ids


def test_query_at_future_rejected(store) -> None:
    rec = make_new_record(type="fact", content="x", author_agent="kiro")
    store.insert(rec)
    with pytest.raises(ValueError):
        store.query_at("2099-01-01T00:00:00.000Z")


def test_query_at_before_first_rejected(store) -> None:
    rec = make_new_record(type="fact", content="x", author_agent="kiro")
    store.insert(rec)
    with pytest.raises(ValueError):
        store.query_at("2000-01-01T00:00:00.000Z")


# --- Миграции и durability ---


def test_migrations_are_idempotent(tmp_path: Path) -> None:
    db = tmp_path / "mig.db"
    s1 = open_store(db)
    s1.close()
    # Повторное открытие не должно пересоздавать схему
    s2 = open_store(db)
    versions = s2._conn.execute(
        "SELECT version FROM schema_migrations ORDER BY version"
    ).fetchall()
    s2.close()
    # Каждая миграция применяется ровно один раз, по возрастанию версии.
    assert [v[0] for v in versions] == [1, 2]


def test_durability_across_reopen(tmp_path: Path) -> None:
    db = tmp_path / "dur.db"
    s = open_store(db)
    rec = make_new_record(type="fact", content="survives", author_agent="kiro")
    s.insert(rec)
    s.close()

    s2 = open_store(db)
    loaded = s2.read_by_id(rec.id)
    s2.close()
    assert loaded is not None
    assert loaded.content == "survives"


def test_wal_mode_enabled(tmp_path: Path) -> None:
    s = open_store(tmp_path / "wal.db")
    mode = s._conn.execute("PRAGMA journal_mode").fetchone()[0]
    s.close()
    assert mode.lower() == "wal"


def test_index_used_for_current_query(store) -> None:
    # EXPLAIN QUERY PLAN должен упомянуть idx_records_current
    plan = store._conn.execute(
        "EXPLAIN QUERY PLAN "
        "SELECT * FROM records WHERE is_current=1 ORDER BY updated_at DESC LIMIT 20"
    ).fetchall()
    text = " ".join(row["detail"] for row in plan)
    assert "idx_records_current" in text or "idx_records_type_updated" in text
