# Agent Limits Monitor

Checked at: `2026-06-27T06:55:32.755770+00:00`
Window: `7` days

| Agent | Status | Observed tokens | Cost | Limit | Remaining | Reset |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Codex | `measured_local` | 772 906 145 | n/a | n/a | n/a | n/a |
| Claude Code | `measured_local` | 101 341 768 | n/a | n/a | n/a | n/a |
| Antigravity CLI | `partial_no_usage` | n/a | n/a | n/a | n/a | n/a |

## Notes

- Codex: Codex observed_tokens is a delta against the previous latest.json snapshot.
- Codex: Local Codex thread tokens come from state_5.sqlite; account quota/remaining/reset is not exposed locally.
- Claude Code: Claude Code usage is parsed from local JSONL request usage fields and deduplicated by requestId.
- Antigravity CLI: Antigravity CLI logs quota refresh events but no numeric token usage/remaining/reset was found locally.

## Reset And Remaining

Remaining/reset values are shown only when `docs/agent-limits/limits-config.json` contains explicit limits. Provider subscription limits that are not exposed locally are marked `n/a`.
