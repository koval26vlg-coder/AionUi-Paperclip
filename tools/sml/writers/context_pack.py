"""Writer для ``docs/context-packs/context-pack-latest.md`` (Req 13.4, Req 14.2).

Формат совместим с текущим ``tools/watch-memory.ps1``:

    # Контекстный пакет

    Дата сборки: YYYY-MM-DD HH:MM:SS

    Этот файл предназначен для быстрого входа любого агента...

    ---

    ## Файл: <path>

    <содержимое>

    ---

    ## Последние записи журнала агентов

    ### docs/agent-log/<file>.md

    <содержимое>
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ._atomic import atomic_write_text, with_file_lock


__all__ = ["build_and_write"]


HEADER = "# Контекстный пакет"
INTRO = "Этот файл предназначен для быстрого входа любого агента в общий контекст."


def _render(sections: list[tuple[str, str]], built_at: str) -> str:
    lines: list[str] = []
    lines.append(HEADER)
    lines.append("")
    lines.append(f"Дата сборки: {built_at}")
    lines.append("")
    lines.append(INTRO)
    lines.append("")
    lines.append("---")
    lines.append("")
    for path, content in sections:
        lines.append(f"## Файл: {path}")
        lines.append("")
        lines.append(content.rstrip("\n"))
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def build_and_write(
    target: Path,
    *,
    sections: Iterable[tuple[str, str]],
    built_at: str,
) -> None:
    """Собирает и пишет pack атомарно. ``sections`` — список ``(rel_path, content)``.

    ``target`` — абсолютный путь к ``context-pack-latest.md``.
    """
    rendered = _render(list(sections), built_at)
    with with_file_lock(target):
        atomic_write_text(target, rendered)
