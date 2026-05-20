"""Writer для ``docs/decisions.md`` — atomic append (Req 13.3, Req 13.5)."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ._atomic import atomic_append_text, with_file_lock


__all__ = ["append_decision"]


def _render_decision_block(
    *,
    title: str,
    context: str,
    decision: str,
    author_agent: str,
    date_utc: str,
    tags: Iterable[str] = (),
) -> str:
    parts = [
        f"## {date_utc} - {title}",
        "",
        "### Контекст",
        context.strip(),
        "",
        "### Решение",
        decision.strip(),
        "",
        f"### Автор: {author_agent}",
    ]
    tags_list = [t for t in tags if t]
    if tags_list:
        parts.append(f"### Теги: {', '.join(tags_list)}")
    parts.append("")  # пустая строка в конце блока
    return "\n".join(parts)


def append_decision(
    target: Path,
    *,
    title: str,
    context: str,
    decision: str,
    author_agent: str,
    date_utc: str,
    tags: Iterable[str] = (),
) -> tuple[int, int]:
    """Атомарно дописывает блок решения в конец файла ``docs/decisions.md``.

    Возвращает пару ``(source_lines_start, source_lines_end)`` — номера строк
    добавленного блока в итоговом файле.
    """
    block = _render_decision_block(
        title=title,
        context=context,
        decision=decision,
        author_agent=author_agent,
        date_utc=date_utc,
        tags=tags,
    )
    with with_file_lock(target):
        return atomic_append_text(target, block)
