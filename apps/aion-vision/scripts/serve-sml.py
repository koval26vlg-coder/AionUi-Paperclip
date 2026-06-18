"""Постоянный HTTP-сервис Aion Vision поверх SML (stdlib, без зависимостей).

В отличие от vite middleware (живёт только в `npm run dev`), этот сервис
работает и для прод-сборки: отдаёт статику из `dist/` и те же API:

- ``GET /api/sml-dashboard`` — текущее состояние памяти (как export-sml-dashboard);
- ``GET /api/search?q=…&limit=…`` — поиск по памяти (семантика + FTS5-фоллбэк);
- всё остальное — статика из ``dist/`` с SPA-фоллбэком на ``index.html``.

Бэкенд-логика переиспользуется из соседних скриптов (`build_payload`,
`search`) через importlib — без дублирования и без подпроцессов на запрос.

Запуск:
    python scripts/serve-sml.py --host 127.0.0.1 --port 8787
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

APP_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = APP_DIR / "scripts"
DIST_DIR = APP_DIR / "dist"

_CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
    ".woff2": "font/woff2",
}


def _load_module(name: str, filename: str):
    """Импортирует скрипт с дефисом в имени через importlib."""
    path = SCRIPTS_DIR / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Не удалось загрузить {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_dashboard = _load_module("export_sml_dashboard", "export-sml-dashboard.py")
_search = _load_module("search_sml", "search-sml.py")


def _build_dashboard() -> dict[str, Any]:
    return _dashboard.build_payload()


def _do_search(query: str, limit: int) -> dict[str, Any]:
    query = (query or "").strip()
    if not query:
        return {"query": "", "mode": "none", "results": []}
    return _search.search(query, max(1, min(50, limit)))


class Handler(BaseHTTPRequestHandler):
    server_version = "AionVisionSML/1.0"

    def log_message(self, *args: Any) -> None:  # тише в консоли
        return

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", _CONTENT_TYPES.get(path.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_static(self, url_path: str) -> None:
        if not DIST_DIR.exists():
            self._send_json(
                404,
                {"error": "dist/ не собран — выполните `npm run build` в apps/aion-vision"},
            )
            return
        rel = url_path.lstrip("/") or "index.html"
        candidate = (DIST_DIR / rel).resolve()
        # защита от выхода за пределы dist/
        if DIST_DIR.resolve() not in candidate.parents and candidate != DIST_DIR.resolve():
            candidate = DIST_DIR / "index.html"
        if candidate.is_file():
            self._send_file(candidate)
        else:
            # SPA-фоллбэк
            self._send_file(DIST_DIR / "index.html")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/sml-dashboard":
                self._send_json(200, _build_dashboard())
            elif parsed.path == "/api/search":
                qs = parse_qs(parsed.query)
                query = (qs.get("q", [""])[0]) or ""
                try:
                    limit = int(qs.get("limit", ["10"])[0])
                except ValueError:
                    limit = 10
                self._send_json(200, _do_search(query, limit))
            else:
                self._serve_static(parsed.path)
        except Exception as exc:  # сервис не должен падать на одном запросе
            self._send_json(500, {"error": f"{type(exc).__name__}: {exc}"})


def main() -> int:
    parser = argparse.ArgumentParser(description="HTTP-сервис Aion Vision поверх SML")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}"
    print(f"Aion Vision SML сервис: {url}  (Ctrl+C для остановки)", flush=True)
    print(f"  /api/sml-dashboard, /api/search?q=…  | статика: {DIST_DIR}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Остановка.", flush=True)
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
