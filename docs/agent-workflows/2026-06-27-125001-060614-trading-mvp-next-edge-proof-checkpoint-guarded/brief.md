Цель: независимый Рой-checkpoint для текущей цели trading_mvp: найти/доказать/отбросить high-winrate edge на non-Binance markets research-only.

Текущий verified context:
- Project: C:\Users\koval\Documents\ZolotyayLopata
- Active run gate must be checked before every step: tools\check_active_run_gate.ps1
- Gate currently READY_FOR_POSTPROCESS for funding_collect_7d_spotliq_visible_20260617_185732, final=true, 2016/2016 cycles, rows=50583, errors=657.
- Funding final-review already blocked current 7d dataset by data quality: guard artifact exports\trading-mvp\funding\funding_final_review_guard_stop_verify_20260627.json, ok=false, status=not_ready_for_postprocess, reason min_min_rows_per_cycle, min_rows_per_cycle=9 < threshold 20. Do not rank/backtest/paper-forward this funding dataset.
- WS replay validation wrapper exists: tools\run_ws_replay_validation_visible.ps1, requires -PostprocessPath and -ExpectedManifestPath; actual replay/grid requires -ConfirmedResearchRun.
- Current next branch from tools\trading_next_goal_step.ps1: SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT. Primary plan command only: pwsh -NoProfile -ExecutionPolicy Bypass -File tools\start_ws_collect_visible.ps1 -Hours 6 -PlanOnly.
- Previous workflow 2026-06-27-124834-918919-trading-mvp-next-edge-proof-checkpoint was created without risk flags and must not be used as decision authority.

Requested Рой task:
1. Verify whether the next engineering step is correct: visible dense 6h WS collect plan for spot maker liquidity_sweep_reversal/event-quality branch, not funding postprocess.
2. Check that the proposed visible collect plan includes a safe post-collect chain: guarded WS postprocess, then replay validation PlanOnly with -ExpectedManifestPath, then explicit human-reviewed -ConfirmedResearchRun only if data-quality gate passes.
3. Confirm no live orders, no API keys, no leverage/margin, no investment advice.
4. Produce approve/revise/block verdict and exact next action for Codex.

Risk flags: trading research and long-running collector. Collector/backtest/replay/grid/paper-forward must be visible and must not be started without explicit user confirmation. No external media/channel/P2P/off-ramp/custody/legal analysis.
