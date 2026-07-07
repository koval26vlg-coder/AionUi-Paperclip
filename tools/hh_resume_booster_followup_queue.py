from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "apps" / "aion-vision" / "data" / "hh-booster-leads.jsonl"

OFFER_LABELS = {
    "avatar": "Аватарка",
    "audit": "Аудит резюме",
    "response": "Отклик под вакансию",
}

INTENT_LABELS = {
    "ready": "Готов оплатить",
    "maybe": "Интересно",
    "not_now": "Не готов",
}

INTENT_PRIORITY = {
    "ready": 0,
    "maybe": 1,
    "not_now": 2,
}

FOLLOWUP_STATUS_LABELS = {
    "new": "Новый",
    "contacted": "Связались",
    "responded": "Ответил",
    "confirmed_paid_intent": "Подтвердил оплату",
    "paid": "Оплатил",
    "declined": "Отказ",
    "no_response": "Нет ответа",
    "invalid": "Невалидный контакт",
}

CLOSED_FOLLOWUP_STATUSES = {"paid", "declined", "no_response", "invalid"}
DEFAULT_FOLLOWUP_STATE = REPO_ROOT / "apps" / "aion-vision" / "data" / "hh-booster-followups.jsonl"


@dataclass(frozen=True)
class QueueLead:
    id: str
    created_at: str | None
    offer: str
    contact: str
    role: str
    intent: str
    channel: str
    notes: str
    source: str
    consent_accepted: bool | None
    row_number: int


def load_rows(path: Path) -> list[QueueLead]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_csv(path)
    if suffix == ".jsonl":
        return load_jsonl(path)
    return load_json(path)


def load_json(path: Path) -> list[QueueLead]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = payload.get("leads", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("JSON must be a list of leads or an object with a leads list")
    return [coerce_lead(row, index) for index, row in enumerate(rows, start=1)]


def load_csv(path: Path) -> list[QueueLead]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [coerce_lead(row, index) for index, row in enumerate(csv.DictReader(handle), start=1)]


def load_jsonl(path: Path) -> list[QueueLead]:
    leads: list[QueueLead] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc
        leads.append(coerce_lead(payload, line_number))
    return leads


def load_followup_state(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    latest: dict[str, tuple[str, int, str]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        lead_id = clean(payload.get("leadId"))
        status = clean(payload.get("status"))
        created_at = clean(payload.get("createdAt"))
        if not lead_id or status not in FOLLOWUP_STATUS_LABELS:
            continue
        current_key = (created_at, line_number, status)
        if lead_id not in latest or current_key >= latest[lead_id]:
            latest[lead_id] = current_key
    return {lead_id: item[2] for lead_id, item in latest.items()}


def coerce_lead(row: Any, row_number: int) -> QueueLead:
    if not isinstance(row, dict):
        raise ValueError(f"Lead row {row_number} must be an object, got {type(row).__name__}")
    offer = clean(row.get("offer"))
    intent = clean(row.get("intent"))
    if offer not in OFFER_LABELS:
        raise ValueError(f"Unknown offer at row {row_number}: {offer!r}")
    if intent not in INTENT_LABELS:
        raise ValueError(f"Unknown intent at row {row_number}: {intent!r}")

    consent_value = row.get("consentAccepted")
    return QueueLead(
        id=clean(row.get("id")) or f"row-{row_number}",
        created_at=clean(row.get("createdAt")) or clean(row.get("clientCreatedAt")) or None,
        offer=offer,
        contact=clean(row.get("contact")),
        role=clean(row.get("role")),
        intent=intent,
        channel=clean(row.get("channel")),
        notes=clean(row.get("notes")),
        source=clean(row.get("source")),
        consent_accepted=consent_value if isinstance(consent_value, bool) else None,
        row_number=row_number,
    )


def clean(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def parse_filter(values: list[str] | None, allowed: set[str], default: set[str]) -> set[str]:
    if not values:
        return set(default)
    result: set[str] = set()
    for value in values:
        for item in value.split(","):
            normalized = item.strip()
            if not normalized:
                continue
            if normalized == "all":
                return set(allowed)
            if normalized not in allowed:
                allowed_list = ", ".join(sorted(allowed | {"all"}))
                raise ValueError(f"Unsupported filter value {normalized!r}; allowed: {allowed_list}")
            result.add(normalized)
    return result or set(default)


def filter_leads(
    leads: list[QueueLead],
    intents: set[str],
    offers: set[str],
    channel: str | None,
    role_contains: str | None,
    days: int | None,
) -> list[QueueLead]:
    min_created_at = datetime.now(timezone.utc) - timedelta(days=days) if days and days > 0 else None
    channel_norm = channel.casefold() if channel else None
    role_query = role_contains.casefold() if role_contains else None

    filtered: list[QueueLead] = []
    for lead in leads:
        if lead.intent not in intents:
            continue
        if lead.offer not in offers:
            continue
        if channel_norm and lead.channel.casefold() != channel_norm:
            continue
        if role_query and role_query not in lead.role.casefold():
            continue
        if min_created_at:
            parsed = parse_datetime(lead.created_at)
            if not parsed or parsed < min_created_at:
                continue
        filtered.append(lead)
    return filtered


def filter_followup_open(leads: list[QueueLead], latest_followup: dict[str, str], include_closed: bool) -> list[QueueLead]:
    if include_closed:
        return leads
    return [
        lead
        for lead in leads
        if latest_followup.get(lead.id, "new") not in CLOSED_FOLLOWUP_STATUSES
    ]


def sort_leads(leads: list[QueueLead], oldest_first: bool) -> list[QueueLead]:
    def sort_key(lead: QueueLead) -> tuple[int, float, int]:
        parsed = parse_datetime(lead.created_at)
        timestamp = parsed.timestamp() if parsed else 0.0
        time_key = timestamp if oldest_first else -timestamp
        return (INTENT_PRIORITY[lead.intent], time_key, lead.row_number)

    return sorted(leads, key=sort_key)


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def mask_contact(value: str) -> str:
    if not value:
        return "n/a"
    if value.startswith("@"):
        return value[:2] + "***" + value[-2:] if len(value) > 4 else "@***"
    if "@" in value:
        name, domain = value.split("@", 1)
        return f"{name[:2]}***@{domain[:2]}***"
    digits = re.sub(r"\D", "", value)
    if len(digits) >= 8:
        return f"{value[:2]}***{value[-2:]}"
    return value[:2] + "***" if len(value) > 2 else "***"


def truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 1)].rstrip() + "…"


def age_label(value: str | None) -> str:
    parsed = parse_datetime(value)
    if not parsed:
        return "n/a"
    delta = datetime.now(timezone.utc) - parsed
    if delta.total_seconds() < 0:
        return "future"
    hours = int(delta.total_seconds() // 3600)
    if hours < 24:
        return f"{hours}h"
    return f"{hours // 24}d"


def date_label(value: str | None) -> str:
    parsed = parse_datetime(value)
    return parsed.strftime("%Y-%m-%d %H:%M") if parsed else "n/a"


def suggested_action(lead: QueueLead) -> str:
    if lead.intent == "not_now":
        return "Не продавать сейчас; зафиксировать возражение и спросить, что сделало бы оффер полезным."
    if lead.intent == "maybe":
        return "Задать 1 уточняющий вопрос и проверить ценовое возражение."
    if lead.offer == "response":
        return "Попросить ссылку на вакансию и резюме; предложить ручной разбор отклика."
    if lead.offer == "audit":
        return "Попросить ссылку/скрин профиля hh.ru; предложить короткий аудит 3 главных правок."
    return "Попросить текущее фото/профиль; дать быстрый разбор первого впечатления."


def lead_to_dict(lead: QueueLead, show_contact: bool, show_notes: bool, latest_followup: dict[str, str]) -> dict[str, Any]:
    followup_status = latest_followup.get(lead.id, "new")
    return {
        "id": lead.id,
        "row_number": lead.row_number,
        "created_at": lead.created_at,
        "age": age_label(lead.created_at),
        "offer": lead.offer,
        "offer_label": OFFER_LABELS[lead.offer],
        "intent": lead.intent,
        "intent_label": INTENT_LABELS[lead.intent],
        "role": lead.role,
        "channel": lead.channel,
        "contact": lead.contact if show_contact else mask_contact(lead.contact),
        "contact_masked": not show_contact,
        "notes": lead.notes if show_notes else truncate(lead.notes, 140),
        "notes_truncated": bool(lead.notes and not show_notes and len(lead.notes) > 140),
        "source": lead.source,
        "consent_accepted": lead.consent_accepted,
        "followup_status": followup_status,
        "followup_status_label": FOLLOWUP_STATUS_LABELS.get(followup_status, followup_status),
        "followup_closed": followup_status in CLOSED_FOLLOWUP_STATUSES,
        "suggested_action": suggested_action(lead),
    }


def render_text(
    rows: list[QueueLead],
    total_filtered: int,
    total_loaded: int,
    input_path: Path,
    intents: set[str],
    offers: set[str],
    show_contact: bool,
    show_notes: bool,
    latest_followup: dict[str, str],
    followup_state_path: Path,
    include_closed: bool,
) -> str:
    lines = [
        "HH Resume Booster follow-up queue",
        f"input: {input_path}",
        f"followup_state: {followup_state_path}",
        f"loaded: {total_loaded}",
        f"matched: {total_filtered}",
        f"shown: {len(rows)}",
        f"intents: {', '.join(sorted(intents, key=lambda item: INTENT_PRIORITY[item]))}",
        f"offers: {', '.join(sorted(offers))}",
        f"contact: {'visible' if show_contact else 'masked; use --show-contact for real follow-up'}",
        f"notes: {'full' if show_notes else 'preview; use --show-notes for full context'}",
        f"closed_followups: {'included' if include_closed else 'hidden; use --include-closed to inspect'}",
        "",
    ]

    if not rows:
        lines.append("Очередь пуста по текущим фильтрам.")
        return "\n".join(lines)

    header = f"{'#':>2}  {'intent':<13} {'offer':<17} {'followup':<15} {'age':<6} {'channel':<14} {'role':<24} {'contact':<22} action"
    lines.append(header)
    lines.append("-" * len(header))
    for index, lead in enumerate(rows, start=1):
        followup_status = latest_followup.get(lead.id, "new")
        lines.append(
            f"{index:>2}  "
            f"{truncate(INTENT_LABELS[lead.intent], 13):<13} "
            f"{truncate(OFFER_LABELS[lead.offer], 17):<17} "
            f"{truncate(FOLLOWUP_STATUS_LABELS.get(followup_status, followup_status), 15):<15} "
            f"{age_label(lead.created_at):<6} "
            f"{truncate(lead.channel or 'n/a', 14):<14} "
            f"{truncate(lead.role or 'n/a', 24):<24} "
            f"{truncate(lead.contact if show_contact else mask_contact(lead.contact), 22):<22} "
            f"{suggested_action(lead)}"
        )

    lines.extend(["", "Details:"])
    for index, lead in enumerate(rows, start=1):
        notes = lead.notes if show_notes else truncate(lead.notes, 180)
        followup_status = latest_followup.get(lead.id, "new")
        lines.append(
            f"- {index}. id={lead.id}; created={date_label(lead.created_at)}; "
            f"followup={FOLLOWUP_STATUS_LABELS.get(followup_status, followup_status)}; "
            f"source={lead.source or 'n/a'}; consent={lead.consent_accepted if lead.consent_accepted is not None else 'n/a'}"
        )
        if notes:
            lines.append(f"  notes: {notes}")
    return "\n".join(lines)


def render_markdown(
    rows: list[QueueLead],
    total_filtered: int,
    total_loaded: int,
    input_path: Path,
    show_contact: bool,
    show_notes: bool,
    latest_followup: dict[str, str],
    followup_state_path: Path,
) -> str:
    lines = [
        "# HH Resume Booster Follow-up Queue",
        "",
        f"- Input: `{input_path}`",
        f"- Follow-up state: `{followup_state_path}`",
        f"- Loaded: `{total_loaded}`",
        f"- Matched: `{total_filtered}`",
        f"- Shown: `{len(rows)}`",
        f"- Contact: `{'visible' if show_contact else 'masked'}`",
        "",
        "| # | Intent | Offer | Follow-up | Age | Channel | Role | Contact | Suggested action |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for index, lead in enumerate(rows, start=1):
        followup_status = latest_followup.get(lead.id, "new")
        notes = lead.notes if show_notes else truncate(lead.notes, 120)
        role = escape_md(truncate(lead.role or "n/a", 80))
        contact = escape_md(truncate(lead.contact if show_contact else mask_contact(lead.contact), 80))
        action = escape_md(suggested_action(lead))
        if notes:
            action = f"{action}<br>Notes: {escape_md(notes)}"
        lines.append(
            f"| {index} | {escape_md(INTENT_LABELS[lead.intent])} | "
            f"{escape_md(OFFER_LABELS[lead.offer])} | "
            f"{escape_md(FOLLOWUP_STATUS_LABELS.get(followup_status, followup_status))} | "
            f"{age_label(lead.created_at)} | "
            f"{escape_md(lead.channel or 'n/a')} | {role} | {contact} | {action} |"
        )
    return "\n".join(lines) + "\n"


def escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a read-only concierge follow-up queue for HH Resume Booster leads.")
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"JSON/CSV/JSONL leads file. Defaults to {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "--intent",
        action="append",
        help="Filter intent: ready, maybe, not_now, all. Comma-separated or repeated. Defaults to ready,maybe.",
    )
    parser.add_argument(
        "--offer",
        action="append",
        help="Filter offer: avatar, audit, response, all. Comma-separated or repeated. Defaults to all.",
    )
    parser.add_argument("--channel", help="Exact channel filter, case-insensitive.")
    parser.add_argument("--role-contains", help="Substring filter for role/profession.")
    parser.add_argument("--days", type=int, help="Only leads created in the last N days.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum rows to show. Defaults to 20.")
    parser.add_argument("--oldest-first", action="store_true", help="Within each intent, show oldest leads first.")
    parser.add_argument("--show-contact", action="store_true", help="Print unmasked contact values for actual follow-up.")
    parser.add_argument("--show-notes", action="store_true", help="Print full notes instead of a short preview.")
    parser.add_argument(
        "--followup-state",
        type=Path,
        default=DEFAULT_FOLLOWUP_STATE,
        help=f"Optional follow-up outcome JSONL state. Defaults to {DEFAULT_FOLLOWUP_STATE}",
    )
    parser.add_argument("--include-closed", action="store_true", help="Include leads with closed follow-up states.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--markdown", action="store_true", help="Print a Markdown table.")
    args = parser.parse_args()

    if args.limit < 1:
        raise ValueError("--limit must be positive")

    intents = parse_filter(args.intent, set(INTENT_LABELS), {"ready", "maybe"})
    offers = parse_filter(args.offer, set(OFFER_LABELS), set(OFFER_LABELS))
    if not args.input.exists():
        if args.json:
            print(
                json.dumps(
                    {
                        "input": str(args.input),
                        "followup_state": str(args.followup_state),
                        "exists": False,
                        "loaded": 0,
                        "matched": 0,
                        "shown": 0,
                        "contact_masked": not args.show_contact,
                        "rows": [],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(
                "\n".join(
                    [
                        "HH Resume Booster follow-up queue",
                        f"input: {args.input}",
                        "loaded: 0",
                        "matched: 0",
                        "shown: 0",
                        "",
                        "Data file is missing. Start the production server and collect the first lead, then rerun the queue.",
                    ]
                )
            )
        return 0

    leads = load_rows(args.input)
    latest_followup = load_followup_state(args.followup_state)
    filtered = filter_leads(leads, intents, offers, args.channel, args.role_contains, args.days)
    filtered = filter_followup_open(filtered, latest_followup, args.include_closed)
    sorted_rows = sort_leads(filtered, args.oldest_first)
    selected = sorted_rows[: args.limit]

    if args.json:
        print(
            json.dumps(
                {
                    "input": str(args.input),
                    "followup_state": str(args.followup_state),
                    "loaded": len(leads),
                    "matched": len(filtered),
                    "shown": len(selected),
                    "contact_masked": not args.show_contact,
                    "closed_followups_included": bool(args.include_closed),
                    "rows": [lead_to_dict(lead, args.show_contact, args.show_notes, latest_followup) for lead in selected],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif args.markdown:
        print(
            render_markdown(
                selected,
                len(filtered),
                len(leads),
                args.input,
                args.show_contact,
                args.show_notes,
                latest_followup,
                args.followup_state,
            ),
            end="",
        )
    else:
        print(
            render_text(
                selected,
                len(filtered),
                len(leads),
                args.input,
                intents,
                offers,
                args.show_contact,
                args.show_notes,
                latest_followup,
                args.followup_state,
                args.include_closed,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
