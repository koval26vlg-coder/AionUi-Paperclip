from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-leads.jsonl"


@dataclass(frozen=True)
class JsonlRecord:
    line_number: int
    raw: str
    payload: dict[str, Any] | None
    error: str | None = None


def load_jsonl(path: Path) -> list[JsonlRecord]:
    if not path.exists():
        return []
    records: list[JsonlRecord] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not raw.strip():
            records.append(JsonlRecord(line_number=line_number, raw=raw, payload=None))
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            records.append(JsonlRecord(line_number=line_number, raw=raw, payload=None, error=str(exc)))
            continue
        records.append(
            JsonlRecord(
                line_number=line_number,
                raw=raw,
                payload=payload if isinstance(payload, dict) else None,
                error=None if isinstance(payload, dict) else f"expected object, got {type(payload).__name__}",
            )
        )
    return records


def normalized(value: Any) -> str:
    return str(value or "").strip().casefold()


def matches(payload: dict[str, Any], args: argparse.Namespace) -> bool:
    if args.id and str(payload.get("id", "")).strip() == args.id:
        return True
    contact = normalized(payload.get("contact"))
    if args.contact and contact == args.contact.strip().casefold():
        return True
    if args.contact_contains and args.contact_contains.strip().casefold() in contact:
        return True
    return False


def mask_contact(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if "@" in text:
        name, domain = text.split("@", 1)
        return f"{name[:2]}***@{domain[:2]}***"
    if len(text) <= 4:
        return "***"
    return f"{text[:2]}***{text[-2:]}"


def summarize_match(record: JsonlRecord) -> dict[str, Any]:
    payload = record.payload or {}
    return {
        "line": record.line_number,
        "id": payload.get("id"),
        "createdAt": payload.get("createdAt"),
        "offer": payload.get("offer"),
        "intent": payload.get("intent"),
        "role": payload.get("role"),
        "channel": payload.get("channel"),
        "contact_masked": mask_contact(payload.get("contact")),
    }


def redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(payload)
    redacted["contact"] = "[deleted by request]"
    redacted["notes"] = "[deleted by request]"
    redacted["consentAccepted"] = False
    redacted["deletedAt"] = datetime.now(timezone.utc).isoformat()
    return redacted


def render_records(records: list[JsonlRecord]) -> str:
    lines: list[str] = []
    for record in records:
        if record.payload is None:
            lines.append(record.raw)
        else:
            lines.append(json.dumps(record.payload, ensure_ascii=False))
    return "\n".join(lines) + ("\n" if lines else "")


def write_with_backup(path: Path, records: list[JsonlRecord], action: str) -> Path:
    backup_dir = path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = backup_dir / f"{path.stem}.{action}.{timestamp}{path.suffix}.bak"
    if path.exists():
        shutil.copy2(path, backup_path)
    else:
        backup_path.write_text("", encoding="utf-8")
    path.write_text(render_records(records), encoding="utf-8")
    return backup_path


def build_output(
    path: Path,
    action: str,
    write: bool,
    matches_found: list[JsonlRecord],
    invalid: list[JsonlRecord],
    backup_path: Path | None,
) -> dict[str, Any]:
    return {
        "path": str(path),
        "action": action,
        "mode": "write" if write else "dry_run",
        "matched_count": len(matches_found),
        "invalid_lines": [{"line": item.line_number, "error": item.error} for item in invalid],
        "backup_path": str(backup_path) if backup_path else None,
        "matches": [summarize_match(item) for item in matches_found],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="HH Resume Booster local JSONL privacy/data admin tool.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="Path to hh-booster-leads.jsonl.")
    parser.add_argument("--id", help="Match a lead by exact id.")
    parser.add_argument("--contact", help="Match a lead by exact contact, case-insensitive.")
    parser.add_argument("--contact-contains", help="Match a lead by contact substring, case-insensitive.")
    parser.add_argument(
        "--action",
        choices=("find", "delete", "redact"),
        default="find",
        help="find is read-only; delete removes rows; redact keeps aggregate row but removes contact/notes.",
    )
    parser.add_argument("--write", action="store_true", help="Actually modify the JSONL file. Default is dry-run.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    if not (args.id or args.contact or args.contact_contains):
        parser.error("one of --id, --contact, or --contact-contains is required")

    records = load_jsonl(args.data)
    invalid = [record for record in records if record.error]
    matched = [record for record in records if record.payload is not None and matches(record.payload, args)]

    backup_path: Path | None = None
    if args.write and args.action in {"delete", "redact"} and matched:
        next_records: list[JsonlRecord] = []
        for record in records:
            if record in matched:
                if args.action == "delete":
                    continue
                redacted = redact_payload(record.payload or {})
                next_records.append(
                    JsonlRecord(
                        line_number=record.line_number,
                        raw=json.dumps(redacted, ensure_ascii=False),
                        payload=redacted,
                    )
                )
            else:
                next_records.append(record)
        backup_path = write_with_backup(args.data, next_records, args.action)

    output = build_output(args.data, args.action, args.write, matched, invalid, backup_path)

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print("HH Resume Booster data admin")
        print(f"path: {output['path']}")
        print(f"action: {output['action']}")
        print(f"mode: {output['mode']}")
        print(f"matched_count: {output['matched_count']}")
        if output["backup_path"]:
            print(f"backup_path: {output['backup_path']}")
        if output["invalid_lines"]:
            print("invalid_lines:")
            for item in output["invalid_lines"]:
                print(f"- line {item['line']}: {item['error']}")
        print("matches:")
        if not output["matches"]:
            print("- n/a")
        for item in output["matches"]:
            print(
                "- "
                f"line={item['line']} id={item['id']} contact={item['contact_masked']} "
                f"offer={item['offer']} intent={item['intent']} role={item['role']} channel={item['channel']}"
            )
        if args.action in {"delete", "redact"} and not args.write:
            print("dry_run: add --write to modify the file; a backup will be created first.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
