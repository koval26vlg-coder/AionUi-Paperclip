"""Поиск по памяти SML для дашборда Aion Vision.

Принимает запрос, возвращает JSON-результаты. Сначала пробует семантический
поиск (Ollama + LanceDB); если Ollama недоступна — деградирует на
полнотекстовый FTS5-поиск (тот же фоллбэк, что и в MCP-адаптере). Поле
``mode`` сообщает клиенту, какой режим сработал.

Только чтение БД, без записи в operation log (в отличие от полного
SMLServer) — безопасно вызывать параллельно с работающим MCP-сервером.

Запуск (используется vite middleware /api/search):

    python scripts/search-sml.py --query "конверсия" --limit 10
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = Path(__file__).resolve().parents[3]
DB_PATH = ROOT_DIR / "var" / "sml" / "state.db"
LANCE_PATH = ROOT_DIR / "var" / "sml" / "lance"

sys.path.insert(0, str(ROOT_DIR))

from tools.sml.temporal_store import open_store  # noqa: E402


def _trim(content: str, limit: int = 280) -> str:
    text = " ".join(str(content or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _record_payload(record: Any, score: float) -> dict[str, Any]:
    return {
        "id": record.id,
        "type": record.type,
        "author": record.author_agent,
        "date": record.updated_at,
        "isCurrent": bool(record.is_current),
        "content": _trim(record.content),
        "relevanceScore": round(float(score), 3),
        "tags": list(record.tags or []),
    }


def search(query: str, limit: int) -> dict[str, Any]:
    if not DB_PATH.exists():
        return {"query": query, "mode": "none", "results": [], "error": f"БД не найдена: {DB_PATH}"}

    store = open_store(DB_PATH)
    try:
        # 1) Пытаемся семантику (Ollama + LanceDB).
        try:
            from tools.sml.embedding_engine import build_default_engine

            engine = build_default_engine(LANCE_PATH)
            hits = engine.search(query, limit=limit)
            results: list[dict[str, Any]] = []
            for hit in hits:
                rec = store.read_by_id(hit.record_id)
                if rec is None or not rec.is_current:
                    continue
                results.append(_record_payload(rec, hit.relevance_score))
            if results:
                return {"query": query, "mode": "semantic", "results": results}
            # Пустая семантика — пробуем текст как запасной вариант.
        except Exception:
            # Ollama недоступна / LanceDB пуст / любая ошибка — тихо на текст.
            pass

        # 2) Полнотекстовый FTS5-фоллбэк.
        pairs = store.text_search(query, limit=limit)
        results = [_record_payload(rec, score) for rec, score in pairs]
        return {"query": query, "mode": "text", "results": results}
    finally:
        store.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Поиск по памяти SML")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    limit = max(1, min(50, args.limit))
    query = (args.query or "").strip()
    if not query:
        payload = {"query": "", "mode": "none", "results": []}
    else:
        payload = search(query, limit)

    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
