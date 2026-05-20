"""Writer для ``docs/agent-log/*.md`` (Req 13.2, Req 13.5)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Optional

from ._atomic import atomic_write_text, with_file_lock


__all__ = ["create_log_file", "slugify"]


_MAX_SLUG_WORDS = 6
_SLUG_WORD_RE = re.compile(r"[A-Za-z0-9А-Яа-яЁё]+")


def slugify(request_text: str) -> str:
    """Формирует slug из первых 6 слов ``request_text``.

    Пробелы и разделители → ``-``. Регистр сохраняется; транслитерации нет.
    Если ни одного слова — возвращает ``entry``.
    """
    words = _SLUG_WORD_RE.findall(request_text or "")
    if not words:
        return "entry"
    return "-".join(w.lower() for w in words[: _MAX_SLUG_WORDS])


def create_log_file(
    base_dir: Path,
    *,
    date_iso_ms: str,
    author_agent: str,
    request: str,
    result: str,
    plan: Optional[str] = None,
    changed_files: Iterable[str] = (),
    risks: Optional[str] = None,
    next_steps: Optional[str] = None,
) -> Path:
    """Создаёт файл ``docs/agent-log/YYYY-MM-DD-HHMM-<agent>-<slug>.md``.

    Возвращает путь созданного файла.
    """
    # date_iso_ms — полная метка ISO 8601 UTC ms; берём YYYY-MM-DD-HHMM.
    # Формат гарантирован timefmt.parse_iso8601_ms.
    date_part = date_iso_ms[:10]  # YYYY-MM-DD
    hhmm = date_iso_ms[11:16].replace(":", "")
    slug = slugify(request)
    name = f"{date_part}-{hhmm}-{author_agent}-{slug}.md"
    target = base_dir / name

    parts = [
        f"# {author_agent} — {date_iso_ms}",
        "",
        "## Запрос",
        request.strip(),
        "",
    ]
    if plan:
        parts.extend(["## План", plan.strip(), ""])
    parts.extend(["## Результат", result.strip(), ""])
    files_list = [f for f in changed_files if f]
    if files_list:
        parts.append("## Изменённые файлы")
        parts.extend(f"- {f}" for f in files_list)
        parts.append("")
    if risks:
        parts.extend(["## Риски и ограничения", risks.strip(), ""])
    if next_steps:
        parts.extend(["## Что следующему агенту", next_steps.strip(), ""])

    content = "\n".join(parts)

    # Защита от коллизии по slug+timestamp: если файл с таким именем уже
    # существует, добавляем суффикс -1, -2 и т.д.
    with with_file_lock(base_dir / ".agent-log"):
        final = target
        i = 1
        while final.exists():
            final = base_dir / f"{target.stem}-{i}{target.suffix}"
            i += 1
        atomic_write_text(final, content)
    return final
