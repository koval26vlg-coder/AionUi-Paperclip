r"""Разовая (и повторяемая) нормализация author_agent в БД SML.

Приводит исторические записи к каноническим именам агентов
(см. ``tools/sml/validation.AUTHOR_CANONICAL``): codex→Codex,
gemini/Gemini-CLI→Gemini CLI, claude→Claude Code и т.д.

Устраняет «расщепление личности» агентов, из-за которого дашборд
показывал больше авторов, чем есть, и строил лишние узлы в графе связей.

Запуск:

    .venv-sml\Scripts\python.exe -X utf8 tools\normalize-sml-authors.py          # применить
    .venv-sml\Scripts\python.exe -X utf8 tools\normalize-sml-authors.py --dry-run # только показать

Безопасность: обновляется только колонка ``author_agent`` в таблице
``records``. Контент, эмбеддинги и content_hash не затрагиваются.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "var" / "sml" / "state.db"

# Импортируем единый источник правды по нормализации из пакета SML.
sys.path.insert(0, str(ROOT_DIR))
from tools.sml.validation import normalize_author  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Нормализация author_agent в SML")
    parser.add_argument("--db", type=Path, default=DB_PATH, help="Путь к state.db")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать запланированные изменения, не записывать",
    )
    args = parser.parse_args()

    if not args.db.exists():
        print(f"Ошибка: БД не найдена: {args.db}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(str(args.db))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT DISTINCT author_agent FROM records WHERE deleted_at IS NULL"
        ).fetchall()

        changes: list[tuple[str, str, int]] = []
        for row in rows:
            old = row["author_agent"]
            new = normalize_author(old)
            if new != old:
                cnt = conn.execute(
                    "SELECT COUNT(*) FROM records WHERE author_agent = ?", (old,)
                ).fetchone()[0]
                changes.append((old, new, int(cnt)))

        if not changes:
            print("Изменений не требуется: все имена авторов уже канонические.")
            return 0

        print("Запланированные изменения author_agent:")
        total = 0
        for old, new, cnt in changes:
            print(f"  {old!r:>24} -> {new!r:<16} ({cnt} зап.)")
            total += cnt
        print(f"Итого записей к обновлению: {total}")

        if args.dry_run:
            print("\n[dry-run] Изменения НЕ применены.")
            return 0

        for old, new, _cnt in changes:
            conn.execute(
                "UPDATE records SET author_agent = ? WHERE author_agent = ?",
                (new, old),
            )
        conn.commit()
        print("\nГотово: имена авторов нормализованы.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
