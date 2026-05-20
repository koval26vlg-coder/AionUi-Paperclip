"""Бенчмарк EmbeddingEngine.search на Typical_Volume = 10 000 записей.

Цель: p99 ≤ 500 мс (Req 11.1).

Использует реальную Ollama с bge-m3 и LanceDB в временной директории.
Чтобы не дёргать Ollama 10 000 раз, эмбеддинги кешируем на диск между
прогонами: при повторном запуске с тем же `cache_path` векторы
переиспользуются.
"""

from __future__ import annotations

import json
import random
import statistics
import tempfile
import time
from pathlib import Path
from typing import Iterable

from tools.sml.embedding_engine import (
    EmbeddingStore,
    OllamaEmbedder,
    EmbeddingEngine,
    EMBEDDING_DIM,
)


RUSSIAN_SEED_PHRASES = [
    "Shared_Memory_Layer хранит факты, решения и журналы",
    "агент записывает отчёт о сессии в docs/agent-log",
    "Codex, Cursor и Kiro подключаются через MCP",
    "pydantic v2 валидирует входные данные",
    "UUIDv7 обеспечивает монотонность идентификаторов",
    "SQLite работает в режиме WAL с synchronous=NORMAL",
    "Ollama обслуживает эмбеддинги модели bge-m3",
    "LanceDB хранит 1024-мерные векторы во встроенном виде",
    "семантический поиск опирается на косинусную близость",
    "временные запросы реконструируют историю записей",
    "рецепт супа харчо с бараниной",
    "прогноз погоды на выходные",
    "настройка CI/CD пайплайна",
    "отладка сегфолта в C++",
    "приготовление тирамису",
    "анализ временных рядов в pandas",
    "заявка на отпуск",
    "починить кран на кухне",
    "игра в шахматы по почте",
    "документация по API PostgreSQL",
]


def synthetic_content(index: int) -> str:
    """Генерирует псевдоразнообразный русский текст, чтобы эмбеддинги не дублировались."""
    seed = RUSSIAN_SEED_PHRASES[index % len(RUSSIAN_SEED_PHRASES)]
    return f"{seed} №{index} — синтетическая запись для бенчмарка ✅"


def precompute_vectors(
    n: int,
    embedder: OllamaEmbedder,
    cache_path: Path,
) -> list[tuple[str, list[float]]]:
    """Готовит пары (id, vector) для n записей. Кеширует на диск."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache: dict[str, list[float]] = {}
    if cache_path.exists():
        with cache_path.open("r", encoding="utf-8") as fh:
            cache = json.load(fh)

    out: list[tuple[str, list[float]]] = []
    dirty = False
    t0 = time.perf_counter()
    for i in range(n):
        text = synthetic_content(i)
        rid = f"bench-{i:06d}"
        if rid in cache:
            vec = cache[rid]
        else:
            vec = embedder.embed_text(text)
            cache[rid] = vec
            dirty = True
        out.append((rid, vec))
        if dirty and (i + 1) % 500 == 0:
            print(f"  … подготовлено {i + 1}/{n} векторов ({time.perf_counter() - t0:.1f}s)")
    if dirty:
        with cache_path.open("w", encoding="utf-8") as fh:
            json.dump(cache, fh)
    return out


def run(n: int = 10_000, samples: int = 200) -> dict[str, float]:
    tmp = Path(tempfile.mkdtemp(prefix="sml-bench-sem-"))
    lance_path = tmp / "lance"
    cache = Path("D:/AionUi-Paperclip/var/sml/bench-embed-cache.json")

    embedder = OllamaEmbedder()
    store = EmbeddingStore.open(lance_path)

    print(f"Подготовка {n} эмбеддингов (кеш: {cache})")
    pairs = precompute_vectors(n, embedder, cache)

    print("Загрузка векторов в LanceDB…")
    t0 = time.perf_counter()
    # Батчевая вставка через add
    rows = [{"id": rid, "vector": vec} for rid, vec in pairs]
    store._table.add(rows)  # type: ignore[attr-defined]
    insert_total = time.perf_counter() - t0
    print(f"LanceDB add {n} rows: {insert_total:.2f}s")

    engine = EmbeddingEngine(embedder, store)

    # Разогрев
    for _ in range(3):
        engine.search("подготовка контекста", limit=20)

    # Измерения на разных запросах, чтобы не пользоваться кешом Ollama
    queries = [
        "как устроена общая память агентов",
        "временные запросы и супер",
        "семантический поиск на русском",
        "детерминированные эмбеддинги bge-m3",
        "SQLite WAL durability",
        "документация PostgreSQL",
        "прогноз погоды",
        "рецепт борща",
        "починка крана",
        "анализ временных рядов",
    ]

    timings_ms: list[float] = []
    for i in range(samples):
        q = queries[i % len(queries)]
        t = time.perf_counter()
        engine.search(q, limit=20)
        timings_ms.append((time.perf_counter() - t) * 1000)

    timings_ms.sort()
    p50 = timings_ms[int(0.50 * samples)]
    p95 = timings_ms[int(0.95 * samples)]
    p99 = timings_ms[min(int(0.99 * samples), samples - 1)]
    mean = statistics.mean(timings_ms)
    print(
        f"semantic_query over {samples} samples (n={n}): "
        f"mean={mean:.1f}ms, p50={p50:.1f}ms, p95={p95:.1f}ms, p99={p99:.1f}ms"
    )
    limit = 500.0
    status = "OK" if p99 <= limit else "FAIL"
    print(f"SLA p99 ≤ {limit}ms → {status}")
    return {"mean": mean, "p50": p50, "p95": p95, "p99": p99}


if __name__ == "__main__":
    run()
