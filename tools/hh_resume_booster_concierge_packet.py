from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hh_resume_booster_followup_queue import (
    DEFAULT_FOLLOWUP_STATE,
    DEFAULT_INPUT,
    FOLLOWUP_STATUS_LABELS,
    INTENT_LABELS,
    INTENT_PRIORITY,
    OFFER_LABELS,
    QueueLead,
    age_label,
    date_label,
    filter_followup_open,
    filter_leads,
    lead_to_dict,
    load_followup_state,
    load_rows,
    mask_contact,
    parse_filter,
    sort_leads,
    truncate,
)


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PATH = ROOT / ".venv-sml" / "Scripts" / "python.exe"
FOLLOWUP_STATE_SCRIPT = ROOT / "tools" / "hh_resume_booster_followup_state.py"

OFFER_PRICES = {
    "avatar": 199,
    "audit": 399,
    "response": 799,
}

OFFER_REQUESTS = {
    "avatar": "пришли текущее фото/аватарку и ссылку на профиль hh.ru, если удобно",
    "audit": "пришли ссылку на резюме hh.ru или PDF/скрин резюме",
    "response": "пришли ссылку на вакансию и резюме, с которым хочешь откликаться",
}

OFFER_PROMISES = {
    "avatar": "дам короткий разбор первого впечатления и что поменять в фото",
    "audit": "верну 3 главные правки по резюме и формулировкам",
    "response": "соберу позиционирование и черновик отклика под конкретную вакансию",
}


@dataclass(frozen=True)
class PacketItem:
    lead: QueueLead
    priority: str
    followup_status: str
    message: str
    mark_commands: list[str]
    missing_inputs: list[str]


def priority_for(lead: QueueLead) -> str:
    if lead.intent == "ready":
        return "P0"
    if lead.intent == "maybe":
        return "P1"
    return "P3"


def missing_inputs_for(lead: QueueLead) -> list[str]:
    missing = []
    if lead.offer == "response":
        missing.extend(["ссылка на вакансию", "резюме/профиль hh.ru"])
    elif lead.offer == "audit":
        missing.append("резюме/профиль hh.ru")
    else:
        missing.append("фото или профиль hh.ru")
    if not lead.role:
        missing.append("роль/должность")
    return missing


def first_message(lead: QueueLead) -> str:
    offer_label = OFFER_LABELS[lead.offer]
    price = OFFER_PRICES[lead.offer]
    request = OFFER_REQUESTS[lead.offer]
    promise = OFFER_PROMISES[lead.offer]
    role_suffix = f" по роли {lead.role}" if lead.role else ""

    if lead.intent == "ready":
        return (
            f"Привет! Спасибо за заявку на {offer_label.lower()}{role_suffix}. "
            f"Формат стоит {price} руб. Если актуально, {request}. "
            f"После этого {promise}. Без обещаний гарантированных приглашений, только практичный разбор."
        )
    if lead.intent == "maybe":
        return (
            f"Привет! Ты отметил интерес к формату {offer_label.lower()}{role_suffix}. "
            f"Хочу понять, что было бы реально полезно перед оплатой: {request}. "
            f"Я коротко скажу, подойдет ли этот формат, и что именно получится на выходе."
        )
    return (
        f"Привет! Спасибо за ответ по формату {offer_label.lower()}. "
        "Не продаю сейчас: хочу понять, чего не хватает, чтобы такой сервис был полезен. "
        "Можешь коротко написать главное сомнение?"
    )


def mark_command(lead_id: str, status: str, note: str) -> str:
    escaped_note = note.replace('"', "'")
    return (
        f'& "{PYTHON_PATH}" "{FOLLOWUP_STATE_SCRIPT}" '
        f'--leads "{DEFAULT_INPUT}" --state "{DEFAULT_FOLLOWUP_STATE}" '
        f'mark "{lead_id}" --status {status} --note "{escaped_note}" --write'
    )


def build_packet_item(lead: QueueLead, latest_followup: dict[str, str]) -> PacketItem:
    followup_status = latest_followup.get(lead.id, "new")
    commands = [
        mark_command(lead.id, "contacted", "first message sent"),
        mark_command(lead.id, "responded", "candidate replied"),
        mark_command(lead.id, "confirmed_paid_intent", "confirmed willingness to pay"),
        mark_command(lead.id, "paid", f"paid {OFFER_PRICES[lead.offer]} rub"),
        mark_command(lead.id, "declined", "declined after follow-up"),
    ]
    return PacketItem(
        lead=lead,
        priority=priority_for(lead),
        followup_status=followup_status,
        message=first_message(lead),
        mark_commands=commands,
        missing_inputs=missing_inputs_for(lead),
    )


def packet_to_dict(item: PacketItem, show_contact: bool, show_notes: bool, latest_followup: dict[str, str]) -> dict[str, Any]:
    lead_dict = lead_to_dict(item.lead, show_contact, show_notes, latest_followup)
    return {
        **lead_dict,
        "priority": item.priority,
        "price_rub": OFFER_PRICES[item.lead.offer],
        "first_message": item.message,
        "missing_inputs": item.missing_inputs,
        "mark_commands": item.mark_commands,
    }


def render_text(
    items: list[PacketItem],
    *,
    input_path: Path,
    followup_state_path: Path,
    total_loaded: int,
    total_matched: int,
    show_contact: bool,
    show_notes: bool,
    latest_followup: dict[str, str],
) -> str:
    lines = [
        "HH Resume Booster concierge packet",
        f"input: {input_path}",
        f"followup_state: {followup_state_path}",
        f"loaded: {total_loaded}",
        f"matched: {total_matched}",
        f"shown: {len(items)}",
        f"contact: {'visible' if show_contact else 'masked; use --show-contact only during real follow-up'}",
        f"notes: {'full' if show_notes else 'preview'}",
        "",
    ]
    if not items:
        lines.append("Нет открытых лидов по текущим фильтрам.")
        return "\n".join(lines)

    for index, item in enumerate(items, start=1):
        lead = item.lead
        contact = lead.contact if show_contact else mask_contact(lead.contact)
        notes = lead.notes if show_notes else truncate(lead.notes, 180)
        lines.extend(
            [
                f"## {index}. {item.priority} / {INTENT_LABELS[lead.intent]} / {OFFER_LABELS[lead.offer]}",
                f"id: {lead.id}",
                f"created: {date_label(lead.created_at)} ({age_label(lead.created_at)})",
                f"followup: {FOLLOWUP_STATUS_LABELS.get(item.followup_status, item.followup_status)}",
                f"channel: {lead.channel or 'n/a'}",
                f"role: {lead.role or 'n/a'}",
                f"contact: {contact or 'n/a'}",
                f"missing_inputs: {', '.join(item.missing_inputs)}",
                "",
                "message:",
                item.message,
                "",
            ]
        )
        if notes:
            lines.extend(["notes:", notes, ""])
        lines.extend(["mark commands:"])
        for command in item.mark_commands:
            lines.append(command)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_markdown(
    items: list[PacketItem],
    *,
    input_path: Path,
    followup_state_path: Path,
    total_loaded: int,
    total_matched: int,
    show_contact: bool,
    latest_followup: dict[str, str],
) -> str:
    lines = [
        "# HH Resume Booster Concierge Packet",
        "",
        f"- Input: `{input_path}`",
        f"- Follow-up state: `{followup_state_path}`",
        f"- Loaded: `{total_loaded}`",
        f"- Matched: `{total_matched}`",
        f"- Shown: `{len(items)}`",
        f"- Contact: `{'visible' if show_contact else 'masked'}`",
        "",
    ]
    if not items:
        lines.append("Нет открытых лидов по текущим фильтрам.")
        return "\n".join(lines) + "\n"

    for index, item in enumerate(items, start=1):
        lead = item.lead
        contact = lead.contact if show_contact else mask_contact(lead.contact)
        lines.extend(
            [
                f"## {index}. {item.priority} - {INTENT_LABELS[lead.intent]} - {OFFER_LABELS[lead.offer]}",
                "",
                f"- ID: `{lead.id}`",
                f"- Created: `{date_label(lead.created_at)}` / `{age_label(lead.created_at)}`",
                f"- Follow-up: `{FOLLOWUP_STATUS_LABELS.get(item.followup_status, item.followup_status)}`",
                f"- Channel: `{lead.channel or 'n/a'}`",
                f"- Role: `{lead.role or 'n/a'}`",
                f"- Contact: `{contact or 'n/a'}`",
                f"- Missing inputs: `{', '.join(item.missing_inputs)}`",
                "",
                "```text",
                item.message,
                "```",
                "",
                "```powershell",
                item.mark_commands[0],
                item.mark_commands[2],
                item.mark_commands[3],
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def select_items(args: argparse.Namespace) -> tuple[list[PacketItem], int, int, dict[str, str]]:
    if not args.input.exists():
        return [], 0, 0, {}
    intents = parse_filter(args.intent, set(INTENT_LABELS), {"ready", "maybe"})
    offers = parse_filter(args.offer, set(OFFER_LABELS), set(OFFER_LABELS))
    leads = load_rows(args.input)
    latest_followup = load_followup_state(args.followup_state)
    filtered = filter_leads(leads, intents, offers, args.channel, args.role_contains, args.days)
    filtered = filter_followup_open(filtered, latest_followup, args.include_closed)
    sorted_rows = sort_leads(filtered, args.oldest_first)
    selected = sorted_rows[: args.limit]
    return [build_packet_item(lead, latest_followup) for lead in selected], len(leads), len(filtered), latest_followup


def main() -> int:
    parser = argparse.ArgumentParser(description="Build copy-ready concierge follow-up packet for HH Resume Booster leads.")
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT, help=f"Leads JSON/CSV/JSONL path. Defaults to {DEFAULT_INPUT}")
    parser.add_argument("--followup-state", type=Path, default=DEFAULT_FOLLOWUP_STATE, help=f"Follow-up state JSONL. Defaults to {DEFAULT_FOLLOWUP_STATE}")
    parser.add_argument("--intent", action="append", help="Filter intent: ready, maybe, not_now, all. Defaults to ready,maybe.")
    parser.add_argument("--offer", action="append", help="Filter offer: avatar, audit, response, all. Defaults to all.")
    parser.add_argument("--channel", help="Exact channel filter, case-insensitive.")
    parser.add_argument("--role-contains", help="Substring filter for role/profession.")
    parser.add_argument("--days", type=int, help="Only leads created in the last N days.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum packet items. Defaults to 10.")
    parser.add_argument("--oldest-first", action="store_true", help="Within each intent, show oldest leads first.")
    parser.add_argument("--include-closed", action="store_true", help="Include closed follow-up states.")
    parser.add_argument("--show-contact", action="store_true", help="Print unmasked contacts for actual follow-up.")
    parser.add_argument("--show-notes", action="store_true", help="Print full notes.")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown packet.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--out", type=Path, help="Optional output path. Requires --write.")
    parser.add_argument("--write", action="store_true", help="Write --out. Without --write, output is printed.")
    args = parser.parse_args()

    if args.limit < 1:
        raise ValueError("--limit must be positive")
    if args.out and not args.write:
        raise ValueError("--out requires --write to avoid accidental artifact writes")

    items, total_loaded, total_matched, latest_followup = select_items(args)
    if args.json:
        output = json.dumps(
            {
                "input": str(args.input),
                "followup_state": str(args.followup_state),
                "exists": args.input.exists(),
                "loaded": total_loaded,
                "matched": total_matched,
                "shown": len(items),
                "contact_masked": not args.show_contact,
                "rows": [
                    packet_to_dict(item, args.show_contact, args.show_notes, latest_followup)
                    for item in items
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    elif args.markdown:
        output = render_markdown(
            items,
            input_path=args.input,
            followup_state_path=args.followup_state,
            total_loaded=total_loaded,
            total_matched=total_matched,
            show_contact=args.show_contact,
            latest_followup=latest_followup,
        )
    else:
        output = render_text(
            items,
            input_path=args.input,
            followup_state_path=args.followup_state,
            total_loaded=total_loaded,
            total_matched=total_matched,
            show_contact=args.show_contact,
            show_notes=args.show_notes,
            latest_followup=latest_followup,
        )

    if args.out and args.write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
        print(str(args.out))
    else:
        print(output, end="" if output.endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
