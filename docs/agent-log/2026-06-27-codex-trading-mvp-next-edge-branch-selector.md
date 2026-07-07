# 2026-06-27 - Codex - trading_mvp next edge branch selector

## Запрос

Продолжить активную цель `trading_mvp` после блокировки funding carry через `Рой` L1/L2.

## Сделано

- Проверен active-run gate проекта: `READY_FOR_POSTPROCESS`, `2016/2016`, `50583` rows, `657` errors.
- Принят L2 handoff workflow `2026-06-27-095557-165108-trading-mvp-7d-funding-checkpoint-review`.
- Workflow переведен на `L3` под `Codex`.
- Добавлен branch selector для выбора следующей research ветки.
- Добавлен visible WS collect wrapper с `-PlanOnly` и обязательным `-ConfirmedLongRun`.
- Зафиксирован следующий branch: `spot_maker_liquidity_sweep_reversal_event_quality`.

## Измененные файлы

- `C:\Users\koval\Documents\ZolotyayLopata\tools\trading_branch_selector.ps1`
- `C:\Users\koval\Documents\ZolotyayLopata\tools\start_ws_collect_visible.ps1`
- `C:\Users\koval\Documents\ZolotyayLopata\tools\trading_next_goal_step.ps1`
- `C:\Users\koval\Documents\ZolotyayLopata\tools\trading_goal_status.ps1`
- `C:\Users\koval\Documents\ZolotyayLopata\docs\plans\2026-06-27-spot-maker-sweep-reversal-proof-plan.md`
- `C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\analysis\spot_maker_sweep_reversal_next_branch_20260627.json`

## Проверки

- `trading_branch_selector.ps1 -Json`: `NEXT_BRANCH_SPOT_MAKER_LIQUIDITY_SWEEP_REVERSAL`
- `start_ws_collect_visible.ps1 -Hours 6 -PlanOnly`: `would_start=false`, requires `-ConfirmedLongRun`
- `trading_next_goal_step.ps1 -Json`: next decision points to branch selector
- `trading_edge_preflight.ps1 -Json`: `ok=true`

## Следующий агент

Не запускать долгий сбор без явного подтверждения пользователя.

Следующий инженерный шаг: определить branch-specific event-quality/OOS gates и подготовить replay/postprocess для `spot_maker_liquidity_sweep_reversal_event_quality`. После этого снова использовать `Рой` на checkpoint перед любым long visible run.

