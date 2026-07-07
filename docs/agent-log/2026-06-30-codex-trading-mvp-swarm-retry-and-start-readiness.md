# Codex trading_mvp swarm retry and visible 72h start readiness

Date: 2026-06-30 14:10 Europe/Volgograd
Agent: Codex

## Request
Continue the active `trading_mvp` goal, use `Рой` for significant checkpoints, and do not start long runs without explicit approval.

## Current gate
`active-run-gate.json` is `READY_FOR_POSTPROCESS`, but current WS postprocess has `replay_allowed=false`; replay/grid on this artifact remain blocked. Next proof step is a new visible 72h dense WS collect after explicit `START72H`.

## Swarm status
Workflow: `2026-06-30-121440-146385-trading-mvp-ws-postprocess-duration-ratio-rejection`.
One retry via `antigravity_workflow_review.py` with timeout 90 seconds failed: `agy --print returned empty stdout and no DB response was recovered`. Recorded another `swarm_limited` event in workflow contract/events. Codex continues manually until swarm is available.

## Start path verification
- `TRADING_START_DENSE_WS_CONFIRMED.cmd` requires typed `START72H` and then calls guarded 72h dense command.
- `tools/start_ws_collect_visible.ps1` requires `-ConfirmedLongRun`, refuses active `RUNNING`, writes `RUNNING` gate, prints monitor progress, and includes zero-line/schema/density guards.
- `tools/trading_ws_collect_readiness.ps1` remains non-starting, checks explicit approval, MEXC chunking and confirmed shortcut.

## Verification
`python -m unittest trading_mvp.tests.test_ws_collector trading_mvp.tests.test_active_run_gate trading_mvp.tests.test_visible_ws_collect_wrapper` -> 25 OK, 1 skipped.

## Next
If the user confirms `START72H`, run only the guarded visible 72h dense WS collect. During `RUNNING`, do only status/ETA checks. After collect completion, run guarded postprocess; replay/grid only if `replay_allowed=true`.
