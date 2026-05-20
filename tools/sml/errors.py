"""Типизированные ошибки SML.

Каждая ошибка имеет фиксированную категорию (``category``) из ровно семи
допустимых значений, которые единообразно возвращаются клиенту через
MCP-ответ. Сообщения — на русском языке (Req 9.3).

Требования: Req 2.5, Req 3.5, Req 4.3, Req 6.3, Req 9.3, Req 10.2, Req 11.4.
"""

from __future__ import annotations

from typing import Literal, Optional

__all__ = [
    "ErrorCategory",
    "SMLError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "SecretRejectedError",
    "IOErrorSML",
    "TimeoutErrorSML",
    "UnsupportedError",
]

ErrorCategory = Literal[
    "validation",
    "not_found",
    "conflict",
    "secret_rejected",
    "io_error",
    "timeout",
    "unsupported",
]


class SMLError(Exception):
    """Базовый класс всех ошибок SML.

    Атрибуты:
    - ``category``  — фиксированная категория для клиента (``ErrorCategory``).
    - ``message``   — русскоязычное сообщение об ошибке.
    - ``operation_id`` — идентификатор операции из ``Operation_Log``.
    """

    category: ErrorCategory = "io_error"

    def __init__(
        self,
        message: str,
        *,
        operation_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.operation_id = operation_id

    def __str__(self) -> str:  # pragma: no cover - тривиально
        return self.message


class ValidationError(SMLError):
    """Нарушение границ полей, формата или обязательности."""

    category: ErrorCategory = "validation"

    @classmethod
    def for_field(cls, field: str, reason: str) -> "ValidationError":
        return cls(f"Поле {field!r}: {reason}")


class NotFoundError(SMLError):
    """Запрошенный объект не существует (например, неизвестный id)."""

    category: ErrorCategory = "not_found"

    @classmethod
    def for_id(cls, record_id: str) -> "NotFoundError":
        return cls(f"Memory_Record с идентификатором {record_id!r} не найден")


class ConflictError(SMLError):
    """Коллизия состояния: дубликат, блокировка, уже суперседировано."""

    category: ErrorCategory = "conflict"


class SecretRejectedError(SMLError):
    """Обнаружен секрет в содержимом записи — операция отклонена."""

    category: ErrorCategory = "secret_rejected"

    @classmethod
    def for_reason(cls, reason_category: str) -> "SecretRejectedError":
        # Сообщение не содержит самого значения секрета — только категорию.
        return cls(
            f"Содержимое отклонено: обнаружен секрет (категория причины: {reason_category})"
        )


class IOErrorSML(SMLError):
    """Сбой ввода-вывода (диск, файл, сеть loopback, SQLite и т.п.)."""

    category: ErrorCategory = "io_error"


class TimeoutErrorSML(SMLError):
    """Операция не уложилась в установленный лимит времени."""

    category: ErrorCategory = "timeout"


class UnsupportedError(SMLError):
    """Запрошенная возможность не поддерживается (например, неизвестный тип)."""

    category: ErrorCategory = "unsupported"
