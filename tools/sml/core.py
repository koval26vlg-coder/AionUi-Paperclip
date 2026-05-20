"""Ядро SML_Core.

Пока содержит только CLI-флаг ``--selfcheck`` (задача 2.1), который
проверяет, что пакет импортируется, а базовые модули готовы к работе.

Требования: Req 1.1 (MCP-сервер как процесс), Req 4.1 (перечень типов
Memory_Record), Req 9.3 (русские сообщения).
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .errors import SMLError
from .ids import new_id, validate_id
from .timefmt import now_utc_ms
from .validation import MEMORY_TYPE_VALUES


def _selfcheck() -> int:
    """Минимальная проверка готовности пакета.

    1. Импортируются базовые модули (уже сделано выше).
    2. Генератор UUIDv7 возвращает валидный id.
    3. Метка времени парсится обратно (round-trip проверяется в timefmt).
    4. Все 8 типов Memory_Record присутствуют.

    Печатает ``sml-selfcheck-ok`` и возвращает 0 при успехе.
    """
    try:
        # (1) импорт моделей и валидации
        from . import models, validation, response  # noqa: F401

        # (2) UUIDv7 и (3) метка времени
        new_ident = new_id()
        validate_id(new_ident)
        _ = now_utc_ms()

        # (4) закрытый список типов
        expected_types = {
            "fact", "preference", "decision", "agent_log",
            "task", "task_link", "constraint", "timeline_event",
        }
        if expected_types != MEMORY_TYPE_VALUES:
            print(
                f"sml-selfcheck-fail: неожиданный набор MemoryType={sorted(MEMORY_TYPE_VALUES)}",
                file=sys.stderr,
            )
            return 1
    except SMLError as exc:
        print(f"sml-selfcheck-fail: SMLError {exc.category}: {exc.message}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - страховка
        print(f"sml-selfcheck-fail: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print("sml-selfcheck-ok")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sml-core",
        description=f"Shared_Memory_Layer Core v{__version__}",
    )
    parser.add_argument(
        "--selfcheck",
        action="store_true",
        help="Проверить готовность пакета и выйти (печатает sml-selfcheck-ok)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.selfcheck:
        return _selfcheck()
    print("sml-core: запуск без --selfcheck пока не реализован (см. задачу 5.1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
