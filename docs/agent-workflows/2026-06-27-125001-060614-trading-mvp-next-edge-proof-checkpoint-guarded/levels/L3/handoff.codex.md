## Что было сделано
- Codex L3 проверил выводы Antigravity L1/L2 и не запускал collector/replay/grid/postprocess.
- Усилен `C:\Users\koval\Documents\ZolotyayLopata\tools\start_ws_collect_visible.ps1`: `-PlanOnly` больше не запускает отдельный тяжелый `trading_branch_selector.ps1`; PlanOnly/gate metadata теперь явно содержат guarded postprocess и replay-validation команды.
- В PlanOnly/gate добавлены поля `postprocess_plan_command_after_ready`, `postprocess_command_after_ready`, `replay_validation_plan_after_postprocess`, `replay_validation_after_review`.
- Replay-validation команда теперь явно связывает `-PostprocessPath` с исходным completed manifest через `-ExpectedManifestPath`.
- Усилен `C:\Users\koval\Documents\ZolotyayLopata\tools\trading_edge_preflight.ps1`: добавлен check `visible_ws_collect_postprocess_chain`.

## На чем основан вывод
- Active run gate перед работой: `READY_FOR_POSTPROCESS`; live process ids отсутствуют.
- `start_ws_collect_visible.ps1 -Hours 6 -PlanOnly` вернул `would_start=false`, `requires_confirmed_long_run=true`, decision `SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT`.
- PlanOnly output содержит postprocess command и replay-validation command с `-ExpectedManifestPath <manifest_path_from_completed_ws_collect>`.
- `trading_edge_preflight.ps1 -Json`: `READY_FOR_EDGE_PROOF_STEP`, все релевантные checks pass, включая `visible_ws_collect_postprocess_chain`.
- `trading_strategy_acceptance_gate.ps1`: `research_only_no_accepted_strategy`, live orders false.
- Unit tests: `python -m unittest discover -s trading_mvp/tests` -> 198 OK.

## Что получилось хорошо
- Рой L1/L2 подтвердил корректность перехода от заблокированной funding ветки к visible dense WS collect plan.
- Следующий long-run остается заблокирован до явного подтверждения пользователя и должен быть видимым.
- После завершения collect следующая цепочка теперь не теряется: active-run gate -> guarded WS postprocess -> replay-validation PlanOnly with ExpectedManifestPath -> explicit ConfirmedResearchRun only after review.

## Что требует доработки
- `start_ws_collect_visible.ps1 -PlanOnly` все еще занимает около 20 секунд из-за `trading_next_goal_step.ps1`; это приемлемо для guarded preview, но если UX важен, можно добавить cache/light mode отдельно.
- Текущий active-run gate metadata все еще относится к старому funding run; это не блокер, потому что funding dataset уже отвергнут guard-review, но после нового WS collect gate будет переписан WS metadata.

## Какие есть риски
- Новый 6h WS dataset может снова не пройти data-quality; тогда replay/grid нельзя запускать.
- Нельзя запускать `-ConfirmedLongRun` без явного пользовательского подтверждения и видимого терминала.
- Нельзя интерпретировать любые результаты как инвестсовет или live-ready стратегию.

## Что нельзя потерять/исказить дальше
- Перед каждым шагом обязательно `tools\check_active_run_gate.ps1`.
- Если gate `RUNNING`, только status/ETA.
- Если WS collect завершится, сначала guarded `run_ws_postprocess_visible.ps1` на exact manifest, затем `run_ws_replay_validation_visible.ps1 -PlanOnly -ExpectedManifestPath <same manifest>`.
- Actual replay/grid только после `replay_allowed=true` и отдельного подтверждения `-ConfirmedResearchRun`.

## Решение
approve
