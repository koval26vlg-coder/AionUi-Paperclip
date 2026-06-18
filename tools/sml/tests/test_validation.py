"""Тесты нормализации имён агентов и валидации.

Карта ``AUTHOR_CANONICAL`` растёт по мере добавления агентов; этот тест
фиксирует контракт ``normalize_author`` напрямую (раньше покрывался только
косвенно через e2e).
"""

from __future__ import annotations

import pytest

from tools.sml.validation import AUTHOR_CANONICAL, normalize_author


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("codex", "Codex"),
        ("Codex", "Codex"),
        ("  codex  ", "Codex"),
        ("CODEX", "Codex"),
        ("gemini", "Gemini CLI"),
        ("Gemini-CLI", "Gemini CLI"),
        ("gemini cli", "Gemini CLI"),
        ("GEMINI CLI", "Gemini CLI"),
        ("claude", "Claude Code"),
        ("claude code", "Claude Code"),
        ("Claude-Code", "Claude Code"),
    ],
)
def test_normalize_known_agents(raw: str, expected: str) -> None:
    assert normalize_author(raw) == expected


def test_normalize_unknown_agent_is_trimmed_not_changed() -> None:
    # Неизвестный агент: обрезаем пробелы, но регистр не трогаем.
    assert normalize_author("  SomeNewBot  ") == "SomeNewBot"
    assert normalize_author("kiro") == "kiro"
    assert normalize_author("Cursor Agent") == "Cursor Agent"


def test_normalize_idempotent() -> None:
    # Повторное применение к каноническому имени ничего не меняет.
    for canonical in set(AUTHOR_CANONICAL.values()):
        assert normalize_author(canonical) == canonical


def test_normalize_non_string_passthrough() -> None:
    # Нестроковые значения не трогаем — их отвергнет валидатор модели.
    assert normalize_author(None) is None  # type: ignore[arg-type]
    assert normalize_author(123) == 123  # type: ignore[arg-type]


def test_canonical_values_are_self_consistent() -> None:
    # Все канонические значения должны быть «неподвижными точками».
    for key, value in AUTHOR_CANONICAL.items():
        assert normalize_author(key) == value
        assert normalize_author(value) == value
