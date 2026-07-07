## Что было сделано
- Принят L2 verdict: `approve`, но с инженерными условиями перед любым фактическим 6h WS collect.
- В `C:\Users\koval\Documents\ZolotyayLopata\tools\start_ws_collect_visible.ps1` добавлен early density guard:
  - параметры `EarlyDensityCheckAfterMinutes`, `EarlyDensityMinLinesPerMinute`, `EarlyDensityMinRawLines`, `EarlyDensityMinRawFiles`;
  - default: проверка через 60 минут, минимум 600 raw lines, минимум 10 lines/min, минимум 1 raw file;
  - при провале monitor останавливает child collector и пишет `STOPPED_INCOMPLETE` + `stop_reason=early_density_guard_failed` в active-run gate.
- В тот же wrapper добавлен raw JSONL schema probe:
  - параметры `SchemaProbeAfterMinutes`, `SchemaProbeMaxLines`;
  - default: проверка через 1 минуту, до 20 строк;
  - обязательные поля: `recv_ts`, `exchange`, `event_type`, `channel`, `symbol`, `payload`;
  - при провале monitor останавливает child collector и пишет `stop_reason=schema_probe_failed`.
- В `tools\trading_edge_preflight.ps1` добавлены проверки `visible_ws_collect_early_quality_guard` и `funding_postprocess_block_readback`.
- Добавлен regression test `trading_mvp\tests\test_visible_ws_collect_wrapper.py`.

## На чем основан вывод
- L1 Antigravity verdict: `approve`, funding postprocess заблокирован, следующий методологически верный шаг - visible dense WS collect plan.
- L2 Antigravity verdict: `approve`, но перед actual 6h collect нужны early density guard, stale next-step block readback и schema validation.
- Active gate сейчас `READY_FOR_POSTPROCESS`, но с `postprocess_block` по funding final-review guard (`min_rows_per_cycle=9`), поэтому funding rank/backtest/paper-forward запрещены.
- `tools\trading_next_goal_step.ps1 -Json` сохраняет `gate_postprocess_block` и направляет в `SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT`.

## Что получилось хорошо
- Future 6h WS collect теперь не обязан впустую ждать весь интервал, если первые 60 минут дают слишком мало raw data.
- Raw JSONL schema probe ловит поломку структуры почти сразу после появления первых строк.
- Preflight теперь защищает эти два класса ошибок и stale funding postprocess route от регресса.
- Проверки прошли: PlanOnly wrapper, preflight, next-goal readback, полный unit suite.

## Что требует доработки
- L4 должен проверить, достаточно ли выбранных default-порогов `600 raw lines / 60 min / 10 lines/min` для первого продакшн research-run, или лучше поднять порог перед фактическим запуском.
- После будущего collect нужен guarded `run_ws_postprocess_visible.ps1`, затем replay validation в `-PlanOnly` с тем же `-ExpectedManifestPath`.
- Если будущий dataset опять провалит quality gate, ветку нужно признавать неполной/нежизнеспособной на текущих источниках данных, а не ослаблять пороги молча.

## Какие есть риски
- Early density threshold может быть слишком мягким для некоторых сигналов и не гарантирует финальную пригодность dataset; он только экономит время при явной деградации.
- Stop-Process останавливает child collector принудительно при guard-fail; это ожидаемое поведение для research collect, но manifest может не появиться, поэтому gate останется `STOPPED_INCOMPLETE`.
- Реальный 6h collect остается long-running и требует видимого терминала и явного подтверждения пользователя.

## Что нельзя потерять/исказить дальше
- Не запускать funding rank/backtest/paper-forward на `funding_collect_7d_spotliq_visible_20260617_185732`.
- Не запускать actual 6h WS collect без явного подтверждения пользователя и `-ConfirmedLongRun`.
- Не запускать replay/grid без guarded WS postprocess, `replay_allowed=true`, `ExpectedManifestPath` и отдельного подтверждения research-run.
- Не обсуждать live trading/API keys/leverage/margin как следующий шаг.

## Решение
approve
