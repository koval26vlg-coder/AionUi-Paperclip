from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hh_resume_booster_data_quality import (
    build_audit as build_data_quality_audit,
    load_experiment as load_data_quality_experiment,
    load_rows as load_data_quality_rows,
)
from hh_resume_booster_metrics import load_payload, summarize
from hh_resume_booster_followup_queue import OFFER_LABELS, load_rows as load_followup_rows
from hh_resume_booster_followup_state import load_events, summarize as summarize_followups


def get_offer(summary: dict[str, Any], offer_id: str) -> dict[str, Any]:
    for item in summary["by_offer"]:
        if item["offer"] == offer_id:
            return item
    raise KeyError(offer_id)


def data_quality_ready(audit: dict[str, Any]) -> bool:
    return audit["error_count"] == 0 and audit["warning_count"] == 0


def data_quality_blockers(audit: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if audit["error_count"]:
        blockers.append(f"data_quality_errors: {audit['error_count']}")
    if audit["warning_count"]:
        blockers.append(f"data_quality_warnings: {audit['warning_count']}")
    return blockers


def decision_blockers(summary: dict[str, Any], data_quality_audit: dict[str, Any]) -> list[str]:
    experiment = summary["experiment"]
    blockers: list[str] = data_quality_blockers(data_quality_audit)
    if not experiment["started_at"]:
        blockers.append("test_not_started: нет даты старта experiment state")
    if not experiment["days_complete"]:
        blockers.append(
            f"days_not_complete: день {experiment['elapsed_days']}/{experiment['duration_days']}"
        )
    if summary["total_leads"] < experiment["target_leads"]:
        blockers.append(f"leads: {summary['total_leads']}/{experiment['target_leads']}")
    if summary["total_paid_intent"] < experiment["target_paid_intent"]:
        blockers.append(f"paid_intent: {summary['total_paid_intent']}/{experiment['target_paid_intent']}")
    if summary["unique_channels"] < experiment["target_channels"]:
        blockers.append(f"channels: {summary['unique_channels']}/{experiment['target_channels']}")
    if summary["unique_roles"] < experiment["target_roles"]:
        blockers.append(f"roles: {summary['unique_roles']}/{experiment['target_roles']}")
    for item in summary.get("offer_coverage", []):
        if not item["ready"]:
            blockers.append(f"offer_coverage_{item['offer']}: {item['leads']}/{item['target']}")
    return blockers


def build_decision(summary: dict[str, Any]) -> dict[str, str]:
    avatar = get_offer(summary, "avatar")
    audit = get_offer(summary, "audit")
    response = get_offer(summary, "response")
    non_avatar = max([audit, response], key=lambda item: (item["paid_intent"], item["leads"]))
    winner = summary["winner"]

    if avatar["paid_intent"] > non_avatar["paid_intent"]:
        return {
            "decision": "avatar_primary_candidate",
            "headline": "Аватарка может быть самостоятельным front-offer.",
            "recommendation": (
                "Оставить avatar-only как платный входной оффер, но не отказываться от расширения в audit/response: "
                "их стоит использовать как upsell после первичной заявки."
            ),
        }

    if avatar["paid_intent"] == non_avatar["paid_intent"]:
        return {
            "decision": "inconclusive_avatar_tie",
            "headline": "Аватарка не доказала преимущество над большим оффером.",
            "recommendation": (
                "Не делать avatar-only ядром продукта по этим данным. Оставить как лид-магнит или недорогой вход, "
                "а следующий тест усилить сегментом, ценой или формулировкой audit/response."
            ),
        }

    if winner["offer"] == "audit":
        return {
            "decision": "avatar_lead_magnet_build_resume_audit",
            "headline": "Аватарку оставить лид-магнитом, основной MVP строить вокруг аудита резюме.",
            "recommendation": (
                "Позиционировать продукт как аудит профиля hh.ru: фото, заголовок, опыт, блок о себе и приоритет правок. "
                "Аватарку использовать как быстрый вход в воронку."
            ),
        }

    return {
        "decision": "avatar_module_build_vacancy_response_pack",
        "headline": "Аватарку оставить модулем, основной MVP строить вокруг отклика под вакансию.",
        "recommendation": (
            "Позиционировать продукт как пакет под конкретную вакансию: адаптация резюме, короткое письмо, "
            "аргументы fit и чеклист перед отправкой. Фото остается частью пакета, а не отдельным ядром."
        ),
    }


def format_gate_row(label: str, value: Any, target: Any, ready: bool) -> str:
    status = "ok" if ready else "wait"
    return f"| {label} | {value} | {target} | {status} |"


def default_followup_state_path(input_path: Path) -> Path:
    if input_path.name == "hh-booster-leads.jsonl":
        return input_path.with_name("hh-booster-followups.jsonl")
    return input_path.with_suffix(".followups.jsonl")


def load_followup_summary(input_path: Path, followup_state_path: Path | None) -> tuple[Path | None, dict[str, Any] | None]:
    candidate = followup_state_path or default_followup_state_path(input_path)
    if not candidate.exists():
        return (candidate if followup_state_path else None), None
    leads = load_followup_rows(input_path)
    events = load_events(candidate)
    return candidate, summarize_followups(events, leads)


def default_data_quality_experiment_path(input_path: Path, explicit_path: Path | None) -> Path | None:
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(explicit_path)
    if input_path.name == "hh-booster-leads.jsonl":
        candidates.append(input_path.with_name("hh-booster-experiment.json"))
    candidates.append(input_path.with_suffix(".experiment.json"))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return explicit_path


def load_data_quality_audit(input_path: Path, experiment_path: Path | None) -> tuple[Path | None, dict[str, Any]]:
    resolved_experiment = default_data_quality_experiment_path(input_path, experiment_path)
    experiment = load_data_quality_experiment(resolved_experiment) if resolved_experiment else {}
    rows = load_data_quality_rows(input_path)
    return resolved_experiment, build_data_quality_audit(rows, experiment)


def get_followup_offer(followup_summary: dict[str, Any] | None, offer_id: str) -> dict[str, Any]:
    if not followup_summary:
        return {
            "offer": offer_id,
            "label": OFFER_LABELS[offer_id],
            "tracked": 0,
            "confirmed_paid_intent": 0,
            "paid": 0,
            "declined": 0,
            "open": 0,
        }
    for item in followup_summary["by_offer"]:
        if item["offer"] == offer_id:
            return item
    raise KeyError(offer_id)


def followup_winner(followup_summary: dict[str, Any] | None) -> dict[str, Any] | None:
    if not followup_summary or followup_summary["tracked_leads"] == 0:
        return None
    return max(
        followup_summary["by_offer"],
        key=lambda item: (item["confirmed_paid_intent"], item["paid"], item["tracked"]),
    )


def render_followup_signal(summary: dict[str, Any], followup_summary: dict[str, Any] | None) -> list[str]:
    winner = followup_winner(followup_summary)
    if not followup_summary:
        return [
            "Follow-up state: `not_available`",
            "",
            "Follow-up outcomes were not provided. Product decision uses only primary paid intent from the form.",
        ]
    if followup_summary["tracked_leads"] == 0:
        return [
            "Follow-up state: `empty`",
            "",
            "No manual follow-up outcomes have been tracked yet.",
        ]

    primary_winner = summary["winner"]["offer"]
    lines = [
        "Follow-up state: `available`",
        "",
        f"- Tracked leads: `{followup_summary['tracked_leads']}`",
        f"- Open follow-ups: `{followup_summary['open_followups']}`",
        f"- Confirmed paid intent: `{followup_summary['confirmed_paid_intent']}`",
        f"- Paid: `{followup_summary['paid']}`",
    ]
    if winner:
        lines.append(f"- Follow-up winner: **{winner['label']}**")
        if winner["offer"] != primary_winner and (winner["confirmed_paid_intent"] or winner["paid"]):
            lines.append(
                "- Caveat: follow-up winner differs from primary form winner. Treat final product decision as needing manual review."
            )
    return lines


def render_data_quality_signal(audit: dict[str, Any]) -> list[str]:
    state = "passed" if data_quality_ready(audit) else "blocked"
    lines = [
        f"Data quality state: `{state}`",
        "",
        f"- Rows checked: `{audit['total_rows']}`",
        f"- Errors: `{audit['error_count']}`",
        f"- Warnings: `{audit['warning_count']}`",
        f"- Info: `{audit['info_count']}`",
        "",
        "Issue counts:",
    ]
    if audit["issue_counts"]:
        lines.extend([f"- `{code}`: `{count}`" for code, count in audit["issue_counts"].items()])
    else:
        lines.append("- `n/a`")

    blocking_issues = [
        item for item in audit["issues"] if item["severity"] in {"error", "warn"}
    ][:12]
    lines.extend(["", "Blocking issues:"])
    if not blocking_issues:
        lines.append("- `n/a`")
    for item in blocking_issues:
        contact = item["contact_masked"] or "n/a"
        lead_id = item["id"] or "n/a"
        lines.append(
            f"- `{item['severity']}` row `{item['row']}` code `{item['code']}` "
            f"id `{lead_id}` contact `{contact}`: {item['detail']}"
        )
    return lines


def render_report(
    summary: dict[str, Any],
    input_path: Path,
    experiment_path: Path | None,
    draft: bool,
    followup_state_path: Path | None,
    followup_summary: dict[str, Any] | None,
    data_quality_experiment_path: Path | None,
    data_quality_audit: dict[str, Any],
) -> str:
    blockers = decision_blockers(summary, data_quality_audit)
    ready = summary["decision_ready"] and data_quality_ready(data_quality_audit)
    decision = build_decision(summary) if ready else None
    experiment = summary["experiment"]
    generated_at = datetime.now(timezone.utc).isoformat()

    lines = [
        "# HH Resume Booster Decision Report",
        "",
        f"Generated at: `{generated_at}`",
        f"Input: `{input_path}`",
        f"Experiment state: `{experiment_path or 'auto/embedded'}`",
        f"Data quality experiment state: `{data_quality_experiment_path or 'auto/not_available'}`",
        f"Follow-up state: `{followup_state_path or 'auto/not_available'}`",
        f"Mode: `{'draft' if draft else 'strict'}`",
        "",
        "## Decision",
        "",
    ]

    if ready and decision:
        lines.extend(
            [
                f"Status: `ready`",
                f"Decision code: `{decision['decision']}`",
                "",
                f"**{decision['headline']}**",
                "",
                decision["recommendation"],
            ]
        )
    else:
        lines.extend(
            [
                "Status: `not_ready`",
                "",
                "Финальное решение не принимается, потому что gate еще не пройден.",
                "",
                "Blockers:",
            ]
        )
        lines.extend([f"- `{item}`" for item in blockers] or ["- `unknown`"])

    lines.extend(
        [
            "",
            "## Gate",
            "",
            "| Gate | Current | Target | Status |",
            "| --- | ---: | ---: | --- |",
            format_gate_row(
                "Days",
                experiment["elapsed_days"],
                experiment["duration_days"],
                bool(experiment["days_complete"]),
            ),
            format_gate_row(
                "Leads",
                summary["total_leads"],
                experiment["target_leads"],
                summary["total_leads"] >= experiment["target_leads"],
            ),
            format_gate_row(
                "Paid intent",
                summary["total_paid_intent"],
                experiment["target_paid_intent"],
                summary["total_paid_intent"] >= experiment["target_paid_intent"],
            ),
            format_gate_row(
                "Channels",
                summary["unique_channels"],
                experiment["target_channels"],
                summary["unique_channels"] >= experiment["target_channels"],
            ),
            format_gate_row(
                "Roles",
                summary["unique_roles"],
                experiment["target_roles"],
                summary["unique_roles"] >= experiment["target_roles"],
            ),
            format_gate_row(
                "Per-offer leads",
                "ok" if summary["offer_coverage_ready"] else "wait",
                experiment["target_min_leads_per_offer"],
                bool(summary["offer_coverage_ready"]),
            ),
            "",
            "## Paid Intent By Offer",
            "",
            "| Offer | Leads | Paid intent | Paid rate |",
            "| --- | ---: | ---: | ---: |",
        ]
    )

    for item in summary["by_offer"]:
        lines.append(
            f"| {item['label']} | {item['leads']} | {item['paid_intent']} | {item['paid_intent_rate']}% |"
        )

    lines.extend(
        [
            "",
            "## Offer Coverage",
            "",
            "| Offer | Leads | Target | Status |",
            "| --- | ---: | ---: | --- |",
        ]
    )

    for item in summary["offer_coverage"]:
        lines.append(
            f"| {item['label']} | {item['leads']} | {item['target']} | {'ok' if item['ready'] else 'wait'} |"
        )

    lines.extend(
        [
            "",
            "## Data Quality",
            "",
            *render_data_quality_signal(data_quality_audit),
            "",
            "## Follow-up Outcomes",
            "",
            *render_followup_signal(summary, followup_summary),
            "",
            "| Offer | Tracked | Confirmed paid intent | Paid | Declined | Open |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for offer_id in OFFER_LABELS:
        item = get_followup_offer(followup_summary, offer_id)
        lines.append(
            f"| {item['label']} | {item['tracked']} | {item['confirmed_paid_intent']} | "
            f"{item['paid']} | {item['declined']} | {item['open']} |"
        )

    lines.extend(
        [
            "",
            f"Winner by current metric: **{summary['winner']['label']}**.",
            "",
            "## Daily Pace",
            "",
            f"- Active days with leads: `{summary['daily']['active_days']}`",
            f"- Days available: `{summary['daily']['days_available']}`",
            f"- Average leads/day: `{summary['daily']['average_leads_per_active_day']}`",
            f"- Average paid/day: `{summary['daily']['average_paid_per_active_day']}`",
            f"- Required leads/day: `{summary['daily']['required_leads_per_remaining_day']}`",
            f"- Required paid/day: `{summary['daily']['required_paid_per_remaining_day']}`",
            "",
            "## Interpretation Rules",
            "",
            "- `ready` допустим только после 14 дней и всех минимальных порогов.",
            "- Каждый оффер должен набрать минимальную выборку, иначе сравнение трех офферов не считается готовым.",
            "- Если `avatar` уступает `audit` или `response`, аватарка остается лид-магнитом или модулем.",
            "- Если `audit` выигрывает, MVP строится как аудит профиля hh.ru.",
            "- Если `response` выигрывает, MVP строится вокруг отклика под конкретную вакансию.",
            "- Если `avatar` выигрывает, его можно тестировать как самостоятельный front-offer с upsell.",
            "- Follow-up outcomes не заменяют 14-дневный gate, но усиливают или ослабляют качество primary paid-intent сигнала.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build HH Resume Booster paid-intent decision report.")
    parser.add_argument("input", type=Path, help="Exported JSON/CSV or server JSONL with leads.")
    parser.add_argument("--experiment-state", type=Path, help="Optional experiment state JSON.")
    parser.add_argument(
        "--followup-state",
        type=Path,
        help="Optional follow-up outcome JSONL. Server JSONL automatically tries hh-booster-followups.jsonl next to leads.",
    )
    parser.add_argument("--out", type=Path, help="Write Markdown report to this file.")
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Allow report generation before decision gates are complete.",
    )
    args = parser.parse_args()

    data_quality_experiment_path, data_quality_audit = load_data_quality_audit(args.input, args.experiment_state)
    leads, experiment = load_payload(args.input, args.experiment_state)
    summary = summarize(leads, experiment)
    followup_path, followup_summary = load_followup_summary(args.input, args.followup_state)
    report = render_report(
        summary,
        args.input,
        args.experiment_state,
        args.draft,
        followup_path,
        followup_summary,
        data_quality_experiment_path,
        data_quality_audit,
    )

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")

    if (not summary["decision_ready"] or not data_quality_ready(data_quality_audit)) and not args.draft:
        print(
            "Decision gate is not ready or data quality audit is not clean. "
            "Rerun with --draft to write a draft report before gates pass.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
