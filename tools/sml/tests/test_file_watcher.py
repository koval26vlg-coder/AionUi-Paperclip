"""Тесты SyncService (задачи 6.1, 6.3, 6.4, 6.8; P4)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.sml.file_watcher import (
    FILE_TO_TYPE,
    SyncService,
    split_into_blocks,
)
from tools.sml.operation_log import OperationLog
from tools.sml.temporal_store import open_store


def _write_file(root: Path, rel: str, content: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def sync_service(tmp_path: Path):
    store = open_store(tmp_path / "state.db")
    op_log = OperationLog(tmp_path / "logs")
    svc = SyncService(store=store, op_log=op_log, root=tmp_path)
    yield svc
    op_log.close()
    store.close()


# --- split_into_blocks ---


def test_split_heading_sections() -> None:
    text = (
        "# Название\n\n"
        "## Секция 1\n"
        "Текст первого раздела\n\n"
        "## Секция 2\n"
        "Текст второго раздела\n"
    )
    blocks = split_into_blocks(text, "docs/decisions.md")
    assert len(blocks) == 2
    assert "Секция 1" in blocks[0].content
    assert "Секция 2" in blocks[1].content


def test_split_no_headings_single_block() -> None:
    text = "Просто текст без заголовков\nв две строки"
    blocks = split_into_blocks(text, "docs/memory/layers/facts.md")
    assert len(blocks) == 1
    assert blocks[0].content == text
    assert blocks[0].start_line == 1


def test_split_tasks_md_checkbox_items() -> None:
    text = (
        "# Задачи\n\n"
        "- [ ] Первая задача\n"
        "  описание первой\n"
        "- [x] Вторая задача\n"
        "- [ ] Третья задача\n"
    )
    blocks = split_into_blocks(text, "docs/tasks.md")
    assert len(blocks) == 3
    assert "Первая" in blocks[0].content
    assert "Вторая" in blocks[1].content
    assert "Третья" in blocks[2].content


# --- SyncService.sync_file ---


def test_sync_inserts_records(sync_service: SyncService, tmp_path: Path) -> None:
    _write_file(
        tmp_path,
        "docs/memory/layers/facts.md",
        "# Факты\n\n## Факт 1\nЛокальная SML хранит память.\n\n"
        "## Факт 2\nАгенты подключаются через MCP.\n",
    )
    touched = sync_service.sync_file("docs/memory/layers/facts.md")
    assert touched == 2
    all_rows = sync_service.store._conn.execute(
        "SELECT type, source_file, source_lines FROM records WHERE deleted_at IS NULL"
    ).fetchall()
    assert len(all_rows) == 2
    for row in all_rows:
        assert row["type"] == "fact"
        assert row["source_file"] == "docs/memory/layers/facts.md"


def test_sync_is_idempotent(sync_service: SyncService, tmp_path: Path) -> None:
    _write_file(
        tmp_path,
        "docs/decisions.md",
        "## Решение A\nТекст A.\n\n## Решение B\nТекст B.\n",
    )
    first = sync_service.sync_file("docs/decisions.md")
    assert first == 2
    second = sync_service.sync_file("docs/decisions.md")
    assert second == 0  # hash совпал — ничего не делаем


def test_sync_updates_changed_block(sync_service: SyncService, tmp_path: Path) -> None:
    path = _write_file(
        tmp_path,
        "docs/memory/layers/preferences.md",
        "## Preference A\nРусский язык.\n\n## Preference B\nКраткость.\n",
    )
    sync_service.sync_file("docs/memory/layers/preferences.md")
    # Меняем первый блок
    path.write_text(
        "## Preference A\nРусский язык и эмодзи 🎉\n\n## Preference B\nКраткость.\n",
        encoding="utf-8",
    )
    touched = sync_service.sync_file("docs/memory/layers/preferences.md")
    assert touched == 1
    rows = sync_service.store._conn.execute(
        "SELECT content FROM records WHERE is_current=1 AND source_file=? ORDER BY source_lines",
        ("docs/memory/layers/preferences.md",),
    ).fetchall()
    contents = [r["content"] for r in rows]
    assert any("эмодзи 🎉" in c for c in contents)


def test_sync_all_visits_every_known_file(sync_service: SyncService, tmp_path: Path) -> None:
    # Создадим только два файла — остальные должны быть пропущены.
    _write_file(
        tmp_path,
        "docs/memory/layers/facts.md",
        "## F1\nФакт 1.\n",
    )
    _write_file(tmp_path, "docs/tasks.md", "# Задачи\n\n- [ ] задача\n")
    result = sync_service.sync_all()
    # Все ключи из FILE_TO_TYPE присутствуют в result
    assert set(result) == set(FILE_TO_TYPE)
    # Для существующих — touched ≥ 0 без ошибок
    assert result["docs/memory/layers/facts.md"] == 1
    assert result["docs/tasks.md"] == 1


def test_sync_unknown_file_returns_zero(sync_service: SyncService, tmp_path: Path) -> None:
    _write_file(tmp_path, "docs/random.md", "# Рандом\nТекст.\n")
    assert sync_service.sync_file("docs/random.md") == 0


def test_sync_file_authority_replaces_manual_edit(
    sync_service: SyncService, tmp_path: Path
) -> None:
    """P4: запись в БД приводится к файлу при расхождении."""
    path = _write_file(
        tmp_path,
        "docs/memory/layers/facts.md",
        "## Факт\nОригинальный текст.\n",
    )
    sync_service.sync_file("docs/memory/layers/facts.md")
    # Симулируем ручное изменение ``content`` в БД, минуя SML
    sync_service.store._conn.execute(
        "UPDATE records SET content = 'ПОДДЕЛЬНЫЙ ТЕКСТ', content_hash = 'x' WHERE is_current=1"
    )
    # Сбрасываем sync_state, чтобы sync увидел, что файл "изменился"
    sync_service.store._conn.execute("DELETE FROM sync_state WHERE source_file = ?", ("docs/memory/layers/facts.md",))
    touched = sync_service.sync_file("docs/memory/layers/facts.md")
    assert touched == 1
    rec = sync_service.store._conn.execute(
        "SELECT content FROM records WHERE is_current=1 AND source_file=?",
        ("docs/memory/layers/facts.md",),
    ).fetchone()
    assert "Оригинальный текст" in rec["content"]
