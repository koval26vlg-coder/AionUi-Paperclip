from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
WORKFLOWS_DIR = ROOT / "docs" / "agent-workflows"
LIMITS_DIR = ROOT / "docs" / "agent-limits"
DEFAULT_LIMITS_CONFIG = LIMITS_DIR / "limits-config.json"
DEFAULT_LIMITS_SNAPSHOT = LIMITS_DIR / "latest.json"
DEFAULT_WORKFLOW_ID = "2026-06-20-103732-814300-drift-workflow-dashboard-prototype"
REFERENCE_RENDER = "/drift-arena-tuned-kei-ru.png"


PRESENTATION: dict[str, dict[str, Any]] = {
    "L1.0": {
        "id": "mimo",
        "role": "AUTO-первичный проход",
        "car": "Autozam AZ-1 / Suzuki Cappuccino tuned kei scout",
        "carCode": "kei",
        "color": "#f5f5f4",
        "accent": "#f59e0b",
        "position": {"x": 24, "y": 22, "rotate": -8},
        "subagentColors": ["#fbbf24", "#fde68a", "#fb923c"],
    },
    "L1.1": {
        "id": "antigravity-l1",
        "role": "резервная исследовательская проверка",
        "car": "Toyota AE86 Trueno",
        "carCode": "AE86",
        "color": "#1d4ed8",
        "accent": "#38bdf8",
        "position": {"x": 66, "y": 20, "rotate": 7},
        "subagentColors": ["#38bdf8", "#818cf8", "#22d3ee", "#60a5fa"],
    },
    "L2": {
        "id": "antigravity-l2",
        "role": "резервная инженерная проверка",
        "car": "Nissan 180SX Type X",
        "carCode": "180SX",
        "color": "#2563eb",
        "accent": "#60a5fa",
        "position": {"x": 73, "y": 47, "rotate": 18},
        "subagentColors": ["#60a5fa", "#93c5fd", "#38bdf8", "#818cf8"],
    },
    "L3": {
        "id": "codex-l3",
        "role": "реализация и тесты",
        "car": "Toyota Chaser JZX100",
        "carCode": "JZX100",
        "color": "#27272a",
        "accent": "#ef4444",
        "position": {"x": 50, "y": 48, "rotate": -14},
        "subagentColors": ["#ef4444", "#f97316", "#22d3ee", "#a78bfa"],
    },
    "L4": {
        "id": "codex-l4",
        "role": "архитектурный синтез",
        "car": "Nissan Silvia S15",
        "carCode": "S15",
        "color": "#7f1d1d",
        "accent": "#fb7185",
        "position": {"x": 25, "y": 78, "rotate": 4},
        "subagentColors": ["#fb7185", "#f97316", "#ef4444", "#a78bfa"],
    },
    "L5": {
        "id": "claude-l5",
        "role": "финальное техническое заключение",
        "car": "Toyota Supra A80, легенда дрифта",
        "carCode": "A80",
        "color": "#f8fafc",
        "accent": "#a855f7",
        "position": {"x": 68, "y": 78, "rotate": -5},
        "subagentColors": ["#a855f7", "#22d3ee", "#84cc16", "#f8fafc"],
    },
}


EVENT_LABELS = {
    "workflow_created": "задача создана",
    "level_claimed": "уровень взят",
    "level_submitted": "уровень сдан",
    "level_approved": "уровень принят",
    "revision_requested": "запрошена ревизия",
    "finalized": "final-report принят",
}


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def read_text(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def workflow_dir(workflow_id: str | None, explicit_dir: Path | None = None) -> Path:
    if explicit_dir is not None:
        return explicit_dir
    candidate_id = workflow_id or DEFAULT_WORKFLOW_ID
    candidate = WORKFLOWS_DIR / candidate_id
    if candidate.exists():
        return candidate

    matches = []
    for contract_path in WORKFLOWS_DIR.glob("*/contract.json"):
        contract = read_json(contract_path, {})
        title = str(contract.get("title") or "").lower()
        wid = str(contract.get("workflow_id") or contract_path.parent.name).lower()
        if "drift" in title and "prototype" in title or "drift-workflow-dashboard-prototype" in wid:
            matches.append(contract_path.parent)
    if matches:
        return max(matches, key=lambda item: item.stat().st_mtime)
    raise FileNotFoundError(f"Workflow not found: {candidate_id}")


def status_to_state(status: str | None, *, is_allowed: bool, workflow_done: bool) -> str:
    normalized = (status or "pending").lower()
    if workflow_done or normalized == "approved":
        return "done"
    if normalized in {"revision_requested", "revision"}:
        return "revision"
    if normalized == "blocked":
        return "blocked"
    if normalized in {"claimed", "in_progress", "submitted"}:
        return "active"
    if is_allowed:
        return "next"
    return "waiting"


def compact_label(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        return "агент"
    first = cleaned.split()[0].replace("AUTO-", "").replace("Gate", "gate")
    return first[:12].lower()


def build_subagents(subagents: list[dict[str, Any]], state: str, colors: list[str]) -> list[dict[str, str]]:
    result = []
    for index, subagent in enumerate(subagents):
        name = str(subagent.get("name") or subagent.get("id") or f"subagent-{index + 1}")
        result.append(
            {
                "id": str(subagent.get("id") or f"subagent-{index + 1}"),
                "label": compact_label(name),
                "role": str(subagent.get("role") or name),
                "state": state,
                "color": colors[index % len(colors)] if colors else "#ffffff",
            }
        )
    return result


def build_agent(level: str, data: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    meta = PRESENTATION[level]
    allowed_agents = set(contract.get("allowed_next_agents") or [])
    workflow_done = contract.get("state") == "done"
    is_allowed = str(data.get("agent") or "") in allowed_agents
    state = status_to_state(data.get("status"), is_allowed=is_allowed, workflow_done=workflow_done)
    role = str(data.get("purpose") or meta["role"])
    subagents = build_subagents(data.get("subagents") or [], state, meta["subagentColors"])
    return {
        "id": meta["id"],
        "level": level,
        "name": str(data.get("agent") or level),
        "role": role,
        "car": meta["car"],
        "carCode": meta["carCode"],
        "state": state,
        "color": meta["color"],
        "accent": meta["accent"],
        "position": meta["position"],
        "subagents": subagents,
    }


def iter_assignments(contract: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    levels = contract.get("levels") or {}
    result: list[tuple[str, dict[str, Any]]] = []
    l1 = levels.get("L1") or {}
    subroles = {str(item.get("id")): item for item in l1.get("subroles") or []}
    for level in ("L1.0", "L1.1"):
        if level in subroles:
            result.append((level, subroles[level]))
    for level in ("L2", "L3", "L4", "L5"):
        data = levels.get(level)
        if isinstance(data, dict):
            result.append((level, data))
    return result


def parse_events(events_path: Path) -> list[dict[str, str]]:
    events = []
    if not events_path.exists():
        return events
    for index, line in enumerate(events_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        event_name = str(item.get("event") or "event")
        decision = "pending"
        if "approved" in event_name or "submitted" in event_name or event_name in {"workflow_created", "finalized"}:
            decision = "approve"
        if "revision" in event_name or "diagnose" in event_name:
            decision = "diagnose"
        if "block" in event_name:
            decision = "blocked"
        timestamp = str(item.get("time") or "")
        time_label = timestamp[11:16] if len(timestamp) >= 16 else "--:--"
        events.append(
            {
                "id": f"event-{index:03d}",
                "time": time_label,
                "agent": str(item.get("agent") or "unknown"),
                "event": EVENT_LABELS.get(event_name, event_name.replace("_", " ")),
                "level": str(item.get("assignment") or item.get("level") or "корень"),
                "decision": decision,
            }
        )
    return events


def short_number(value: int | float | None) -> str:
    if not isinstance(value, (int, float)):
        return "n/a"
    abs_value = abs(float(value))
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(int(value))


def build_limit_item(agent: str, latest_by_agent: dict[str, Any], config: dict[str, Any]) -> dict[str, str]:
    latest = latest_by_agent.get(agent) or {}
    measured = latest.get("measured") or {}
    limits = latest.get("limits") or {}
    manual = ((config.get("agents") or {}).get(agent) or {})
    status = str(latest.get("status") or "not_available")

    observed_tokens = measured.get("observed_tokens")
    observed = "не измерено"
    if isinstance(observed_tokens, (int, float)):
        observed = f"измерено: {short_number(observed_tokens)} токенов"
    if agent == "MiMo" and measured.get("cost_usd") is not None:
        observed = f"измерено: {short_number(observed_tokens)} токенов / ${measured['cost_usd']:.2f}"
    if agent == "Antigravity CLI" and measured.get("conversation_dbs") is not None:
        observed = f"частично: {measured['conversation_dbs']} локальных диалогов"
    if status == "not_available":
        observed = "источник недоступен"

    remaining = "неизвестно"
    for key in ("token_remaining", "message_remaining", "cost_remaining_usd"):
        if limits.get(key) is not None:
            remaining = str(limits[key])
            break
    reset = str(limits.get("reset_at") or manual.get("reset_at") or "неизвестно")

    visual_status = "known" if remaining != "неизвестно" or reset != "неизвестно" else "partial"
    if status in {"not_available", "error"} and observed == "источник недоступен":
        visual_status = "unknown"
    return {
        "agent": agent,
        "observed": observed,
        "remaining": remaining,
        "reset": reset,
        "status": visual_status,
    }


def build_limits(config_path: Path, latest_path: Path) -> list[dict[str, str]]:
    config = read_json(config_path, {"agents": {}})
    latest = read_json(latest_path, {"agents": []})
    latest_by_agent = {item.get("agent"): item for item in latest.get("agents") or []}
    configured_agents = list((config.get("agents") or {}).keys())
    agents = configured_agents or ["Codex", "Claude Code", "MiMo", "Antigravity CLI"]
    return [build_limit_item(agent, latest_by_agent, config) for agent in agents]


def first_nonempty_line_after_heading(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    heading_index = next((index for index, line in enumerate(lines) if line.strip().lower() == heading.lower()), None)
    if heading_index is None:
        return None
    for line in lines[heading_index + 1 :]:
        stripped = line.strip()
        if stripped.startswith("## "):
            return None
        if stripped:
            return stripped
    return None


def resolve_relative(workflow: Path, relative: str | None) -> Path | None:
    if not relative:
        return None
    path = (workflow / relative).resolve()
    try:
        path.relative_to(workflow.resolve())
    except ValueError:
        return None
    return path


def build_diagnostics(
    contract: dict[str, Any],
    handoff_text: str,
    final_report_text: str,
    limits_config_path: Path,
    limits_latest_path: Path,
) -> list[str]:
    diagnostics = [
        "live adapter: contract.json + events.jsonl прочитаны напрямую",
        "handoff.md прочитан напрямую" if handoff_text else "handoff.md недоступен",
        "final-report.md прочитан напрямую" if final_report_text else "final-report.md недоступен",
        f"limits: {limits_config_path.name}" + (" + latest.json" if limits_latest_path.exists() else ""),
    ]
    final_decision = first_nonempty_line_after_heading(final_report_text, "## Решение")
    if final_decision:
        diagnostics.append(f"final-report decision: {final_decision}")
    unresolved = [item for item in contract.get("blockers") or [] if not item.get("resolved")]
    if unresolved:
        diagnostics.append(f"active blockers: {len(unresolved)}")
    return diagnostics


def build_snapshot(
    workflow: Path,
    *,
    limits_config: Path = DEFAULT_LIMITS_CONFIG,
    limits_latest: Path = DEFAULT_LIMITS_SNAPSHOT,
) -> dict[str, Any]:
    contract_path = workflow / "contract.json"
    events_path = workflow / "events.jsonl"
    contract = read_json(contract_path, {})
    if not contract:
        raise FileNotFoundError(f"Invalid or missing contract: {contract_path}")

    handoff_path = resolve_relative(workflow, contract.get("last_handoff"))
    final_report_path = resolve_relative(workflow, contract.get("final_report"))
    handoff_text = read_text(handoff_path)
    final_report_text = read_text(final_report_path)

    agents = [build_agent(level, data, contract) for level, data in iter_assignments(contract)]
    snapshot = {
        "workflowId": contract.get("workflow_id") or workflow.name,
        "title": contract.get("title") or "Drift workflow",
        "state": contract.get("state") or "unknown",
        "currentLevel": contract.get("current_level") or "",
        "allowedNextAgents": contract.get("allowed_next_agents") or [],
        "referenceRender": REFERENCE_RENDER,
        "diagnostics": build_diagnostics(contract, handoff_text, final_report_text, limits_config, limits_latest),
        "agents": agents,
        "events": parse_events(events_path),
        "limits": build_limits(limits_config, limits_latest),
        "source": {
            "generatedAt": datetime.now().astimezone().isoformat(),
            "workflowDir": str(workflow),
            "contractPath": str(contract_path),
            "eventsPath": str(events_path),
            "handoffPath": str(handoff_path) if handoff_path else None,
            "finalReportPath": str(final_report_path) if final_report_path else None,
            "limitsConfigPath": str(limits_config),
            "limitsLatestPath": str(limits_latest) if limits_latest.exists() else None,
        },
    }
    return snapshot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export live read-only drift workflow dashboard snapshot.")
    parser.add_argument("--workflow-id", default=DEFAULT_WORKFLOW_ID)
    parser.add_argument("--workflow-dir", type=Path)
    parser.add_argument("--limits-config", type=Path, default=DEFAULT_LIMITS_CONFIG)
    parser.add_argument("--limits-latest", type=Path, default=DEFAULT_LIMITS_SNAPSHOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    snapshot = build_snapshot(
        workflow_dir(args.workflow_id, args.workflow_dir),
        limits_config=args.limits_config,
        limits_latest=args.limits_latest,
    )
    print(json.dumps(snapshot, ensure_ascii=False, indent=2 if args.json else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
