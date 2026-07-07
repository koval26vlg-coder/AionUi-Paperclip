from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / "tools" / "agent_workflow.py"


HANDOFF = """# Handoff

## Что было сделано
Сделана работа уровня.

## На чем основан вывод
На исходном brief и событиях workflow.

## Что получилось хорошо
Контекст сохранен.

## Что требует доработки
Нет.

## Какие есть риски
Нет.

## Что нельзя потерять/исказить дальше
Исходную цель пользователя.

## Решение
approve
"""


def run_cli(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    workflows = tmp_path / "agent-workflows"
    cmd = [sys.executable, str(CLI), "--root", str(workflows), *args]
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def write_handoff(tmp_path: Path, name: str = "handoff.md") -> Path:
    path = tmp_path / name
    path.write_text(HANDOFF, encoding="utf-8")
    return path


def write_report(tmp_path: Path) -> Path:
    path = tmp_path / "final-report-source.md"
    path.write_text("# Финальный отчет\n\nЗадача прошла L1-L4.\n", encoding="utf-8")
    return path


def new_workflow(tmp_path: Path, *extra: str) -> str:
    result = run_cli(tmp_path, "new", "--title", "Demo", "--brief", "# Demo\n", *extra)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def load_contract(tmp_path: Path, workflow_id: str) -> dict:
    path = tmp_path / "agent-workflows" / workflow_id / "contract.json"
    return json.loads(path.read_text(encoding="utf-8"))


def executor_args(executor: str | None) -> list[str]:
    return ["--executor", executor] if executor else []


def submit_current_level(
    tmp_path: Path, workflow_id: str, agent: str, executor: str | None = None
) -> None:
    handoff = write_handoff(tmp_path, f"{workflow_id}-{agent}-handoff.md")
    claimed = run_cli(tmp_path, "claim", workflow_id, "--agent", agent, *executor_args(executor))
    assert claimed.returncode == 0, claimed.stderr
    submitted = run_cli(
        tmp_path,
        "submit-work",
        workflow_id,
        "--agent",
        agent,
        "--handoff-file",
        str(handoff),
        *executor_args(executor),
    )
    assert submitted.returncode == 0, submitted.stderr


def test_new_workflow_starts_with_grok_antigravity_without_mimo(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path)
    data = load_contract(tmp_path, workflow_id)

    assert data["state"] == "planned"
    assert data["workflow_profile"] == "grok-antigravity"
    assert data["current_level"] == "L1"
    assert data.get("current_subrole") is None
    assert data["allowed_next_agents"] == ["Grok Build"]
    assert data["levels"]["L1"]["agent"] == "Grok Build"
    assert not data["levels"]["L1"].get("subroles")
    assert data["levels"]["L2"]["agent"] == "Antigravity CLI"
    assert data["levels"]["L3"]["agent"] == "Codex"
    assert data["levels"]["L4"]["agent"] == "Codex"
    assert data["levels"]["L5"]["agent"] == "Claude Code"
    assert data["levels"]["L1"]["subagents"][0]["id"] == "grok-memory-bootstrapper"
    assert data["levels"]["L1"]["subagents"][-1]["id"] == "grok-handoff-editor"
    assert data["levels"]["L2"]["subagents"][0]["id"] == "antigravity-engineering-reviewer"
    assert data["levels"]["L5"]["subagents"][-1]["id"] == "claude-final-decision-writer"
    assert data["levels"]["L1"]["subagents"][0]["model"] == {
        "provider": "xAI Grok Build",
        "name": "Grok Build 0.2.87",
        "effort": "High",
    }
    assert "MiMo" not in json.dumps(data["levels"], ensure_ascii=False)
    assert data["levels"]["L3"]["subagents"][0]["model"]["name"] == "codex-5.3"
    assert data["levels"]["L3"]["subagents"][2]["model"]["name"] == "gpt-5.4 mini"
    assert data["levels"]["L5"]["subagents"][-1]["model"]["name"] == "Claude Opus 4.8 alias"


def test_new_workflow_can_select_antigravity_profile(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path, "--profile", "antigravity")
    data = load_contract(tmp_path, workflow_id)

    assert data["workflow_profile"] == "antigravity"
    assert data["allowed_next_agents"] == ["Antigravity CLI"]
    assert data["levels"]["L1"]["agent"] == "Antigravity CLI"
    assert data["levels"]["L2"]["agent"] == "Antigravity CLI"
    assert data["levels"]["L1"]["subagents"][0]["id"] == "antigravity-source-verifier"
    assert data["levels"]["L2"]["subagents"][0]["id"] == "antigravity-engineering-reviewer"


def test_new_workflow_can_select_gemini_vertex_fallback_profile(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path, "--profile", "gemini-vertex")
    data = load_contract(tmp_path, workflow_id)

    assert data["workflow_profile"] == "gemini-vertex"
    assert data["allowed_next_agents"] == ["Gemini Vertex"]
    assert data["levels"]["L1"]["agent"] == "Gemini Vertex"
    assert data["levels"]["L2"]["agent"] == "Gemini Vertex"
    assert data["levels"]["L1"]["subagents"][0]["id"] == "gemini-source-verifier"
    assert data["levels"]["L2"]["subagents"][0]["id"] == "gemini-engineering-reviewer"
    assert data["levels"]["L1"]["subagents"][0]["model"] == {
        "provider": "Google Vertex AI",
        "name": "gemini-2.5-flash via Vertex AI",
        "effort": "High",
    }


def test_new_workflow_can_select_grok_gemini_profile(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path, "--profile", "grok-gemini")
    data = load_contract(tmp_path, workflow_id)

    assert data["workflow_profile"] == "grok-gemini"
    assert data["allowed_next_agents"] == ["Grok Build"]
    assert data["levels"]["L1"]["agent"] == "Grok Build"
    assert data["levels"]["L2"]["agent"] == "Gemini Vertex"
    assert data["levels"]["L3"]["agent"] == "Codex"
    assert data["levels"]["L4"]["agent"] == "Codex"
    assert data["levels"]["L5"]["agent"] == "Claude Code"
    assert data["levels"]["L1"]["subagents"][0]["id"] == "grok-memory-bootstrapper"
    assert data["levels"]["L1"]["subagents"][-1]["id"] == "grok-handoff-editor"
    assert data["levels"]["L2"]["subagents"][0]["id"] == "gemini-engineering-reviewer"
    assert data["levels"]["L1"]["subagents"][0]["model"] == {
        "provider": "xAI Grok Build",
        "name": "Grok Build 0.2.87",
        "effort": "High",
    }


def test_unlisted_agent_cannot_claim(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path)

    result = run_cli(tmp_path, "claim", workflow_id, "--agent", "Codex")

    assert result.returncode == 2
    assert "not allowed" in result.stderr


def test_l1_cannot_escalate_directly_to_l5(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path)
    submit_current_level(tmp_path, workflow_id, "Grok Build", executor="Codex")

    result = run_cli(
        tmp_path,
        "escalate",
        workflow_id,
        "--agent",
        "Antigravity CLI",
        "--executor",
        "Codex",
        "--target-level",
        "L5",
        "--reason",
        "skip",
    )

    assert result.returncode == 2
    assert "direct jumps" in result.stderr


def test_approve_level_requires_submitted_handoff(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path)

    result = run_cli(
        tmp_path,
        "approve-level",
        workflow_id,
        "--agent",
        "Grok Build",
        "--executor",
        "Codex",
    )

    assert result.returncode == 2
    assert "handoff" in result.stderr


def test_antigravity_cli_cannot_mutate_workflow_without_trusted_executor(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path, "--profile", "antigravity")

    result = run_cli(tmp_path, "claim", workflow_id, "--agent", "Antigravity CLI")

    assert result.returncode == 2
    assert "review-only" in result.stderr


def test_gemini_vertex_cannot_mutate_workflow_without_trusted_executor(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path, "--profile", "gemini-vertex")

    result = run_cli(tmp_path, "claim", workflow_id, "--agent", "Gemini Vertex")

    assert result.returncode == 2
    assert "review-only" in result.stderr


def test_grok_build_cannot_mutate_workflow_without_trusted_executor(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path)

    result = run_cli(tmp_path, "claim", workflow_id, "--agent", "Grok Build")

    assert result.returncode == 2
    assert "review-only" in result.stderr


def test_codex_can_mutate_workflow_for_antigravity_cli(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path, "--profile", "antigravity")

    result = run_cli(
        tmp_path,
        "claim",
        workflow_id,
        "--agent",
        "Antigravity CLI",
        "--executor",
        "Codex",
    )

    assert result.returncode == 0, result.stderr
    data = load_contract(tmp_path, workflow_id)
    assert data["current_level"] == "L1"
    assert data["levels"]["L1"]["status"] == "in_progress"
    events = (
        tmp_path / "agent-workflows" / workflow_id / "events.jsonl"
    ).read_text(encoding="utf-8")
    assert '"agent": "Antigravity CLI"' in events
    assert '"executor": "Codex"' in events


def test_submit_work_accepts_assignment_handoff_target_path(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path)
    target = (
        tmp_path
        / "agent-workflows"
        / workflow_id
        / "levels"
        / "L1"
        / "handoff.md"
    )
    target.parent.mkdir(parents=True)
    target.write_text(HANDOFF, encoding="utf-8")

    claimed = run_cli(
        tmp_path,
        "claim",
        workflow_id,
        "--agent",
        "Grok Build",
        "--executor",
        "Codex",
    )
    assert claimed.returncode == 0, claimed.stderr
    submitted = run_cli(
        tmp_path,
        "submit-work",
        workflow_id,
        "--agent",
        "Grok Build",
        "--handoff-file",
        str(target),
        "--executor",
        "Codex",
    )

    assert submitted.returncode == 0, submitted.stderr
    data = load_contract(tmp_path, workflow_id)
    assert data["levels"]["L1"]["handoff"] == "levels/L1/handoff.md"
    latest = (tmp_path / "agent-workflows" / workflow_id / "handoff.md").read_text(
        encoding="utf-8"
    )
    assert latest == HANDOFF


def test_finalize_blocked_by_unresolved_revision(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path)
    submit_current_level(tmp_path, workflow_id, "Grok Build", executor="Codex")
    revised = run_cli(
        tmp_path,
        "request-revision",
        workflow_id,
        "--agent",
        "Antigravity CLI",
        "--executor",
        "Codex",
        "--reason",
        "needs more evidence",
    )
    assert revised.returncode == 0, revised.stderr

    result = run_cli(
        tmp_path,
        "finalize",
        workflow_id,
        "--agent",
        "Grok Build",
        "--executor",
        "Codex",
        "--report-file",
        str(write_report(tmp_path)),
    )

    assert result.returncode == 2
    assert "unresolved revision" in result.stderr


def test_full_smoke_path_reaches_final_report(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path)

    submit_current_level(tmp_path, workflow_id, "Grok Build", executor="Codex")
    assert run_cli(
        tmp_path,
        "approve-level",
        workflow_id,
        "--agent",
        "Antigravity CLI",
        "--executor",
        "Codex",
    ).returncode == 0

    submit_current_level(tmp_path, workflow_id, "Antigravity CLI", executor="Codex")
    assert run_cli(tmp_path, "approve-level", workflow_id, "--agent", "Codex").returncode == 0

    submit_current_level(tmp_path, workflow_id, "Codex")
    assert run_cli(tmp_path, "approve-level", workflow_id, "--agent", "Codex").returncode == 0

    submit_current_level(tmp_path, workflow_id, "Codex")
    report = write_report(tmp_path)
    finalized = run_cli(
        tmp_path,
        "finalize",
        workflow_id,
        "--agent",
        "Claude Code",
        "--report-file",
        str(report),
    )

    assert finalized.returncode == 0, finalized.stderr
    data = load_contract(tmp_path, workflow_id)
    assert data["state"] == "done"
    assert data["current_level"] == "L5"
    assert data["final_report"] == "final-report.md"
    report_text = (
        tmp_path / "agent-workflows" / workflow_id / "final-report.md"
    ).read_text(encoding="utf-8")
    assert "L1 Исследовательский отдел: status=approved" in report_text
    assert "subagent grok-memory-bootstrapper" in report_text
    assert "L2 Инженерная проверка: status=approved" in report_text
    assert "subagent antigravity-engineering-reviewer" in report_text
    assert "Grok Build 0.2.87 / High" in report_text
    assert "Antigravity CLI AUTO / High" in report_text
    assert "Claude Opus 4.8 alias / xhigh" in report_text
    assert "L4 Архитектурный синтез: status=approved" in report_text
    assert "L5 Финальная инстанция для пользователя: status=approved" in report_text


def test_risk_workflow_cannot_finalize_without_risk_review(tmp_path: Path) -> None:
    workflow_id = new_workflow(tmp_path, "--risk-trading")

    submit_current_level(tmp_path, workflow_id, "Grok Build", executor="Codex")
    assert run_cli(
        tmp_path,
        "approve-level",
        workflow_id,
        "--agent",
        "Antigravity CLI",
        "--executor",
        "Codex",
    ).returncode == 0
    submit_current_level(tmp_path, workflow_id, "Antigravity CLI", executor="Codex")
    assert run_cli(tmp_path, "approve-level", workflow_id, "--agent", "Codex").returncode == 0
    submit_current_level(tmp_path, workflow_id, "Codex")
    assert run_cli(tmp_path, "approve-level", workflow_id, "--agent", "Codex").returncode == 0
    submit_current_level(tmp_path, workflow_id, "Codex")

    result = run_cli(
        tmp_path,
        "finalize",
        workflow_id,
        "--agent",
        "Claude Code",
        "--report-file",
        str(write_report(tmp_path)),
    )

    assert result.returncode == 2
    assert "risk_gate" in result.stderr

    risk = run_cli(
        tmp_path,
        "approve-risk",
        workflow_id,
        "--agent",
        "Claude Code",
        "--summary",
        "paper-only checked",
    )
    assert risk.returncode == 0, risk.stderr

    finalized = run_cli(
        tmp_path,
        "finalize",
        workflow_id,
        "--agent",
        "Claude Code",
        "--report-file",
        str(write_report(tmp_path)),
    )
    assert finalized.returncode == 0, finalized.stderr

