from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.antigravity_workflow_review import (
    build_prompt,
    changed_files,
    snapshot_tree,
    validate_handoff,
)


def test_validate_handoff_requires_standard_headings() -> None:
    missing = validate_handoff("## Что было сделано\n")

    assert "## Решение" in missing
    assert "## Какие есть риски" in missing


def test_snapshot_tree_detects_workflow_mutation(tmp_path: Path) -> None:
    root = tmp_path / "workflow"
    root.mkdir()
    target = root / "contract.json"
    target.write_text("before", encoding="utf-8")
    before = snapshot_tree(root)

    target.write_text("after", encoding="utf-8")
    after = snapshot_tree(root)

    assert changed_files(before, after) == ["contract.json"]


def test_build_prompt_does_not_expose_workspace_absolute_path(tmp_path: Path) -> None:
    wf_dir = tmp_path / "wf"
    wf_dir.mkdir()
    (wf_dir / "brief.md").write_text("# Brief\n", encoding="utf-8")
    (wf_dir / "handoff.md").write_text("## Что было сделано\nDone\n", encoding="utf-8")
    (wf_dir / "events.jsonl").write_text('{"event":"x"}\n', encoding="utf-8")
    contract = {
        "workflow_id": "wf",
        "title": "Demo",
        "state": "planned",
        "current_level": "L2",
        "allowed_next_agents": ["Antigravity CLI"],
        "last_handoff": "handoff.md",
    }
    (wf_dir / "contract.json").write_text(json.dumps(contract), encoding="utf-8")

    prompt = build_prompt(wf_dir, contract, "review")

    assert str(ROOT) not in prompt
    assert "не пиши файлы" in prompt
    assert "не используй веб-поиск" in prompt
    assert "## Решение" in prompt
