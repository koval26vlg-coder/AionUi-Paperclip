"""Smoke-тесты ядра SML_Core (задача 2.1)."""

from __future__ import annotations

from tools.sml import __version__
from tools.sml.core import main as core_main
from tools.sml.errors import ValidationError, NotFoundError
from tools.sml.validation import MEMORY_TYPE_VALUES


def test_version_is_set() -> None:
    assert __version__ == "0.1.0"


def test_memory_types_are_exactly_eight() -> None:
    expected = {
        "fact",
        "preference",
        "decision",
        "agent_log",
        "task",
        "task_link",
        "constraint",
        "timeline_event",
    }
    assert MEMORY_TYPE_VALUES == expected


def test_selfcheck_returns_zero(capsys) -> None:
    rc = core_main(["--selfcheck"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out == "sml-selfcheck-ok"


def test_errors_preserve_russian_message() -> None:
    err = ValidationError("поле 'content' не должно быть пустым")
    assert err.category == "validation"
    assert "не должно быть пустым" in str(err)

    nf = NotFoundError.for_id("00000000-0000-7000-8000-000000000000")
    assert nf.category == "not_found"
    assert "не найден" in nf.message
