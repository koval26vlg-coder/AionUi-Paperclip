from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hh_resume_booster_data_quality import build_audit, load_experiment, load_rows as load_data_quality_rows
from hh_resume_booster_followup_queue import load_rows as load_followup_rows
from hh_resume_booster_followup_state import load_events, summarize as summarize_followups
from hh_resume_booster_metrics import default_experiment, load_experiment_for_data, load_payload, summarize
from hh_resume_booster_outreach_plan import build_plan
from hh_resume_booster_outreach_log import load_events as load_outreach_events, summarize as summarize_outreach


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-leads.jsonl"
DEFAULT_EXPERIMENT_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-experiment.json"
DEFAULT_FOLLOWUP_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-followups.jsonl"
DEFAULT_OUTREACH_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-outreach.jsonl"
DEFAULT_SNAPSHOT_DIR = ROOT / "apps" / "aion-vision" / "data" / "daily"


def load_summary(data_path: Path, experiment_path: Path | None) -> dict[str, Any]:
    if not data_path.exists():
        leads = []
        experiment = load_experiment_for_data(data_path, experiment_path) if experiment_path else default_experiment()
    else:
        leads, experiment = load_payload(data_path, experiment_path)
    return summarize(leads, experiment)


def load_followup_summary(data_path: Path, followup_path: Path) -> dict[str, Any] | None:
    if not data_path.exists() and not followup_path.exists():
        return None
    leads = load_followup_rows(data_path) if data_path.exists() else []
    events = load_events(followup_path) if followup_path.exists() else []
    return summarize_followups(events, leads)


def load_outreach_summary(data_path: Path, outreach_path: Path) -> dict[str, Any]:
    leads, _ = load_payload(data_path) if data_path.exists() else ([], default_experiment())
    events = load_outreach_events(outreach_path) if outreach_path.exists() else []
    return summarize_outreach(events, leads)


def build_data_quality_summary(data_path: Path, experiment_path: Path | None) -> dict[str, Any]:
    experiment = load_experiment(experiment_path)
    audit = build_audit(load_data_quality_rows(data_path), experiment)
    blocking_issues = [
        {
            "severity": item["severity"],
            "code": item["code"],
            "row": item["row"],
            "id": item["id"],
            "offer": item["offer"],
            "intent": item["intent"],
            "channel": item["channel"],
            "contact_masked": item["contact_masked"],
            "detail": item["detail"],
        }
        for item in audit["issues"]
        if item["severity"] in {"error", "warn"}
    ][:12]
    return {
        "ok": audit["error_count"] == 0 and audit["warning_count"] == 0,
        "state": "passed" if audit["error_count"] == 0 and audit["warning_count"] == 0 else "blocked",
        "total_rows": audit["total_rows"],
        "error_count": audit["error_count"],
        "warning_count": audit["warning_count"],
        "info_count": audit["info_count"],
        "issue_counts": audit["issue_counts"],
        "blocking_issues": blocking_issues,
    }


def build_snapshot(
    data_path: Path,
    experiment_path: Path | None,
    followup_path: Path,
    outreach_path: Path,
    public_base_url: str | None,
    note: str,
) -> dict[str, Any]:
    metrics = load_summary(data_path, experiment_path)
    plan = build_plan(data_path, experiment_path, public_base_url)
    followups = load_followup_summary(data_path, followup_path)
    outreach = load_outreach_summary(data_path, outreach_path)
    data_quality = build_data_quality_summary(data_path, experiment_path)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "date": datetime.now().date().isoformat(),
        "note": note,
        "paths": {
            "data": str(data_path),
            "experiment": str(experiment_path) if experiment_path else None,
            "followups": str(followup_path),
            "outreach": str(outreach_path),
        },
        "metrics": metrics,
        "data_quality": data_quality,
        "outreach_activity": outreach,
        "outreach_plan": {
            "deficits": plan["deficits"],
            "recommended_today": plan["recommended_today"],
            "channels": plan["channels"],
            "actions": plan["actions"],
            "local_url_warning": plan["local_url_warning"],
        },
        "followups": followups,
    }


def render_markdown(snapshot: dict[str, Any]) -> str:
    metrics = snapshot["metrics"]
    experiment = metrics["experiment"]
    daily = metrics["daily"]
    data_quality = snapshot["data_quality"]
    outreach = snapshot["outreach_activity"]
    plan = snapshot["outreach_plan"]
    followups = snapshot["followups"]
    lines = [
        "# HH Resume Booster Daily Snapshot",
        "",
        f"Generated at: `{snapshot['generated_at']}`",
        f"Date: `{snapshot['date']}`",
        f"Note: {snapshot['note'] or 'n/a'}",
        "",
        "## Gate",
        "",
        f"- Day: `{experiment['elapsed_days']}/{experiment['duration_days']}`",
        f"- Started at: `{experiment['started_at'] or 'n/a'}`",
        f"- Ends at: `{experiment['ends_at'] or 'n/a'}`",
        f"- Days complete: `{bool_text(experiment['days_complete'])}`",
        f"- Decision ready: `{bool_text(metrics['decision_ready'])}`",
        "",
        "## Metrics",
        "",
        f"- Leads: `{metrics['total_leads']}/{experiment['target_leads']}`",
        f"- Paid intent: `{metrics['total_paid_intent']}/{experiment['target_paid_intent']}`",
        f"- Channels: `{metrics['unique_channels']}/{experiment['target_channels']}`",
        f"- Roles: `{metrics['unique_roles']}/{experiment['target_roles']}`",
        f"- Paid intent rate: `{metrics['paid_intent_rate']}%`",
        "",
        "## Data Quality",
        "",
        f"- State: `{data_quality['state']}`",
        f"- Rows checked: `{data_quality['total_rows']}`",
        f"- Errors: `{data_quality['error_count']}`",
        f"- Warnings: `{data_quality['warning_count']}`",
        f"- Info: `{data_quality['info_count']}`",
        "",
        "### Issue Counts",
        "",
    ]
    if data_quality["issue_counts"]:
        lines.extend(f"- `{code}`: `{count}`" for code, count in data_quality["issue_counts"].items())
    else:
        lines.append("- `n/a`")

    lines.extend(["", "### Blocking Issues", ""])
    if data_quality["blocking_issues"]:
        for item in data_quality["blocking_issues"]:
            contact = item["contact_masked"] or "n/a"
            lead_id = item["id"] or "n/a"
            lines.append(
                f"- `{item['severity']}` row `{item['row']}` code `{item['code']}` "
                f"id `{lead_id}` contact `{contact}`: {item['detail']}"
            )
    else:
        lines.append("- `n/a`")

    lines.extend(
        [
            "",
            "## Pace",
            "",
            f"- Active days: `{daily['active_days']}`",
            f"- Days available: `{daily['days_available']}`",
            f"- Average leads/day: `{daily['average_leads_per_active_day']}`",
            f"- Average paid/day: `{daily['average_paid_per_active_day']}`",
            f"- Required leads/day: `{daily['required_leads_per_remaining_day']}`",
            f"- Required paid/day: `{daily['required_paid_per_remaining_day']}`",
            "",
            "## Offer Coverage",
            "",
            "| Offer | Leads | Target | Paid intent | Status |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    by_offer = {item["offer"]: item for item in metrics["by_offer"]}
    for item in metrics["offer_coverage"]:
        offer = by_offer[item["offer"]]
        lines.append(
            f"| {item['label']} | {item['leads']} | {item['target']} | {offer['paid_intent']} | "
            f"{'ok' if item['ready'] else 'wait'} |"
        )

    lines.extend(
        [
            "",
            "## Outreach Activity",
            "",
            f"- Events: `{outreach['events']}`",
            f"- Messages sent: `{outreach['messages_sent']}`",
            f"- Audience count: `{outreach['audience_count']}`",
            f"- Leads per 100 sent: `{outreach['leads_per_100_sent'] if outreach['leads_per_100_sent'] is not None else 'n/a'}`",
            "",
            "| Channel | Events | Sent | Audience | Leads | Paid intent | Leads / 100 sent |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    if outreach["by_channel"]:
        for item in outreach["by_channel"]:
            conversion = item["leads_per_100_sent"] if item["leads_per_100_sent"] is not None else "n/a"
            lines.append(
                f"| {item['channel']} | {item['events']} | {item['messages_sent']} | {item['audience_count']} | "
                f"{item['leads']} | {item['paid_intent']} | {conversion} |"
            )
    else:
        lines.append("| n/a | 0 | 0 | 0 | 0 | 0 | n/a |")

    lines.extend(
        [
            "",
            "| Offer focus | Events | Sent | Audience | Leads | Paid intent | Leads / 100 sent |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in outreach["by_offer"]:
        conversion = item["leads_per_100_sent"] if item["leads_per_100_sent"] is not None else "n/a"
        lines.append(
            f"| {item['label']} | {item['events']} | {item['messages_sent']} | {item['audience_count']} | "
            f"{item['leads']} | {item['paid_intent']} | {conversion} |"
        )

    lines.extend(
        [
            "",
            "## Outreach Plan",
            "",
            f"- Leads deficit: `{plan['deficits']['leads']}`",
            f"- Paid intent deficit: `{plan['deficits']['paid_intent']}`",
            f"- Channels deficit: `{plan['deficits']['channels']}`",
            f"- Roles deficit: `{plan['deficits']['roles']}`",
            f"- Offer coverage deficit: `{plan['deficits']['offer_coverage']}`",
            f"- Local URL warning: `{bool_text(plan['local_url_warning'])}`",
            "",
            "### Recommended Today",
            "",
            f"- Leads: `{plan['recommended_today']['leads']}`",
            f"- Paid intent: `{plan['recommended_today']['paid_intent']}`",
        ]
    )
    for item in plan["recommended_today"]["offers"]:
        lines.append(
            f"- {item['label']}: leads `{item['leads']}/{item['target']}`, "
            f"deficit `{item['deficit']}`, today `{item['recommended_leads_today']}`"
        )
    lines.extend(["", "### Actions", ""])
    lines.extend(f"- {action}" for action in plan["actions"])

    lines.extend(["", "## Follow-up Outcomes", ""])
    if followups is None:
        lines.append("Follow-up state: `not_available`")
    else:
        lines.extend(
            [
                f"- Loaded leads: `{followups['loaded_leads']}`",
                f"- Events: `{followups['events']}`",
                f"- Tracked leads: `{followups['tracked_leads']}`",
                f"- Untracked leads: `{followups['untracked_leads']}`",
                f"- Open follow-ups: `{followups['open_followups']}`",
                f"- Confirmed paid intent: `{followups['confirmed_paid_intent']}`",
                f"- Paid: `{followups['paid']}`",
                "",
                "| Offer | Tracked | Confirmed | Paid | Declined | Open |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for item in followups["by_offer"]:
            lines.append(
                f"| {item['label']} | {item['tracked']} | {item['confirmed_paid_intent']} | "
                f"{item['paid']} | {item['declined']} | {item['open']} |"
            )

    lines.extend(["", "## Source Paths", ""])
    for key, path in snapshot["paths"].items():
        lines.append(f"- {key}: `{path or 'n/a'}`")
    return "\n".join(lines)


def default_snapshot_path() -> Path:
    return DEFAULT_SNAPSHOT_DIR / f"hh-booster-daily-snapshot-{datetime.now().date().isoformat()}.md"


def bool_text(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a PII-safe daily snapshot for HH Resume Booster.")
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_DATA_PATH, help="Leads JSON/CSV/JSONL.")
    parser.add_argument("--experiment-state", type=Path, default=DEFAULT_EXPERIMENT_PATH, help="Experiment state JSON.")
    parser.add_argument("--followup-state", type=Path, default=DEFAULT_FOLLOWUP_PATH, help="Follow-up outcome JSONL.")
    parser.add_argument("--outreach-state", type=Path, default=DEFAULT_OUTREACH_PATH, help="Outreach activity JSONL.")
    parser.add_argument("--public-base-url", help="Public base URL used for outreach plan warnings/links.")
    parser.add_argument("--note", default="", help="Short operator note for this snapshot. Do not include personal data.")
    parser.add_argument("--out", type=Path, help="Write Markdown/JSON snapshot to this file.")
    parser.add_argument("--default-out", action="store_true", help=f"Write Markdown snapshot to {DEFAULT_SNAPSHOT_DIR}.")
    parser.add_argument("--strict-data-quality", action="store_true", help="Return exit code 2 when data quality has errors/warnings.")
    parser.add_argument("--json", action="store_true", help="Print or write machine-readable JSON.")
    args = parser.parse_args()

    snapshot = build_snapshot(
        args.input,
        args.experiment_state,
        args.followup_state,
        args.outreach_state,
        args.public_base_url,
        args.note,
    )
    output = json.dumps(snapshot, ensure_ascii=False, indent=2) if args.json else render_markdown(snapshot)

    out_path = args.out
    if args.default_out and not out_path:
        out_path = default_snapshot_path()
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    if args.strict_data_quality and not snapshot["data_quality"]["ok"]:
        print("Data quality audit is not clean. Snapshot was still generated for audit trail.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
