from __future__ import annotations

import argparse
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hh_resume_booster_metrics import OFFER_LABELS, load_payload


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-leads.jsonl"
DEFAULT_STATE_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-outreach.jsonl"

OUTREACH_TYPES = {
    "direct_message": "Личное сообщение",
    "post": "Пост",
    "comment": "Комментарий",
    "referral": "Рекомендация",
    "offline": "Оффлайн",
    "other": "Другое",
}
OFFER_CHOICES = set(OFFER_LABELS) | {"mixed"}


@dataclass(frozen=True)
class OutreachEvent:
    event_id: str
    created_at: str
    actor: str
    channel: str
    outreach_type: str
    offer: str
    messages_sent: int
    audience_count: int
    link_url: str
    note: str
    row_number: int


def clean(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def positive_int(value: Any, fallback: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if parsed >= 0 else fallback


def parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def coerce_event(row: Any, row_number: int) -> OutreachEvent:
    if not isinstance(row, dict):
        raise ValueError(f"Outreach row {row_number} must be an object, got {type(row).__name__}")
    created_at = clean(row.get("createdAt"))
    if not parse_datetime(created_at):
        raise ValueError(f"Invalid createdAt at row {row_number}: {created_at!r}")
    outreach_type = clean(row.get("type"))
    if outreach_type not in OUTREACH_TYPES:
        raise ValueError(f"Unknown outreach type at row {row_number}: {outreach_type!r}")
    offer = clean(row.get("offer")) or "mixed"
    if offer not in OFFER_CHOICES:
        raise ValueError(f"Unknown offer at row {row_number}: {offer!r}")
    channel = clean(row.get("channel"))
    if not channel:
        raise ValueError(f"Missing channel at row {row_number}")
    return OutreachEvent(
        event_id=clean(row.get("eventId")) or f"row-{row_number}",
        created_at=created_at,
        actor=clean(row.get("actor")) or "operator",
        channel=channel,
        outreach_type=outreach_type,
        offer=offer,
        messages_sent=positive_int(row.get("messagesSent")),
        audience_count=positive_int(row.get("audienceCount")),
        link_url=clean(row.get("linkUrl")),
        note=clean(row.get("note")),
        row_number=row_number,
    )


def load_events(path: Path) -> list[OutreachEvent]:
    if not path.exists():
        return []
    events: list[OutreachEvent] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc
        events.append(coerce_event(payload, line_number))
    return events


def make_event(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "eventId": str(uuid.uuid4()),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "actor": clean(args.actor) or "operator",
        "channel": clean(args.channel),
        "type": args.type,
        "offer": args.offer,
        "messagesSent": max(0, args.messages_sent),
        "audienceCount": max(0, args.audience_count),
        "linkUrl": clean(args.link_url),
        "note": clean(args.note),
    }
    return {key: value for key, value in payload.items() if value not in {"", None}}


def append_event(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def load_leads_for_summary(path: Path) -> list[Any]:
    if not path.exists():
        return []
    leads, _ = load_payload(path)
    return leads


def summarize(events: list[OutreachEvent], leads: list[Any]) -> dict[str, Any]:
    by_channel: dict[str, dict[str, Any]] = {}
    by_offer: dict[str, dict[str, Any]] = {
        offer: {
            "offer": offer,
            "label": label,
            "events": 0,
            "messages_sent": 0,
            "audience_count": 0,
            "leads": 0,
            "paid_intent": 0,
            "leads_per_100_sent": None,
        }
        for offer, label in OFFER_LABELS.items()
    }
    by_offer["mixed"] = {
        "offer": "mixed",
        "label": "Смешанный",
        "events": 0,
        "messages_sent": 0,
        "audience_count": 0,
        "leads": 0,
        "paid_intent": 0,
        "leads_per_100_sent": None,
    }

    for event in events:
        channel = by_channel.setdefault(
            event.channel,
            {
                "channel": event.channel,
                "events": 0,
                "messages_sent": 0,
                "audience_count": 0,
                "leads": 0,
                "paid_intent": 0,
                "leads_per_100_sent": None,
            },
        )
        channel["events"] += 1
        channel["messages_sent"] += event.messages_sent
        channel["audience_count"] += event.audience_count

        offer = by_offer[event.offer]
        offer["events"] += 1
        offer["messages_sent"] += event.messages_sent
        offer["audience_count"] += event.audience_count

    for lead in leads:
        if lead.channel:
            channel = by_channel.setdefault(
                lead.channel,
                {
                    "channel": lead.channel,
                    "events": 0,
                    "messages_sent": 0,
                    "audience_count": 0,
                    "leads": 0,
                    "paid_intent": 0,
                    "leads_per_100_sent": None,
                },
            )
            channel["leads"] += 1
            channel["paid_intent"] += 1 if lead.paid_intent else 0
        if lead.offer in by_offer:
            by_offer[lead.offer]["leads"] += 1
            by_offer[lead.offer]["paid_intent"] += 1 if lead.paid_intent else 0

    for collection in (by_channel.values(), by_offer.values()):
        for item in collection:
            sent = int(item["messages_sent"])
            item["leads_per_100_sent"] = round((int(item["leads"]) / sent) * 100, 2) if sent else None

    total_messages = sum(event.messages_sent for event in events)
    total_audience = sum(event.audience_count for event in events)
    total_leads = len(leads)
    total_paid = sum(1 for lead in leads if lead.paid_intent)
    return {
        "events": len(events),
        "messages_sent": total_messages,
        "audience_count": total_audience,
        "loaded_leads": total_leads,
        "paid_intent": total_paid,
        "leads_per_100_sent": round((total_leads / total_messages) * 100, 2) if total_messages else None,
        "by_channel": sorted(by_channel.values(), key=lambda item: (-int(item["messages_sent"]), item["channel"])),
        "by_offer": list(by_offer.values()),
        "recent_events": [
            {
                "created_at": event.created_at,
                "channel": event.channel,
                "type": event.outreach_type,
                "offer": event.offer,
                "messages_sent": event.messages_sent,
                "audience_count": event.audience_count,
            }
            for event in sorted(events, key=lambda item: item.created_at, reverse=True)[:10]
        ],
    }


def render_summary(summary: dict[str, Any], state_path: Path, leads_path: Path) -> str:
    lines = [
        "HH Resume Booster outreach activity",
        f"state: {state_path}",
        f"leads: {leads_path}",
        f"events: {summary['events']}",
        f"messages_sent: {summary['messages_sent']}",
        f"audience_count: {summary['audience_count']}",
        f"loaded_leads: {summary['loaded_leads']}",
        f"paid_intent: {summary['paid_intent']}",
        f"leads_per_100_sent: {summary['leads_per_100_sent'] if summary['leads_per_100_sent'] is not None else 'n/a'}",
        "",
        "by_channel:",
    ]
    if summary["by_channel"]:
        for item in summary["by_channel"]:
            conversion = item["leads_per_100_sent"] if item["leads_per_100_sent"] is not None else "n/a"
            lines.append(
                f"- {item['channel']}: events={item['events']}, sent={item['messages_sent']}, "
                f"audience={item['audience_count']}, leads={item['leads']}, paid={item['paid_intent']}, "
                f"leads_per_100_sent={conversion}"
            )
    else:
        lines.append("- n/a")
    lines.extend(["", "by_offer:"])
    for item in summary["by_offer"]:
        conversion = item["leads_per_100_sent"] if item["leads_per_100_sent"] is not None else "n/a"
        lines.append(
            f"- {item['label']}: events={item['events']}, sent={item['messages_sent']}, "
            f"audience={item['audience_count']}, leads={item['leads']}, paid={item['paid_intent']}, "
            f"leads_per_100_sent={conversion}"
        )
    return "\n".join(lines)


def render_dry_run(payload: dict[str, Any], state_path: Path) -> str:
    return "\n".join(
        [
            "HH Resume Booster outreach activity dry-run",
            f"state: {state_path}",
            "write: false",
            "payload:",
            json.dumps(payload, ensure_ascii=False, indent=2),
            "",
            "Rerun with --write to append. Do not put candidate personal data in note.",
        ]
    )


def add_command(args: argparse.Namespace) -> int:
    payload = make_event(args)
    if not payload.get("channel"):
        raise SystemExit("channel is required")
    if not args.write:
        print(render_dry_run(payload, args.state))
        return 0
    append_event(args.state, payload)
    print(json.dumps({"ok": True, "state": str(args.state), "event": payload}, ensure_ascii=False, indent=2))
    return 0


def summary_command(args: argparse.Namespace) -> int:
    events = load_events(args.state)
    leads = load_leads_for_summary(args.leads)
    summary = summarize(events, leads)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(render_summary(summary, args.state, args.leads))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track HH Resume Booster outreach activity without personal data.")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE_PATH, help="Outreach activity JSONL.")
    parser.add_argument("--leads", type=Path, default=DEFAULT_DATA_PATH, help="Leads JSON/CSV/JSONL for denominator summary.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="Append one outreach activity event. Dry-run unless --write is set.")
    add.add_argument("--channel", required=True, help="Channel, for example Telegram, VK, hh.ru, Авито Работа.")
    add.add_argument("--type", choices=sorted(OUTREACH_TYPES), default="direct_message")
    add.add_argument("--offer", choices=sorted(OFFER_CHOICES), default="mixed", help="Offer focus for this activity.")
    add.add_argument("--messages-sent", type=int, default=0, help="Direct messages or individual sends.")
    add.add_argument("--audience-count", type=int, default=0, help="Estimated post/group audience reached.")
    add.add_argument("--link-url", default="", help="Published candidate link. Do not include secrets.")
    add.add_argument("--actor", default="operator")
    add.add_argument("--note", default="", help="Short non-personal note. Do not include contacts or candidate details.")
    add.add_argument("--write", action="store_true", help="Actually append to state JSONL.")
    add.set_defaults(func=add_command)

    summary_parser = subparsers.add_parser("summary", help="Summarize outreach activity versus collected leads.")
    summary_parser.add_argument("--json", action="store_true")
    summary_parser.set_defaults(func=summary_command)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
