"""Бенчмарк `TemporalStore.read_by_id` на 10 000 записей.

Цель: p99 ≤ 200 мс (Req 11.3).

Запуск из pwsh:
    $env:PYTHONUTF8='1'; $env:PYTHONPATH='D:\\AionUi-Paperclip'; \
        D:\\AionUi-Paperclip\\.venv-sml\\Scripts\\python.exe \
        -m tools.sml.bench.bench_read
"""

from __future__ import annotations

import random
import statistics
import tempfile
import time
from pathlib import Path

from tools.sml.temporal_store import make_new_record, open_store


def run(n: int = 10_000, samples: int = 1_000) -> dict[str, float]:
    tmp = Path(tempfile.mkdtemp(prefix="sml-bench-"))
    db_path = tmp / "bench.db"
    store = open_store(db_path)
    ids: list[str] = []
    types = ["fact", "preference", "decision", "agent_log", "task", "constraint", "timeline_event"]
    try:
        t0 = time.perf_counter()
        for i in range(n):
            rec = make_new_record(
                type=types[i % len(types)],
                content=f"синтетическая запись №{i} — русский текст с эмодзи ✅",
                author_agent="kiro",
                tags=[f"bench-{i % 100}"],
            )
            store.insert(rec)
            ids.append(rec.id)
        insert_total = time.perf_counter() - t0
        print(f"Inserted {n} records in {insert_total:.2f}s ({n / insert_total:.1f} rec/s)")

        # Разогрев
        for _ in range(100):
            store.read_by_id(random.choice(ids))

        # Измерения
        timings_ms: list[float] = []
        for _ in range(samples):
            rid = random.choice(ids)
            t = time.perf_counter()
            store.read_by_id(rid)
            timings_ms.append((time.perf_counter() - t) * 1000)

        timings_ms.sort()
        p50 = timings_ms[int(0.50 * samples)]
        p95 = timings_ms[int(0.95 * samples)]
        p99 = timings_ms[int(0.99 * samples)]
        mean = statistics.mean(timings_ms)
        print(
            f"read_by_id over {samples} samples: "
            f"mean={mean:.3f}ms, p50={p50:.3f}ms, p95={p95:.3f}ms, p99={p99:.3f}ms"
        )
        return {"mean": mean, "p50": p50, "p95": p95, "p99": p99, "samples": samples}
    finally:
        store.close()


if __name__ == "__main__":
    stats = run()
    limit = 200.0
    status = "OK" if stats["p99"] <= limit else "FAIL"
    print(f"SLA p99 ≤ {limit}ms → {status}")
