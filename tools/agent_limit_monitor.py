from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "agent-limits"
DEFAULT_CONFIG = DEFAULT_OUTPUT_DIR / "limits-config.json"
DEFAULT_GEMINI_VERTEX_USAGE_LOG = DEFAULT_OUTPUT_DIR / "gemini-vertex-usage.jsonl"
GEMINI_25_FLASH_STANDARD_INPUT_PER_1M_USD = 0.30
GEMINI_25_FLASH_STANDARD_CACHED_INPUT_PER_1M_USD = 0.03
GEMINI_25_FLASH_STANDARD_OUTPUT_PER_1M_USD = 2.50


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_compact_number(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip().replace(",", "")
    if not text:
        return None
    multiplier = 1.0
    suffix = text[-1].upper()
    if suffix == "K":
        multiplier = 1_000.0
        text = text[:-1]
    elif suffix == "M":
        multiplier = 1_000_000.0
        text = text[:-1]
    elif suffix == "B":
        multiplier = 1_000_000_000.0
        text = text[:-1]
    try:
        return float(text) * multiplier
    except ValueError:
        return None


def format_int(value: int | float | None) -> str:
    if value is None:
        return "n/a"
    return f"{int(round(value)):,}".replace(",", " ")


def format_money(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"${value:.4f}"


def read_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"agents": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"agents": {}, "config_error": str(exc)}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stable_path_entries() -> list[str]:
    home = Path.home()
    system_root = Path(os.environ.get("SystemRoot") or r"C:\Windows")
    preferred = [
        system_root / "system32",
        system_root,
        home / "bat",
        Path(r"C:\Program Files\PowerShell\7"),
        Path(r"C:\Program Files\nodejs"),
        home / "AppData" / "Roaming" / "npm",
        home / "AppData" / "Local" / "agy" / "bin",
        Path(r"C:\Program Files\Git\cmd"),
        home / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "node" / "bin",
    ]
    entries: list[str] = []

    def add(raw: str | os.PathLike[str] | None) -> None:
        if raw is None:
            return
        text = os.path.expandvars(str(raw).strip())
        if not text or text == "${PATH}":
            return
        path = Path(text)
        if not path.exists():
            return
        normalized = str(path)
        if normalized.lower() not in {item.lower() for item in entries}:
            entries.append(normalized)

    for item in preferred:
        add(item)
    for key in ("Path", "PATH"):
        for item in os.environ.get(key, "").split(os.pathsep):
            add(item)
    return entries


def stable_path_value() -> str:
    return os.pathsep.join(stable_path_entries())


def find_executable(name: str, fallback: Path | None = None) -> str | None:
    found = shutil.which(name, path=stable_path_value())
    if found:
        return found
    if fallback and fallback.exists():
        return str(fallback)
    return None


def node_path_env() -> dict[str, str]:
    env = os.environ.copy()
    stable = stable_path_value()
    env["Path"] = stable
    env["PATH"] = stable
    return env


@dataclass
class AgentUsage:
    agent: str
    source: str
    status: str
    measured: dict[str, Any]
    limits: dict[str, Any]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "source": self.source,
            "status": self.status,
            "measured": self.measured,
            "limits": self.limits,
            "notes": self.notes,
        }


def limit_summary(agent: str, measured: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    agent_cfg = (config.get("agents") or {}).get(agent, {})
    token_limit = agent_cfg.get("token_limit")
    cost_limit = agent_cfg.get("cost_limit_usd")
    message_limit = agent_cfg.get("message_limit")
    reset_at = agent_cfg.get("reset_at")

    observed_tokens = measured.get("observed_tokens")
    observed_cost = measured.get("cost_usd")
    observed_messages = measured.get("messages")

    result: dict[str, Any] = {
        "token_limit": token_limit,
        "token_remaining": None,
        "cost_limit_usd": cost_limit,
        "cost_remaining_usd": None,
        "message_limit": message_limit,
        "message_remaining": None,
        "reset_at": reset_at,
        "reset_in_hours": None,
        "source": "manual_config" if agent_cfg else "not_configured",
    }
    if isinstance(token_limit, (int, float)) and isinstance(observed_tokens, (int, float)):
        result["token_remaining"] = max(0, int(token_limit - observed_tokens))
    if isinstance(cost_limit, (int, float)) and isinstance(observed_cost, (int, float)):
        result["cost_remaining_usd"] = max(0.0, float(cost_limit - observed_cost))
    if isinstance(message_limit, (int, float)) and isinstance(observed_messages, (int, float)):
        result["message_remaining"] = max(0, int(message_limit - observed_messages))
    reset_dt = parse_iso(reset_at)
    if reset_dt:
        result["reset_in_hours"] = round((reset_dt - utc_now()).total_seconds() / 3600, 2)
    return result


def previous_agent_snapshot(previous: dict[str, Any] | None, agent: str) -> dict[str, Any] | None:
    if not previous:
        return None
    for item in previous.get("agents") or []:
        if item.get("agent") == agent:
            return item
    return None


def int_field(data: dict[str, Any], key: str) -> int:
    try:
        return int(data.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def estimate_gemini_vertex_cost_usd(usage: dict[str, Any]) -> float:
    prompt_tokens = int_field(usage, "prompt_token_count")
    cached_tokens = int_field(usage, "cached_content_token_count")
    billable_input_tokens = max(0, prompt_tokens - cached_tokens)
    candidate_tokens = int_field(usage, "candidates_token_count")
    thoughts_tokens = int_field(usage, "thoughts_token_count")
    output_tokens = candidate_tokens + thoughts_tokens
    if output_tokens == 0:
        output_tokens = max(0, int_field(usage, "total_token_count") - prompt_tokens)
    return (
        (billable_input_tokens * GEMINI_25_FLASH_STANDARD_INPUT_PER_1M_USD)
        + (cached_tokens * GEMINI_25_FLASH_STANDARD_CACHED_INPUT_PER_1M_USD)
        + (output_tokens * GEMINI_25_FLASH_STANDARD_OUTPUT_PER_1M_USD)
    ) / 1_000_000


def collect_gemini_vertex(days: int, config: dict[str, Any]) -> AgentUsage:
    path = DEFAULT_GEMINI_VERTEX_USAGE_LOG
    measured: dict[str, Any] = {
        "window_days": days,
        "requests": 0,
        "observed_tokens": 0,
        "prompt_tokens": 0,
        "candidate_tokens": 0,
        "thoughts_tokens": 0,
        "cached_tokens": 0,
        "cost_usd": 0.0,
        "models": {},
        "locations": {},
        "traffic_types": {},
        "updated_after": (utc_now() - timedelta(days=days)).isoformat(),
    }
    notes: list[str] = [
        "Gemini Vertex usage is read from local workflow usage logs, not from Cloud Billing.",
        "Cost is estimated for Gemini 2.5 Flash Standard PayGo text calls: input $0.30/M, cached input $0.03/M, output/reasoning $2.50/M.",
    ]
    if not path.exists():
        return AgentUsage(
            "Gemini Vertex",
            str(path),
            "not_available",
            measured,
            limit_summary("Gemini Vertex", measured, config),
            ["Gemini Vertex usage log not found yet; run workflow L1/L2 after usage logging is enabled."],
        )

    cutoff = utc_now() - timedelta(days=days)
    model_totals: dict[str, int] = defaultdict(int)
    location_totals: dict[str, int] = defaultdict(int)
    traffic_totals: dict[str, int] = defaultdict(int)
    errors = 0
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            errors += 1
            continue
        timestamp = parse_iso(item.get("time"))
        if timestamp and timestamp < cutoff:
            continue
        usage = item.get("usage_metadata")
        if not isinstance(usage, dict):
            continue
        prompt_tokens = int_field(usage, "prompt_token_count")
        candidate_tokens = int_field(usage, "candidates_token_count")
        thoughts_tokens = int_field(usage, "thoughts_token_count")
        cached_tokens = int_field(usage, "cached_content_token_count")
        total_tokens = int_field(usage, "total_token_count")
        if total_tokens == 0:
            total_tokens = prompt_tokens + candidate_tokens + thoughts_tokens
        model = item.get("model") or "unknown"
        location = item.get("location") or "unknown"
        traffic_type = item.get("traffic_type") or usage.get("traffic_type") or "unknown"

        measured["requests"] += 1
        measured["observed_tokens"] += total_tokens
        measured["prompt_tokens"] += prompt_tokens
        measured["candidate_tokens"] += candidate_tokens
        measured["thoughts_tokens"] += thoughts_tokens
        measured["cached_tokens"] += cached_tokens
        measured["cost_usd"] += estimate_gemini_vertex_cost_usd(usage)
        model_totals[model] += total_tokens
        location_totals[location] += total_tokens
        traffic_totals[traffic_type] += total_tokens

    measured["models"] = dict(sorted(model_totals.items(), key=lambda item: item[1], reverse=True))
    measured["locations"] = dict(sorted(location_totals.items(), key=lambda item: item[1], reverse=True))
    measured["traffic_types"] = dict(sorted(traffic_totals.items(), key=lambda item: item[1], reverse=True))
    if errors:
        notes.append(f"Skipped malformed JSONL records: {errors}.")
    return AgentUsage(
        "Gemini Vertex",
        str(path),
        "measured_local",
        measured,
        limit_summary("Gemini Vertex", measured, config),
        notes,
    )


def collect_codex(days: int, config: dict[str, Any], previous: dict[str, Any] | None = None) -> AgentUsage:
    db_path = Path.home() / ".codex" / "state_5.sqlite"
    measured: dict[str, Any] = {
        "window_days": days,
        "threads": 0,
        "observed_tokens": None,
        "delta_tokens_since_previous_snapshot": None,
        "cumulative_tokens_updated_threads": 0,
        "thread_token_snapshot": {},
        "models": {},
        "updated_after": (utc_now() - timedelta(days=days)).isoformat(),
    }
    notes: list[str] = []
    if not db_path.exists():
        return AgentUsage("Codex", str(db_path), "not_available", measured, limit_summary("Codex", measured, config), ["Codex state DB not found"])

    cutoff_ms = int((utc_now() - timedelta(days=days)).timestamp() * 1000)
    model_totals: dict[str, int] = defaultdict(int)
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        rows = con.execute(
            "select id, title, model, tokens_used, updated_at, updated_at_ms from threads"
        ).fetchall()
    except sqlite3.Error as exc:
        return AgentUsage("Codex", str(db_path), "error", measured, limit_summary("Codex", measured, config), [str(exc)])
    finally:
        try:
            con.close()
        except Exception:
            pass

    current_thread_tokens: dict[str, int] = {}
    for thread_id, _title, model, tokens_used, updated_at, updated_at_ms in rows:
        updated = updated_at_ms or ((updated_at or 0) * 1000)
        if updated < cutoff_ms:
            continue
        tokens = int(tokens_used or 0)
        measured["threads"] += 1
        measured["cumulative_tokens_updated_threads"] += tokens
        current_thread_tokens[thread_id] = tokens
        model_totals[model or "unknown"] += tokens
    measured["thread_token_snapshot"] = current_thread_tokens
    previous_codex = previous_agent_snapshot(previous, "Codex")
    previous_threads = ((previous_codex or {}).get("measured") or {}).get("thread_token_snapshot") or {}
    if previous_threads:
        delta = 0
        for thread_id, tokens in current_thread_tokens.items():
            before = int(previous_threads.get(thread_id) or 0)
            if tokens > before:
                delta += tokens - before
        measured["observed_tokens"] = delta
        measured["delta_tokens_since_previous_snapshot"] = delta
        notes.append("Codex observed_tokens is a delta against the previous latest.json snapshot.")
    else:
        notes.append("Codex tokens_used is cumulative per thread; run the monitor twice to get a reliable delta.")
    measured["models"] = dict(sorted(model_totals.items(), key=lambda item: item[1], reverse=True))
    notes.append("Local Codex thread tokens come from state_5.sqlite; account quota/remaining/reset is not exposed locally.")
    return AgentUsage("Codex", str(db_path), "measured_local", measured, limit_summary("Codex", measured, config), notes)


def collect_claude(days: int, config: dict[str, Any]) -> AgentUsage:
    root = Path.home() / ".claude" / "projects"
    measured: dict[str, Any] = {
        "window_days": days,
        "requests": 0,
        "observed_tokens": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
        "models": {},
    }
    notes: list[str] = []
    if not root.exists():
        return AgentUsage("Claude Code", str(root), "not_available", measured, limit_summary("Claude Code", measured, config), ["Claude projects directory not found"])

    cutoff = utc_now() - timedelta(days=days)
    seen: set[str] = set()
    model_totals: dict[str, int] = defaultdict(int)
    for path in root.glob("**/*.jsonl"):
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = item.get("message") or {}
            usage = message.get("usage")
            if not usage:
                continue
            timestamp = parse_iso(item.get("timestamp"))
            if timestamp and timestamp < cutoff:
                continue
            request_key = item.get("requestId") or item.get("uuid")
            if request_key and request_key in seen:
                continue
            if request_key:
                seen.add(request_key)
            model = message.get("model") or "unknown"
            input_tokens = int(usage.get("input_tokens") or 0)
            output_tokens = int(usage.get("output_tokens") or 0)
            cache_create = int(usage.get("cache_creation_input_tokens") or 0)
            cache_read = int(usage.get("cache_read_input_tokens") or 0)
            total = input_tokens + output_tokens + cache_create + cache_read
            measured["requests"] += 1
            measured["input_tokens"] += input_tokens
            measured["output_tokens"] += output_tokens
            measured["cache_creation_input_tokens"] += cache_create
            measured["cache_read_input_tokens"] += cache_read
            measured["observed_tokens"] += total
            model_totals[model] += total
    measured["models"] = dict(sorted(model_totals.items(), key=lambda item: item[1], reverse=True))
    notes.append("Claude Code usage is parsed from local JSONL request usage fields and deduplicated by requestId.")
    return AgentUsage("Claude Code", str(root), "measured_local", measured, limit_summary("Claude Code", measured, config), notes)


def collect_antigravity(days: int, config: dict[str, Any]) -> AgentUsage:
    root = Path.home() / ".gemini" / "antigravity-cli"
    cutoff = utc_now() - timedelta(days=days)
    measured: dict[str, Any] = {
        "window_days": days,
        "conversation_dbs": 0,
        "latest_quota_event": None,
        "observed_tokens": None,
    }
    notes = ["Antigravity CLI logs quota refresh events but no numeric token usage/remaining/reset was found locally."]
    if not root.exists():
        return AgentUsage("Antigravity CLI", str(root), "not_available", measured, limit_summary("Antigravity CLI", measured, config), ["Antigravity directory not found"])
    conversations = root / "conversations"
    if conversations.exists():
        measured["conversation_dbs"] = sum(
            1 for db in conversations.glob("*.db") if datetime.fromtimestamp(db.stat().st_mtime, timezone.utc) >= cutoff
        )
    quota_lines: list[str] = []
    log_files = [root / "cli.log"]
    log_dir = root / "log"
    if log_dir.exists():
        log_files.extend(log_dir.glob("*.log"))
    for log in log_files:
        try:
            text = log.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line in text.splitlines():
            if "quota_manager" in line or "applyAuthResult" in line:
                line = re.sub(r"email=[^,\s]+", "email=<redacted>", line)
                quota_lines.append(line)
    if quota_lines:
        measured["latest_quota_event"] = quota_lines[-1][-500:]
    return AgentUsage("Antigravity CLI", str(root), "partial_no_usage", measured, limit_summary("Antigravity CLI", measured, config), notes)


def build_report(usages: list[AgentUsage], snapshot: dict[str, Any]) -> str:
    lines = [
        "# Agent Limits Monitor",
        "",
        f"Checked at: `{snapshot['checked_at']}`",
        f"Window: `{snapshot['window_days']}` days",
        "",
        "| Agent | Status | Observed tokens | Cost | Limit | Remaining | Reset |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for usage in usages:
        data = usage.measured
        limits = usage.limits
        observed = data.get("observed_tokens")
        cost = data.get("cost_usd")
        limit = limits.get("token_limit") or limits.get("message_limit") or limits.get("cost_limit_usd")
        remaining = limits.get("token_remaining")
        if remaining is None:
            remaining = limits.get("message_remaining")
        if remaining is None:
            remaining = limits.get("cost_remaining_usd")
        lines.append(
            "| {agent} | `{status}` | {observed} | {cost} | {limit} | {remaining} | {reset} |".format(
                agent=usage.agent,
                status=usage.status,
                observed=format_int(observed) if observed is not None else "n/a",
                cost=format_money(cost),
                limit=str(limit) if limit is not None else "n/a",
                remaining=str(remaining) if remaining is not None else "n/a",
                reset=limits.get("reset_at") or "n/a",
            )
        )
    lines.extend(["", "## Notes", ""])
    for usage in usages:
        for note in usage.notes:
            lines.append(f"- {usage.agent}: {note}")
    lines.extend(
        [
            "",
            "## Reset And Remaining",
            "",
            "Remaining/reset values are shown only when `docs/agent-limits/limits-config.json` contains explicit limits. Provider subscription limits that are not exposed locally are marked `n/a`.",
        ]
    )
    return "\n".join(lines) + "\n"


def collect(days: int, config_path: Path, previous_path: Path | None = None) -> dict[str, Any]:
    config = read_config(config_path)
    previous = None
    if previous_path and previous_path.exists():
        try:
            previous = json.loads(previous_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = None
    usages = [
        collect_codex(days, config, previous),
        collect_gemini_vertex(days, config),
        collect_claude(days, config),
        collect_antigravity(days, config),
    ]
    snapshot = {
        "checked_at": utc_now().isoformat(),
        "window_days": days,
        "config_path": str(config_path),
        "agents": [usage.to_dict() for usage in usages],
    }
    if "config_error" in config:
        snapshot["config_error"] = config["config_error"]
    snapshot["markdown"] = build_report(usages, snapshot)
    return snapshot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect local agent token/cost usage and manual limit status.")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    previous_path = args.output_dir / "latest.json"
    snapshot = collect(args.days, args.config, previous_path)
    if not args.no_write:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_json(args.output_dir / "latest.json", {k: v for k, v in snapshot.items() if k != "markdown"})
        (args.output_dir / "latest.md").write_text(snapshot["markdown"], encoding="utf-8")

    if args.json:
        print(json.dumps({k: v for k, v in snapshot.items() if k != "markdown"}, ensure_ascii=False, indent=2))
    else:
        print(snapshot["markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
