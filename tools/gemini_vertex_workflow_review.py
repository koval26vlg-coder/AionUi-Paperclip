from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW_ROOT = ROOT / "docs" / "agent-workflows"
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_LOCATION = "us-central1"
DEFAULT_USAGE_LOG = ROOT / "docs" / "agent-limits" / "gemini-vertex-usage.jsonl"

REQUIRED_HANDOFF_HEADINGS = [
    "## Что было сделано",
    "## На чем основан вывод",
    "## Что получилось хорошо",
    "## Что требует доработки",
    "## Какие есть риски",
    "## Что нельзя потерять/исказить дальше",
    "## Решение",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def get_env_or_user(name: str) -> str | None:
    value = os.environ.get(name)
    if value:
        return value
    if os.name != "nt":
        return None
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            raw, _ = winreg.QueryValueEx(key, name)
            return str(raw) if raw else None
    except FileNotFoundError:
        return None
    except OSError:
        return None


def gcloud_project() -> str | None:
    command = ["gcloud", "config", "get-value", "project"]
    try:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    value = result.stdout.strip().splitlines()[-1].strip() if result.stdout.strip() else ""
    if result.returncode == 0 and value and value != "(unset)":
        return value
    return None


def resolve_vertex_settings(project: str | None, location: str | None) -> tuple[str, str]:
    resolved_project = project or get_env_or_user("GOOGLE_CLOUD_PROJECT") or gcloud_project()
    if not resolved_project:
        raise RuntimeError(
            "GOOGLE_CLOUD_PROJECT is missing and gcloud active project is unset"
        )
    resolved_location = location or get_env_or_user("GOOGLE_CLOUD_LOCATION") or DEFAULT_LOCATION
    return resolved_project, resolved_location


def latest_handoff_path(wf_dir: Path, contract: dict[str, Any]) -> Path:
    rel = contract.get("last_handoff") or "handoff.md"
    return wf_dir / str(rel)


def compact_events(wf_dir: Path, max_chars: int = 12000) -> str:
    events = read_text(wf_dir / "events.jsonl")
    if len(events) <= max_chars:
        return events
    return events[-max_chars:]


def build_prompt(wf_dir: Path, contract: dict[str, Any], task: str) -> str:
    brief = read_text(wf_dir / "brief.md")
    handoff = read_text(latest_handoff_path(wf_dir, contract))
    contract_public = {
        "workflow_id": contract.get("workflow_id"),
        "title": contract.get("title"),
        "workflow_profile": contract.get("workflow_profile"),
        "state": contract.get("state"),
        "current_level": contract.get("current_level"),
        "current_subrole": contract.get("current_subrole"),
        "allowed_next_agents": contract.get("allowed_next_agents"),
        "last_event": contract.get("last_event"),
        "last_handoff": contract.get("last_handoff"),
        "risk_flags": contract.get("risk_flags"),
        "blockers": contract.get("blockers"),
    }
    headings = "\n".join(REQUIRED_HANDOFF_HEADINGS)
    return f"""Ты Gemini Vertex в изолированном review-only режиме.

Критическое правило: не запускай команды, не меняй workflow state и не придумывай факты. У тебя уже есть весь нужный пакет ниже. Верни только markdown handoff.

Задача уровня:
{task}

Краткий contract:
{json.dumps(contract_public, ensure_ascii=False, indent=2)}

Brief:
{brief}

Последний handoff:
{handoff}

Events JSONL:
{compact_events(wf_dir)}

Верни markdown со строго такими разделами:
{headings}

В разделе "Решение" укажи одно слово: approve / revise / escalate / block.
"""


def validate_handoff(text: str) -> list[str]:
    return [heading for heading in REQUIRED_HANDOFF_HEADINGS if heading not in text]


def clean_handoff_output(text: str) -> str:
    start = text.find("## Что было сделано")
    if start > 0:
        text = text[start:]
    decision = re.search(
        r"## Решение\s*\n\s*(approve|revise|escalate|block)\b",
        text,
        flags=re.IGNORECASE,
    )
    if decision:
        text = text[: decision.end()]
    return text.strip()


def response_usage_metadata(response: Any) -> dict[str, Any] | None:
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return None
    if hasattr(usage, "model_dump"):
        return usage.model_dump(mode="json")
    if hasattr(usage, "to_json_dict"):
        return usage.to_json_dict()
    return {"raw": str(usage)}


def append_usage_log(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def run_gemini_vertex(
    prompt: str, project: str, location: str, model: str
) -> tuple[str, dict[str, Any] | None]:
    try:
        from google import genai
        from google.genai import types
    except Exception as exc:
        raise RuntimeError(f"google-genai package unavailable: {exc}") from exc

    client = genai.Client(vertexai=True, project=project, location=location)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2),
    )
    text = (getattr(response, "text", "") or "").strip()
    if not text:
        raise RuntimeError("Gemini Vertex returned empty text")
    return text, response_usage_metadata(response)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Gemini Vertex against a workflow packet without giving it mutation access."
    )
    parser.add_argument("workflow_id")
    parser.add_argument("--root", type=Path, default=DEFAULT_WORKFLOW_ROOT)
    parser.add_argument("--task", required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--project")
    parser.add_argument("--location")
    parser.add_argument("--usage-log", type=Path, default=DEFAULT_USAGE_LOG)
    parser.add_argument("--no-usage-log", action="store_true")
    parser.add_argument("--no-validate", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    wf_dir = args.root / args.workflow_id
    if not wf_dir.exists():
        print(f"workflow not found: {wf_dir}", file=sys.stderr)
        return 1

    try:
        project, location = resolve_vertex_settings(args.project, args.location)
        contract = json.loads(read_text(wf_dir / "contract.json"))
        prompt = build_prompt(wf_dir, contract, args.task)
        raw_output, usage_metadata = run_gemini_vertex(
            prompt, project=project, location=location, model=args.model
        )
        output = clean_handoff_output(raw_output)
        if not args.no_usage_log:
            append_usage_log(
                args.usage_log,
                {
                    "time": datetime.now(timezone.utc).isoformat(),
                    "workflow_id": args.workflow_id,
                    "workflow_profile": contract.get("workflow_profile"),
                    "current_level": contract.get("current_level"),
                    "task_chars": len(args.task),
                    "prompt_chars": len(prompt),
                    "response_chars": len(raw_output),
                    "model": args.model,
                    "project": project,
                    "location": location,
                    "traffic_type": (usage_metadata or {}).get("traffic_type"),
                    "usage_metadata": usage_metadata,
                },
            )
        if not args.no_validate:
            missing = validate_handoff(output)
            if missing:
                print(
                    "Gemini Vertex handoff missing headings: " + ", ".join(missing),
                    file=sys.stderr,
                )
                if output:
                    print(output)
                return 3
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output.rstrip() + "\n", encoding="utf-8")
        print(output)
        return 0
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
