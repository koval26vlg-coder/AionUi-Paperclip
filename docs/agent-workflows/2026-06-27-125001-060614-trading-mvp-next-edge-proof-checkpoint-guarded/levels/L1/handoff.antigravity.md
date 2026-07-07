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
