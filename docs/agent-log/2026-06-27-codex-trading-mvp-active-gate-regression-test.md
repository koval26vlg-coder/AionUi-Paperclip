# Codex trading_mvp active gate regression test

Date: 2026-06-27
Agent: Codex
Workspace: C:\Users\koval\Documents\ZolotyayLopata

## Summary
Continued active trading_mvp goal without long runs. Added regression coverage for active-run gate funding postprocess block behavior.

## Change
Added `trading_mvp/tests/test_active_run_gate.py`. It tests `tools/check_active_run_gate.ps1` using temporary gate/manifest/funding artifacts and ensures a completed funding dataset rejected by `funding_final_review_*.json` exposes `postprocess_block` and does not return stale funding postprocess next-step text.

## Verification
- Targeted test: 2 OK.
- Full tests: 200 OK.
- Gate readback: READY_FOR_POSTPROCESS with postprocess_block.
- Next-step: SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT.
- Preflight: READY_FOR_EDGE_PROOF_STEP, failures=0, warnings=0.
- Acceptance: research_only_no_accepted_strategy.

## Handoff
Funding 7d dataset remains rejected. Do not rank/backtest/paper-forward it. Next proof movement requires explicit user confirmation for visible 6h WS collect.
