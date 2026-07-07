## Что было сделано
Codex L4 выполнил architecture/risk gate текущего `trading_mvp` checkpoint после L1/L2/L3. Проверен контракт цели: funding dataset заблокирован, WS branch является следующим допустимым proof step, long-run запуск требует явного пользовательского подтверждения и видимого monitor/terminal.

## На чем основан вывод
- Gate output фиксирует: `READY_FOR_POSTPROCESS` только формально; `postprocess_block.ok=false`; причина `data_quality:min_min_rows_per_cycle`, `min_rows_per_cycle=9`.
- Unit suite: `205 tests OK`.
- Preflight: `ok=true`, `READY_FOR_EDGE_PROOF_STEP`, `branch_selector_funding_block_override=pass`.
- `start_ws_collect_visible.ps1` имеет hard stop: если нет `-ConfirmedLongRun` и нет `-PlanOnly`, команда падает с явной ошибкой. Это нужная защита для visible long run.
- `-PlanOnly` возвращает `would_start=false`, `requires_confirmed_long_run=true`.

## Что получилось хорошо
- Guard разделяет две ветки корректно: funding blocked; WS collect allowed only as next research data-collection step.
- Риск случайного запуска long collector снижен через явный флаг `-ConfirmedLongRun` и Active Run Gate.
- Старая funding scorecard-команда не уничтожается, а архивируется в `original_scorecard_next_action`, что сохраняет трассируемость.

## Что требует доработки
- Перед реальным 6h WS collect желательно показать пользователю точную confirmed command, чтобы подтверждение было предметным, а не абстрактным.
- Позже можно усилить funding wrappers отдельным guard: если dataset заблокирован, wrapper final-review/rank/backtest должен сам отказываться. Это отдельная защита, но не blocker для WS collect.

## Какие есть риски
- Если пользователь вручную запустит funding wrapper напрямую, минуя next-step scripts, возможен расход времени на уже заблокированную ветку. Этот риск управляем отдельной будущей hardening-задачей.
- Новый WS collect может снова дать недостаточную плотность или качество данных; это не failure стратегии, а фильтр proof pipeline.
- Нельзя переходить к paper/live только по результату collect; нужен guarded postprocess, replay validation, OOS/walk-forward/stress/economics.

## Что нельзя потерять/исказить дальше
- Текущий funding dataset не использовать для rank/backtest/paper-forward.
- Следующий основной шаг только после явного подтверждения: видимый 6h WS collect по `start_ws_collect_visible.ps1 ... -ConfirmedLongRun`.
- Research-only: no live orders, no API keys, no leverage/margin, no investment advice.

## Решение
approve
