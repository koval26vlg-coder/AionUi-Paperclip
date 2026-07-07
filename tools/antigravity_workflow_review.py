from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW_ROOT = ROOT / "docs" / "agent-workflows"
ANTIGRAVITY_PRINT = ROOT / "tools" / "antigravity_print.py"
PYTHON = ROOT / ".venv-sml" / "Scripts" / "python.exe"

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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_tree(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    snapshot: dict[str, str] = {}
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        snapshot[str(item.relative_to(path))] = sha256_file(item)
    return snapshot


def changed_files(before: dict[str, str], after: dict[str, str]) -> list[str]:
    keys = set(before) | set(after)
    return sorted(key for key in keys if before.get(key) != after.get(key))


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
    return f"""Ты Antigravity CLI в изолированном review-only режиме.

Критическое правило: не запускай команды, не читай локальные файлы, не пиши файлы, не меняй workflow state, не используй веб-поиск, интернет и любые внешние инструменты. У тебя уже есть весь нужный пакет ниже — отвечай только на его основе. Верни только markdown handoff.

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


def isolated_cwd() -> Path:
    base = (
        Path.home()
        / ".gemini"
        / "antigravity-cli"
        / "scratch"
        / "aion-antigravity-review"
    )
    base.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix="run-", dir=base))
    (path / "AGENTS.md").write_text(
        "# Isolated Antigravity Review\n\n"
        "This directory is a read-only review packet. Do not inspect or mutate "
        "any external workspace. Return the requested markdown answer only.\n",
        encoding="utf-8",
    )
    return path


def run_antigravity(prompt: str, cwd: Path, timeout: int) -> subprocess.CompletedProcess[str]:
    python = PYTHON if PYTHON.exists() else Path(sys.executable)
    packet = cwd / "review-packet.md"
    packet.write_text(prompt, encoding="utf-8")
    single_line_prompt = (
        "Read the file review-packet.md in the current workspace, follow its "
        "instructions exactly, and return only the requested markdown handoff. "
        "Do not inspect or mutate any other files."
    )
    command = [
        str(python),
        str(ANTIGRAVITY_PRINT),
        "--cwd",
        str(cwd),
        "--process-timeout-seconds",
        str(timeout),
        "--review-only",
        single_line_prompt,
    ]
    return subprocess.run(command, text=True, capture_output=True, check=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Antigravity against a workflow packet without giving it workspace cwd."
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

    contract = json.loads(read_text(wf_dir / "contract.json"))
    before = snapshot_tree(wf_dir)
    cwd = isolated_cwd()
    prompt = build_prompt(wf_dir, contract, args.task)
    result = run_antigravity(prompt, cwd, args.timeout)
    after = snapshot_tree(wf_dir)
    changed = changed_files(before, after)
    if changed:
        print(
            "Antigravity review mutated workflow files; refusing result. "
            "Changed files: " + ", ".join(changed),
            file=sys.stderr,
        )
        return 4
    if result.returncode != 0:
        if result.returncode == 5:
            print(
                "Antigravity review rejected: review-only contract violated "
                "(tool/command/search execution detected).",
                file=sys.stderr,
            )
        if result.stderr.strip():
            print(result.stderr.rstrip(), file=sys.stderr)
        if result.stdout.strip():
            print(result.stdout.rstrip())
        return result.returncode
    output = clean_handoff_output(result.stdout.strip())
    if not args.no_validate:
        missing = validate_handoff(output)
        if missing:
            print("Antigravity handoff missing headings: " + ", ".join(missing), file=sys.stderr)
            if output:
                print(output)
            return 3
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output.rstrip() + "\n", encoding="utf-8")
    print(output)
    if result.stderr.strip():
        print(result.stderr.rstrip(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
