"""Ядро SML_Core — CLI для проверки состояния общей памяти из терминала.

Подкоманды:

- ``selfcheck`` — проверка готовности пакета (импорт, UUIDv7, метка
  времени, полный набор типов). Печатает ``sml-selfcheck-ok``.
- ``ping``      — проверка доступности БД ``var/sml/state.db``.
- ``stats``     — компактная сводка по памяти (записи, агенты, типы).

Флаг ``--selfcheck`` сохранён для обратной совместимости.

Требования: Req 1.1 (MCP-сервер как процесс), Req 4.1 (перечень типов
Memory_Record), Req 9.3 (русские сообщения).
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from . import __version__
from .errors import SMLError
from .ids import new_id, validate_id
from .timefmt import now_utc_ms
from .validation import MEMORY_TYPE_VALUES


def _default_db_path() -> Path:
    """Путь к state.db: ``<repo>/var/sml/state.db`` (две папки вверх от пакета)."""
    return Path(__file__).resolve().parents[2] / "var" / "sml" / "state.db"


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


def _ping(db_path: Path) -> int:
    """Проверяет, что БD SML существует и открывается на чтение."""
    if not db_path.exists():
        print(f"sml-ping-fail: БД не найдена: {db_path}", file=sys.stderr)
        return 1
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            total = conn.execute(
                "SELECT COUNT(*) FROM records WHERE deleted_at IS NULL"
            ).fetchone()[0]
        finally:
            conn.close()
    except Exception as exc:
        print(f"sml-ping-fail: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print(f"sml-ping-ok: {db_path} ({total} записей)")
    return 0


def _stats(db_path: Path) -> int:
    """Печатает компактную сводку по общей памяти."""
    if not db_path.exists():
        print(f"sml-stats-fail: БД не найдена: {db_path}", file=sys.stderr)
        return 1
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        try:
            total = conn.execute(
                "SELECT COUNT(*) FROM records WHERE deleted_at IS NULL"
            ).fetchone()[0]
            current = conn.execute(
                "SELECT COUNT(*) FROM records WHERE deleted_at IS NULL AND is_current = 1"
            ).fetchone()[0]
            authors = conn.execute(
                """
                SELECT author_agent, COUNT(*) AS n, MAX(updated_at) AS last
                  FROM records WHERE deleted_at IS NULL
                 GROUP BY author_agent ORDER BY n DESC
                """
            ).fetchall()
            types = conn.execute(
                """
                SELECT type, COUNT(*) AS n
                  FROM records WHERE deleted_at IS NULL
                 GROUP BY type ORDER BY n DESC
                """
            ).fetchall()
        finally:
            conn.close()
    except Exception as exc:
        print(f"sml-stats-fail: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print(f"SML v{__version__} — {db_path}")
    print(f"Записей: {total} (актуальных {current}, замещённых {total - current})")
    print(f"Агентов: {len(authors)}")
    for row in authors:
        print(f"  {row['author_agent']:<16} {row['n']:>4}  посл. {row['last']}")
    print("Типы:")
    for row in types:
        print(f"  {row['type']:<16} {row['n']:>4}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sml-core",
        description=f"Shared_Memory_Layer Core v{__version__}",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["selfcheck", "ping", "stats"],
        help="Подкоманда: selfcheck | ping | stats",
    )
    parser.add_argument(
        "--selfcheck",
        action="store_true",
        help="Алиас команды selfcheck (обратная совместимость)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Путь к state.db (по умолчанию var/sml/state.db)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    db_path = args.db or _default_db_path()

    command = args.command
    if args.selfcheck:
        command = "selfcheck"

    if command == "selfcheck":
        return _selfcheck()
    if command == "ping":
        return _ping(db_path)
    if command == "stats":
        return _stats(db_path)

    # Без команды — короткая справка вместо WIP-заглушки.
    print("sml-core: укажите команду — selfcheck | ping | stats")
    print("Пример: python -m tools.sml.core stats")
    return 0


if __name__ == "__main__":
    sys.exit(main())
