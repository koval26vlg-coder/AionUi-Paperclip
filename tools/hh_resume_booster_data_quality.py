from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-leads.jsonl"
DEFAULT_EXPERIMENT_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-experiment.json"
VALID_OFFERS = {"avatar", "audit", "response"}
VALID_INTENTS = {"ready", "maybe", "not_now"}
QA_MARKERS = ("qa", "test", "preflight", "smoke", "example.test", "temporary", "write-smoke")
REDACTED_CONTACTS = {"[deleted by request]", "[deleted]", "deleted"}


@dataclass(frozen=True)
class DataRow:
    row_number: int
    payload: dict[str, Any] | None
    source: str
    error: str | None = None


def load_rows(path: Path) -> list[DataRow]:
    suffix = path.suffix.lower()
    if not path.exists():
        return []
    if suffix == ".jsonl":
        return load_jsonl(path)
    if suffix == ".json":
        return load_json(path)
    if suffix == ".csv":
        return load_csv(path)
    raise ValueError(f"Unsupported input format: {path.suffix}")


def load_jsonl(path: Path) -> list[DataRow]:
    rows: list[DataRow] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not raw.strip():
            rows.append(DataRow(line_number, None, "jsonl", "empty line"))
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            rows.append(DataRow(line_number, None, "jsonl", f"invalid json: {exc}"))
            continue
        rows.append(coerce_payload(payload, line_number, "jsonl"))
    return rows


def load_json(path: Path) -> list[DataRow]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = payload.get("leads", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("JSON must be a list of leads or an object with a leads list")
    return [coerce_payload(item, index, "json") for index, item in enumerate(rows, start=1)]


def load_csv(path: Path) -> list[DataRow]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [coerce_payload(row, index, "csv") for index, row in enumerate(csv.DictReader(handle), start=1)]


def coerce_payload(payload: Any, row_number: int, source: str) -> DataRow:
    if not isinstance(payload, dict):
        return DataRow(row_number, None, source, f"expected object, got {type(payload).__name__}")
    return DataRow(row_number, payload, source)


def load_experiment(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        return {}
    return payload.get("experimentState") or payload.get("experiment") or payload


def parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def clean(value: Any) -> str:
    return str(value or "").strip()


def normalized(value: Any) -> str:
    return clean(value).casefold()


def is_redacted(payload: dict[str, Any]) -> bool:
    return bool(payload.get("deletedAt")) or normalized(payload.get("contact")) in REDACTED_CONTACTS


def mask_contact(value: Any) -> str:
    text = clean(value)
    if not text:
        return ""
    if "@" in text:
        name, domain = text.split("@", 1)
        return f"{name[:2]}***@{domain[:2]}***"
    if len(text) <= 4:
        return "***"
    return f"{text[:2]}***{text[-2:]}"


def is_qa_like(payload: dict[str, Any]) -> bool:
    haystack = " ".join(
        clean(payload.get(key))
        for key in ("id", "contact", "role", "channel", "notes", "source")
    ).casefold()
    return any(marker in haystack for marker in QA_MARKERS)


def issue(severity: str, code: str, row: DataRow, detail: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or row.payload or {}
    return {
        "severity": severity,
        "code": code,
        "row": row.row_number,
        "id": payload.get("id"),
        "offer": payload.get("offer"),
        "intent": payload.get("intent"),
        "channel": payload.get("channel"),
        "contact_masked": mask_contact(payload.get("contact")),
        "detail": detail,
    }


def build_audit(rows: list[DataRow], experiment: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    valid_payloads: list[tuple[DataRow, dict[str, Any]]] = []
    started_at = parse_datetime(experiment.get("startedAt"))
    duration_days = experiment.get("durationDays") if isinstance(experiment.get("durationDays"), int) else 14
    ends_at = None
    if started_at:
        from datetime import timedelta

        ends_at = started_at + timedelta(days=duration_days)

    for row in rows:
        if row.error:
            issues.append(issue("error", "invalid_row", row, row.error))
            continue
        if row.payload is None:
            issues.append(issue("error", "missing_payload", row, "row did not contain an object"))
            continue
        payload = row.payload
        redacted = is_redacted(payload)
        if redacted:
            issues.append(issue("info", "redacted_row", row, "row was redacted by privacy request", payload))

        required = ["id", "createdAt", "offer", "intent", "role", "channel"]
        if not redacted:
            required.append("contact")
        for key in required:
            if not clean(payload.get(key)):
                issues.append(issue("error", f"missing_{key}", row, f"missing required field `{key}`", payload))

        offer = clean(payload.get("offer"))
        intent = clean(payload.get("intent"))
        if offer and offer not in VALID_OFFERS:
            issues.append(issue("error", "invalid_offer", row, f"unknown offer `{offer}`", payload))
        if intent and intent not in VALID_INTENTS:
            issues.append(issue("error", "invalid_intent", row, f"unknown intent `{intent}`", payload))

        created_at = parse_datetime(payload.get("createdAt"))
        if not created_at:
            issues.append(issue("error", "invalid_createdAt", row, "createdAt is missing or not ISO datetime", payload))
        elif started_at and created_at < started_at:
            issues.append(issue("warn", "before_experiment_start", row, "lead createdAt is before experiment startedAt", payload))
        elif ends_at and created_at > ends_at:
            issues.append(issue("warn", "after_experiment_end", row, "lead createdAt is after experiment window", payload))

        consent = payload.get("consentAccepted")
        if redacted:
            pass
        elif consent is False:
            issues.append(issue("error", "consent_false", row, "consentAccepted is false", payload))
        elif consent is not True:
            issues.append(issue("warn", "consent_missing", row, "consentAccepted is not true; acceptable only for local/browser exports", payload))

        if is_qa_like(payload):
            issues.append(issue("warn", "qa_or_smoke_like", row, "row looks like QA/preflight/test data", payload))

        valid_payloads.append((row, payload))

    add_duplicate_issues(valid_payloads, issues, "id", "duplicate_id", "error")
    add_duplicate_issues(valid_payloads, issues, "contact", "duplicate_contact", "warn", skip_redacted=True)

    severity_counts = Counter(item["severity"] for item in issues)
    code_counts = Counter(item["code"] for item in issues)
    rows_with_errors = {item["row"] for item in issues if item["severity"] == "error"}
    rows_with_warnings = {item["row"] for item in issues if item["severity"] == "warn"}
    return {
        "ok": severity_counts["error"] == 0,
        "total_rows": len(rows),
        "valid_rows": len(valid_payloads),
        "error_count": severity_counts["error"],
        "warning_count": severity_counts["warn"],
        "info_count": severity_counts["info"],
        "rows_with_errors": len(rows_with_errors),
        "rows_with_warnings": len(rows_with_warnings),
        "issue_counts": dict(sorted(code_counts.items())),
        "issues": issues,
    }


def add_duplicate_issues(
    rows: list[tuple[DataRow, dict[str, Any]]],
    issues: list[dict[str, Any]],
    field: str,
    code: str,
    severity: str,
    skip_redacted: bool = False,
) -> None:
    grouped: dict[str, list[tuple[DataRow, dict[str, Any]]]] = defaultdict(list)
    for row, payload in rows:
        if skip_redacted and is_redacted(payload):
            continue
        value = normalized(payload.get(field))
        if value:
            grouped[value].append((row, payload))
    for items in grouped.values():
        if len(items) <= 1:
            continue
        line_numbers = ", ".join(str(row.row_number) for row, _ in items)
        for row, payload in items:
            issues.append(issue(severity, code, row, f"duplicate `{field}` across rows {line_numbers}", payload))


def render_text(audit: dict[str, Any]) -> str:
    lines = [
        "HH Resume Booster data quality audit",
        f"ok: {str(audit['ok']).lower()}",
        f"total_rows: {audit['total_rows']}",
        f"valid_rows: {audit['valid_rows']}",
        f"errors: {audit['error_count']}",
        f"warnings: {audit['warning_count']}",
        f"info: {audit['info_count']}",
        "",
        "issue_counts:",
    ]
    if audit["issue_counts"]:
        for code, count in audit["issue_counts"].items():
            lines.append(f"- {code}: {count}")
    else:
        lines.append("- n/a")
    lines.extend(["", "issues:"])
    if not audit["issues"]:
        lines.append("- n/a")
    for item in audit["issues"]:
        lines.append(
            f"- [{item['severity']}] row={item['row']} code={item['code']} "
            f"id={item['id'] or 'n/a'} contact={item['contact_masked'] or 'n/a'} detail={item['detail']}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only data quality audit for HH Resume Booster leads.")
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_DATA_PATH, help="Leads JSON/CSV/JSONL.")
    parser.add_argument("--experiment-state", type=Path, default=DEFAULT_EXPERIMENT_PATH, help="Experiment state JSON.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Return exit code 2 when warnings are present.")
    args = parser.parse_args()

    rows = load_rows(args.input)
    experiment = load_experiment(args.experiment_state)
    audit = build_audit(rows, experiment)
    if args.json:
        print(json.dumps(audit, ensure_ascii=False, indent=2))
    else:
        print(render_text(audit))
    if audit["error_count"] or (args.strict and audit["warning_count"]):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
