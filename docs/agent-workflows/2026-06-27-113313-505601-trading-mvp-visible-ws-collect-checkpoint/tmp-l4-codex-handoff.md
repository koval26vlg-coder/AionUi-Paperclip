## Что было сделано
- Проведен L4 архитектурный/risk-gate синтез текущего `Рой` workflow `2026-06-27-113313-505601-trading-mvp-visible-ws-collect-checkpoint`.
- Сверены L1/L2 approvals, L3 implementation handoff, active-run gate и PlanOnly output.
- Подтверждено: следующий допустимый шаг цели - не live/paper-forward и не acceptance стратегии, а только видимый 6h dense WS collect после явного подтверждения пользователя.

## На чем основан вывод
- L1 Antigravity CLI: `approve`, видимый 6h WS collect допустим при research-only ограничениях.
- L2 Antigravity CLI: `approve`, но с обязательными constraints: acceptance gates, ETA/status, корректное завершение без явного approval.
- L3 Codex: проверены gate/PlanOnly и исправлена неоднозначная reason-строка в `tools/trading_next_goal_step.ps1`.
- Свежий PlanOnly output: `would_start=false`, `requires_confirmed_long_run=true`, `next_goal_decision=SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT`.

## Что получилось хорошо
- Workflow соблюдает Trading Swarm Rule: ключевое решение прошло независимую L1/L2 проверку.
- Active Run Gate Rule не нарушен: текущий gate `READY_FOR_POSTPROCESS`, нет live PIDs.
- Visible Run Rule не нарушен: фактический long collect не запускался.
- Следующий command после approval явно включает `-ConfirmedLongRun` и quoted args.

## Что требует доработки
- До фактического запуска или сразу в wrapper нужно убедиться, что терминал/monitor показывает: elapsed, ETA, rows, per-exchange/per-symbol counts, last write age, reconnect/errors.
- После завершения collect нужен отдельный guarded postprocess, который сначала проверяет manifest/final/coverage, а не сразу делает optimistic replay.
- Acceptance для стратегии должна оставаться строгой: OOS/walk-forward/stress/net PnL after costs/sample size/fill risk, а не winrate-only.

## Какие есть риски
- Свежий 6h dataset может снова оказаться недостаточно плотным или нерепрезентативным; это должно привести к `inconclusive/rejected`, а не к подгонке параметров.
- WebSocket обрывы или VPN могут дать partial dataset; partial нельзя смешивать с final без явной маркировки.
- Формулировка `approve` в L1/L2 может быть ошибочно прочитана как `strategy approved`; это запрещено. Approved только data-collection step.

## Что нельзя потерять/исказить дальше
- Research-only режим.
- Нет API keys/live orders/leverage/margin.
- Нет скрытых фоновых долгих процессов.
- Нет нового анализа каналов/P2P/off-ramp/custody/legal.
- Если `Рой` лимиты будут недоступны на следующем checkpoint, фиксировать `swarm_limited` и продолжать Codex вручную до восстановления лимитов.

## Решение
approve
