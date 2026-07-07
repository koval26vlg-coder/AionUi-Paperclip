# Codex trading_mvp next-goal approval contract

Date: 2026-06-30 14:18 Europe/Volgograd
Agent: Codex

## Context
Active gate is `READY_FOR_POSTPROCESS`, but the current WS postprocess is rejected: `replay_allowed=false`. Replay/grid on this artifact remain blocked. Next proof step is a visible 72h dense WS collect only after explicit `START72H`.

## Work completed
- Added `requires_user_approval_for_actual_collect` to `tools/trading_next_goal_step.ps1`.
- For `SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT`, the new field is `true` while `requires_user_approval=false` remains only for the safe PlanOnly preview command.
- Added regression coverage in `trading_mvp/tests/test_visible_ws_collect_wrapper.py`.

## Verification
- `python -m unittest trading_mvp.tests.test_visible_ws_collect_wrapper.VisibleWsCollectWrapperTests.test_next_goal_legacy_visible_collect_follows_active_branch` -> OK.
- `python -m unittest trading_mvp.tests.test_visible_ws_collect_wrapper trading_mvp.tests.test_active_run_gate` -> 19 OK, 1 skipped.
- `tools/trading_next_goal_step.ps1 -Json` -> `requires_user_approval=false`, `requires_user_approval_for_actual_collect=true`, primary command is still PlanOnly.
- `tools/trading_edge_preflight.ps1 -Json` -> ok=true, fail_count=0, warn_count=0.
- `tools/check_active_run_gate.ps1 -Json` -> READY_FOR_POSTPROCESS, replay_allowed=false, explicit collect approval required.

## Next
No long run started. If user confirms `START72H`, start only the guarded visible 72h dense WS collect. During RUNNING, do only status/ETA checks. After collect, run guarded postprocess; replay/grid only if `replay_allowed=true`.
