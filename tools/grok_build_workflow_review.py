from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW_ROOT = ROOT / "docs" / "agent-workflows"

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


def latest_handoff_path(wf_dir: Path, contract: dict[str, Any]) -> Path:
    rel = contract.get("last_handoff") or "handoff.md"
    return wf_dir / str(rel)


def compact_events(wf_dir: Path, max_chars: int = 12000) -> str:
    events = read_text(wf_dir / "events.jsonl")
    if len(events) <= max_chars:
        return events
    return events[-max_chars:]


def l2_agent_label(contract: dict[str, Any]) -> str:
    levels = contract.get("levels") or {}
    l2 = levels.get("L2") or {}
    agent = l2.get("agent")
    return f"{agent} L2" if agent else "L2"


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
    next_review_agent = l2_agent_label(contract)
    return f"""Ты Grok Build в изолированном review-only режиме L1.

Критическое правило: не запускай команды, не меняй workflow state и не пиши файлы. У тебя уже есть весь нужный пакет ниже. Верни только markdown handoff на русском языке.

Твоя роль L1:
- подтянуть смысл SML-памяти из переданного пакета;
- сформулировать задачу и ограничения;
- найти непроверенные предположения;
- подготовить аккуратный handoff для {next_review_agent}.

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


def filter_success_stderr(stderr: str) -> str:
    noisy_fragments = [
        "unexpected content type: Some(\"text/plain; charset=utf-8\")",
        "UnexpectedContentType(Some(\"text/plain; charset=utf-8\"))",
        "Auth(AuthorizationRequired)",
    ]
    kept: list[str] = []
    for line in stderr.splitlines():
        if any(fragment in line for fragment in noisy_fragments):
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def isolated_cwd() -> Path:
    base = Path.home() / ".grok" / "scratch" / "aion-grok-review"
    base.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix="run-", dir=base))
    (path / "AGENTS.md").write_text(
        "# Isolated Grok Build Review\n\n"
        "This directory is a read-only review packet. Do not inspect or mutate "
        "any external workspace. Return the requested markdown answer only.\n",
        encoding="utf-8",
    )
    return path


def resolve_grok_command() -> str:
    grok = shutil.which("grok")
    if grok:
        return grok
    if os.name == "nt":
        npm_global = Path.home() / "AppData" / "Roaming" / "npm" / "grok.cmd"
        if npm_global.exists():
            return str(npm_global)
    raise RuntimeError("grok command not found in PATH")


def grok_subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    if os.name == "nt":
        candidates = [
            Path.home() / "AppData" / "Roaming" / "npm",
            Path("C:/Program Files/nodejs"),
            Path("C:/Program Files/Git/cmd"),
            Path("C:/Program Files/Git/bin"),
            Path("C:/Windows/System32"),
            Path("C:/Windows"),
        ]
        existing = [str(path) for path in candidates if path.exists()]
        current_path = env.get("PATH") or env.get("Path") or ""
        env["PATH"] = ";".join(existing + ([current_path] if current_path else []))
    env["SML_MCP_TOOL_NAME_MODE"] = "grok-safe"
    return env


def run_grok(prompt: str, cwd: Path, timeout: int) -> subprocess.CompletedProcess[str]:
    grok = resolve_grok_command()
    packet = cwd / "review-packet.md"
    packet.write_text(prompt, encoding="utf-8")
    command = [
        grok,
        "--model",
        "grok-build",
        "--no-auto-update",
        "--prompt-file",
        str(packet),
        "--output-format",
        "plain",
        "--max-turns",
        "4",
        "--disable-web-search",
        "--no-subagents",
    ]
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        env=grok_subprocess_env(),
        timeout=timeout,
        check=False,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Grok Build against a workflow packet without giving it mutation access."
    )
    parser.add_argument("workflow_id")
    parser.add_argument("--root", type=Path, default=DEFAULT_WORKFLOW_ROOT)
    parser.add_argument("--task", required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--timeout", type=int, default=390)
    parser.add_argument("--no-validate", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    wf_dir = args.root / args.workflow_id
    if not wf_dir.exists():
        print(f"workflow not found: {wf_dir}", file=sys.stderr)
        return 1

    try:
        contract = json.loads(read_text(wf_dir / "contract.json"))
        prompt = build_prompt(wf_dir, contract, args.task)
        result = run_grok(prompt, isolated_cwd(), args.timeout)
        if result.returncode != 0:
            if result.stderr.strip():
                print(result.stderr.rstrip(), file=sys.stderr)
            if result.stdout.strip():
                print(result.stdout.rstrip())
            return result.returncode
        output = clean_handoff_output(result.stdout.strip())
        if not args.no_validate:
            missing = validate_handoff(output)
            if missing:
                print("Grok Build handoff missing headings: " + ", ".join(missing), file=sys.stderr)
                if output:
                    print(output)
                return 3
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output.rstrip() + "\n", encoding="utf-8")
        print(output)
        filtered_stderr = filter_success_stderr(result.stderr)
        if filtered_stderr:
            print(filtered_stderr, file=sys.stderr)
        return 0
    except subprocess.TimeoutExpired:
        print(f"Grok Build timed out after {args.timeout} seconds", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
