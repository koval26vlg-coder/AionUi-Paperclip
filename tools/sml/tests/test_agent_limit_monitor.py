from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from agent_limit_monitor import (
    estimate_gemini_vertex_cost_usd,
    limit_summary,
    node_path_env,
    parse_compact_number,
)


def test_parse_compact_number() -> None:
    assert parse_compact_number("12") == 12
    assert parse_compact_number("1.5K") == 1500
    assert parse_compact_number("2.25M") == 2_250_000
    assert parse_compact_number("bad") is None


def test_limit_summary_uses_manual_config() -> None:
    summary = limit_summary(
        "Codex",
        {"observed_tokens": 40, "messages": 2, "cost_usd": 1.25},
        {"agents": {"Codex": {"token_limit": 100, "message_limit": 5, "cost_limit_usd": 2.0}}},
    )
    assert summary["token_remaining"] == 60
    assert summary["message_remaining"] == 3
    assert summary["cost_remaining_usd"] == 0.75


def test_node_path_env_normalizes_broken_literal_path(monkeypatch) -> None:
    monkeypatch.setenv("Path", r"C:\Program Files\PowerShell\7;${PATH}")
    env = node_path_env()

    assert "${PATH}" not in env["Path"]
    assert "${PATH}" not in env["PATH"]
    assert env["Path"] == env["PATH"]


def test_estimate_gemini_vertex_cost_counts_reasoning_as_output() -> None:
    cost = estimate_gemini_vertex_cost_usd(
        {
            "prompt_token_count": 1000,
            "candidates_token_count": 100,
            "thoughts_token_count": 300,
            "total_token_count": 1400,
        }
    )

    assert round(cost, 7) == 0.0013
