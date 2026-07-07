from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


OFFER_LABELS = {
    "avatar": "Аватарка",
    "audit": "Аудит резюме",
    "response": "Отклик под вакансию",
}


@dataclass(frozen=True)
class Lead:
    offer: str
    intent: str
    role: str
    channel: str
    created_at: str | None

    @property
    def paid_intent(self) -> bool:
        return self.intent == "ready"


@dataclass(frozen=True)
class ExperimentInfo:
    started_at: str | None
    duration_days: int
    target_leads: int
    target_paid_intent: int
    target_channels: int
    target_roles: int
    target_min_leads_per_offer: int


def load_payload(path: Path, experiment_path: Path | None = None) -> tuple[list[Lead], ExperimentInfo]:
    if path.suffix.lower() == ".csv":
        return load_csv(path), load_experiment_for_data(path, experiment_path)
    if path.suffix.lower() == ".jsonl":
        return load_jsonl(path), load_experiment_for_data(path, experiment_path)
    leads, experiment = load_json(path)
    if experiment_path:
        experiment = load_experiment_file(experiment_path)
    return leads, experiment


def load_json(path: Path) -> tuple[list[Lead], ExperimentInfo]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = payload.get("leads", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("JSON must be a list of leads or an object with a leads list")
    experiment = payload.get("experimentState", {}) if isinstance(payload, dict) else {}
    return [coerce_lead(row) for row in rows], coerce_experiment(experiment)


def load_csv(path: Path) -> list[Lead]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [coerce_lead(row) for row in csv.DictReader(handle)]


def load_jsonl(path: Path) -> list[Lead]:
    leads: list[Lead] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc
        leads.append(coerce_lead(row))
    return leads


def default_experiment() -> ExperimentInfo:
    return ExperimentInfo(None, 14, 30, 10, 2, 5, 5)


def load_experiment_for_data(data_path: Path, explicit_path: Path | None = None) -> ExperimentInfo:
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(explicit_path)
    if data_path.name == "hh-booster-leads.jsonl":
        candidates.append(data_path.with_name("hh-booster-experiment.json"))
    candidates.append(data_path.with_suffix(".experiment.json"))
    for candidate in candidates:
        if candidate.exists():
            return load_experiment_file(candidate)
    return default_experiment()


def load_experiment_file(path: Path) -> ExperimentInfo:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(payload, dict):
        experiment = payload.get("experimentState")
        if experiment is None:
            experiment = payload.get("experiment")
        if experiment is None:
            experiment = payload
        return coerce_experiment(experiment)
    return default_experiment()


def coerce_lead(row: Any) -> Lead:
    if not isinstance(row, dict):
        raise ValueError(f"Lead row must be an object, got {type(row).__name__}")
    offer = str(row.get("offer", "")).strip()
    intent = str(row.get("intent", "")).strip()
    role = str(row.get("role", "")).strip()
    channel = str(row.get("channel", "")).strip()
    created_at = row.get("createdAt")
    if offer not in OFFER_LABELS:
        raise ValueError(f"Unknown offer: {offer!r}")
    if intent not in {"ready", "maybe", "not_now"}:
        raise ValueError(f"Unknown intent: {intent!r}")
    return Lead(
        offer=offer,
        intent=intent,
        role=role,
        channel=channel,
        created_at=created_at if isinstance(created_at, str) and created_at.strip() else None,
    )


def coerce_experiment(row: Any) -> ExperimentInfo:
    if not isinstance(row, dict):
        row = {}
    return ExperimentInfo(
        started_at=row.get("startedAt") if isinstance(row.get("startedAt"), str) else None,
        duration_days=positive_int(row.get("durationDays"), 14),
        target_leads=positive_int(row.get("targetLeads"), 30),
        target_paid_intent=positive_int(row.get("targetPaidIntent"), 10),
        target_channels=positive_int(row.get("targetChannels"), 2),
        target_roles=positive_int(row.get("targetRoles"), 5),
        target_min_leads_per_offer=positive_int(row.get("targetMinLeadsPerOffer"), 5),
    )


def positive_int(value: Any, fallback: int) -> int:
    return value if isinstance(value, int) and value > 0 else fallback


def summarize(leads: list[Lead], experiment: ExperimentInfo) -> dict[str, Any]:
    by_offer = []
    for offer_id, label in OFFER_LABELS.items():
        offer_leads = [lead for lead in leads if lead.offer == offer_id]
        paid_intent = sum(1 for lead in offer_leads if lead.paid_intent)
        by_offer.append(
            {
                "offer": offer_id,
                "label": label,
                "leads": len(offer_leads),
                "paid_intent": paid_intent,
                "paid_intent_rate": round((paid_intent / len(offer_leads)) * 100, 2) if offer_leads else 0.0,
            }
        )

    total_paid = sum(item["paid_intent"] for item in by_offer)
    winner = max(by_offer, key=lambda item: (item["paid_intent"], item["leads"]))
    offer_coverage = [
        {
            "offer": item["offer"],
            "label": item["label"],
            "leads": item["leads"],
            "target": experiment.target_min_leads_per_offer,
            "ready": item["leads"] >= experiment.target_min_leads_per_offer,
        }
        for item in by_offer
    ]
    offer_coverage_ready = all(item["ready"] for item in offer_coverage)
    unique_roles = sorted({lead.role for lead in leads if lead.role})
    unique_channels = sorted({lead.channel for lead in leads if lead.channel})
    started_at = parse_datetime(experiment.started_at)
    ends_at = started_at + timedelta(days=experiment.duration_days) if started_at else None
    days_complete = bool(ends_at and datetime.now(timezone.utc) >= ends_at)
    elapsed_days = max(0, (datetime.now(timezone.utc) - started_at).days + 1) if started_at else 0
    current_day = min(experiment.duration_days, elapsed_days) if started_at else 0
    days_available = max(0, experiment.duration_days - current_day + 1) if started_at else experiment.duration_days
    by_day = summarize_by_day(leads)
    active_days = len(by_day)

    return {
        "total_leads": len(leads),
        "total_paid_intent": total_paid,
        "paid_intent_rate": round((total_paid / len(leads)) * 100, 2) if leads else 0.0,
        "unique_roles": len(unique_roles),
        "unique_channels": len(unique_channels),
        "experiment": {
            "started_at": experiment.started_at,
            "duration_days": experiment.duration_days,
            "target_leads": experiment.target_leads,
            "target_paid_intent": experiment.target_paid_intent,
            "target_channels": experiment.target_channels,
            "target_roles": experiment.target_roles,
            "target_min_leads_per_offer": experiment.target_min_leads_per_offer,
            "ends_at": ends_at.isoformat() if ends_at else None,
            "elapsed_days": current_day,
            "days_complete": days_complete,
        },
        "daily": {
            "active_days": active_days,
            "days_available": days_available,
            "average_leads_per_active_day": round(len(leads) / active_days, 2) if active_days else 0.0,
            "average_paid_per_active_day": round(total_paid / active_days, 2) if active_days else 0.0,
            "required_leads_per_remaining_day": (
                round(max(0, experiment.target_leads - len(leads)) / days_available, 2)
                if days_available
                else 0.0
            ),
            "required_paid_per_remaining_day": (
                round(max(0, experiment.target_paid_intent - total_paid) / days_available, 2)
                if days_available
                else 0.0
            ),
            "by_day": by_day,
        },
        "by_offer": by_offer,
        "offer_coverage": offer_coverage,
        "offer_coverage_ready": offer_coverage_ready,
        "winner": winner,
        "decision_ready": (
            days_complete
            and len(leads) >= experiment.target_leads
            and total_paid >= experiment.target_paid_intent
            and len(unique_channels) >= experiment.target_channels
            and len(unique_roles) >= experiment.target_roles
            and offer_coverage_ready
        ),
    }


def summarize_by_day(leads: list[Lead]) -> list[dict[str, Any]]:
    by_day: dict[str, dict[str, Any]] = {}
    for lead in leads:
        date_key = date_key_from_iso(lead.created_at)
        row = by_day.setdefault(
            date_key,
            {
                "date": date_key,
                "leads": 0,
                "paid_intent": 0,
                "avatar": 0,
                "audit": 0,
                "response": 0,
            },
        )
        row["leads"] += 1
        if lead.paid_intent:
            row["paid_intent"] += 1
        row[lead.offer] += 1
    return sorted(by_day.values(), key=lambda item: item["date"], reverse=True)


def date_key_from_iso(value: str | None) -> str:
    parsed = parse_datetime(value)
    return parsed.date().isoformat() if parsed else "unknown"


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        "HH Resume Booster metrics",
        f"total_leads: {summary['total_leads']}",
        f"total_paid_intent: {summary['total_paid_intent']}",
        f"paid_intent_rate: {summary['paid_intent_rate']}%",
        f"unique_roles: {summary['unique_roles']}",
        f"unique_channels: {summary['unique_channels']}",
        f"started_at: {summary['experiment']['started_at'] or 'n/a'}",
        f"ends_at: {summary['experiment']['ends_at'] or 'n/a'}",
        f"days_complete: {str(summary['experiment']['days_complete']).lower()}",
        f"duration_days: {summary['experiment']['duration_days']}",
        f"target_min_leads_per_offer: {summary['experiment']['target_min_leads_per_offer']}",
        "",
        "daily:",
        f"active_days: {summary['daily']['active_days']}",
        f"days_available: {summary['daily']['days_available']}",
        f"average_leads_per_active_day: {summary['daily']['average_leads_per_active_day']}",
        f"average_paid_per_active_day: {summary['daily']['average_paid_per_active_day']}",
        f"required_leads_per_remaining_day: {summary['daily']['required_leads_per_remaining_day']}",
        f"required_paid_per_remaining_day: {summary['daily']['required_paid_per_remaining_day']}",
        "by_day:",
    ]
    if summary["daily"]["by_day"]:
        for item in summary["daily"]["by_day"]:
            lines.append(
                f"- {item['date']}: leads={item['leads']}, paid_intent={item['paid_intent']}, "
                f"avatar={item['avatar']}, audit={item['audit']}, response={item['response']}"
            )
    else:
        lines.append("- n/a")
    lines.extend(
        [
            "",
            "by_offer:",
        ]
    )
    for item in summary["by_offer"]:
        lines.append(
            f"- {item['label']}: leads={item['leads']}, "
            f"paid_intent={item['paid_intent']}, rate={item['paid_intent_rate']}%"
        )
    lines.extend(
        [
            "",
            "offer_coverage:",
        ]
    )
    for item in summary["offer_coverage"]:
        status = "ok" if item["ready"] else "wait"
        lines.append(f"- {item['label']}: leads={item['leads']}/{item['target']}, status={status}")
    lines.extend(
        [
            "",
            f"winner: {summary['winner']['label']}",
            f"decision_ready: {str(summary['decision_ready']).lower()}",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize HH Resume Booster validation leads.")
    parser.add_argument("input", type=Path, help="Exported JSON or CSV with leads.")
    parser.add_argument(
        "--experiment-state",
        type=Path,
        help="Optional experiment state JSON. JSONL automatically tries hh-booster-experiment.json next to the data file.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    leads, experiment = load_payload(args.input, args.experiment_state)
    summary = summarize(leads, experiment)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(render_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
