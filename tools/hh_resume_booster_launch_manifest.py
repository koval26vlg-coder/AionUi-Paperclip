from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

from hh_resume_booster_metrics import OFFER_LABELS, default_experiment, load_experiment_for_data, load_payload, summarize


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-leads.jsonl"
DEFAULT_EXPERIMENT_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-experiment.json"
DEFAULT_FOLLOWUP_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-followups.jsonl"
DEFAULT_REPORT_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-decision-report.md"
DEFAULT_OPERATOR_BASE_URL = "http://127.0.0.1:8787"
CHANNELS = ["hh.ru", "Telegram", "VK", "Авито Работа", "Рекомендация", "Другое"]
OFFERS = [
    {"id": "avatar", "label": OFFER_LABELS["avatar"], "price_rub": 199, "slug": "avatar-only"},
    {"id": "audit", "label": OFFER_LABELS["audit"], "price_rub": 399, "slug": "full-resume-audit"},
    {"id": "response", "label": OFFER_LABELS["response"], "price_rub": 799, "slug": "vacancy-response-pack"},
]


def normalize_base_url(value: str | None, fallback: str | None = None) -> str | None:
    raw = value if value is not None and value.strip() else fallback
    if not raw:
        return None
    return raw.strip().rstrip("/")


def is_local_url(value: str | None) -> bool:
    if not value:
        return True
    lowered = value.lower()
    return "127.0.0.1" in lowered or "localhost" in lowered or "//[::1]" in lowered


def is_placeholder_url(value: str | None) -> bool:
    if not value:
        return True
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower().rstrip(".")
    lowered = value.lower()
    if not host:
        return True
    if host in {"public_host", "public-host", "example.com", "example.net", "example.org", "example.test"}:
        return True
    if host.endswith(".example") or host.endswith(".test") or host.endswith(".invalid"):
        return True
    return "public_host" in lowered or "public-host" in host or "your-public" in host


def is_ephemeral_tunnel_url(value: str | None) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower().rstrip(".")
    return (
        host.endswith(".loca.lt")
        or host.endswith(".ngrok-free.app")
        or host.endswith(".trycloudflare.com")
        or host.endswith(".localhost.run")
    )


def public_links(base_url: str | None) -> list[dict[str, str]]:
    base = normalize_base_url(base_url, DEFAULT_OPERATOR_BASE_URL)
    assert base is not None
    return [
        {
            "channel": channel,
            "url": f"{base}/#hh-booster-public?channel={quote(channel)}",
        }
        for channel in CHANNELS
    ]


def offer_links(base_url: str | None) -> list[dict[str, str]]:
    base = normalize_base_url(base_url, DEFAULT_OPERATOR_BASE_URL)
    assert base is not None
    return [
        {
            "offer": offer["id"],
            "label": offer["label"],
            "url": f"{base}/#hh-booster-public?offer={quote(offer['id'])}",
        }
        for offer in OFFERS
    ]


def offer_channel_links(base_url: str | None) -> list[dict[str, str]]:
    base = normalize_base_url(base_url, DEFAULT_OPERATOR_BASE_URL)
    assert base is not None
    return [
        {
            "offer": offer["id"],
            "label": offer["label"],
            "channel": channel,
            "url": f"{base}/#hh-booster-public?channel={quote(channel)}&offer={quote(offer['id'])}",
        }
        for offer in OFFERS
        for channel in CHANNELS
    ]


def load_summary(data_path: Path, experiment_path: Path | None) -> dict[str, Any]:
    if data_path.exists():
        leads, experiment = load_payload(data_path, experiment_path)
        return summarize(leads, experiment)
    experiment = load_experiment_for_data(data_path, experiment_path) if experiment_path else default_experiment()
    return summarize([], experiment)


def build_manifest(
    data_path: Path,
    experiment_path: Path | None,
    followup_path: Path,
    report_path: Path,
    operator_base_url: str,
    public_base_url: str | None,
) -> dict[str, Any]:
    operator_base = normalize_base_url(operator_base_url, DEFAULT_OPERATOR_BASE_URL) or DEFAULT_OPERATOR_BASE_URL
    public_base = normalize_base_url(public_base_url)
    share_base = public_base or operator_base
    summary = load_summary(data_path, experiment_path)
    experiment = summary["experiment"]
    dist_index = ROOT / "apps" / "aion-vision" / "dist" / "index.html"
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "name": "HH Resume Booster 14-day validation test",
        "status": {
            "dist_exists": dist_index.exists(),
            "public_url_ready": bool(public_base and not is_local_url(public_base) and not is_placeholder_url(public_base)),
            "experiment_started": bool(experiment["started_at"]),
            "data_exists": data_path.exists(),
            "local_url_warning": is_local_url(share_base),
            "placeholder_url_warning": is_placeholder_url(public_base),
            "ephemeral_url_warning": is_ephemeral_tunnel_url(public_base),
        },
        "urls": {
            "operator": f"{operator_base}/#hh-booster",
            "public_form": f"{share_base}/#hh-booster-public",
            "public_base": public_base,
            "channel_links": public_links(share_base),
            "offer_links": offer_links(share_base),
            "offer_channel_links": offer_channel_links(share_base),
        },
        "paths": {
            "data": str(data_path),
            "experiment": str(experiment_path) if experiment_path else None,
            "followups": str(followup_path),
            "decision_report": str(report_path),
        },
        "offers": OFFERS,
        "gate": {
            "duration_days": experiment["duration_days"],
            "target_leads": experiment["target_leads"],
            "target_paid_intent": experiment["target_paid_intent"],
            "target_channels": experiment["target_channels"],
            "target_roles": experiment["target_roles"],
            "target_min_leads_per_offer": experiment["target_min_leads_per_offer"],
            "started_at": experiment["started_at"],
            "ends_at": experiment["ends_at"],
            "days_complete": experiment["days_complete"],
            "decision_ready": summary["decision_ready"],
        },
        "current_metrics": {
            "total_leads": summary["total_leads"],
            "total_paid_intent": summary["total_paid_intent"],
            "unique_channels": summary["unique_channels"],
            "unique_roles": summary["unique_roles"],
            "offer_coverage": summary["offer_coverage"],
        },
        "commands": {
            "start_server": (
                '& "D:\\AionUi-Paperclip\\apps\\aion-vision\\scripts\\start-hh-booster-test.ps1" '
                "-Port 8787"
                + (f' -PublicBaseUrl "{public_base}"' if public_base else "")
            ),
            "preflight": '& "D:\\AionUi-Paperclip\\apps\\aion-vision\\scripts\\preflight-hh-booster-test.ps1" -BaseUrl "http://127.0.0.1:8787"',
            "watch": '& "D:\\AionUi-Paperclip\\apps\\aion-vision\\scripts\\watch-hh-booster-test.ps1" -Watch -IntervalSeconds 60',
            "outreach_plan": (
                '& "D:\\AionUi-Paperclip\\.venv-sml\\Scripts\\python.exe" '
                '"D:\\AionUi-Paperclip\\tools\\hh_resume_booster_outreach_plan.py" '
                f'"{data_path}" --experiment-state "{experiment_path or DEFAULT_EXPERIMENT_PATH}"'
                + (f' --public-base-url "{public_base}"' if public_base else "")
            ),
            "followup_queue": (
                '& "D:\\AionUi-Paperclip\\.venv-sml\\Scripts\\python.exe" '
                '"D:\\AionUi-Paperclip\\tools\\hh_resume_booster_followup_queue.py" '
                f'"{data_path}"'
            ),
            "final_report": (
                '& "D:\\AionUi-Paperclip\\.venv-sml\\Scripts\\python.exe" '
                '"D:\\AionUi-Paperclip\\tools\\hh_resume_booster_decision_report.py" '
                f'"{data_path}" --followup-state "{followup_path}" --out "{report_path}"'
            ),
        },
        "rules": [
            "Do not publish localhost/127.0.0.1 links to remote candidates.",
            "Use #hh-booster-public for candidates; operator #hh-booster is internal.",
            "Do not collect photos or resumes in this concierge form.",
            "Do not log in to hh.ru, scrape, or auto-respond through this test.",
            "Strong paid intent is only `Готов оплатить`.",
            "Final decision requires 14 days and all gates, including per-offer coverage.",
        ],
    }
    return manifest


def render_markdown(manifest: dict[str, Any]) -> str:
    status = manifest["status"]
    gate = manifest["gate"]
    metrics = manifest["current_metrics"]
    lines = [
        "# HH Resume Booster Launch Manifest",
        "",
        f"Generated at: `{manifest['generated_at']}`",
        "",
        "## Launch Status",
        "",
        f"- Dist exists: `{bool_text(status['dist_exists'])}`",
        f"- Public URL ready: `{bool_text(status['public_url_ready'])}`",
        f"- Experiment started: `{bool_text(status['experiment_started'])}`",
        f"- Data file exists: `{bool_text(status['data_exists'])}`",
        f"- Local URL warning: `{bool_text(status['local_url_warning'])}`",
        f"- Placeholder URL warning: `{bool_text(status['placeholder_url_warning'])}`",
        f"- Ephemeral tunnel warning: `{bool_text(status['ephemeral_url_warning'])}`",
        "",
        "## URLs",
        "",
        f"- Operator: `{manifest['urls']['operator']}`",
        f"- Public form: `{manifest['urls']['public_form']}`",
        f"- Public base: `{manifest['urls']['public_base'] or 'n/a'}`",
        "",
        "### Channel Links",
        "",
    ]
    for link in manifest["urls"]["channel_links"]:
        lines.append(f"- {link['channel']}: `{link['url']}`")
    lines.extend(
        [
            "",
            "### Offer Links",
            "",
        ]
    )
    for link in manifest["urls"]["offer_links"]:
        lines.append(f"- {link['label']}: `{link['url']}`")
    lines.extend(
        [
            "",
            "### Offer + Channel Links",
            "",
        ]
    )
    for link in manifest["urls"]["offer_channel_links"]:
        lines.append(f"- {link['label']} / {link['channel']}: `{link['url']}`")
    lines.extend(
        [
            "",
            "## Offers",
            "",
            "| Offer | Slug | Price |",
            "| --- | --- | ---: |",
        ]
    )
    for offer in manifest["offers"]:
        lines.append(f"| {offer['label']} | `{offer['slug']}` | {offer['price_rub']} RUB |")
    lines.extend(
        [
            "",
            "## Decision Gate",
            "",
            f"- Duration: `{gate['duration_days']}` days",
            f"- Target leads: `{gate['target_leads']}`",
            f"- Target paid intent: `{gate['target_paid_intent']}`",
            f"- Target channels: `{gate['target_channels']}`",
            f"- Target roles: `{gate['target_roles']}`",
            f"- Min leads per offer: `{gate['target_min_leads_per_offer']}`",
            f"- Started at: `{gate['started_at'] or 'n/a'}`",
            f"- Ends at: `{gate['ends_at'] or 'n/a'}`",
            f"- Decision ready: `{bool_text(gate['decision_ready'])}`",
            "",
            "## Current Metrics",
            "",
            f"- Leads: `{metrics['total_leads']}`",
            f"- Paid intent: `{metrics['total_paid_intent']}`",
            f"- Channels: `{metrics['unique_channels']}`",
            f"- Roles: `{metrics['unique_roles']}`",
            "",
            "| Offer | Leads | Target | Status |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for item in metrics["offer_coverage"]:
        lines.append(f"| {item['label']} | {item['leads']} | {item['target']} | {'ok' if item['ready'] else 'wait'} |")
    lines.extend(
        [
            "",
            "## Commands",
            "",
        ]
    )
    for name, command in manifest["commands"].items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append("```powershell")
        lines.append(command)
        lines.append("```")
        lines.append("")
    lines.extend(
        [
            "## Rules",
            "",
            *[f"- {rule}" for rule in manifest["rules"]],
            "",
        ]
    )
    return "\n".join(lines)


def bool_text(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a launch manifest for the HH Resume Booster 14-day test.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="Leads JSONL path.")
    parser.add_argument("--experiment-state", type=Path, default=DEFAULT_EXPERIMENT_PATH, help="Experiment state JSON path.")
    parser.add_argument("--followup-state", type=Path, default=DEFAULT_FOLLOWUP_PATH, help="Follow-up outcome JSONL path.")
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT_PATH, help="Final report output path.")
    parser.add_argument("--operator-base-url", default=DEFAULT_OPERATOR_BASE_URL, help="Local/operator base URL.")
    parser.add_argument("--public-base-url", help="Public base URL for candidate links.")
    parser.add_argument("--out", type=Path, help="Write Markdown manifest to this file.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON instead of Markdown.")
    args = parser.parse_args()

    manifest = build_manifest(
        args.data,
        args.experiment_state,
        args.followup_state,
        args.report_out,
        args.operator_base_url,
        args.public_base_url,
    )
    if args.json:
        output = json.dumps(manifest, ensure_ascii=False, indent=2)
    else:
        output = render_markdown(manifest)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
