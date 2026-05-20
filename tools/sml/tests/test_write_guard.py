"""Тесты для guard_secret (задача 7.3; P6)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.sml.errors import SecretRejectedError
from tools.sml.operation_log import OperationLog
from tools.sml.write_guard import guard_secret


def _read_lines(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def test_guard_passes_safe_text(tmp_path: Path) -> None:
    log = OperationLog(tmp_path)
    # Не должен бросать исключение и не должен ничего логировать.
    guard_secret(
        agent="kiro",
        op="write",
        text="русский текст без секретов",
        op_log=log,
        record_id="r1",
    )
    log.close()
    # active-файл даже не создавался — write-путь не должен ничего писать
    # при passthrough (логирование успеха делает вызывающий код).
    assert not log.active_path.exists()


def test_guard_rejects_openai_key(tmp_path: Path) -> None:
    log = OperationLog(tmp_path)
    with pytest.raises(SecretRejectedError) as excinfo:
        guard_secret(
            agent="kiro",
            op="write",
            text="мой токен: sk-" + "a" * 40,
            op_log=log,
            record_id="r1",
            operation_id="op-1",
        )
    assert excinfo.value.category == "secret_rejected"

    # В Operation_Log должна быть запись rejected с категорией причины.
    lines = _read_lines(log.active_path)
    assert len(lines) == 1
    entry = lines[0]
    assert entry["op"] == "write"
    assert entry["result"] == "rejected"
    assert entry["reason_category"] == "openai_api_key"
    assert entry["record_id"] == "r1"
    assert entry["operation_id"] == "op-1"
    # Значения самого секрета в логе быть не должно.
    assert "sk-" not in json.dumps(entry, ensure_ascii=False)
    log.close()


def test_guard_works_without_op_log(tmp_path: Path) -> None:
    # op_log=None допустим — guard просто бросит ошибку, но без записи.
    with pytest.raises(SecretRejectedError):
        guard_secret(
            agent="kiro",
            op="write",
            text="ghp_" + "x" * 40,
            op_log=None,
            record_id="r1",
        )
