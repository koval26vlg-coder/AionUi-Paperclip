"""Тесты Operation_Log (задачи 7.4, 7.5, 7.7)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.sml.operation_log import OperationLog


def _read_lines(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def test_single_log_entry_written(tmp_path: Path) -> None:
    log = OperationLog(tmp_path)
    log.log(agent="kiro", op="ping", result="success")
    log.close()
    lines = _read_lines(log.active_path)
    assert len(lines) == 1
    entry = lines[0]
    assert entry["agent"] == "kiro"
    assert entry["op"] == "ping"
    assert entry["result"] == "success"
    assert "ts" in entry


def test_error_entry_requires_reason(tmp_path: Path) -> None:
    log = OperationLog(tmp_path)
    with pytest.raises(ValueError):
        log.log(agent="codex", op="write", result="rejected")
    log.log(
        agent="codex",
        op="write",
        result="rejected",
        reason_category="validation",
        record_id="abc",
    )
    log.close()
    lines = _read_lines(log.active_path)
    assert lines[0]["reason_category"] == "validation"
    assert lines[0]["record_id"] == "abc"


def test_append_only_multiple_entries(tmp_path: Path) -> None:
    log = OperationLog(tmp_path)
    for i in range(5):
        log.log(agent="kiro", op="read", result="success", record_id=f"id-{i}")
    log.close()
    lines = _read_lines(log.active_path)
    assert len(lines) == 5
    assert [entry["record_id"] for entry in lines] == [f"id-{i}" for i in range(5)]


def test_readable_without_close(tmp_path: Path) -> None:
    """Req 10.3: файл читается во время работы SML (flush+fsync)."""
    log = OperationLog(tmp_path)
    log.log(agent="kiro", op="ping", result="success")
    # Не закрываем — читаем "вживую"
    lines = _read_lines(log.active_path)
    assert len(lines) == 1
    log.close()


def test_rejects_unknown_op(tmp_path: Path) -> None:
    log = OperationLog(tmp_path)
    with pytest.raises(ValueError):
        log.log(agent="kiro", op="unknown_op", result="success")
    log.close()


def test_rotation_renames_previous_day(tmp_path: Path) -> None:
    log = OperationLog(tmp_path)
    # Пишем первую запись — файл создаётся и _current_date = сегодня.
    log.log(agent="kiro", op="ping", result="success")
    lines_before = _read_lines(log.active_path)
    today = lines_before[0]["ts"][:10]
    # Вычисляем next_day как today + 1 день, чтобы cleanup_old_files
    # не удалил только что ротированный файл (он моложе retention_days).
    from datetime import datetime, timedelta, timezone

    next_day = (
        datetime.strptime(today, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        + timedelta(days=1)
    ).strftime("%Y-%m-%d")
    log.force_rotate_to(next_day)
    files_after = sorted(p.name for p in tmp_path.iterdir())
    assert not log.active_path.exists(), f"files: {files_after}"
    rotated = tmp_path / f"sml-operation-log-{today}.ndjson"
    assert rotated.exists(), f"today={today!r}, files={files_after}"
    # Новый день — пустой активный файл появится после следующего log()
    log.log(agent="kiro", op="ping", result="success")
    assert log.active_path.exists()
    active_lines = _read_lines(log.active_path)
    assert len(active_lines) == 1
    log.close()


def test_retention_deletes_old_files(tmp_path: Path) -> None:
    log = OperationLog(tmp_path, retention_days=30)
    # Создаём фейковые ротированные файлы: один старый (100 дней назад),
    # один свежий (3 дня назад).
    old_file = tmp_path / "sml-operation-log-2000-01-01.ndjson"
    fresh_file = tmp_path / "sml-operation-log-2026-05-01.ndjson"
    old_file.write_text("{}\n", encoding="utf-8")
    fresh_file.write_text("{}\n", encoding="utf-8")
    # Дёргаем очистку через переход на дату 2026-05-11
    log.force_rotate_to("2026-05-11")
    assert not old_file.exists()
    assert fresh_file.exists()
    log.close()
