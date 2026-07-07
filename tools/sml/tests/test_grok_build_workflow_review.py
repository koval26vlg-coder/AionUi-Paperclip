from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.grok_build_workflow_review as grok_review
from tools.grok_build_workflow_review import (
    build_prompt,
    clean_handoff_output,
    filter_success_stderr,
    grok_subprocess_env,
    resolve_grok_command,
    validate_handoff,
)


def test_validate_handoff_requires_standard_headings() -> None:
    missing = validate_handoff("## Что было сделано\n")

    assert "## Решение" in missing
    assert "## Какие есть риски" in missing


def test_build_prompt_is_review_only_and_targets_contract_l2_handoff(tmp_path: Path) -> None:
    wf_dir = tmp_path / "wf"
    wf_dir.mkdir()
    (wf_dir / "brief.md").write_text("# Brief\n", encoding="utf-8")
    (wf_dir / "handoff.md").write_text("## Что было сделано\nПока нет.\n", encoding="utf-8")
    (wf_dir / "events.jsonl").write_text('{"event":"workflow_created"}\n', encoding="utf-8")
    contract = {
        "workflow_id": "wf",
        "title": "Demo",
        "workflow_profile": "grok-antigravity",
        "state": "planned",
        "current_level": "L1",
        "allowed_next_agents": ["Grok Build"],
        "last_handoff": "handoff.md",
        "levels": {"L2": {"agent": "Antigravity CLI"}},
    }
    (wf_dir / "contract.json").write_text(json.dumps(contract), encoding="utf-8")

    prompt = build_prompt(wf_dir, contract, "review")

    assert str(ROOT) not in prompt
    assert "не меняй workflow state" in prompt
    assert "не пиши файлы" in prompt
    assert "Antigravity CLI L2" in prompt
    assert "Grok Build" in prompt
    assert "## Решение" in prompt


def test_clean_handoff_output_trims_wrapper_text() -> None:
    raw = "intro\n## Что было сделано\nDone\n\n## Решение\napprove\nextra"

    assert clean_handoff_output(raw).endswith("approve")


def test_filter_success_stderr_keeps_real_sml_errors() -> None:
    stderr = "\n".join(
        [
            '2026 ERROR unexpected content type: Some("text/plain; charset=utf-8")',
            "2026 ERROR tool_name=sml__sml.ping is invalid",
        ]
    )

    assert filter_success_stderr(stderr) == "2026 ERROR tool_name=sml__sml.ping is invalid"


def test_resolve_grok_command_uses_windows_npm_fallback(tmp_path: Path, monkeypatch) -> None:
    npm_dir = tmp_path / "AppData" / "Roaming" / "npm"
    npm_dir.mkdir(parents=True)
    fallback = npm_dir / "grok.cmd"
    fallback.write_text("@echo off\n", encoding="utf-8")

    monkeypatch.setattr(grok_review.shutil, "which", lambda _name: None)
    monkeypatch.setattr(grok_review.os, "name", "nt")
    monkeypatch.setattr(grok_review.Path, "home", staticmethod(lambda: tmp_path))

    assert resolve_grok_command() == str(fallback)


def test_grok_subprocess_env_prepends_git_on_windows(tmp_path: Path, monkeypatch) -> None:
    git_cmd = tmp_path / "Program Files" / "Git" / "cmd"
    git_cmd.mkdir(parents=True)

    monkeypatch.setenv("PATH", "C:\\Original")
    monkeypatch.setattr(grok_review.os, "name", "nt")
    original_path = grok_review.Path

    class FakePath:
        @staticmethod
        def home() -> Path:
            return tmp_path

        def __new__(cls, value: str) -> Path:
            if value == "C:/Program Files/Git/cmd":
                return git_cmd
            return original_path(value)

    monkeypatch.setattr(grok_review, "Path", FakePath)

    env = grok_subprocess_env()

    assert str(git_cmd) in env["PATH"]
    assert env["PATH"].endswith("C:\\Original")
    assert env["SML_MCP_TOOL_NAME_MODE"] == "grok-safe"
