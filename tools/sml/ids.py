"""Генератор идентификаторов UUIDv7 для Memory_Record.

UUIDv7 — старшие 48 бит представляют миллисекунды Unix time (UTC), далее
идут биты версии/варианта и случайные биты. Лексикографический порядок
соответствует временному.

Гарантируется монотонность в пределах одного процесса: если два id
сгенерированы в одну миллисекунду или с откатом часов назад, младшие биты
инкрементируются, чтобы сохранить строгое возрастание.

Требования: Req 4.2 (уникальность и метка времени), Req 10.1 (ссылка на
запись в Operation_Log).
"""

from __future__ import annotations

import re
import secrets
import threading
import time

__all__ = ["new_id", "validate_id", "UUIDV7_RE"]

# Каноническая форма UUID длиной 36 символов, вариант RFC 4122 (a/b/8/9)
# и версия 7: ``xxxxxxxx-xxxx-7xxx-[89ab]xxx-xxxxxxxxxxxx``.
UUIDV7_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

_lock = threading.Lock()
_last_int: int = 0


def _compose_uuidv7(timestamp_ms: int, rand_a: int, rand_b: int) -> int:
    """Собирает 128-битное целое UUIDv7 из компонент.

    - 48 бит: ``timestamp_ms``.
    -  4 бита: версия = 7.
    - 12 бит: ``rand_a`` (младшие 12 бит).
    -  2 бита: вариант = 10 (RFC 4122).
    - 62 бита: ``rand_b`` (младшие 62 бита).
    """
    ts = timestamp_ms & ((1 << 48) - 1)
    rand_a &= (1 << 12) - 1
    rand_b &= (1 << 62) - 1
    value = (ts << 80) | (0x7 << 76) | (rand_a << 64) | (0b10 << 62) | rand_b
    return value


def _format_uuid(value: int) -> str:
    hex_str = f"{value:032x}"
    return (
        f"{hex_str[0:8]}-{hex_str[8:12]}-{hex_str[12:16]}-"
        f"{hex_str[16:20]}-{hex_str[20:32]}"
    )


def new_id() -> str:
    """Возвращает новый UUIDv7 в канонической строковой форме (36 символов).

    Монотонность: если в пределах одного процесса генерируется несколько
    id за одну миллисекунду, общий счётчик ``_last_int`` сдвигает новые
    значения вверх минимум на 1.
    """
    global _last_int
    ts_ms = int(time.time() * 1000)
    rand_a = secrets.randbits(12)
    rand_b = secrets.randbits(62)
    candidate = _compose_uuidv7(ts_ms, rand_a, rand_b)
    with _lock:
        if candidate <= _last_int:
            candidate = _last_int + 1
        _last_int = candidate
    return _format_uuid(candidate)


def validate_id(value: str) -> None:
    """Проверяет, что ``value`` — каноническая строка UUIDv7 длиной 36.

    Бросает ``ValueError`` при несоответствии формата (для использования в
    pydantic-валидаторах и тестах).
    """
    if not isinstance(value, str):
        raise ValueError(f"Ожидалась строка UUIDv7, получено {type(value).__name__}")
    if len(value) != 36:
        raise ValueError(
            f"Длина UUID должна быть 36 символов, получено {len(value)}"
        )
    if UUIDV7_RE.fullmatch(value) is None:
        raise ValueError(f"Строка {value!r} не является валидным UUIDv7")
