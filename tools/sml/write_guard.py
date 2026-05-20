"""Интеграционная обвязка для write-пути SML (задача 7.3; P6).

Единая функция ``guard_secret(agent, op, text, op_log)`` вызывается
перед любой записью (``sml.write``, ``sml.add_decision``, ``sml.add_log``):

1. Запускает ``security.check_secret(text)``.
2. Если найден секрет — пишет в ``Operation_Log`` запись ``rejected`` с
   категорией и бросает ``SecretRejectedError`` (без самого секрета).
3. Если всё чисто — возвращает управление без побочных эффектов.

Отдельные write-пути сами решают, что писать в Operation_Log на успехе —
у них разный ``record_id`` и иные детали.
"""

from __future__ import annotations

from typing import Optional

from .errors import SecretRejectedError
from .operation_log import OperationLog
from .security import check_secret

__all__ = ["guard_secret"]


def guard_secret(
    *,
    agent: str,
    op: str,
    text: str,
    op_log: Optional[OperationLog] = None,
    record_id: Optional[str] = None,
    operation_id: Optional[str] = None,
) -> None:
    """Если ``text`` содержит секрет — отклоняет операцию.

    При обнаружении секрета в Operation_Log пишется запись с
    ``result="rejected"`` и ``reason_category`` из детектора. Далее
    бросается ``SecretRejectedError`` без значения самого секрета.
    """
    check = check_secret(text)
    if not check.is_secret:
        return
    if op_log is not None:
        op_log.log(
            agent=agent,
            op=op,
            result="rejected",
            record_id=record_id,
            reason_category=check.reason_category or "secret_rejected",
            operation_id=operation_id,
        )
    raise SecretRejectedError.for_reason(check.reason_category or "unknown")
