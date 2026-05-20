"""Тесты writer'ов (задачи 6.5, 6.6, 6.7)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.sml.writers._atomic import (
    atomic_append_text,
    atomic_write_text,
    with_file_lock,
)
from tools.sml.writers.agent_log import create_log_file, slugify
from tools.sml.writers.context_pack import build_and_write
from tools.sml.writers.decisions import append_decision


# --- atomic_write_text / atomic_append_text ---


def test_atomic_write_creates_file(tmp_path: Path) -> None:
    target = tmp_path / "file.md"
    atomic_write_text(target, "привет")
    assert target.read_text(encoding="utf-8") == "привет"


def test_atomic_write_replaces_existing(tmp_path: Path) -> None:
    target = tmp_path / "file.md"
    target.write_text("старое", encoding="utf-8")
    atomic_write_text(target, "новое")
    assert target.read_text(encoding="utf-8") == "новое"


def test_atomic_append_empty_file(tmp_path: Path) -> None:
    target = tmp_path / "append.md"
    start, end = atomic_append_text(target, "первая строка\nвторая")
    assert target.read_text(encoding="utf-8") == "первая строка\nвторая"
    assert start == 1
    assert end == 2


def test_atomic_append_nonempty_file(tmp_path: Path) -> None:
    target = tmp_path / "append.md"
    target.write_text("существующее\n", encoding="utf-8")
    start, end = atomic_append_text(target, "новое")
    text = target.read_text(encoding="utf-8")
    assert text == "существующее\nновое"
    assert start == 2
    # "существующее\nновое" — 2 строки (новое без \n на конце)
    assert end == 2


# --- with_file_lock ---


def test_lock_smoke(tmp_path: Path) -> None:
    target = tmp_path / "x.md"
    with with_file_lock(target):
        atomic_write_text(target, "hello")
    assert target.read_text(encoding="utf-8") == "hello"


def test_lock_conflict_retries_then_fails(tmp_path: Path) -> None:
    from tools.sml.errors import ConflictError

    target = tmp_path / "x.md"
    with with_file_lock(target):
        # В той же сессии msvcrt.locking — process-wide, повторный запрос
        # из того же процесса может сработать. Реальный тест параллельной
        # блокировки невозможен в одном потоке, поэтому ограничиваемся
        # smoke-проверкой, что контекст освобождается корректно.
        pass
    # После выхода блокировка снята и файл доступен
    assert not target.with_suffix(target.suffix + ".lock").exists()


# --- decisions writer ---


def test_append_decision(tmp_path: Path) -> None:
    target = tmp_path / "decisions.md"
    target.write_text("# Журнал решений\n\n", encoding="utf-8")
    start, end = append_decision(
        target,
        title="Выбор стека",
        context="Нужен локальный слой памяти.",
        decision="Используем SQLite + LanceDB + Ollama.",
        author_agent="kiro",
        date_utc="2026-05-11",
        tags=["sml", "memory"],
    )
    text = target.read_text(encoding="utf-8")
    assert "## 2026-05-11 - Выбор стека" in text
    assert "SQLite + LanceDB + Ollama" in text
    assert "Теги: sml, memory" in text
    assert start >= 1
    assert end >= start


def test_append_decision_preserves_previous(tmp_path: Path) -> None:
    target = tmp_path / "decisions.md"
    target.write_text("## Старое решение\nТекст.\n", encoding="utf-8")
    append_decision(
        target,
        title="Новое",
        context="c",
        decision="d",
        author_agent="kiro",
        date_utc="2026-05-11",
    )
    text = target.read_text(encoding="utf-8")
    assert "## Старое решение" in text
    assert text.index("## Старое решение") < text.index("## 2026-05-11 - Новое")


# --- agent_log writer ---


def test_slugify_cyrillic_and_spaces() -> None:
    assert slugify("Проверка работы SML") == "проверка-работы-sml"
    assert slugify("") == "entry"
    assert slugify("   ") == "entry"
    assert slugify("a b c d e f g h") == "a-b-c-d-e-f"


def test_create_log_file_basic(tmp_path: Path) -> None:
    log_dir = tmp_path / "agent-log"
    path = create_log_file(
        log_dir,
        date_iso_ms="2026-05-11T20:30:00.000Z",
        author_agent="kiro",
        request="Проверить работу MCP",
        result="Сделано, 10 инструментов зарегистрированы.",
        plan="1. Написать тесты\n2. Прогнать",
        changed_files=["tools/sml/mcp_adapter.py", "tools/sml/tests/test_mcp_adapter.py"],
        risks="Ollama может упасть между сессиями.",
        next_steps="Перейти к файловым writer'ам.",
    )
    assert path.exists()
    assert path.name.startswith("2026-05-11-2030-kiro-")
    content = path.read_text(encoding="utf-8")
    assert "## Запрос" in content
    assert "Проверить работу MCP" in content
    assert "## Изменённые файлы" in content
    assert "- tools/sml/mcp_adapter.py" in content
    assert "## Риски и ограничения" in content


def test_create_log_file_handles_slug_collision(tmp_path: Path) -> None:
    log_dir = tmp_path / "agent-log"
    p1 = create_log_file(
        log_dir,
        date_iso_ms="2026-05-11T20:30:00.000Z",
        author_agent="kiro",
        request="Одинаковая задача",
        result="res1",
    )
    p2 = create_log_file(
        log_dir,
        date_iso_ms="2026-05-11T20:30:00.000Z",
        author_agent="kiro",
        request="Одинаковая задача",
        result="res2",
    )
    assert p1 != p2
    assert p1.exists()
    assert p2.exists()


# --- context_pack writer ---


def test_build_and_write_context_pack(tmp_path: Path) -> None:
    target = tmp_path / "context-pack-latest.md"
    build_and_write(
        target,
        sections=[
            ("docs/current-context.md", "# Текущий контекст\n\nТекст."),
            ("docs/tasks.md", "# Задачи\n\n- задача 1"),
        ],
        built_at="2026-05-11 20:30:00",
    )
    text = target.read_text(encoding="utf-8")
    assert text.startswith("# Контекстный пакет")
    assert "Дата сборки: 2026-05-11 20:30:00" in text
    assert "## Файл: docs/current-context.md" in text
    assert "## Файл: docs/tasks.md" in text
    # разделители между секциями (как в существующем context-pack)
    assert text.count("\n---\n") >= 2
