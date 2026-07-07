from __future__ import annotations

import argparse
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hh_resume_booster_followup_queue import (
    DEFAULT_INPUT,
    OFFER_LABELS,
    QueueLead,
    load_rows,
    mask_contact,
    parse_datetime,
    truncate,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-followups.jsonl"

STATUS_LABELS = {
    "contacted": "Связались",
    "responded": "Ответил",
    "confirmed_paid_intent": "Подтвердил оплату",
    "paid": "Оплатил",
    "declined": "Отказ",
    "no_response": "Нет ответа",
    "invalid": "Невалидный контакт",
}

CLOSED_STATUSES = {"paid", "declined", "no_response", "invalid"}
PAID_SIGNAL_STATUSES = {"confirmed_paid_intent", "paid"}


@dataclass(frozen=True)
class FollowupEvent:
    event_id: str
    lead_id: str
    status: str
    created_at: str
    actor: str
    offer: str
    amount: float | None
    note: str
    row_number: int


def clean(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def coerce_event(row: Any, row_number: int) -> FollowupEvent:
    if not isinstance(row, dict):
        raise ValueError(f"Follow-up row {row_number} must be an object, got {type(row).__name__}")
    status = clean(row.get("status"))
    if status not in STATUS_LABELS:
        raise ValueError(f"Unknown follow-up status at row {row_number}: {status!r}")
    offer = clean(row.get("offer"))
    if offer and offer not in OFFER_LABELS:
        raise ValueError(f"Unknown offer at row {row_number}: {offer!r}")
    amount = row.get("amount")
    if amount is not None:
        try:
            amount = float(amount)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid amount at row {row_number}: {amount!r}") from exc
    created_at = clean(row.get("createdAt"))
    if not parse_datetime(created_at):
        raise ValueError(f"Invalid createdAt at row {row_number}: {created_at!r}")
    lead_id = clean(row.get("leadId"))
    if not lead_id:
        raise ValueError(f"Missing leadId at row {row_number}")
    return FollowupEvent(
        event_id=clean(row.get("eventId")) or f"row-{row_number}",
        lead_id=lead_id,
        status=status,
        created_at=created_at,
        actor=clean(row.get("actor")) or "operator",
        offer=offer,
        amount=amount,
        note=clean(row.get("note")),
        row_number=row_number,
    )


def load_events(path: Path) -> list[FollowupEvent]:
    if not path.exists():
        return []
    events: list[FollowupEvent] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc
        events.append(coerce_event(payload, line_number))
    return events


def latest_by_lead(events: list[FollowupEvent]) -> dict[str, FollowupEvent]:
    latest: dict[str, FollowupEvent] = {}
    for event in events:
        previous = latest.get(event.lead_id)
        if not previous or event_sort_key(event) >= event_sort_key(previous):
            latest[event.lead_id] = event
    return latest


def event_sort_key(event: FollowupEvent) -> tuple[float, int]:
    parsed = parse_datetime(event.created_at)
    return ((parsed.timestamp() if parsed else 0.0), event.row_number)


def lead_map(leads: list[QueueLead]) -> dict[str, QueueLead]:
    return {lead.id: lead for lead in leads}


def make_event(args: argparse.Namespace, lead: QueueLead | None) -> dict[str, Any]:
    offer = args.offer or (lead.offer if lead else "")
    payload: dict[str, Any] = {
        "eventId": str(uuid.uuid4()),
        "leadId": args.lead_id,
        "status": args.status,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "actor": args.actor,
        "offer": offer,
        "amount": args.amount,
        "note": clean(args.note),
    }
    return {key: value for key, value in payload.items() if value not in {"", None}}


def append_event(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def load_leads_if_available(path: Path) -> list[QueueLead]:
    if not path.exists():
        return []
    return load_rows(path)


def summarize(events: list[FollowupEvent], leads: list[QueueLead]) -> dict[str, Any]:
    latest = latest_by_lead(events)
    leads_by_id = lead_map(leads)
    status_counts = {status: 0 for status in STATUS_LABELS}
    by_offer: dict[str, dict[str, Any]] = {
        offer: {
            "offer": offer,
            "label": label,
            "tracked": 0,
            "confirmed_paid_intent": 0,
            "paid": 0,
            "declined": 0,
            "open": 0,
        }
        for offer, label in OFFER_LABELS.items()
    }

    for lead_id, event in latest.items():
        status_counts[event.status] += 1
        lead = leads_by_id.get(lead_id)
        offer = lead.offer if lead else event.offer
        if offer in by_offer:
            by_offer[offer]["tracked"] += 1
            if event.status in PAID_SIGNAL_STATUSES:
                by_offer[offer]["confirmed_paid_intent"] += 1
            if event.status == "paid":
                by_offer[offer]["paid"] += 1
            if event.status == "declined":
                by_offer[offer]["declined"] += 1
            if event.status not in CLOSED_STATUSES:
                by_offer[offer]["open"] += 1

    untracked = [lead for lead in leads if lead.id not in latest]
    open_items = [
        event
        for event in latest.values()
        if event.status not in CLOSED_STATUSES
    ]
    paid_signal = [
        event
        for event in latest.values()
        if event.status in PAID_SIGNAL_STATUSES
    ]
    paid = [
        event
        for event in latest.values()
        if event.status == "paid"
    ]

    return {
        "loaded_leads": len(leads),
        "events": len(events),
        "tracked_leads": len(latest),
        "untracked_leads": len(untracked),
        "open_followups": len(open_items),
        "confirmed_paid_intent": len(paid_signal),
        "paid": len(paid),
        "closed": sum(1 for event in latest.values() if event.status in CLOSED_STATUSES),
        "status_counts": status_counts,
        "by_offer": list(by_offer.values()),
    }


def render_summary(summary: dict[str, Any], state_path: Path, leads_path: Path) -> str:
    lines = [
        "HH Resume Booster follow-up outcomes",
        f"state: {state_path}",
        f"leads: {leads_path}",
        f"loaded_leads: {summary['loaded_leads']}",
        f"events: {summary['events']}",
        f"tracked_leads: {summary['tracked_leads']}",
        f"untracked_leads: {summary['untracked_leads']}",
        f"open_followups: {summary['open_followups']}",
        f"confirmed_paid_intent: {summary['confirmed_paid_intent']}",
        f"paid: {summary['paid']}",
        "",
        "status_counts:",
    ]
    for status, label in STATUS_LABELS.items():
        lines.append(f"- {label}: {summary['status_counts'][status]}")
    lines.extend(["", "by_offer:"])
    for item in summary["by_offer"]:
        lines.append(
            f"- {item['label']}: tracked={item['tracked']}, confirmed_paid_intent={item['confirmed_paid_intent']}, "
            f"paid={item['paid']}, declined={item['declined']}, open={item['open']}"
        )
    return "\n".join(lines)


def render_event_row(
    event: FollowupEvent,
    lead: QueueLead | None,
    show_contact: bool,
) -> str:
    contact = lead.contact if lead and show_contact else mask_contact(lead.contact if lead else "")
    offer = OFFER_LABELS.get(lead.offer if lead else event.offer, event.offer or "n/a")
    role = lead.role if lead else "n/a"
    channel = lead.channel if lead else "n/a"
    return (
        f"- lead={event.lead_id} status={STATUS_LABELS[event.status]} offer={offer} "
        f"role={truncate(role or 'n/a', 32)} channel={channel or 'n/a'} contact={contact or 'n/a'} "
        f"updated={event.created_at} note={truncate(event.note or 'n/a', 120)}"
    )


def filter_latest(
    latest: dict[str, FollowupEvent],
    leads_by_id: dict[str, QueueLead],
    statuses: set[str] | None,
    offer: str | None,
) -> list[FollowupEvent]:
    rows: list[FollowupEvent] = []
    for event in latest.values():
        if statuses and event.status not in statuses:
            continue
        lead = leads_by_id.get(event.lead_id)
        event_offer = lead.offer if lead else event.offer
        if offer and event_offer != offer:
            continue
        rows.append(event)
    return sorted(rows, key=event_sort_key, reverse=True)


def parse_status_filter(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    result: set[str] = set()
    for value in values:
        for item in value.split(","):
            status = item.strip()
            if not status:
                continue
            if status == "all":
                return None
            if status not in STATUS_LABELS:
                allowed = ", ".join(sorted(set(STATUS_LABELS) | {"all"}))
                raise ValueError(f"Unsupported status {status!r}; allowed: {allowed}")
            result.add(status)
    return result or None


def command_mark(args: argparse.Namespace) -> int:
    leads = load_leads_if_available(args.leads)
    lead = lead_map(leads).get(args.lead_id)
    if leads and not lead:
        raise ValueError(f"Lead id not found in {args.leads}: {args.lead_id}")
    if args.offer and args.offer not in OFFER_LABELS:
        raise ValueError(f"Unknown offer: {args.offer!r}")
    event = make_event(args, lead)

    if args.write:
        append_event(args.state, event)

    output = {
        "state": str(args.state),
        "mode": "write" if args.write else "dry_run",
        "event": event,
        "lead": lead_summary(lead, args.show_contact) if lead else None,
    }
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print("HH Resume Booster follow-up mark")
        print(f"state: {args.state}")
        print(f"mode: {output['mode']}")
        print(f"lead_id: {args.lead_id}")
        print(f"status: {STATUS_LABELS[args.status]}")
        if lead:
            print(
                f"lead: offer={OFFER_LABELS[lead.offer]} intent={lead.intent} role={lead.role or 'n/a'} "
                f"channel={lead.channel or 'n/a'} contact={lead.contact if args.show_contact else mask_contact(lead.contact)}"
            )
        if not args.write:
            print("dry_run: add --write to append this event.")
    return 0


def lead_summary(lead: QueueLead | None, show_contact: bool) -> dict[str, Any] | None:
    if not lead:
        return None
    return {
        "id": lead.id,
        "offer": lead.offer,
        "intent": lead.intent,
        "role": lead.role,
        "channel": lead.channel,
        "contact": lead.contact if show_contact else mask_contact(lead.contact),
        "contact_masked": not show_contact,
    }


def command_summary(args: argparse.Namespace) -> int:
    leads = load_leads_if_available(args.leads)
    events = load_events(args.state)
    result = summarize(events, leads)
    payload = {
        "state": str(args.state),
        "leads": str(args.leads),
        **result,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_summary(result, args.state, args.leads))
    return 0


def command_list(args: argparse.Namespace) -> int:
    leads = load_leads_if_available(args.leads)
    events = load_events(args.state)
    leads_by_id = lead_map(leads)
    rows = filter_latest(latest_by_lead(events), leads_by_id, parse_status_filter(args.status), args.offer)
    rows = rows[: args.limit]
    if args.json:
        print(
            json.dumps(
                {
                    "state": str(args.state),
                    "leads": str(args.leads),
                    "shown": len(rows),
                    "rows": [
                        {
                            "lead_id": event.lead_id,
                            "status": event.status,
                            "status_label": STATUS_LABELS[event.status],
                            "created_at": event.created_at,
                            "offer": (leads_by_id.get(event.lead_id).offer if event.lead_id in leads_by_id else event.offer),
                            "lead": lead_summary(leads_by_id.get(event.lead_id), args.show_contact),
                            "amount": event.amount,
                            "note": event.note,
                        }
                        for event in rows
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print("HH Resume Booster follow-up latest states")
        print(f"state: {args.state}")
        if not rows:
            print("- n/a")
        for event in rows:
            print(render_event_row(event, leads_by_id.get(event.lead_id), args.show_contact))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track manual HH Resume Booster concierge follow-up outcomes.")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE_PATH, help="Follow-up JSONL state file.")
    parser.add_argument("--leads", type=Path, default=DEFAULT_INPUT, help="HH Booster leads JSON/CSV/JSONL file.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    mark = subparsers.add_parser("mark", help="Append a follow-up outcome event.")
    mark.add_argument("lead_id", help="Lead id from hh-booster-leads.jsonl.")
    mark.add_argument("--status", required=True, choices=sorted(STATUS_LABELS), help="Latest follow-up status.")
    mark.add_argument("--offer", choices=sorted(OFFER_LABELS), help="Optional offer override when lead file is unavailable.")
    mark.add_argument("--amount", type=float, help="Optional paid or quoted amount.")
    mark.add_argument("--note", default="", help="Short non-sensitive note or objection.")
    mark.add_argument("--actor", default="operator", help="Who performed the follow-up.")
    mark.add_argument("--show-contact", action="store_true", help="Print unmasked contact in command output.")
    mark.add_argument("--write", action="store_true", help="Actually append the event. Default is dry-run.")
    mark.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    mark.set_defaults(func=command_mark)

    summary_cmd = subparsers.add_parser("summary", help="Summarize latest follow-up outcomes.")
    summary_cmd.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    summary_cmd.set_defaults(func=command_summary)

    list_cmd = subparsers.add_parser("list", help="List latest follow-up states by lead.")
    list_cmd.add_argument("--status", action="append", help="Filter statuses. Comma-separated/repeated; use all for no filter.")
    list_cmd.add_argument("--offer", choices=sorted(OFFER_LABELS), help="Filter by lead offer.")
    list_cmd.add_argument("--limit", type=int, default=50, help="Maximum rows to show.")
    list_cmd.add_argument("--show-contact", action="store_true", help="Print unmasked contacts.")
    list_cmd.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    list_cmd.set_defaults(func=command_list)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "limit") and args.limit < 1:
        raise ValueError("--limit must be positive")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
