## Что было сделано
- Реализован guarded wrapper `C:\Users\koval\Documents\ZolotyayLopata\tools\run_ws_replay_validation_visible.ps1`.
- Wrapper требует явный `-PostprocessPath` на `ws_postprocess_*.json`, проверяет `mode=ws_postprocess_guarded`, наличие `replay_allowed`, существование `normalized_output` и active-run gate.
- При `replay_allowed=false` возвращает `reason=data_quality_rejected` и не запускает replay/grid.
- Фактические `event-quality`, `event-slice`, `event-validation`, `ws-grid-search`, optional `ws-replay` и `sweep_reversal_acceptance_gate` запускаются только с `-ConfirmedResearchRun`; без него wrapper возвращает `reason=confirmed_research_run_required`.
- Подключены preflight checks `ws_replay_validation_wrapper` и `ws_replay_validation_quality_gate`.
- `trading_next_goal_step.ps1` теперь показывает команды PlanOnly и ConfirmedResearchRun для replay validation после принятого WS postprocess.

## На чем основан вывод
- L1 Antigravity: approve на guarded WS replay/validation wrapper.
- L2 Antigravity: approve при условиях explicit `PostprocessPath`, schema validation, replay_allowed gate, detailed rejection reasons, no collector/replay/grid without confirmation.
- Active-run gate перед работой: `READY_FOR_POSTPROCESS`, live process ids отсутствуют.

## Что получилось хорошо
- Replay/grid больше не являются неявным следующим шагом после postprocess: между ними появился guard.
- Wrapper не выбирает latest artifact автоматически, что снижает риск старого/невалидного dataset.
- PlanOnly и confirm-required smoke проверены.
- Acceptance gate остается research-only: live/paper-forward заблокированы.

## Что требует доработки
- После реального видимого 6h WS collect нужно сначала запустить `run_ws_postprocess_visible.ps1`, затем `run_ws_replay_validation_visible.ps1 -PostprocessPath <artifact> -PlanOnly`.
- Фактический `-ConfirmedResearchRun` запуск replay/grid не выполнялся в этом шаге, потому что пользователь не подтверждал запуск replay/grid и текущий smoke artifact не является реальным 6h dataset.

## Какие есть риски
- Если пользователь передаст неверный, но формально валидный `ws_postprocess_*.json`, wrapper все равно опирается на его metadata; поэтому explicit path нужно сверять с нужным run label.
- Новый wrapper не делает стратегию принятой, он только защищает replay/validation stage.

## Что нельзя потерять/исказить дальше
- Не запускать новый 6h WS collect без явного подтверждения пользователя.
- Не запускать replay/grid на artifact с `replay_allowed=false`.
- Не выдавать winrate/PnL/ROI claims без OOS/walk-forward/stress/economics/sample-size gates.
- No live orders, no API keys, no leverage/margin.

## Решение
approve
