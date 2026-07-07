from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.gemini_vertex_workflow_review import (
    append_usage_log,
    build_prompt,
    response_usage_metadata,
    validate_handoff,
)


def test_validate_handoff_requires_standard_headings() -> None:
    missing = validate_handoff("## Что было сделано\n")

    assert "## Решение" in missing
    assert "## Какие есть риски" in missing


def test_build_prompt_does_not_expose_workspace_absolute_path(tmp_path: Path) -> None:
    wf_dir = tmp_path / "wf"
    wf_dir.mkdir()
    (wf_dir / "brief.md").write_text("# Brief\n", encoding="utf-8")
    (wf_dir / "handoff.md").write_text("## Что было сделано\nDone\n", encoding="utf-8")
    (wf_dir / "events.jsonl").write_text('{"event":"x"}\n', encoding="utf-8")
    contract = {
        "workflow_id": "wf",
        "title": "Demo",
        "workflow_profile": "gemini-vertex",
        "state": "planned",
        "current_level": "L1",
        "allowed_next_agents": ["Gemini Vertex"],
        "last_handoff": "handoff.md",
    }
    (wf_dir / "contract.json").write_text(json.dumps(contract), encoding="utf-8")

    prompt = build_prompt(wf_dir, contract, "review")

    assert str(ROOT) not in prompt
    assert "не меняй workflow state" in prompt
    assert "Gemini Vertex" in prompt
    assert "## Решение" in prompt


def test_response_usage_metadata_serializes_model_dump() -> None:
    class Usage:
        def model_dump(self, mode: str) -> dict[str, object]:
            assert mode == "json"
            return {"prompt_token_count": 6, "total_token_count": 7}

    class Response:
        usage_metadata = Usage()

    assert response_usage_metadata(Response()) == {
        "prompt_token_count": 6,
        "total_token_count": 7,
    }


def test_append_usage_log_does_not_require_prompt_text(tmp_path: Path) -> None:
    usage_log = tmp_path / "usage.jsonl"
    append_usage_log(
        usage_log,
        {
            "time": "2026-07-02T00:00:00+00:00",
            "workflow_id": "wf",
            "prompt_chars": 100,
            "usage_metadata": {"total_token_count": 7},
        },
    )

    line = usage_log.read_text(encoding="utf-8").strip()
    assert '"workflow_id": "wf"' in line
    assert "prompt text" not in line
