Ты Claude Code L5 в Aion Agent Swarm. Верни только финальное markdown-заключение для пользователя.

Workflow: 2026-06-27-134209-319447-trading-mvp-status-command-alignment-checkpoint
Задача: проверить и финально решить, корректно ли выровнен trading_mvp status/next-step command path после блокировки funding branch.

Контекст:
- Research-only. No live orders, no API keys, no leverage, no margin, no investment advice.
- Active gate: READY_FOR_POSTPROCESS only formally, but funding postprocess blocked by guard review: data_quality:min_min_rows_per_cycle; min_rows_per_cycle=9.
- Funding dataset funding_collect_7d_spotliq_visible_20260617_185732 remains rejected for rank/backtest/paper-forward.
- Current proof branch: guarded visible 6h WS collect plan. Actual long run requires explicit user approval and -ConfirmedLongRun. No collector/backtest/replay/grid was launched.

L1 Antigravity decision: approve.
- Found stale legacy visible_collect_command in tools/trading_goal_status.ps1 as real risk because it pointed to old funding collect while funding_blocked_by_swarm=true.
- Recommended redirecting legacy visible_collect to guarded WS path or marking blocked/deprecated.

L2 Antigravity decision: approve.
- Confirmed engineering risk and required tests: status output should not point legacy visible_collect to funding when funding_blocked_by_swarm=true; next_goal/preflight must remain consistent; status scripts must have no side effects.

L3 Codex implementation decision: approve.
Changed files:
- C:\Users\koval\Documents\ZolotyayLopata\tools\trading_goal_status.ps1
- C:\Users\koval\Documents\ZolotyayLopata\tools\trading_next_goal_step.ps1
- C:\Users\koval\Documents\ZolotyayLopata\trading_mvp\tests\test_visible_ws_collect_wrapper.py

Implemented:
- Added explicit funding fields: funding_visible_collect_preview_command / funding_visible_collect_command in goal_status; funding_visible_collect_preview / funding_visible_collect_after_approval in next_goal.
- Added legacy resolution markers: visible_collect_command_legacy_resolution and visible_collect_legacy_resolution.
- If funding_blocked_by_swarm=true, legacy visible_collect aliases resolve to WS collect commands, not funding collect.
- Explicit funding commands remain available only as non-primary branch fields.

Verification:
- trading_goal_status.ps1 -Json: funding_blocked_by_swarm=true; visible_collect_command_legacy_resolution=redirected_to_ws_collect_because_funding_blocked_by_swarm; visible_collect_command == visible_ws_collect_command; funding_visible_collect_command still points to start_funding_collect_visible.ps1.
- trading_next_goal_step.ps1 -Json: decision=SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT; primary_command=start_ws_collect_visible.ps1 -Hours 6 -PlanOnly; visible_collect_after_approval == visible_ws_collect_after_approval; funding_visible_collect_after_approval remains explicit funding path.
- trading_edge_preflight.ps1 -Json: READY_FOR_EDGE_PROOF_STEP, ok=true, fail_count=0, warn_count=0.
- start_ws_collect_visible.ps1 -Hours 6 -PlanOnly: would_start=false, requires_confirmed_long_run=true, zero_line/schema/early_density guards enabled.
- Full tests: 204 OK.

L4 Codex architecture/risk decision: approve.
- Change is guard/command hygiene, not a strategy proof.
- Does not relax gate, does not launch long runs, does not permit live trading.
- Remaining requirement: actual 6h WS collect only after explicit user confirmation and visible terminal/monitor.

Return markdown with sections:
## Что было сделано
## На чем основан вывод
## Что получилось хорошо
## Что требует доработки
## Какие есть риски
## Что нельзя потерять/исказить дальше
## Решение
In Решение use one word: approve / revise / escalate / block.
