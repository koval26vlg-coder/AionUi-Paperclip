"""Единый формат ответов MCP-инструментов SML.

Все ответы имеют поле ``ok`` (bool). Для ``ok=false`` — вложенный объект
``error`` с категорией, русскоязычным сообщением и ``operation_id``.

Требования: Req 2.5, Req 5.4, Req 9.3.
"""

from __future__ import annotations

from typing import Any, Dict

from .errors import SMLError

__all__ = ["ok_response", "error_response", "format_score"]


def ok_response(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Собирает успешный ответ ``{"ok": true, ...payload}``.

    Поле ``ok`` всегда идёт первым для удобства человека, читающего лог.
    """
    response: Dict[str, Any] = {"ok": True}
    if payload:
        response.update(payload)
    return response


def error_response(err: SMLError, operation_id: str) -> Dict[str, Any]:
    """Собирает ответ-ошибку для MCP-клиента.

    Сообщение возвращается в UTF-8 без экранирования — JSON-сериализация
    должна выполняться с ``ensure_ascii=False`` (Req 9.3).
    """
    return {
        "ok": False,
        "error": {
            "category": err.category,
            "message": err.message,
            "operation_id": operation_id,
        },
    }


def format_score(value: float) -> float:
    """Округляет релевантность до трёх знаков в диапазоне [0.0, 1.0].

    Выход требования 5.4 — ``relevance_score`` с точностью не менее трёх
    знаков после запятой. Значение за пределами ``[0, 1]`` обрезается.
    """
    clamped = max(0.0, min(1.0, float(value)))
    return round(clamped, 3)
