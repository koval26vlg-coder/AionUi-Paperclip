from __future__ import annotations

import os
import sqlite3
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.antigravity_print import (
    extract_latest_response_from_db,
    recent_conversation_dbs,
    recover_from_conversations,
    review_violation,
    run_process_with_tree_timeout,
    stdout_looks_recoverable_failure,
)


def write_db(tmp_path: Path, payloads: list[bytes]) -> Path:
    db_path = tmp_path / "conversation.db"
    con = sqlite3.connect(db_path)
    con.execute(
        "create table steps (idx integer primary key, step_type integer not null, status integer not null, step_payload blob)"
    )
    for idx, payload in enumerate(payloads):
        con.execute(
            "insert into steps (idx, step_type, status, step_payload) values (?, 15, 3, ?)",
            (idx, payload),
        )
    con.commit()
    con.close()
    return db_path


def test_extract_latest_response_prefers_final_text_over_internal_trace(tmp_path: Path) -> None:
    payload = (
        b"sessionID\0"
        b"OK\0\0"
        b"**Acknowledge the Request**\n\n"
        b"I've registered the user's explicit demand for a simple response.\0"
        b"run_command\0"
    )
    db_path = write_db(tmp_path, [payload])

    assert extract_latest_response_from_db(db_path) == "OK"


def test_extract_latest_response_keeps_multichunk_russian_answer(tmp_path: Path) -> None:
    payload = (
        "sessionID\0"
        "37d0060c-1bd0-4db5-a681-272cfedaaed5\0\0"
        "Я выполнил требования L2 workflow.\0\0"
        "### Что было сделано\nПроверены риски, ограничения и handoff.\0\0"
        "**Verifying Context Pack Generation**\0\0"
        "run_command\0"
    ).encode("utf-8")
    db_path = write_db(tmp_path, [payload])

    response = extract_latest_response_from_db(db_path)

    assert response is not None
    assert "Я выполнил требования L2 workflow." in response
    assert "Проверены риски" in response
    assert "Verifying Context Pack" not in response
    assert "run_command" not in response


def test_extract_latest_response_skips_internal_i_am_trace(tmp_path: Path) -> None:
    payload = (
        "sessionID\0"
        "I am now focusing on the user's explicit request.\0\0"
        "1j25w3az\0\0"
        "## Что было сделано\nПроверен handoff без записи файлов.\0"
    ).encode("utf-8")
    db_path = write_db(tmp_path, [payload])

    response = extract_latest_response_from_db(db_path)

    assert response is not None
    assert "I am now focusing" not in response
    assert "1j25w3az" not in response
    assert "Проверен handoff" in response


def test_readiness_stdout_is_recoverable_failure() -> None:
    text = (
        "Да, я готов к работе. Я запущен в качестве Antigravity CLI "
        "в изолированном режиме только для чтения. Что вас интересует?"
    )

    assert stdout_looks_recoverable_failure(text)


def test_db_recovery_skips_clarifying_readiness_response(tmp_path: Path) -> None:
    stale_but_valid = "## Что было сделано\nПроверен handoff.\n\n## Решение\napprove".encode("utf-8")
    clarifying = (
        "Да, я подтверждаю, что работаю в качестве Antigravity CLI.\n\n"
        "Пожалуйста, сообщите, какой вопрос или задачу требуется разобрать.\n\n"
        "**Clarifying Initial Instructions**"
    ).encode("utf-8")
    db_path = write_db(tmp_path, [stale_but_valid, clarifying])

    response, recovered_from = recover_from_conversations(tmp_path, 0)

    assert recovered_from == db_path
    assert response is not None
    assert "Проверен handoff" in response
    assert "Пожалуйста, сообщите" not in response


def _touch_db(tmp_path: Path, name: str, mtime: float) -> Path:
    db_path = tmp_path / name
    db_path.write_bytes(b"x")
    os.utime(db_path, (mtime, mtime))
    return db_path


def test_recent_conversation_dbs_ignores_dbs_written_before_run(tmp_path: Path) -> None:
    # Session correlation: a DB from a different, earlier run must not be picked
    # up when this run wrote nothing after started_at.
    now = time.time()
    _touch_db(tmp_path, "foreign-old.db", now - 3600)
    fresh = _touch_db(tmp_path, "this-run.db", now + 1)

    recent = recent_conversation_dbs(tmp_path, started_at=now)

    assert recent == [fresh]


def test_recent_conversation_dbs_returns_empty_when_only_stale_dbs(tmp_path: Path) -> None:
    now = time.time()
    _touch_db(tmp_path, "foreign-old.db", now - 3600)

    assert recent_conversation_dbs(tmp_path, started_at=now) == []


def test_review_violation_flags_command_execution() -> None:
    text = 'run_command {"CommandLine": "ls", "WaitMsBeforeAsync": 100}'
    assert review_violation(text) is not None


def test_review_violation_flags_external_search_call() -> None:
    assert review_violation("google_search(query='hh.ru')") is not None


def test_review_violation_ignores_plain_reasoning_mention() -> None:
    # Merely mentioning a tool name in reasoning is not a violation.
    assert review_violation("Я бы мог использовать read_file, но не стал.") is None
    assert review_violation("## Что было сделано\nПроверен handoff.") is None


def test_run_process_with_tree_timeout_kills_slow_process(tmp_path: Path) -> None:
    started = time.time()
    result = run_process_with_tree_timeout(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        cwd=str(tmp_path),
        env=None,
        timeout=2,
    )
    elapsed = time.time() - started

    assert result.timed_out is True
    assert result.returncode == 124
    # the kill must be prompt, not wait out the full 30s sleep
    assert elapsed < 20


def test_run_process_with_tree_timeout_returns_normal_output(tmp_path: Path) -> None:
    result = run_process_with_tree_timeout(
        [sys.executable, "-c", "print('hello-tree')"],
        cwd=str(tmp_path),
        env=None,
        timeout=30,
    )

    assert result.timed_out is False
    assert result.returncode == 0
    assert "hello-tree" in result.stdout
