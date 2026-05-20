from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APP_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = Path(__file__).resolve().parents[3]
DB_PATH = ROOT_DIR / "var" / "sml" / "state.db"
DEFAULT_OUT = APP_DIR / "public" / "aion-data.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _empty_payload(message: str) -> dict[str, Any]:
    return {
        "generatedAt": _utc_now(),
        "status": {"state": "error", "label": "Ошибка данных", "message": message},
        "totals": {
            "recordsTotal": 0,
            "currentRecords": 0,
            "supersededRecords": 0,
            "authorsTotal": 0,
            "sourceFilesTotal": 0,
        },
        "records": [],
        "typeCounts": [],
        "dailyActivity": [],
        "agents": [],
    }


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _scalar(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> int:
    value = conn.execute(sql, params).fetchone()[0]
    return int(value or 0)


def _trim_content(content: str, limit: int = 900) -> str:
    text = " ".join(str(content or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _agent_status(last_updated: str | None) -> str:
    if not last_updated:
        return "Нет данных"
    try:
        parsed = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
    except ValueError:
        return "Проверить"
    age_seconds = (datetime.now(timezone.utc) - parsed).total_seconds()
    if age_seconds <= 48 * 60 * 60:
        return "Активен"
    return "Архив"


def build_payload(db_path: Path = DB_PATH) -> dict[str, Any]:
    if not db_path.exists():
        return _empty_payload(f"SML SQLite не найден: {db_path}")

    try:
        with _connect(db_path) as conn:
            records_total = _scalar(conn, "SELECT COUNT(*) FROM records WHERE deleted_at IS NULL")
            current_records = _scalar(
                conn,
                "SELECT COUNT(*) FROM records WHERE deleted_at IS NULL AND is_current = 1",
            )
            superseded_records = max(0, records_total - current_records)
            authors_total = _scalar(
                conn,
                "SELECT COUNT(DISTINCT author_agent) FROM records WHERE deleted_at IS NULL",
            )
            source_files_total = _scalar(
                conn,
                "SELECT COUNT(DISTINCT source_file) FROM records WHERE deleted_at IS NULL AND source_file IS NOT NULL",
            )

            latest_rows = conn.execute(
                """
                SELECT id, type, content, author_agent, created_at, updated_at,
                       is_current, source_file, source_lines, tags_json
                  FROM records
                 WHERE deleted_at IS NULL
                 ORDER BY updated_at DESC
                 LIMIT 12
                """
            ).fetchall()
            records = [
                {
                    "id": row["id"],
                    "type": row["type"],
                    "author": row["author_agent"],
                    "date": row["updated_at"],
                    "createdAt": row["created_at"],
                    "content": _trim_content(row["content"]),
                    "isCurrent": bool(row["is_current"]),
                    "sourceFile": row["source_file"],
                    "sourceLines": row["source_lines"],
                    "tags": json.loads(row["tags_json"] or "[]"),
                }
                for row in latest_rows
            ]

            type_counts = [
                {
                    "type": row["type"],
                    "total": int(row["total"] or 0),
                    "current": int(row["current"] or 0),
                }
                for row in conn.execute(
                    """
                    SELECT type,
                           COUNT(*) AS total,
                           SUM(CASE WHEN is_current = 1 THEN 1 ELSE 0 END) AS current
                      FROM records
                     WHERE deleted_at IS NULL
                     GROUP BY type
                     ORDER BY total DESC, type ASC
                    """
                ).fetchall()
            ]

            daily_activity = [
                {
                    "date": row["day"],
                    "total": int(row["total"] or 0),
                    "current": int(row["current"] or 0),
                }
                for row in conn.execute(
                    """
                    SELECT substr(updated_at, 1, 10) AS day,
                           COUNT(*) AS total,
                           SUM(CASE WHEN is_current = 1 THEN 1 ELSE 0 END) AS current
                      FROM records
                     WHERE deleted_at IS NULL
                     GROUP BY day
                     ORDER BY day DESC
                     LIMIT 10
                    """
                ).fetchall()[::-1]
            ]

            agents = [
                {
                    "name": row["author_agent"],
                    "records": int(row["records"] or 0),
                    "lastUpdated": row["last_updated"],
                    "status": _agent_status(row["last_updated"]),
                }
                for row in conn.execute(
                    """
                    SELECT author_agent,
                           COUNT(*) AS records,
                           MAX(updated_at) AS last_updated
                      FROM records
                     WHERE deleted_at IS NULL
                     GROUP BY author_agent
                     ORDER BY records DESC, author_agent ASC
                     LIMIT 8
                    """
                ).fetchall()
            ]

            # NexusGraph: расчет связей
            # 1. Связи через общие файлы
            collab_rows = conn.execute(
                """
                SELECT a.author_agent as source, b.author_agent as target, COUNT(*) as weight
                FROM records a
                JOIN records b ON a.source_file = b.source_file
                WHERE a.author_agent < b.author_agent 
                  AND a.source_file IS NOT NULL
                  AND a.deleted_at IS NULL AND b.deleted_at IS NULL
                GROUP BY a.author_agent, b.author_agent
                """
            ).fetchall()
            
            # 2. Связи через замещение (supersede)
            supersede_rows = conn.execute(
                """
                SELECT author_agent as source, superseded_by_agent as target, COUNT(*) as weight
                FROM (
                    SELECT r1.author_agent, r2.author_agent as superseded_by_agent
                    FROM records r1
                    JOIN records r2 ON r1.id = r2.supersedes_id
                    WHERE r1.author_agent != r2.author_agent
                      AND r1.deleted_at IS NULL AND r2.deleted_at IS NULL
                )
                GROUP BY source, target
                """
            ).fetchall()

            nexus_nodes = [{"id": a["name"], "records": a["records"]} for a in agents]
            nexus_links = []
            for r in collab_rows:
                nexus_links.append({"source": r["source"], "target": r["target"], "type": "collab", "weight": r["weight"]})
            for r in supersede_rows:
                nexus_links.append({"source": r["source"], "target": r["target"], "type": "supersede", "weight": r["weight"]})

            state = "live" if records_total else "empty"
            return {
                "generatedAt": _utc_now(),
                "status": {
                    "state": state,
                    "label": "SML подключен" if state == "live" else "SML пуст",
                    "message": f"Прочитано записей: {records_total}. Источник: {db_path}",
                },
                "totals": {
                    "recordsTotal": records_total,
                    "currentRecords": current_records,
                    "supersededRecords": superseded_records,
                    "authorsTotal": authors_total,
                    "sourceFilesTotal": source_files_total,
                },
                "records": records,
                "typeCounts": type_counts,
                "dailyActivity": daily_activity,
                "agents": agents,
                "nexusGraph": {
                    "nodes": nexus_nodes,
                    "links": nexus_links
                }
            }
    except Exception as exc:
        return _empty_payload(f"Не удалось прочитать SML SQLite: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print dashboard JSON to stdout")
    parser.add_argument("--out", type=Path, default=None, help="Write dashboard JSON snapshot")
    args = parser.parse_args()

    payload = build_payload()
    text = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.json:
        sys.stdout.reconfigure(encoding="utf-8")
        print(text)

    out = args.out
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")

    if not args.json and out is None:
        DEFAULT_OUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_OUT.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {DEFAULT_OUT}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
