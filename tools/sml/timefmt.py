"""Форматирование меток времени ISO 8601 UTC с миллисекундами.

Формат: ``YYYY-MM-DDTHH:MM:SS.sssZ`` (миллисекунды, часовой пояс UTC).

Требования: Req 6.1 (формат меток времени Memory_Record).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

__all__ = ["now_utc_ms", "format_iso8601_ms", "parse_iso8601_ms"]


# YYYY-MM-DDTHH:MM:SS.sssZ
_ISO8601_MS_RE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"\.(?P<ms>\d{3})Z$"
)


def now_utc_ms() -> str:
    """Возвращает текущее время в формате ISO 8601 UTC с миллисекундами."""
    return format_iso8601_ms(datetime.now(timezone.utc))


def format_iso8601_ms(dt: datetime) -> str:
    """Форматирует ``datetime`` в ISO 8601 UTC с миллисекундами.

    Требования:
    - точность до миллисекунд (не микро-, не нано-);
    - часовой пояс — UTC, суффикс ``Z``;
    - без offset-строк вида ``+00:00``.

    Если ``dt`` без tz — считается UTC.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    # Округляем до миллисекунд (микросекунды / 1000)
    ms = dt.microsecond // 1000
    return (
        f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}"
        f"T{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}.{ms:03d}Z"
    )


def parse_iso8601_ms(value: str) -> datetime:
    """Разбирает строку ISO 8601 UTC с миллисекундами.

    Принимает только строгий формат ``YYYY-MM-DDTHH:MM:SS.sssZ``.
    Отклоняет:
    - значения без ``Z`` (naive);
    - offset вида ``+00:00``;
    - значения без миллисекунд или с другим числом цифр после точки.
    """
    if not isinstance(value, str):
        raise ValueError(f"Ожидалась строка ISO 8601, получено {type(value).__name__}")
    m = _ISO8601_MS_RE.match(value)
    if m is None:
        raise ValueError(
            f"Неверный формат ISO 8601 UTC с миллисекундами: {value!r}. "
            "Ожидается YYYY-MM-DDTHH:MM:SS.sssZ."
        )
    try:
        return datetime(
            int(m["year"]),
            int(m["month"]),
            int(m["day"]),
            int(m["hour"]),
            int(m["minute"]),
            int(m["second"]),
            int(m["ms"]) * 1000,
            tzinfo=timezone.utc,
        )
    except ValueError as exc:
        raise ValueError(
            f"Некорректная дата/время в {value!r}: {exc}"
        ) from exc
