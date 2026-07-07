from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "apps" / "aion-vision" / "scripts" / "export-drift-workflow.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("export_drift_workflow", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def make_workflow(tmp_path: Path, *, state: str = "done", l5_status: str = "approved") -> Path:
    workflow = tmp_path / "wf"
    write_json(
        workflow / "contract.json",
        {
            "workflow_id": "wf",
            "title": "Drift workflow dashboard prototype",
            "state": state,
            "current_level": "L5",
            "allowed_next_agents": ["Claude Code"] if l5_status == "pending" else [],
            "last_handoff": "levels/L4/handoff.md",
            "final_report": "final-report.md",
            "levels": {
                "L1": {
                    "status": "approved",
                    "subroles": [
                        {
                            "id": "L1.0",
                            "agent": "MiMo AUTO",
                            "status": "approved",
                            "purpose": "AUTO pass",
                            "subagents": [{"id": "mimo-risk", "name": "Risk", "role": "Find risks"}],
                        },
                        {
                            "id": "L1.1",
                            "agent": "Antigravity CLI",
                            "status": "approved",
                            "purpose": "Research pass",
                            "subagents": [],
                        },
                    ],
                },
                "L2": {"agent": "Antigravity CLI", "status": "approved", "subagents": []},
                "L3": {"agent": "Codex", "status": "approved", "subagents": []},
                "L4": {"agent": "Codex", "status": "approved", "subagents": []},
                "L5": {
                    "agent": "Claude Code",
                    "status": l5_status,
                    "subagents": [{"id": "claude-summary", "name": "Summary", "role": "Write final"}],
                },
            },
            "blockers": [],
        },
    )
    (workflow / "events.jsonl").write_text(
        json.dumps({"time": "2026-06-20T10:37:32+03:00", "event": "workflow_created", "agent": "Codex"}, ensure_ascii=False)
        + "\n"
        + json.dumps({"time": "2026-06-20T18:57:25+03:00", "event": "finalized", "agent": "Claude Code"}, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    (workflow / "levels" / "L4").mkdir(parents=True)
    (workflow / "levels" / "L4" / "handoff.md").write_text("# L4\n\n## Решение\n\napprove\n", encoding="utf-8")
    (workflow / "final-report.md").write_text("# Final Report\n\n## Решение\n\napprove\n", encoding="utf-8")
    return workflow


def test_build_snapshot_reads_workflow_events_report_and_limits(tmp_path: Path) -> None:
    module = load_module()
    workflow = make_workflow(tmp_path)
    limits_config = tmp_path / "limits-config.json"
    limits_latest = tmp_path / "latest.json"
    write_json(limits_config, {"agents": {"Codex": {}, "Claude Code": {}}})
    write_json(
        limits_latest,
        {
            "agents": [
                {
                    "agent": "Codex",
                    "status": "measured_local",
                    "measured": {"observed_tokens": 40},
                    "limits": {"token_remaining": 60, "reset_at": None},
                }
            ]
        },
    )

    snapshot = module.build_snapshot(workflow, limits_config=limits_config, limits_latest=limits_latest)

    assert snapshot["state"] == "done"
    assert snapshot["currentLevel"] == "L5"
    assert snapshot["source"]["contractPath"].endswith("contract.json")
    assert snapshot["source"]["eventsPath"].endswith("events.jsonl")
    assert snapshot["source"]["finalReportPath"].endswith("final-report.md")
    assert "handoff.md прочитан напрямую" in snapshot["diagnostics"]
    assert "final-report decision: approve" in snapshot["diagnostics"]
    assert [event["event"] for event in snapshot["events"]] == ["задача создана", "final-report принят"]
    assert snapshot["limits"][0]["agent"] == "Codex"
    assert snapshot["limits"][0]["observed"] == "измерено: 40 токенов"
    assert snapshot["limits"][0]["remaining"] == "60"


def test_allowed_pending_l5_becomes_next(tmp_path: Path) -> None:
    module = load_module()
    workflow = make_workflow(tmp_path, state="ready_for_final", l5_status="pending")
    limits_config = tmp_path / "limits-config.json"
    limits_latest = tmp_path / "latest.json"
    write_json(limits_config, {"agents": {}})
    write_json(limits_latest, {"agents": []})

    snapshot = module.build_snapshot(workflow, limits_config=limits_config, limits_latest=limits_latest)
    l5 = next(agent for agent in snapshot["agents"] if agent["level"] == "L5")

    assert l5["state"] == "next"
