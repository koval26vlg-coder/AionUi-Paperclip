# Codex trading_mvp goal-status approval contract

Date: 2026-06-30 14:25 Europe/Volgograd
Agent: Codex

## Context
Active gate is `READY_FOR_POSTPROCESS`, but the current WS postprocess is rejected: `replay_allowed=false`. Replay/grid remain blocked. `trading_next_goal_step.ps1` already separates safe PlanOnly preview from actual collect approval, but `trading_goal_status.ps1` showed the actual collect command without a machine-readable approval flag.

## Work completed
- Added `visible_ws_collect_requires_user_approval` and `requires_user_approval_for_actual_collect` to `tools/trading_goal_status.ps1`.
- Added a human-readable `requires approval` line near the actual visible WS collect command.
- Added regression coverage in `trading_mvp/tests/test_visible_ws_collect_wrapper.py`.

## Verification
- `python -m unittest trading_mvp.tests.test_visible_ws_collect_wrapper.VisibleWsCollectWrapperTests.test_goal_status_legacy_visible_collect_follows_active_branch` -> OK.
- `python -m unittest trading_mvp.tests.test_visible_ws_collect_wrapper trading_mvp.tests.test_active_run_gate` -> 19 OK, 1 skipped.
- `tools/trading_goal_status.ps1 -Json` -> `visible_ws_collect_requires_user_approval=true`, `requires_user_approval_for_actual_collect=true`.
- `tools/trading_next_goal_step.ps1 -Json` -> safe PlanOnly approval false, actual collect approval true.
- `tools/trading_edge_preflight.ps1 -Json` -> ok=true, fail_count=0, warn_count=0.
- `tools/check_active_run_gate.ps1 -Json` -> READY_FOR_POSTPROCESS, replay_allowed=false, actual collect approval required.

## Next
No long run started. If user confirms `START72H`, start only the guarded visible 72h dense WS collect. During RUNNING, do only status/ETA checks. After collect, run guarded postprocess; replay/grid only if `replay_allowed=true`.
