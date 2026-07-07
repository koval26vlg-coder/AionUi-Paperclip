from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hh_resume_booster_metrics import default_experiment, load_payload, summarize


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-leads.jsonl"
DEFAULT_STATE_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-experiment.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SystemExit(f"Invalid ISO datetime for --started-at: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()


def positive_int(value: Any, fallback: int) -> int:
    return value if isinstance(value, int) and value > 0 else fallback


def default_state() -> dict[str, Any]:
    experiment = default_experiment()
    return {
        "startedAt": experiment.started_at,
        "durationDays": experiment.duration_days,
        "targetLeads": experiment.target_leads,
        "targetPaidIntent": experiment.target_paid_intent,
        "targetChannels": experiment.target_channels,
        "targetRoles": experiment.target_roles,
        "targetMinLeadsPerOffer": experiment.target_min_leads_per_offer,
    }


def coerce_state(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        payload = {}
    defaults = default_state()
    started_at = payload.get("startedAt")
    if started_at is not None:
        if not isinstance(started_at, str) or not started_at.strip():
            started_at = None
        else:
            started_at = parse_iso(started_at)
    state = {
        "startedAt": started_at,
        "durationDays": positive_int(payload.get("durationDays"), defaults["durationDays"]),
        "targetLeads": positive_int(payload.get("targetLeads"), defaults["targetLeads"]),
        "targetPaidIntent": positive_int(payload.get("targetPaidIntent"), defaults["targetPaidIntent"]),
        "targetChannels": positive_int(payload.get("targetChannels"), defaults["targetChannels"]),
        "targetRoles": positive_int(payload.get("targetRoles"), defaults["targetRoles"]),
        "targetMinLeadsPerOffer": positive_int(
            payload.get("targetMinLeadsPerOffer"),
            defaults["targetMinLeadsPerOffer"],
        ),
    }
    if isinstance(payload.get("updatedAt"), str):
        state["updatedAt"] = payload["updatedAt"]
    return state


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return default_state()
    return coerce_state(json.loads(path.read_text(encoding="utf-8-sig")))


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_leads(data_path: Path, state_path: Path) -> tuple[list[Any], dict[str, Any]]:
    if not data_path.exists():
        return [], summarize([], default_experiment())
    leads, experiment = load_payload(data_path, state_path)
    return leads, summarize(leads, experiment)


def state_with_targets(args: argparse.Namespace, current: dict[str, Any]) -> dict[str, Any]:
    state = dict(current)
    for attr, key in (
        ("duration_days", "durationDays"),
        ("target_leads", "targetLeads"),
        ("target_paid_intent", "targetPaidIntent"),
        ("target_channels", "targetChannels"),
        ("target_roles", "targetRoles"),
        ("target_min_leads_per_offer", "targetMinLeadsPerOffer"),
    ):
        value = getattr(args, attr, None)
        if value is not None:
            state[key] = value
    return state


def render_status(state_path: Path, data_path: Path, state: dict[str, Any], summary: dict[str, Any]) -> str:
    experiment = summary["experiment"]
    return "\n".join(
        [
            "HH Resume Booster experiment state",
            f"state: {state_path}",
            f"data: {data_path}",
            f"started_at: {experiment['started_at'] or 'n/a'}",
            f"ends_at: {experiment['ends_at'] or 'n/a'}",
            f"elapsed_days: {experiment['elapsed_days']}",
            f"days_complete: {str(experiment['days_complete']).lower()}",
            f"duration_days: {experiment['duration_days']}",
            f"target_leads: {experiment['target_leads']}",
            f"target_paid_intent: {experiment['target_paid_intent']}",
            f"target_channels: {experiment['target_channels']}",
            f"target_roles: {experiment['target_roles']}",
            f"target_min_leads_per_offer: {experiment['target_min_leads_per_offer']}",
            f"total_leads: {summary['total_leads']}",
            f"total_paid_intent: {summary['total_paid_intent']}",
            f"decision_ready: {str(summary['decision_ready']).lower()}",
            f"updated_at: {state.get('updatedAt') or 'n/a'}",
        ]
    )


def status_command(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    _, summary = load_leads(args.data, args.state)
    payload = {
        "state_path": str(args.state),
        "data_path": str(args.data),
        "state": state,
        "summary": summary,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_status(args.state, args.data, state, summary))
    return 0


def start_command(args: argparse.Namespace) -> int:
    current = load_state(args.state)
    leads, _ = load_leads(args.data, args.state)
    if current.get("startedAt") and not args.force:
        print(f"Experiment already started at {current['startedAt']}. Use --force to restart.", file=sys.stderr)
        return 2
    if leads and not args.allow_existing_leads:
        print(
            f"Refusing to start with {len(leads)} existing leads. Use --allow-existing-leads if this is intentional.",
            file=sys.stderr,
        )
        return 2
    state = state_with_targets(args, current)
    state["startedAt"] = parse_iso(args.started_at) if args.started_at else now_iso()
    state["updatedAt"] = now_iso()
    if args.json:
        print(json.dumps({"write": bool(args.write), "state_path": str(args.state), "state": state}, ensure_ascii=False, indent=2))
    else:
        print("HH Resume Booster experiment start")
        print(f"state: {args.state}")
        print(f"write: {str(bool(args.write)).lower()}")
        print(f"startedAt: {state['startedAt']}")
        print("Rerun with --write to persist." if not args.write else "Persisting experiment state.")
    if args.write:
        write_state(args.state, state)
    return 0


def reset_command(args: argparse.Namespace) -> int:
    current = load_state(args.state)
    if not args.force:
        print("Reset requires --force to avoid accidentally clearing the 14-day start date.", file=sys.stderr)
        return 2
    state = state_with_targets(args, current)
    state["startedAt"] = None
    state["updatedAt"] = now_iso()
    if args.json:
        print(json.dumps({"write": bool(args.write), "state_path": str(args.state), "state": state}, ensure_ascii=False, indent=2))
    else:
        print("HH Resume Booster experiment reset")
        print(f"state: {args.state}")
        print(f"write: {str(bool(args.write)).lower()}")
        print("Rerun with --write --force to persist." if not args.write else "Persisting reset state.")
    if args.write:
        write_state(args.state, state)
    return 0


def add_target_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--duration-days", type=int)
    parser.add_argument("--target-leads", type=int)
    parser.add_argument("--target-paid-intent", type=int)
    parser.add_argument("--target-channels", type=int)
    parser.add_argument("--target-roles", type=int)
    parser.add_argument("--target-min-leads-per-offer", type=int)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage HH Resume Booster experiment state. Dry-run unless --write is set.")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE_PATH, help="Experiment state JSON path.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="Leads JSON/CSV/JSONL path.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Show current experiment state and gate summary.")
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=status_command)

    start = subparsers.add_parser("start", help="Start or restart the 14-day test. Dry-run unless --write is set.")
    start.add_argument("--started-at", help="ISO datetime override. Defaults to now UTC.")
    start.add_argument("--allow-existing-leads", action="store_true", help="Allow starting when leads already exist.")
    start.add_argument("--force", action="store_true", help="Allow restart when startedAt already exists.")
    start.add_argument("--write", action="store_true", help="Persist experiment state.")
    start.add_argument("--json", action="store_true")
    add_target_args(start)
    start.set_defaults(func=start_command)

    reset = subparsers.add_parser("reset", help="Clear startedAt. Requires --force and dry-run unless --write is set.")
    reset.add_argument("--force", action="store_true")
    reset.add_argument("--write", action="store_true")
    reset.add_argument("--json", action="store_true")
    add_target_args(reset)
    reset.set_defaults(func=reset_command)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
