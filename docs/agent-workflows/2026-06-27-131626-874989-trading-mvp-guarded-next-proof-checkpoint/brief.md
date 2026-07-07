Задача: независимый guarded checkpoint по цели trading_mvp.

Контекст:
- Проект: C:\Users\koval\Documents\ZolotyayLopata.
- Активная цель: доказать или честно отбросить high-winrate trading edge для non-Binance markets через данные, replay/backtest, OOS/walk-forward, stress, economics и paper-forward gates.
- Запрещено: live orders, API keys, leverage/margin, investment advice, канал/YouTube/P2P/off-ramp/custody/legal анализ.
- Visible Run Rule: long collectors/backtests/replays/grid/paper-forward только в видимом терминале/monitor и только после явного подтверждения пользователя.
- Active Run Gate сейчас: READY_FOR_POSTPROCESS, но funding postprocess blocked by guard review.
- Gate warning: funding dataset final, but funding rank/backtest/paper-forward запрещены из-за guard-review.
- Blocking guard artifact: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\funding\funding_final_review_guard_stop_verify_20260627.json.
- Причина блока: data_quality:min_min_rows_per_cycle, min_rows_per_cycle=9.
- trading_next_goal_step decision: SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT.
- Primary safe command is plan-only: pwsh -NoProfile -ExecutionPolicy Bypass -File C:\Users\koval\Documents\ZolotyayLopata\tools\start_ws_collect_visible.ps1 -Hours 6 -PlanOnly.
- Не запускать actual long collect без явного подтверждения пользователя и -ConfirmedLongRun.

Что должен сделать Рой:
1. Проверить, корректен ли следующий proof-step: guarded visible dense WS collect/postprocess/replay-validation path вместо funding rank/backtest.
2. Проверить gate logic: не допускает ли stale next_step_after_ready запуск funding postprocess на забракованном dataset.
3. Проверить, достаточно ли текущих preflight/guard scripts для предотвращения повторного overfit/тонкой выборки.
4. Сформулировать approve/revise/block и конкретные минимальные инженерные правки, если нужны.
5. Не запускать collectors, backtests, grid-search, paper-forward или внешние записи.
6. Если предлагается collect, это только рекомендация/команда plan-only; actual long run требует отдельного подтверждения пользователя.

Ожидаемый результат:
- L1/L2/L3/L4/L5 handoff/final-report с verdict approve/revise/block.
- Конкретный next action для Codex, не нарушающий Active Run Gate и Visible Run Rule.
