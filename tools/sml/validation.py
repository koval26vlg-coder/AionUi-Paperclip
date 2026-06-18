"""Валидация типов и подформатов Memory_Record.

Требования:
- Req 4.1: закрытый перечень из 8 типов.
- Req 4.3: неверный тип/формат → запись отклоняется, состояние не меняется.
- Req 8.4: формат ``source_lines`` = ``начальная_строка-конечная_строка``,
  обе положительные, начало ≤ конец.
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import List, Optional

from .errors import ValidationError, UnsupportedError

__all__ = [
    "MemoryType",
    "MEMORY_TYPE_VALUES",
    "validate_type",
    "validate_source_lines",
    "validate_tags",
    "normalize_author",
    "AUTHOR_CANONICAL",
]


# Канонические имена активных агентов. Ключ — нормализованная (lower/strip)
# форма входящего ``author_agent``, значение — каноническое имя для хранения.
# Цель: убрать расщепление личности агентов в SML (codex/Codex,
# gemini/Gemini-CLI/Gemini CLI, claude/Claude Code), которое искажало
# метрику «Агенты» и граф связей дашборда.
AUTHOR_CANONICAL: dict[str, str] = {
    "codex": "Codex",
    "claude": "Claude Code",
    "claude code": "Claude Code",
    "claude-code": "Claude Code",
    "claudecode": "Claude Code",
    "gemini": "Gemini CLI",
    "gemini cli": "Gemini CLI",
    "gemini-cli": "Gemini CLI",
    "geminicli": "Gemini CLI",
}


def normalize_author(raw: str) -> str:
    """Приводит имя агента к каноническому виду.

    Известные синонимы (см. ``AUTHOR_CANONICAL``) маппятся на единое имя.
    Неизвестные значения возвращаются обрезанными по краям, но без изменения
    регистра — чтобы не ломать будущих агентов, которых нет в карте.

    Пустую/нестроковую величину не трогаем — её отвергнёт валидатор модели.
    """
    if not isinstance(raw, str):
        return raw
    key = raw.strip().lower()
    canonical = AUTHOR_CANONICAL.get(key)
    if canonical is not None:
        return canonical
    return raw.strip() or raw


class MemoryType(StrEnum):
    """Допустимые типы ``Memory_Record`` (дизайн §5.2, Req 4.1)."""

    FACT = "fact"
    PREFERENCE = "preference"
    DECISION = "decision"
    AGENT_LOG = "agent_log"
    TASK = "task"
    TASK_LINK = "task_link"
    CONSTRAINT = "constraint"
    TIMELINE_EVENT = "timeline_event"


MEMORY_TYPE_VALUES = frozenset(t.value for t in MemoryType)

_SOURCE_LINES_RE = re.compile(r"^(\d+)-(\d+)$")


def validate_type(raw: str) -> MemoryType:
    """Возвращает нормализованное значение ``MemoryType``.

    Бросает ``UnsupportedError``, если ``raw`` не входит в закрытый список.
    """
    if not isinstance(raw, str):
        raise UnsupportedError(
            f"Тип Memory_Record должен быть строкой, получено {type(raw).__name__}"
        )
    if raw not in MEMORY_TYPE_VALUES:
        raise UnsupportedError(
            f"Неизвестный тип Memory_Record: {raw!r}. "
            f"Допустимые значения: {sorted(MEMORY_TYPE_VALUES)}"
        )
    return MemoryType(raw)


def validate_source_lines(value: Optional[str]) -> Optional[str]:
    """Проверяет формат ``source_lines`` = ``<start>-<end>``.

    ``None`` допустим (поле опциональное). Бросает ``ValidationError`` при
    нарушении формата или логики (start ≤ end, обе > 0).
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError.for_field(
            "source_lines",
            f"ожидалась строка, получено {type(value).__name__}",
        )
    m = _SOURCE_LINES_RE.fullmatch(value)
    if m is None:
        raise ValidationError.for_field(
            "source_lines",
            f"неверный формат {value!r}, ожидается 'start-end' (цифры)",
        )
    start = int(m.group(1))
    end = int(m.group(2))
    if start <= 0 or end <= 0:
        raise ValidationError.for_field(
            "source_lines",
            f"значения должны быть положительными, получено start={start}, end={end}",
        )
    if start > end:
        raise ValidationError.for_field(
            "source_lines",
            f"start должен быть ≤ end, получено {start}>{end}",
        )
    return value


def validate_tags(value: Optional[List[str]]) -> List[str]:
    """Проверяет список тегов.

    Правила:
    - 0–20 элементов;
    - каждый тег 1–64 символа UTF-8;
    - без дубликатов (точное совпадение).
    """
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValidationError.for_field(
            "tags",
            f"ожидался список, получено {type(value).__name__}",
        )
    if len(value) > 20:
        raise ValidationError.for_field(
            "tags", f"не более 20 тегов, получено {len(value)}"
        )
    seen: set[str] = set()
    for tag in value:
        if not isinstance(tag, str):
            raise ValidationError.for_field(
                "tags",
                f"каждый тег должен быть строкой, получено {type(tag).__name__}",
            )
        if not 1 <= len(tag) <= 64:
            raise ValidationError.for_field(
                "tags",
                f"длина тега должна быть 1–64 символа, получено {len(tag)}",
            )
        if tag in seen:
            raise ValidationError.for_field(
                "tags", f"дубликат тега {tag!r} недопустим"
            )
        seen.add(tag)
    return list(value)
