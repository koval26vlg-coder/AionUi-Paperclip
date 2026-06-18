r"""Ежедневный бэкап БД SML с ротацией.

Делает консистентную копию ``var/sml/state.db`` через ``VACUUM INTO`` —
это безопасно даже при включённом WAL (захватывает зафиксированное
состояние без копирования сырого WAL-файла). Копии складываются в
``var/sml/backups/state-YYYY-MM-DD.db``. Хранится ``--keep`` последних.

Память SML — единственный экземпляр в одном файле (~1.4 МБ) без бэкапа,
поэтому случайное повреждение означало бы потерю всей общей памяти.

Запуск:

    .venv-sml\Scripts\python.exe -X utf8 tools\backup-sml.py            # сделать бэкап сейчас
    .venv-sml\Scripts\python.exe -X utf8 tools\backup-sml.py --if-stale # только если за сегодня нет
    .venv-sml\Scripts\python.exe -X utf8 tools\backup-sml.py --keep 30  # хранить 30 копий

``--if-stale`` используется watcher-ом: он вызывается часто, но бэкап
делается не чаще одного раза в день.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "var" / "sml" / "state.db"
BACKUP_DIR = ROOT_DIR / "var" / "sml" / "backups"


def _today_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _backup_path(stamp: str) -> Path:
    return BACKUP_DIR / f"state-{stamp}.db"


def _records_count(db_path: Path) -> int:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        return int(conn.execute("SELECT COUNT(*) FROM records").fetchone()[0])
    finally:
        conn.close()


def make_backup(db_path: Path, target: Path) -> None:
    """Консистентная копия через VACUUM INTO (безопасно при WAL)."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        # VACUUM INTO требует, чтобы целевого файла не существовало.
        conn.execute("VACUUM INTO ?", (str(target),))
    finally:
        conn.close()


def verify_backup(db_path: Path, target: Path) -> tuple[bool, str]:
    """Проверяет, что копия открывается и число записей совпадает с оригиналом.

    Бэкап, который не проверяли восстановлением, нельзя считать бэкапом.
    Возвращает ``(ok, message)``.
    """
    if not target.exists():
        return False, f"копия не создана: {target}"
    try:
        # integrity_check ловит повреждение файла копии.
        conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
        try:
            integ = conn.execute("PRAGMA integrity_check").fetchone()[0]
        finally:
            conn.close()
        if integ != "ok":
            return False, f"integrity_check копии: {integ}"
        src = _records_count(db_path)
        dst = _records_count(target)
        if src != dst:
            return False, f"расхождение числа записей: оригинал {src}, копия {dst}"
        return True, f"проверено: {dst} записей, integrity ok"
    except sqlite3.Error as exc:
        return False, f"ошибка чтения копии: {exc}"


def rotate(backup_dir: Path, keep: int) -> list[Path]:
    """Оставляет ``keep`` самых свежих бэкапов, остальные удаляет."""
    backups = sorted(
        backup_dir.glob("state-*.db"),
        key=lambda p: p.name,
        reverse=True,
    )
    removed: list[Path] = []
    for old in backups[keep:]:
        old.unlink()
        removed.append(old)
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Бэкап БД SML с ротацией")
    parser.add_argument("--db", type=Path, default=DB_PATH, help="Путь к state.db")
    parser.add_argument("--keep", type=int, default=14, help="Сколько копий хранить")
    parser.add_argument(
        "--if-stale",
        action="store_true",
        help="Делать бэкап только если за сегодня его ещё нет",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="После копии проверить integrity и совпадение числа записей",
    )
    args = parser.parse_args()

    if not args.db.exists():
        print(f"Ошибка: БД не найдена: {args.db}", file=sys.stderr)
        return 1

    stamp = _today_stamp()
    target = _backup_path(stamp)

    if args.if_stale and target.exists():
        return 0

    make_backup(args.db, target)
    size_kb = target.stat().st_size / 1024
    print(f"Бэкап создан: {target} ({size_kb:.0f} КБ)")

    if args.verify:
        ok, message = verify_backup(args.db, target)
        print(f"Verify: {message}")
        if not ok:
            print("ОШИБКА: бэкап не прошёл проверку!", file=sys.stderr)
            return 1

    removed = rotate(BACKUP_DIR, args.keep)
    if removed:
        print(f"Удалено старых копий: {len(removed)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
