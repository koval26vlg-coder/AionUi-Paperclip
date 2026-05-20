"""Интеграционный тест сосуществования SML и tools/watch-memory.ps1 (задача 6.9).

Тест запускается руками (не через pytest), потому что:
- использует реальный `tools/build-context-pack.ps1` через pwsh;
- дёргает систему параллельно в течение ~30 секунд;
- пишет в реальный `docs/context-packs/context-pack-latest.md`.

Алгоритм:
1. Сохраняем исходное содержимое `docs/context-packs/context-pack-latest.md`.
2. Запускаем два потока:
   - PS-поток: 30 раз зовёт `tools/build-context-pack.ps1`.
   - SML-поток: 30 раз зовёт `sml.build_context_pack` через SMLServer.
3. Проверяем:
   - итоговый файл корректный Markdown (начинается с `# Контекстный пакет`);
   - количество `conflict`-ошибок в Operation_Log ≤ 10% от 30 = 3;
   - не возникло фатальных исключений;
4. Восстанавливаем исходное содержимое файла.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.sml.mcp_adapter import SMLServer, handle_request  # noqa: E402


def _pwsh() -> str:
    return r"C:\Program Files\PowerShell\7\pwsh.exe"


def _build_via_ps(iterations: int, errors: list) -> None:
    script = PROJECT_ROOT / "tools" / "build-context-pack.ps1"
    for i in range(iterations):
        try:
            subprocess.run(
                [_pwsh(), "-NoProfile", "-File", str(script)],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(PROJECT_ROOT),
            )
        except Exception as exc:  # pragma: no cover
            errors.append(("ps", i, str(exc)))
        time.sleep(0.1)


def _build_via_sml(iterations: int, conflicts: list, errors: list) -> None:
    srv = SMLServer.from_defaults()
    try:
        for i in range(iterations):
            try:
                resp = handle_request(
                    srv,
                    {
                        "jsonrpc": "2.0",
                        "id": 1000 + i,
                        "method": "tools/call",
                        "params": {
                            "name": "sml.build_context_pack",
                            "arguments": {"reason": f"integration-{i}"},
                        },
                    },
                )
                body = resp["result"]
                if not body["ok"]:
                    cat = body["error"]["category"]
                    if cat == "conflict":
                        conflicts.append(i)
                    else:
                        errors.append(("sml", i, cat))
            except Exception as exc:  # pragma: no cover
                errors.append(("sml", i, str(exc)))
            time.sleep(0.1)
    finally:
        srv.close()


def run() -> None:
    pack_path = PROJECT_ROOT / "docs" / "context-packs" / "context-pack-latest.md"
    backup_path = pack_path.with_suffix(".integration-backup.md")
    if pack_path.exists():
        shutil.copyfile(pack_path, backup_path)

    iterations = 30
    errors: list = []
    conflicts: list = []

    ps_thread = threading.Thread(target=_build_via_ps, args=(iterations, errors))
    sml_thread = threading.Thread(
        target=_build_via_sml, args=(iterations, conflicts, errors)
    )

    start = time.time()
    ps_thread.start()
    sml_thread.start()
    ps_thread.join()
    sml_thread.join()
    elapsed = time.time() - start

    ok = True
    print(f"Elapsed: {elapsed:.1f}s for {iterations} × 2 iterations")
    print(f"SML conflicts: {len(conflicts)} / {iterations} ({len(conflicts)*100/iterations:.1f}%)")
    print(f"Fatal errors: {len(errors)}")
    for err in errors[:5]:
        print(f"  - {err}")

    if pack_path.exists():
        content = pack_path.read_text(encoding="utf-8")
        head = content.splitlines()[0] if content.splitlines() else ""
        print(f"Pack first line: {head!r}")
        if not head.startswith("# Контекстный пакет"):
            print("FAIL: pack is not a valid context pack")
            ok = False
    else:
        print("FAIL: pack disappeared")
        ok = False

    if len(conflicts) > iterations * 0.1:
        print("FAIL: conflict rate > 10%")
        ok = False
    if errors:
        print("FAIL: fatal errors present")
        ok = False

    # Восстанавливаем исходное содержимое
    if backup_path.exists():
        shutil.copyfile(backup_path, pack_path)
        backup_path.unlink()

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    run()
