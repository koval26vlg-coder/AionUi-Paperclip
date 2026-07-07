Ты Claude Code L5 в workflow Рой. Работай только по пакету ниже, без вызова инструментов и без чтения файлов.

Задача: финально проверить, не искажен ли вывод L1-L4, и дать final-report для пользователя.

Критичные правила:
- research-only; никаких live orders, API keys, leverage/margin, investment advice.
- не запускать long collector/backtest/replay/grid; только verdict.
- долгий 6h WS collect можно запускать только в видимом терминале и только после явного подтверждения пользователя.
- funding 7d dataset отвергнут data-quality guard; не предлагать rank/backtest/paper-forward по нему.
- next step должен быть только PlanOnly/explicit confirmation visible WS collect path, затем guarded WS postprocess, затем replay-validation PlanOnly with ExpectedManifestPath, затем ConfirmedResearchRun только после accepted quality and explicit review.

Верни markdown с разделами:
## Итог
## Проверка искажения
## Допустимый следующий шаг
## Блокировки
## Решение
В разделе Решение укажи одно слово: approve / revise / escalate / block.

# Brief
Цель: независимый Рой-checkpoint для текущей цели trading_mvp: найти/доказать/отбросить high-winrate edge на non-Binance markets research-only.

Текущий verified context:
- Project: C:\Users\koval\Documents\ZolotyayLopata
- Active run gate must be checked before every step: tools\check_active_run_gate.ps1
- Gate currently READY_FOR_POSTPROCESS for funding_collect_7d_spotliq_visible_20260617_185732, final=true, 2016/2016 cycles, rows=50583, errors=657.
- Funding final-review already blocked current 7d dataset by data quality: guard artifact exports\trading-mvp\funding\funding_final_review_guard_stop_verify_20260627.json, ok=false, status=not_ready_for_postprocess, reason min_min_rows_per_cycle, min_rows_per_cycle=9 < threshold 20. Do not rank/backtest/paper-forward this funding dataset.
- WS replay validation wrapper exists: tools\run_ws_replay_validation_visible.ps1, requires -PostprocessPath and -ExpectedManifestPath; actual replay/grid requires -ConfirmedResearchRun.
- Current next branch from tools\trading_next_goal_step.ps1: SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT. Primary plan command only: pwsh -NoProfile -ExecutionPolicy Bypass -File tools\start_ws_collect_visible.ps1 -Hours 6 -PlanOnly.
- Previous workflow 2026-06-27-124834-918919-trading-mvp-next-edge-proof-checkpoint was created without risk flags and must not be used as decision authority.

Requested Рой task:
1. Verify whether the next engineering step is correct: visible dense 6h WS collect plan for spot maker liquidity_sweep_reversal/event-quality branch, not funding postprocess.
2. Check that the proposed visible collect plan includes a safe post-collect chain: guarded WS postprocess, then replay validation PlanOnly with -ExpectedManifestPath, then explicit human-reviewed -ConfirmedResearchRun only if data-quality gate passes.
3. Confirm no live orders, no API keys, no leverage/margin, no investment advice.
4. Produce approve/revise/block verdict and exact next action for Codex.

Risk flags: trading research and long-running collector. Collector/backtest/replay/grid/paper-forward must be visible and must not be started without explicit user confirmation. No external media/channel/P2P/off-ramp/custody/legal analysis.


# L1 Antigravity
## Что было сделано
- Проведен независимый анализ L1-чекпоинта для текущей цели `trading_mvp` в файле [review-packet.md](file:///C:/Users/koval/.gemini/antigravity-cli/scratch/aion-antigravity-review/run-l4_0gfc9/review-packet.md).
- Изучен статус прохождения проверки качества данных (data quality gate) для фандинг-датасета `funding_collect_7d_spotliq_visible_20260617_185732` с помощью отчета [funding_final_review_guard_stop_verify_20260627.json](file:///C:/Users/koval/Documents/ZolotyayLopata/exports/trading-mvp/funding/funding_final_review_guard_stop_verify_20260627.json).
- Оценена корректность переключения на ветку `SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT` для сбора WebSocket-данных через скрипт [start_ws_collect_visible.ps1](file:///C:/Users/koval/Documents/ZolotyayLopata/tools/start_ws_collect_visible.ps1).
- Верифицирована цепочка последующих действий, включая валидацию через [run_ws_replay_validation_visible.ps1](file:///C:/Users/koval/Documents/ZolotyayLopata/tools/run_ws_replay_validation_visible.ps1) и запуск гейта [check_active_run_gate.ps1](file:///C:/Users/koval/Documents/ZolotyayLopata/tools/check_active_run_gate.ps1).
- Подтверждено соблюдение всех правил безопасности (отсутствие реальных ордеров, кредитного плеча, API-ключей и маржинальных настроек).

## На чем основан вывод
- **Блокировка предыдущего этапа**: Data-quality gate заблокировал фандинг-датасет в файле [funding_final_review_guard_stop_verify_20260627.json](file:///C:/Users/koval/Documents/ZolotyayLopata/exports/trading-mvp/funding/funding_final_review_guard_stop_verify_20260627.json) из-за `min_rows_per_cycle=9 < 20`, что делает невозможным дальнейшую постобработку или запуск бэктестов на этих данных.
- **Обоснованность альтернативного шага**: Переход на сбор WebSocket-данных высокой плотности (6 часов) является логичным и верным следующим шагом, определенным скриптом [trading_next_goal_step.ps1](file:///C:/Users/koval/Documents/ZolotyayLopata/tools/trading_next_goal_step.ps1).
- **Безопасность первого шага**: Скрипт запускается с ключом `-PlanOnly`, что исключает запись или активные операции до проверки сформированного манифеста.
- **Безопасность симуляции**: Весь планируемый пайплайн (replay validation) использует только `-ExpectedManifestPath` и требует явного флага `-ConfirmedResearchRun` после прохождения гейтов качества, исключая совершение реальных транзакций.

## Что получилось хорошо
- Автоматизированный контроль качества данных успешно предотвратил использование непригодного датасета фандинга.
- Переход на альтернативный сбор данных высокой плотности выполняется в полностью изолированном и безопасном режиме предварительного планирования (`-PlanOnly`).
- Исключены невалидные источники принятия решений (предыдущий некорректно созданный workflow без риск-флагов).

## Что требует доработки
- Codex должен строго придерживаться указанной последовательности: сначала безопасный WS-сбор, затем guarded WS postprocess, после чего запуск [run_ws_replay_validation_visible.ps1](file:///C:/Users/koval/Documents/ZolotyayLopata/tools/run_ws_replay_validation_visible.ps1) с ключом `PlanOnly` для сверки манифестов, и только при успешном прохождении проверок — запуск с флагом `-ConfirmedResearchRun`.

## Какие есть риски
- **Риск качества данных нового сбора**: 6-часовой WS-датасет также может не пройти пороги плотности. Этот риск минимизируется обязательной проверкой гейта после сбора.
- **Длительное время выполнения**: Процесс сбора данных занимает 6 часов, поэтому он должен выполняться прозрачно (visible) и логироваться.
- **Несанкционированный переход к исполнению**: Риск случайного запуска симуляции без ручного подтверждения со стороны пользователя.

## Что нельзя потерять/исказить дальше
- Обязательный предварительный вызов гейта [check_active_run_gate.ps1](file:///C:/Users/koval/Documents/ZolotyayLopata/tools/check_active_run_gate.ps1) перед каждым шагом.
- Использование режима `-PlanOnly` для первичной валидации манифеста симуляции.
- Полное отсутствие в конфигурации реальных ордеров, API-ключей, левериджа или маржинальных параметров.

## Решение
approve


# L2 Antigravity
## Что было сделано
- Проведен независимый анализ L1-чекпоинта для текущей цели `trading_mvp` в файле [review-packet.md](file:///C:/Users/koval/.gemini/antigravity-cli/scratch/aion-antigravity-review/run-3sbr15hy/review-packet.md).
- Изучен статус прохождения проверки качества данных (data quality gate) для фандинг-датасета `funding_collect_7d_spotliq_visible_20260617_185732` с помощью отчета [funding_final_review_guard_stop_verify_20260627.json](file:///C:/Users/koval/Documents/ZolotyayLopata/exports/trading-mvp/funding/funding_final_review_guard_stop_verify_20260627.json).
- Оценена корректность переключения на ветку `SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT` для сбора WebSocket-данных через скрипт [start_ws_collect_visible.ps1](file:///C:/Users/koval/Documents/ZolotyayLopata/tools/start_ws_collect_visible.ps1).
- Верифицирована цепочка последующих действий, включая валидацию через [run_ws_replay_validation_visible.ps1](file:///C:/Users/koval/Documents/ZolotyayLopata/tools/run_ws_replay_validation_visible.ps1) и запуск гейта [check_active_run_gate.ps1](file:///C:/Users/koval/Documents/ZolotyayLopata/tools/check_active_run_gate.ps1).
- Подтверждено соблюдение всех правил безопасности (отсутствие реальных ордеров, кредитного плеча, API-ключей и маржинальных настроек).

## На чем основан вывод
- **Блокировка предыдущего этапа**: Data-quality gate заблокировал фандинг-датасет в файле [funding_final_review_guard_stop_verify_20260627.json](file:///C:/Users/koval/Documents/ZolotyayLopata/exports/trading-mvp/funding/funding_final_review_guard_stop_verify_20260627.json) из-за `min_rows_per_cycle=9 < 20`, что делает невозможным дальнейшую постобработку или запуск бэктестов на этих данных.
- **Обоснованность альтернативного шага**: Переход на сбор WebSocket-данных высокой плотности (6 часов) является логичным и верным следующим шагом, определенным скриптом [trading_next_goal_step.ps1](file:///C:/Users/koval/Documents/ZolotyayLopata/tools/trading_next_goal_step.ps1).
- **Безопасность первого шага**: Скрипт запускается с ключом `-PlanOnly`, что исключает запись или активные операции до проверки сформированного манифеста.
- **Безопасность симуляции**: Весь планируемый пайплайн (replay validation) использует только `-ExpectedManifestPath` и требует явного флага `-ConfirmedResearchRun` после прохождения гейтов качества, исключая совершение реальных транзакций.

## Что получилось хорошо
- Автоматизированный контроль качества данных успешно предотвратил использование непригодного датасета фандинга.
- Переход на альтернативный сбор данных высокой плотности выполняется в полностью изолированном и безопасном режиме предварительного планирования (`-PlanOnly`).
- Исключены невалидные источники принятия решений (предыдущий некорректно созданный workflow без риск-флагов).

## Что требует доработки
- Codex должен строго придерживаться указанной последовательности: сначала безопасный WS-сбор, затем guarded WS postprocess, после чего запуск [run_ws_replay_validation_visible.ps1](file:///C:/Users/koval/Documents/ZolotyayLopata/tools/run_ws_replay_validation_visible.ps1) с ключом `PlanOnly` для сверки манифестов, и только при успешном прохождении проверок — запуск с флагом `-ConfirmedResearchRun`.

## Какие есть риски
- **Риск качества данных нового сбора**: 6-часовой WS-датасет также может не пройти пороги плотности. Этот риск минимизируется обязательной проверкой гейта после сбора.
- **Длительное время выполнения**: Процесс сбора данных занимает 6 часов, поэтому он должен выполняться прозрачно (visible) и логироваться.
- **Несанкционированный переход к исполнению**: Риск случайного запуска симуляции без ручного подтверждения со стороны пользователя.

## Что нельзя потерять/исказить дальше
- Обязательный предварительный вызов гейта [check_active_run_gate.ps1](file:///C:/Users/koval/Documents/ZolotyayLopata/tools/check_active_run_gate.ps1) перед каждым шагом.
- Использование режима `-PlanOnly` для первичной валидации манифеста симуляции.
- Полное отсутствие в конфигурации реальных ордеров, API-ключей, левериджа или маржинальных параметров.

## Решение
approve


# L3 Codex
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


# L4 Codex
## Что было сделано
- Codex L4 провел архитектурный и risk gate по результатам L1-L3.
- Проверено, что изменения относятся только к guard/automation слою, а не к стратегии, параметрам alpha, live execution или paper-forward acceptance.
- Проверено, что Рой-процесс не отменяет Active Run Gate Rule и Visible Run Rule.

## На чем основан вывод
- L1 Antigravity: approve, следующий шаг visible dense WS collect plan после funding data-quality block.
- L2 Antigravity: approve, подтвердил обязательность PlanOnly/explicit confirmation/data-quality/ExpectedManifestPath.
- L3 Codex: `start_ws_collect_visible.ps1` и `trading_edge_preflight.ps1` усилены; проверки прошли.
- Verification: gate `READY_FOR_POSTPROCESS`; PlanOnly `would_start=false`; preflight `READY_FOR_EDGE_PROOF_STEP`; acceptance gate `research_only_no_accepted_strategy`; tests `198 OK`.

## Что получилось хорошо
- Decision path теперь не смешивает funding branch и WS branch: funding dataset остается rejected, WS branch требует нового visible dense data.
- Post-collect pipeline выражен явно и повторяемо: completed manifest -> guarded postprocess -> replay-validation PlanOnly with same manifest -> explicit ConfirmedResearchRun only after data-quality acceptance.
- User-cost/limit control соблюден: во время долгого прогона дальнейшие инженерные шаги будут запрещены gate-status `RUNNING`.

## Что требует доработки
- Перед фактическим стартом 6h collect пользователь должен отдельно подтвердить `-ConfirmedLongRun`.
- После collect нужно проверить, что active-run-gate перезаписан WS run metadata и не ссылается на старый funding run.
- Если L5 Claude Code недоступен, workflow нужно оставить как `swarm_limited`/ожидающий L5 и продолжить Codex-управление без выдачи финального Claude-verdict.

## Какие есть риски
- 6h data может быть недостаточно для доказательства edge; это только следующий data-quality step, не acceptance.
- Любой replay/grid на rejected data создаст ложный edge; поэтому `replay_allowed=true` обязателен.
- Старый funding gate status `READY_FOR_POSTPROCESS` может вводить в заблуждение, поэтому next-goal logic и guard artifact должны иметь приоритет над старой строкой `next_step_after_ready`.

## Что нельзя потерять/исказить дальше
- Не запускать новый long collector без явного подтверждения пользователя.
- Не запускать replay/grid до guarded postprocess и replay-validation PlanOnly.
- Не использовать канал/новые видео/P2P/off-ramp/custody/legal как вход в текущую цель.
- Не оптимизировать winrate отдельно от expectancy, net PnL after costs, PF, drawdown, sample size, liquidity/fill risk и OOS устойчивости.

## Решение
approve

