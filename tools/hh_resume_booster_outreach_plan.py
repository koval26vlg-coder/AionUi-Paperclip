from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from hh_resume_booster_metrics import (
    Lead,
    OFFER_LABELS,
    default_experiment,
    load_experiment_for_data,
    load_payload,
    summarize,
)


CHANNELS = ["hh.ru", "Telegram", "VK", "Авито Работа", "Рекомендация", "Другое"]
DEFAULT_DATA_PATH = Path("apps/aion-vision/data/hh-booster-leads.jsonl")
OFFERS = [
    {"offer": "avatar", "label": OFFER_LABELS["avatar"]},
    {"offer": "audit", "label": OFFER_LABELS["audit"]},
    {"offer": "response", "label": OFFER_LABELS["response"]},
]


@dataclass(frozen=True)
class OfferPlan:
    offer: str
    label: str
    leads: int
    target: int
    deficit: int
    recommended_leads_today: int


def normalize_base_url(value: str | None) -> str | None:
    if not value:
        return None
    trimmed = value.strip().rstrip("/")
    return trimmed or None


def is_local_base_url(value: str | None) -> bool:
    if not value:
        return True
    lowered = value.lower()
    return "127.0.0.1" in lowered or "localhost" in lowered


def load_current_state(data_path: Path, experiment_path: Path | None) -> tuple[list[Lead], Any]:
    if data_path.exists():
        return load_payload(data_path, experiment_path)
    if experiment_path and experiment_path.exists():
        return [], load_experiment_for_data(data_path, experiment_path)
    return [], default_experiment()


def used_channels(leads: list[Lead]) -> list[str]:
    return sorted({lead.channel for lead in leads if lead.channel})


def channel_links(public_base_url: str | None) -> list[dict[str, str]]:
    base = normalize_base_url(public_base_url) or "http://127.0.0.1:8787"
    return [
        {
            "channel": channel,
            "url": f"{base}/#hh-booster-public?channel={quote(channel)}",
        }
        for channel in CHANNELS
    ]


def offer_links(public_base_url: str | None, summary: dict[str, Any] | None = None) -> list[dict[str, str]]:
    base = normalize_base_url(public_base_url) or "http://127.0.0.1:8787"
    offers = summary.get("offer_coverage", []) if summary else OFFERS
    return [
        {
            "offer": item["offer"],
            "label": item["label"],
            "url": f"{base}/#hh-booster-public?offer={quote(item['offer'])}",
        }
        for item in offers
    ]


def offer_channel_links(public_base_url: str | None, summary: dict[str, Any] | None = None) -> list[dict[str, str]]:
    base = normalize_base_url(public_base_url) or "http://127.0.0.1:8787"
    offers = summary.get("offer_coverage", []) if summary else OFFERS
    return [
        {
            "offer": item["offer"],
            "label": item["label"],
            "channel": channel,
            "url": f"{base}/#hh-booster-public?channel={quote(channel)}&offer={quote(item['offer'])}",
        }
        for item in offers
        for channel in CHANNELS
    ]


def build_offer_plan(summary: dict[str, Any]) -> list[OfferPlan]:
    days_available = max(1, int(summary["daily"]["days_available"] or 0))
    plans: list[OfferPlan] = []
    for item in summary["offer_coverage"]:
        deficit = max(0, int(item["target"]) - int(item["leads"]))
        plans.append(
            OfferPlan(
                offer=item["offer"],
                label=item["label"],
                leads=int(item["leads"]),
                target=int(item["target"]),
                deficit=deficit,
                recommended_leads_today=ceil_div(deficit, days_available),
            )
        )
    return sorted(plans, key=lambda item: (item.deficit, -item.leads), reverse=True)


def ceil_div(value: int, divisor: int) -> int:
    if value <= 0:
        return 0
    return (value + divisor - 1) // divisor


def build_plan(data_path: Path, experiment_path: Path | None, public_base_url: str | None) -> dict[str, Any]:
    leads, experiment = load_current_state(data_path, experiment_path)
    summary = summarize(leads, experiment)
    experiment_summary = summary["experiment"]
    days_available = max(1, int(summary["daily"]["days_available"] or 0))
    offer_plan = build_offer_plan(summary)
    channels_used = used_channels(leads)
    channel_candidates = [channel for channel in CHANNELS if channel.casefold() not in {item.casefold() for item in channels_used}]
    channel_deficit = max(0, int(experiment_summary["target_channels"]) - int(summary["unique_channels"]))
    lead_deficit = max(0, int(experiment_summary["target_leads"]) - int(summary["total_leads"]))
    paid_deficit = max(0, int(experiment_summary["target_paid_intent"]) - int(summary["total_paid_intent"]))
    role_deficit = max(0, int(experiment_summary["target_roles"]) - int(summary["unique_roles"]))

    actions: list[str] = []
    if not experiment_summary["started_at"]:
        actions.append("Нажать `Старт теста` в операторской панели, чтобы зафиксировать начало 14-дневного окна.")
    if is_local_base_url(public_base_url):
        actions.append("Не публиковать localhost/127.0.0.1; перед внешней раздачей указать `-PublicBaseUrl`.")
    if channel_deficit:
        recommended_channels = channel_candidates[:channel_deficit] or CHANNELS[:channel_deficit]
        actions.append(f"Добавить канал привлечения: {', '.join(recommended_channels)}.")
    if role_deficit:
        actions.append(f"Добрать роли/профессии: минимум еще {role_deficit}.")
    for item in offer_plan:
        if item.deficit:
            actions.append(
                f"Дособрать `{item.label}`: еще {item.deficit} лидов, сегодня минимум {item.recommended_leads_today}."
            )
    if paid_deficit:
        actions.append(
            f"Усилить paid intent: нужно еще {paid_deficit} `Готов оплатить`; первыми обрабатывать ready/maybe follow-up."
        )
    if not actions:
        actions.append("Все текущие операционные gates закрыты; продолжать сбор до конца 14 дней или готовить final report.")

    return {
        "data_path": str(data_path),
        "experiment_path": str(experiment_path) if experiment_path else None,
        "public_base_url": normalize_base_url(public_base_url),
        "local_url_warning": is_local_base_url(public_base_url),
        "summary": summary,
        "deficits": {
            "leads": lead_deficit,
            "paid_intent": paid_deficit,
            "channels": channel_deficit,
            "roles": role_deficit,
            "offer_coverage": sum(item.deficit for item in offer_plan),
        },
        "recommended_today": {
            "leads": ceil_div(lead_deficit, days_available),
            "paid_intent": ceil_div(paid_deficit, days_available),
            "offers": [asdict(item) for item in offer_plan],
        },
        "channels": {
            "used": channels_used,
            "candidates": channel_candidates,
            "links": channel_links(public_base_url),
        },
        "offer_links": offer_links(public_base_url, summary),
        "offer_channel_links": offer_channel_links(public_base_url, summary),
        "actions": actions,
    }


def render_text(plan: dict[str, Any]) -> str:
    summary = plan["summary"]
    deficits = plan["deficits"]
    today = plan["recommended_today"]
    lines = [
        "HH Resume Booster outreach plan",
        f"data_path: {plan['data_path']}",
        f"started_at: {summary['experiment']['started_at'] or 'n/a'}",
        f"day: {summary['experiment']['elapsed_days']}/{summary['experiment']['duration_days']}",
        f"days_available: {summary['daily']['days_available']}",
        f"decision_ready: {str(summary['decision_ready']).lower()}",
        "",
        "deficits:",
        f"- leads: {deficits['leads']}",
        f"- paid_intent: {deficits['paid_intent']}",
        f"- channels: {deficits['channels']}",
        f"- roles: {deficits['roles']}",
        f"- offer_coverage: {deficits['offer_coverage']}",
        "",
        "recommended_today:",
        f"- leads: {today['leads']}",
        f"- paid_intent: {today['paid_intent']}",
        "- offers:",
    ]
    for item in today["offers"]:
        lines.append(
            f"  - {item['label']}: leads={item['leads']}/{item['target']}, "
            f"deficit={item['deficit']}, today={item['recommended_leads_today']}"
        )
    lines.extend(["", "channels:"])
    lines.append(f"- used: {', '.join(plan['channels']['used']) if plan['channels']['used'] else 'n/a'}")
    lines.append(
        f"- candidates: {', '.join(plan['channels']['candidates']) if plan['channels']['candidates'] else 'n/a'}"
    )
    if plan["local_url_warning"]:
        lines.append("- warning: public URL is local or missing")
    lines.extend(["", "offer_links:"])
    for link in plan["offer_links"]:
        lines.append(f"- {link['label']}: {link['url']}")
    lines.extend(["", "offer_channel_examples:"])
    for link in plan["offer_channel_links"][:6]:
        lines.append(f"- {link['label']} / {link['channel']}: {link['url']}")
    lines.extend(["", "actions:"])
    lines.extend(f"- {action}" for action in plan["actions"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a read-only daily outreach plan for HH Resume Booster.")
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"Leads JSON/CSV/JSONL. Defaults to {DEFAULT_DATA_PATH}.",
    )
    parser.add_argument("--experiment-state", type=Path, help="Optional experiment state JSON.")
    parser.add_argument("--public-base-url", help="Public base URL used for candidate links.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    plan = build_plan(args.input, args.experiment_state, args.public_base_url)
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(render_text(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
