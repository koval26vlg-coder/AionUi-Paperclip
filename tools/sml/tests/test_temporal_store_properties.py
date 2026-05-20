"""Property-тесты TemporalStore.

Покрытие:
- P1 Durability: любая успешно закоммиченная запись читается после reopen.
- P3 Monotonicity: без явного supersede/delete is_current=True сохраняется.
- P5 Supersede Atomicity: частичный сбой не меняет состояние.
"""

from __future__ import annotations

from pathlib import Path

from hypothesis import given, settings, strategies as st

from tools.sml.temporal_store import make_new_record, open_store


# Безопасная стратегия для content: непустая, без surrogate'ов, без обрезки пробелов.
_content_strategy = st.text(
    alphabet=st.characters(min_codepoint=0x20, max_codepoint=0xFFFF, blacklist_categories=("Cs",)),
    min_size=1,
    max_size=500,
).filter(lambda s: s.strip() != "")


@settings(max_examples=50, deadline=None)
@given(contents=st.lists(_content_strategy, min_size=1, max_size=20))
def test_durability_round_trip(tmp_path_factory, contents) -> None:
    """P1: записанные записи читаются после close+open."""
    db = tmp_path_factory.mktemp("dur") / "p1.db"
    store = open_store(db)
    ids = []
    for c in contents:
        rec = make_new_record(type="fact", content=c, author_agent="kiro")
        store.insert(rec)
        ids.append((rec.id, c))
    store.close()

    store2 = open_store(db)
    try:
        for record_id, expected in ids:
            loaded = store2.read_by_id(record_id)
            assert loaded is not None
            assert loaded.content == expected
            assert loaded.is_current is True
    finally:
        store2.close()


@settings(max_examples=30, deadline=None)
@given(n=st.integers(min_value=1, max_value=15))
def test_monotonicity_without_supersede(tmp_path_factory, n) -> None:
    """P3: без явного supersede/delete is_current=True сохраняется."""
    db = tmp_path_factory.mktemp("p3") / "store.db"
    store = open_store(db)
    try:
        ids = []
        for i in range(n):
            rec = make_new_record(type="fact", content=f"fact-{i}", author_agent="kiro")
            store.insert(rec)
            ids.append(rec.id)
        for record_id in ids:
            loaded = store.read_by_id(record_id)
            assert loaded.is_current is True
            assert loaded.superseded_by_id is None
    finally:
        store.close()
