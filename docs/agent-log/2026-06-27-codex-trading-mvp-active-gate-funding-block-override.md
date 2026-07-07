# Codex trading_mvp active gate funding block override

Date: 2026-06-27
Agent: Codex
Workspace: C:\Users\koval\Documents\ZolotyayLopata

## Summary
Continued active trading_mvp goal without starting long runs. Fixed stale active-run gate readback for completed funding run that had already been blocked by funding final-review guard.

## Change
`tools/check_active_run_gate.ps1` now detects matching `funding_final_review_*.json` guard artifacts for completed funding runs. If guard review blocks postprocess, the checker returns `postprocess_block`, keeps the raw gate next-step, and overrides `next_step_after_ready` toward `tools/trading_next_goal_step.ps1` and guarded WS collect/postprocess/replay-validation path.

## Verification
- Active gate: READY_FOR_POSTPROCESS with postprocess_block path and warning.
- Next goal step: SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT.
- Preflight: READY_FOR_EDGE_PROOF_STEP, failures=0, warnings=0.
- Tests: 198 OK.

## Handoff
Funding 7d dataset remains rejected. No rank/backtest/paper-forward on it. Next long action remains visible 6h WS collect after explicit user confirmation only.
