# Codex trading_mvp branch-selector approval contract

Date: 2026-06-30 14:34 Europe/Volgograd
Agent: Codex

## Context
Active gate is `READY_FOR_POSTPROCESS`, but current WS postprocess is rejected: `replay_allowed=false`. Replay/grid remain blocked. `trading_next_goal_step.ps1` and `trading_goal_status.ps1` already expose actual collect approval flags. `trading_branch_selector.ps1` showed actual WS collect command in artifacts without an explicit machine-readable approval flag.

## Work completed
- Added `requires_user_approval_for_actual_collect` to `tools/trading_branch_selector.ps1`.
- Added `artifacts.visible_ws_collect_requires_user_approval` to the same branch selector output.
- Added regression coverage in `trading_mvp/tests/test_visible_ws_collect_wrapper.py`.

## Verification
- `python -m unittest trading_mvp.tests.test_visible_ws_collect_wrapper.VisibleWsCollectWrapperTests.test_branch_selector_blocks_stale_funding_next_action` -> OK.
- `python -m unittest trading_mvp.tests.test_visible_ws_collect_wrapper trading_mvp.tests.test_active_run_gate` -> 19 OK, 1 skipped.
- `tools/trading_branch_selector.ps1 -Json` -> immediate work approval false, actual collect approval true, artifact collect approval true.
- `tools/trading_goal_status.ps1 -Json` -> actual collect approval true.
- `tools/trading_next_goal_step.ps1 -Json` -> safe PlanOnly approval false, actual collect approval true.
- `tools/trading_edge_preflight.ps1 -Json` -> ok=true, fail_count=0, warn_count=0.
- `tools/check_active_run_gate.ps1 -Json` -> READY_FOR_POSTPROCESS, replay_allowed=false, actual collect approval required.

## Next
No long run started. If user confirms `START72H`, start only guarded visible 72h dense WS collect. During RUNNING, do status/ETA only. After collect, run guarded postprocess; replay/grid only if `replay_allowed=true`.
