"""Постоянный HTTP-сервис Aion Vision поверх SML (stdlib, без зависимостей).

В отличие от vite middleware (живёт только в `npm run dev`), этот сервис
работает и для прод-сборки: отдаёт статику из `dist/` и те же API:

- ``GET /api/sml-dashboard`` — текущее состояние памяти (как export-sml-dashboard);
- ``GET /api/search?q=…&limit=…`` — поиск по памяти (семантика + FTS5-фоллбэк);
- ``GET /api/drift-workflow`` — live read-only snapshot agent workflow dashboard;
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
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

APP_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = APP_DIR / "scripts"
DIST_DIR = APP_DIR / "dist"
DATA_DIR = APP_DIR / "data"
HH_BOOSTER_LEADS_PATH = DATA_DIR / "hh-booster-leads.jsonl"
HH_BOOSTER_EXPERIMENT_PATH = DATA_DIR / "hh-booster-experiment.json"
DEFAULT_HH_BOOSTER_EXPERIMENT = {
    "startedAt": None,
    "durationDays": 14,
    "targetLeads": 30,
    "targetPaidIntent": 10,
    "targetChannels": 2,
    "targetRoles": 5,
    "targetMinLeadsPerOffer": 5,
}

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
_drift = _load_module("export_drift_workflow", "export-drift-workflow.py")


def _build_dashboard() -> dict[str, Any]:
    return _dashboard.build_payload()


def _do_search(query: str, limit: int) -> dict[str, Any]:
    query = (query or "").strip()
    if not query:
        return {"query": "", "mode": "none", "results": []}
    return _search.search(query, max(1, min(50, limit)))


def _build_drift_workflow() -> dict[str, Any]:
    workflow = _drift.workflow_dir(_drift.DEFAULT_WORKFLOW_ID)
    return _drift.build_snapshot(workflow)


def _clean_text(payload: dict[str, Any], key: str, max_len: int, required: bool = True) -> str:
    value = payload.get(key, "")
    text = str(value).strip() if value is not None else ""
    if required and not text:
        raise ValueError(f"missing {key}")
    return text[:max_len]


def _build_hh_booster_lead(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    if payload.get("consentAccepted") is not True:
        raise ValueError("consent required")
    offer = _clean_text(payload, "offer", 32)
    intent = _clean_text(payload, "intent", 32)
    if offer not in {"avatar", "audit", "response"}:
        raise ValueError("invalid offer")
    if intent not in {"ready", "maybe", "not_now"}:
        raise ValueError("invalid intent")
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": _clean_text(payload, "id", 80, required=False) or str(uuid4()),
        "createdAt": now,
        "clientCreatedAt": _clean_text(payload, "createdAt", 80, required=False),
        "offer": offer,
        "contact": _clean_text(payload, "contact", 160),
        "role": _clean_text(payload, "role", 120),
        "intent": intent,
        "channel": _clean_text(payload, "channel", 80, required=False) or "unknown",
        "notes": _clean_text(payload, "notes", 1000, required=False),
        "consentAccepted": True,
        "source": "hh-booster-public",
    }


def _append_hh_booster_lead(payload: Any) -> dict[str, Any]:
    lead = _build_hh_booster_lead(payload)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with HH_BOOSTER_LEADS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(lead, ensure_ascii=False) + "\n")
    return lead


def _read_hh_booster_leads(limit: int = 1000) -> list[dict[str, Any]]:
    if not HH_BOOSTER_LEADS_PATH.exists():
        return []
    leads: list[dict[str, Any]] = []
    for line in HH_BOOSTER_LEADS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            leads.append(payload)
    return leads[-max(1, min(5000, limit)) :]


def _positive_int(payload: dict[str, Any], key: str, fallback: int) -> int:
    value = payload.get(key, fallback)
    if isinstance(value, bool):
        return fallback
    if isinstance(value, int) and value > 0:
        return value
    return fallback


def _coerce_hh_booster_experiment(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("experiment payload must be an object")
    started_at = payload.get("startedAt")
    if started_at is not None:
        if not isinstance(started_at, str) or not started_at.strip():
            raise ValueError("startedAt must be an ISO string or null")
        try:
            datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("startedAt must be a valid ISO datetime") from exc
    return {
        "startedAt": started_at,
        "durationDays": _positive_int(payload, "durationDays", DEFAULT_HH_BOOSTER_EXPERIMENT["durationDays"]),
        "targetLeads": _positive_int(payload, "targetLeads", DEFAULT_HH_BOOSTER_EXPERIMENT["targetLeads"]),
        "targetPaidIntent": _positive_int(
            payload,
            "targetPaidIntent",
            DEFAULT_HH_BOOSTER_EXPERIMENT["targetPaidIntent"],
        ),
        "targetChannels": _positive_int(payload, "targetChannels", DEFAULT_HH_BOOSTER_EXPERIMENT["targetChannels"]),
        "targetRoles": _positive_int(payload, "targetRoles", DEFAULT_HH_BOOSTER_EXPERIMENT["targetRoles"]),
        "targetMinLeadsPerOffer": _positive_int(
            payload,
            "targetMinLeadsPerOffer",
            DEFAULT_HH_BOOSTER_EXPERIMENT["targetMinLeadsPerOffer"],
        ),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }


def _read_hh_booster_experiment() -> dict[str, Any]:
    if not HH_BOOSTER_EXPERIMENT_PATH.exists():
        return dict(DEFAULT_HH_BOOSTER_EXPERIMENT)
    payload = json.loads(HH_BOOSTER_EXPERIMENT_PATH.read_text(encoding="utf-8"))
    experiment = _coerce_hh_booster_experiment(payload)
    if isinstance(payload, dict) and isinstance(payload.get("updatedAt"), str):
        experiment["updatedAt"] = payload["updatedAt"]
    return experiment


def _write_hh_booster_experiment(payload: Any) -> dict[str, Any]:
    experiment = _coerce_hh_booster_experiment(payload)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HH_BOOSTER_EXPERIMENT_PATH.write_text(
        json.dumps(experiment, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return experiment


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

    def _read_json_body(self) -> Any:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("invalid content length") from exc
        if length <= 0:
            raise ValueError("empty body")
        if length > 16_384:
            raise ValueError("body too large")
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

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
            elif parsed.path == "/api/drift-workflow":
                self._send_json(200, _build_drift_workflow())
            elif parsed.path == "/api/search":
                qs = parse_qs(parsed.query)
                query = (qs.get("q", [""])[0]) or ""
                try:
                    limit = int(qs.get("limit", ["10"])[0])
                except ValueError:
                    limit = 10
                self._send_json(200, _do_search(query, limit))
            elif parsed.path == "/api/hh-booster/leads":
                qs = parse_qs(parsed.query)
                try:
                    limit = int(qs.get("limit", ["1000"])[0])
                except ValueError:
                    limit = 1000
                self._send_json(
                    200,
                    {
                        "ok": True,
                        "path": str(HH_BOOSTER_LEADS_PATH),
                        "leads": _read_hh_booster_leads(limit),
                    },
                )
            elif parsed.path == "/api/hh-booster/experiment":
                self._send_json(
                    200,
                    {
                        "ok": True,
                        "path": str(HH_BOOSTER_EXPERIMENT_PATH),
                        "experiment": _read_hh_booster_experiment(),
                    },
                )
            else:
                self._serve_static(parsed.path)
        except Exception as exc:  # сервис не должен падать на одном запросе
            self._send_json(500, {"error": f"{type(exc).__name__}: {exc}"})

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/hh-booster/leads":
                lead = _append_hh_booster_lead(self._read_json_body())
                self._send_json(201, {"ok": True, "lead": lead, "path": str(HH_BOOSTER_LEADS_PATH)})
            elif parsed.path == "/api/hh-booster/experiment":
                experiment = _write_hh_booster_experiment(self._read_json_body())
                self._send_json(
                    200,
                    {"ok": True, "experiment": experiment, "path": str(HH_BOOSTER_EXPERIMENT_PATH)},
                )
            else:
                self._send_json(404, {"error": "unknown endpoint"})
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid json"})
        except Exception as exc:
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
