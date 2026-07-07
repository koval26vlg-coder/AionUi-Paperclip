# Codex trading_mvp data sufficiency planner

Дата: 2026-06-28 16:33 +03:00
Агент: Codex

## Контекст
Продолжена цель trading_mvp после завершенного visible 6h WS confirmed research run. Active gate был `READY_FOR_POSTPROCESS`, preflight `READY_FOR_EDGE_PROOF_STEP`, активного RUNNING процесса не было.

## Сделано
- Добавлен `C:\Users\koval\Documents\ZolotyayLopata\tools\trading_data_sufficiency_plan.ps1`.
- Добавлен preflight check `data_sufficiency_planner`.
- Добавлен unit/regression test в `trading_mvp/tests/test_visible_ws_collect_wrapper.py`.
- Сохранен artifact `exports/trading-mvp/analysis/trading_data_sufficiency_plan_ws_confirmed_research_6h_20260628.json`.

## Результат
Текущий 6h dataset дал 43 sweep-события на 16 рынках. Acceptance gate требует 1000 событий. При наблюдаемой плотности нужно около 139.5 часов на тех же 16 рынках, около 69.8 часов на 32 рынках или около 46.5 часов на 48 рынках, если плотность на дополнительных рынках сохранится.

## Проверки
- `C:\Program Files\Python313\python.exe -m unittest trading_mvp.tests.test_visible_ws_collect_wrapper trading_mvp.tests.test_active_run_gate`: 15 OK, 1 skipped.
- `C:\Program Files\Python313\python.exe -m unittest discover -s trading_mvp\tests`: 213 OK, 1 skipped.
- `tools/trading_edge_preflight.ps1 -Json`: READY_FOR_EDGE_PROOF_STEP, fail=0, warn=0.
- `tools/check_active_run_gate.ps1 -Json`: READY_FOR_POSTPROCESS.

## Следующий шаг
Не запускать еще один слепой 6h collect. Планировать следующий visible dense collect по market-hours и выбирать более плотные markets. Actual long run только в видимом терминале и только после явного подтверждения пользователя.
