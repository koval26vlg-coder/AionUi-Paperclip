# Codex trading_mvp dense WS collect planner

Дата: 2026-06-28 16:47 +03:00
Агент: Codex

## Контекст
Продолжена цель trading_mvp после 6h WS run и data-sufficiency расчета. Active gate был READY_FOR_POSTPROCESS, preflight READY_FOR_EDGE_PROOF_STEP.

## Сделано
- Добавлен `C:\Users\koval\Documents\ZolotyayLopata\tools\trading_dense_ws_collect_plan.ps1`.
- `start_ws_collect_visible.ps1` получил `-UniversePath` и теперь в `-PlanOnly` включает `dense_collect_plan` + recommended command.
- `trading_edge_preflight.ps1` получил check `dense_ws_collect_planner`.
- Сохранены artifacts:
  - `exports/trading-mvp/analysis/trading_dense_ws_collect_plan_20260628.json`
  - `exports/trading-mvp/universe/no_binance_dense_ws_sweep_20260628.csv`
  - `exports/trading-mvp/run/ws_collect_6h_plan_preview_latest.json`

## Результат
На текущей плотности 43 sweep events за 6h/16 markets до acceptance target 1000 событий:
- 16 markets: ~139.5h
- 24 markets: ~93.0h
- 32 markets: ~69.8h, выбранный вариант rounded to 72h
- 48 markets: ~46.5h, быстрее, но выше WS load

Рекомендованный actual command только после явного подтверждения пользователя:
`pwsh -NoProfile -ExecutionPolicy Bypass -File "C:\Users\koval\Documents\ZolotyayLopata\tools\start_ws_collect_visible.ps1" -Hours 72 -MaxPairsPerExchange 16 -UniversePath "C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\universe\no_binance_dense_ws_sweep_20260628.csv" -ConfirmedLongRun`

## Рой
Создан checkpoint workflow:
`2026-06-28-164718-083294-trading-mvp-dense-ws-collect-plan-review`
state=planned, current_level=L1, allowed_next_agents=Antigravity CLI.

## Проверки
- Targeted tests: 16 OK, 1 skipped.
- Full tests: 214 OK, 1 skipped.
- Preflight: READY_FOR_EDGE_PROOF_STEP, fail=0, warn=0.
- Acceptance gate: accepted=false, live_orders=false.

## Следующий шаг
Не стартовать long collect без explicit user approval and visible terminal. Желательно дождаться/запустить L1 review Роя; если swarm limited, Codex может продолжить ручной gate, но actual run все равно только после подтверждения.
