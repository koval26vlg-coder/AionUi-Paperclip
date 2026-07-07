from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

from hh_resume_booster_data_quality import build_audit, load_experiment, load_rows
from hh_resume_booster_launch_manifest import (
    CHANNELS,
    OFFERS,
    build_manifest,
    is_ephemeral_tunnel_url,
    is_local_url,
    is_placeholder_url,
    normalize_base_url,
)
from hh_resume_booster_metrics import load_experiment_for_data, load_payload, summarize


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "apps" / "aion-vision"
DEFAULT_DATA_PATH = APP_DIR / "data" / "hh-booster-leads.jsonl"
DEFAULT_EXPERIMENT_PATH = APP_DIR / "data" / "hh-booster-experiment.json"
DEFAULT_FOLLOWUP_PATH = APP_DIR / "data" / "hh-booster-followups.jsonl"
DEFAULT_MANIFEST_PATH = APP_DIR / "data" / "hh-booster-launch-manifest.md"
DEFAULT_REPORT_PATH = APP_DIR / "data" / "hh-booster-decision-report.md"
DEFAULT_OPERATOR_BASE_URL = "http://127.0.0.1:8787"


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def add_check(checks: list[Check], name: str, status: str, detail: str) -> None:
    if status not in {"pass", "warn", "fail", "skip"}:
        raise ValueError(f"invalid check status: {status}")
    checks.append(Check(name, status, detail))


def check_exists(checks: list[Check], name: str, path: Path, required: bool = True) -> None:
    if path.exists():
        add_check(checks, name, "pass", f"{path} exists")
    else:
        status = "fail" if required else "warn"
        add_check(checks, name, status, f"{path} missing")


def parse_http_json(url: str, timeout_seconds: float = 8) -> dict[str, Any]:
    request = Request(url, headers={"Accept": "application/json"})
    with urlopen(request, timeout=timeout_seconds) as response:
        raw = response.read().decode("utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("HTTP JSON payload is not an object")
    return payload


def parse_http_text(url: str, timeout_seconds: float = 8) -> tuple[int, str]:
    request = Request(url, headers={"Accept": "text/html,*/*"})
    with urlopen(request, timeout=timeout_seconds) as response:
        raw = response.read().decode("utf-8", errors="replace")
        return int(response.status), raw


def looks_like_app_shell(body: str) -> bool:
    return 'id="root"' in body or "<title>Aion Vision</title>" in body


def looks_like_tunnel_interstitial(body: str) -> bool:
    lowered = body.lower()
    return any(
        marker in lowered
        for marker in (
            "tunnel password",
            "friendly reminder",
            "to access this website, please enter the tunnel password",
            "localtunnel",
        )
    )


def check_url_shape(checks: list[Check], public_base_url: str | None, allow_local_public_url: bool) -> None:
    if not public_base_url:
        add_check(
            checks,
            "public_url",
            "fail",
            "PublicBaseUrl is required before sending candidate links",
        )
        return
    parsed = urlparse(public_base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        add_check(checks, "public_url", "fail", f"PublicBaseUrl is not a valid HTTP(S) URL: {public_base_url}")
        return
    if is_local_url(public_base_url) and not allow_local_public_url:
        add_check(checks, "public_url", "fail", "PublicBaseUrl points to localhost; use a tunnel/domain")
        return
    if is_placeholder_url(public_base_url):
        add_check(checks, "public_url", "fail", "PublicBaseUrl is a placeholder/test URL; use the real public tunnel/domain")
        return
    if parsed.scheme != "https" and not is_local_url(public_base_url):
        add_check(checks, "public_url", "warn", "PublicBaseUrl is not HTTPS")
        return
    if is_ephemeral_tunnel_url(public_base_url):
        add_check(
            checks,
            "ephemeral_public_url",
            "warn",
            "PublicBaseUrl is a temporary tunnel; recheck immediately before launch and prefer a stable domain for a 14-day test",
        )
    add_check(checks, "public_url", "pass", f"candidate links will use {public_base_url}")


def check_server(checks: list[Check], operator_base_url: str, public_base_url: str | None, check_public_http: bool) -> None:
    try:
        status_code, body = parse_http_text(f"{operator_base_url}/")
        if status_code == 200 and body:
            add_check(checks, "operator_http_root", "pass", f"{operator_base_url}/ returned 200")
        else:
            add_check(checks, "operator_http_root", "warn", f"{operator_base_url}/ returned HTTP {status_code}")
    except (OSError, URLError, TimeoutError, ValueError) as exc:
        add_check(checks, "operator_http_root", "fail", f"{operator_base_url}/ unavailable: {exc}")

    try:
        leads_payload = parse_http_json(f"{operator_base_url}/api/hh-booster/leads?limit=1")
        if leads_payload.get("ok") is True and isinstance(leads_payload.get("leads"), list):
            add_check(checks, "operator_api_leads", "pass", "GET /api/hh-booster/leads ok")
        else:
            add_check(checks, "operator_api_leads", "fail", "GET /api/hh-booster/leads returned unexpected payload")
    except (OSError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        add_check(checks, "operator_api_leads", "fail", f"GET /api/hh-booster/leads failed: {exc}")

    try:
        experiment_payload = parse_http_json(f"{operator_base_url}/api/hh-booster/experiment")
        if experiment_payload.get("ok") is True and isinstance(experiment_payload.get("experiment"), dict):
            started = experiment_payload["experiment"].get("startedAt") or "not started"
            add_check(checks, "operator_api_experiment", "pass", f"GET /api/hh-booster/experiment ok, startedAt={started}")
        else:
            add_check(checks, "operator_api_experiment", "fail", "GET /api/hh-booster/experiment returned unexpected payload")
    except (OSError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        add_check(checks, "operator_api_experiment", "fail", f"GET /api/hh-booster/experiment failed: {exc}")

    if check_public_http and public_base_url:
        try:
            status_code, body = parse_http_text(f"{public_base_url}/")
            if looks_like_tunnel_interstitial(body):
                add_check(checks, "public_http_root", "fail", f"{public_base_url}/ returned a tunnel interstitial/password page")
            elif status_code == 200 and looks_like_app_shell(body):
                add_check(checks, "public_http_root", "pass", f"{public_base_url}/ returned 200")
            elif status_code == 200:
                add_check(checks, "public_http_root", "warn", f"{public_base_url}/ returned 200, but content did not look like app shell")
            else:
                add_check(checks, "public_http_root", "warn", f"{public_base_url}/ returned HTTP {status_code}")
        except (OSError, URLError, TimeoutError, ValueError) as exc:
            add_check(checks, "public_http_root", "fail", f"{public_base_url}/ unavailable: {exc}")

        try:
            public_leads_payload = parse_http_json(f"{public_base_url}/api/hh-booster/leads?limit=1")
            if public_leads_payload.get("ok") is True and isinstance(public_leads_payload.get("leads"), list):
                add_check(checks, "public_api_leads", "pass", "GET public /api/hh-booster/leads ok")
            else:
                add_check(checks, "public_api_leads", "fail", "GET public /api/hh-booster/leads returned unexpected payload")
        except (OSError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            add_check(checks, "public_api_leads", "fail", f"GET public /api/hh-booster/leads failed: {exc}")

        try:
            public_experiment_payload = parse_http_json(f"{public_base_url}/api/hh-booster/experiment")
            if public_experiment_payload.get("ok") is True and isinstance(public_experiment_payload.get("experiment"), dict):
                started = public_experiment_payload["experiment"].get("startedAt") or "not started"
                add_check(checks, "public_api_experiment", "pass", f"GET public /api/hh-booster/experiment ok, startedAt={started}")
            else:
                add_check(
                    checks,
                    "public_api_experiment",
                    "fail",
                    "GET public /api/hh-booster/experiment returned unexpected payload",
                )
        except (OSError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            add_check(checks, "public_api_experiment", "fail", f"GET public /api/hh-booster/experiment failed: {exc}")


def check_experiment(checks: list[Check], data_path: Path, experiment_path: Path) -> dict[str, Any]:
    experiment = load_experiment_for_data(data_path, experiment_path)
    started_at = experiment.started_at
    if not started_at:
        add_check(checks, "experiment_started", "fail", "experiment startedAt is empty; press `Старт теста` before publishing")
    else:
        add_check(checks, "experiment_started", "pass", f"experiment startedAt={started_at}")

    if experiment.duration_days == 14:
        add_check(checks, "experiment_duration", "pass", "durationDays=14")
    else:
        add_check(checks, "experiment_duration", "fail", f"durationDays={experiment.duration_days}, expected 14")

    target_tuple = (
        experiment.target_leads,
        experiment.target_paid_intent,
        experiment.target_channels,
        experiment.target_roles,
        experiment.target_min_leads_per_offer,
    )
    if target_tuple == (30, 10, 2, 5, 5):
        add_check(checks, "experiment_targets", "pass", "targets match 30/10/2/5/5")
    else:
        add_check(checks, "experiment_targets", "fail", f"targets are {target_tuple}, expected (30, 10, 2, 5, 5)")

    leads, experiment_for_summary = load_payload(data_path, experiment_path) if data_path.exists() else ([], experiment)
    summary = summarize(leads, experiment_for_summary)
    if summary["experiment"]["elapsed_days"] > experiment.duration_days and not summary["experiment"]["days_complete"]:
        add_check(checks, "experiment_clock", "warn", "experiment clock looks inconsistent")
    elif summary["experiment"]["days_complete"]:
        add_check(checks, "experiment_clock", "warn", "14-day window is already complete; do not treat this as prelaunch")
    else:
        day = summary["experiment"]["elapsed_days"]
        add_check(checks, "experiment_clock", "pass", f"prelaunch/day status ok, elapsed_days={day}")
    return summary


def check_data_quality(checks: list[Check], data_path: Path, experiment_path: Path) -> dict[str, Any]:
    rows = load_rows(data_path)
    experiment = load_experiment(experiment_path)
    audit = build_audit(rows, experiment)
    if audit["error_count"] == 0 and audit["warning_count"] == 0:
        add_check(checks, "data_quality", "pass", f"clean audit, rows={audit['total_rows']}")
    else:
        add_check(
            checks,
            "data_quality",
            "fail",
            f"errors={audit['error_count']}, warnings={audit['warning_count']}, rows={audit['total_rows']}",
        )
    return audit


def fragment_params(url: str) -> dict[str, list[str]]:
    fragment = urlparse(url).fragment
    query = fragment.split("?", 1)[1] if "?" in fragment else ""
    return parse_qs(query, keep_blank_values=True)


def check_manifest(
    checks: list[Check],
    data_path: Path,
    experiment_path: Path,
    followup_path: Path,
    report_path: Path,
    manifest_path: Path,
    operator_base_url: str,
    public_base_url: str | None,
) -> dict[str, Any]:
    manifest = build_manifest(
        data_path,
        experiment_path,
        followup_path,
        report_path,
        operator_base_url,
        public_base_url,
    )
    if manifest_path.exists():
        text = manifest_path.read_text(encoding="utf-8", errors="replace")
        if "HH Resume Booster Launch Manifest" in text:
            add_check(checks, "launch_manifest", "pass", f"{manifest_path} exists")
        else:
            add_check(checks, "launch_manifest", "warn", f"{manifest_path} exists but title was not recognized")
    else:
        add_check(checks, "launch_manifest", "fail", f"{manifest_path} missing; save launch freeze before publishing")

    if manifest["status"]["dist_exists"]:
        add_check(checks, "manifest_dist_status", "pass", "manifest sees dist_exists=yes")
    else:
        add_check(checks, "manifest_dist_status", "fail", "manifest sees dist_exists=no")

    if manifest["status"]["public_url_ready"]:
        add_check(checks, "manifest_public_status", "pass", "manifest sees public_url_ready=yes")
    else:
        add_check(checks, "manifest_public_status", "fail", "manifest sees public_url_ready=no")

    if len(manifest["urls"]["channel_links"]) == len(CHANNELS):
        add_check(checks, "channel_links", "pass", f"{len(CHANNELS)} channel links configured")
    else:
        add_check(checks, "channel_links", "fail", "channel link count mismatch")

    expected_offer_ids = {offer["id"] for offer in OFFERS}
    offer_links = manifest["urls"].get("offer_links", [])
    offer_link_ids = {link.get("offer") for link in offer_links}
    offer_link_urls_ok = all(
        (link.get("offer") in fragment_params(str(link.get("url", ""))).get("offer", [])) for link in offer_links
    )
    if len(offer_links) == len(OFFERS) and offer_link_ids == expected_offer_ids and offer_link_urls_ok:
        add_check(checks, "offer_links", "pass", f"{len(OFFERS)} direct offer links configured")
    else:
        add_check(checks, "offer_links", "fail", "direct offer links are missing or malformed")

    offer_channel_links = manifest["urls"].get("offer_channel_links", [])
    expected_pairs = {(offer["id"], channel) for offer in OFFERS for channel in CHANNELS}
    actual_pairs: set[tuple[str, str]] = set()
    urls_ok = True
    for link in offer_channel_links:
        offer = str(link.get("offer", ""))
        channel = str(link.get("channel", ""))
        actual_pairs.add((offer, channel))
        params = fragment_params(str(link.get("url", "")))
        if offer not in params.get("offer", []) or channel not in params.get("channel", []):
            urls_ok = False
    if len(offer_channel_links) == len(expected_pairs) and actual_pairs == expected_pairs and urls_ok:
        add_check(checks, "offer_channel_links", "pass", f"{len(expected_pairs)} offer+channel links configured")
    else:
        add_check(checks, "offer_channel_links", "fail", "offer+channel link matrix is missing or malformed")

    if [offer["slug"] for offer in OFFERS] == ["avatar-only", "full-resume-audit", "vacancy-response-pack"]:
        add_check(checks, "offer_slugs", "pass", "three offer slugs match the test design")
    else:
        add_check(checks, "offer_slugs", "fail", "offer slug configuration drifted")
    return manifest


def build_prelaunch_report(args: argparse.Namespace) -> dict[str, Any]:
    checks: list[Check] = []
    operator_base_url = normalize_base_url(args.operator_base_url, DEFAULT_OPERATOR_BASE_URL) or DEFAULT_OPERATOR_BASE_URL
    public_base_url = normalize_base_url(args.public_base_url)

    check_exists(checks, "dist_index", APP_DIR / "dist" / "index.html", required=True)
    check_exists(checks, "serve_script", APP_DIR / "scripts" / "serve-sml.py", required=True)
    check_exists(checks, "start_script", APP_DIR / "scripts" / "start-hh-booster-test.ps1", required=True)
    check_exists(checks, "preflight_script", APP_DIR / "scripts" / "preflight-hh-booster-test.ps1", required=True)
    check_url_shape(checks, public_base_url, args.allow_local_public_url)

    if args.skip_server_check:
        add_check(checks, "server_http", "skip", "server checks skipped by --skip-server-check")
    else:
        check_server(checks, operator_base_url, public_base_url, args.check_public_http)

    summary = check_experiment(checks, args.data, args.experiment_state)
    audit = check_data_quality(checks, args.data, args.experiment_state)
    manifest = check_manifest(
        checks,
        args.data,
        args.experiment_state,
        args.followup_state,
        args.report_out,
        args.manifest,
        operator_base_url,
        public_base_url,
    )

    failed = [check for check in checks if check.status == "fail"]
    warnings = [check for check in checks if check.status == "warn"]
    next_actions = build_next_actions(checks, operator_base_url, public_base_url)
    return {
        "generated_at": now_iso(),
        "ok": not failed,
        "status": "GO" if not failed else "NO-GO",
        "operator_base_url": operator_base_url,
        "public_base_url": public_base_url,
        "operator_url": f"{operator_base_url}/#hh-booster",
        "public_form_url": f"{public_base_url}/#hh-booster-public" if public_base_url else None,
        "failed": len(failed),
        "warnings": len(warnings),
        "checks": [check.__dict__ for check in checks],
        "summary": {
            "total_leads": summary["total_leads"],
            "total_paid_intent": summary["total_paid_intent"],
            "experiment": summary["experiment"],
            "offer_coverage": summary["offer_coverage"],
        },
        "data_quality": {
            "ok": audit["ok"] and audit["warning_count"] == 0,
            "total_rows": audit["total_rows"],
            "error_count": audit["error_count"],
            "warning_count": audit["warning_count"],
            "issue_counts": audit["issue_counts"],
        },
        "manifest_status": manifest["status"],
        "next_actions": next_actions,
    }


def build_next_actions(checks: list[Check], operator_base_url: str, public_base_url: str | None) -> list[str]:
    by_name = {check.name: check for check in checks}
    actions: list[str] = []
    if by_name.get("dist_index", Check("", "", "")).status == "fail":
        actions.append("Run npm run build in apps/aion-vision before launch.")
    if by_name.get("operator_http_root", Check("", "", "")).status == "fail":
        actions.append(
            f"Start visible server: & \"{APP_DIR}\\scripts\\start-hh-booster-test.ps1\" -Port 8787"
            + (f" -PublicBaseUrl \"{public_base_url}\"" if public_base_url else "")
        )
    if by_name.get("public_url", Check("", "", "")).status == "fail":
        actions.append("Create a public HTTPS tunnel/domain and rerun with --public-base-url.")
    if by_name.get("ephemeral_public_url", Check("", "", "")).status == "warn":
        actions.append("Use a stable public domain for the 14-day test when possible; if using the temporary tunnel, rerun public API/prelaunch immediately before publishing links.")
    if by_name.get("experiment_started", Check("", "", "")).status == "fail":
        actions.append(
            "Open operator UI and press `Старт теста`, or run "
            "`python tools/hh_resume_booster_experiment_state.py start --write`, then rerun the prelaunch check."
        )
    if by_name.get("launch_manifest", Check("", "", "")).status == "fail":
        actions.append(
            f"Save launch manifest: python tools/hh_resume_booster_launch_manifest.py "
            f"--public-base-url \"{public_base_url or 'https://PUBLIC_HOST'}\" --out \"{DEFAULT_MANIFEST_PATH}\""
        )
    if by_name.get("offer_links", Check("", "", "")).status == "fail" or by_name.get(
        "offer_channel_links", Check("", "", "")
    ).status == "fail":
        actions.append("Fix offer-specific candidate links before launch; each public link must preserve explicit offer and channel.")
    if by_name.get("data_quality", Check("", "", "")).status == "fail":
        actions.append("Clean QA/preflight/test-like or invalid rows with data-admin dry-run/write flow, then rerun.")
    if not actions:
        actions.append("Publish candidate links and start daily loop: data quality -> metrics -> outreach plan -> follow-up -> snapshot.")
    return actions


def render_text(report: dict[str, Any]) -> str:
    lines = [
        "HH Resume Booster prelaunch GO/NO-GO",
        "====================================",
        f"Status: {report['status']}",
        f"Generated at: {report['generated_at']}",
        f"Operator: {report['operator_url']}",
        f"Public form: {report['public_form_url'] or 'n/a'}",
        f"Failed: {report['failed']}",
        f"Warnings: {report['warnings']}",
        "",
        "Checks:",
    ]
    for check in report["checks"]:
        lines.append(f"- [{check['status']}] {check['name']}: {check['detail']}")
    lines.extend(
        [
            "",
            "Data quality:",
            f"- rows: {report['data_quality']['total_rows']}",
            f"- errors: {report['data_quality']['error_count']}",
            f"- warnings: {report['data_quality']['warning_count']}",
            "",
            "Next actions:",
        ]
    )
    for action in report["next_actions"]:
        lines.append(f"- {action}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only GO/NO-GO verifier before publishing HH Resume Booster candidate links.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="Leads JSONL/JSON/CSV path.")
    parser.add_argument("--experiment-state", type=Path, default=DEFAULT_EXPERIMENT_PATH, help="Experiment state JSON path.")
    parser.add_argument("--followup-state", type=Path, default=DEFAULT_FOLLOWUP_PATH, help="Follow-up outcome JSONL path.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH, help="Saved launch manifest path.")
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT_PATH, help="Final decision report output path.")
    parser.add_argument("--operator-base-url", default=DEFAULT_OPERATOR_BASE_URL, help="Local/operator base URL.")
    parser.add_argument("--public-base-url", help="Public base URL used in candidate links.")
    parser.add_argument("--allow-local-public-url", action="store_true", help="Allow localhost PublicBaseUrl for local rehearsal only.")
    parser.add_argument("--skip-server-check", action="store_true", help="Do not call operator HTTP/API endpoints.")
    parser.add_argument("--check-public-http", action="store_true", help="Also call PublicBaseUrl over HTTP(S).")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    report = build_prelaunch_report(args)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
