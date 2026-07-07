## Что было сделано
Codex L3 проверил выводы L1/L2 и сопоставил их с текущим кодом проекта `trading_mvp`. Дополнительно выполнены read-only проверки: full unit suite `205 OK`, `trading_edge_preflight.ps1 -Json` возвращает `ok=true`, `status=READY_FOR_EDGE_PROOF_STEP`, `branch_selector_funding_block_override=pass`; `start_ws_collect_visible.ps1 -PlanOnly` возвращает план без запуска долгого сбора.

## На чем основан вывод
- Active gate: `READY_FOR_POSTPROCESS` только формально; текущий funding dataset завершен, но postprocess заблокирован guard review по `data_quality:min_min_rows_per_cycle`, `min_rows_per_cycle=9`.
- `tools/trading_edge_preflight.ps1` содержит source-level check `branch_selector_funding_block_override`, чтобы не возникала рекурсия preflight -> branch selector -> preflight.
- `tools/trading_branch_selector.ps1` сохраняет `original_scorecard_next_action`, но текущий funding `next_action` переопределяет на `blocked_by_swarm_do_not_run_7d_funding_collect_or_final_review; follow guarded WS collect planning via trading_next_goal_step.ps1.`
- `trading_mvp/tests/test_visible_ws_collect_wrapper.py` покрывает runtime branch selector regression и preflight check.
- `tools/start_ws_collect_visible.ps1` уже блокирует фактический долгий запуск без `-ConfirmedLongRun`; `-PlanOnly` не запускает collector.

## Что получилось хорошо
- Stale funding path закрыт на уровне branch selector, preflight и regression tests.
- Сохранен audit trail: исходный scorecard action не теряется, но не используется как исполняемый next action.
- Следующий шаг pipeline остается research-only и видимым: только explicit user approval для 6h WS collect, затем guarded ws-postprocess и replay validation.

## Что требует доработки
- L2-рекомендацию "добавить прямую проверку funding_blocked_by_swarm в start_ws_collect_visible.ps1" нельзя принимать буквально: WS collect является разрешенным successor-путем после блокировки funding. Прямая блокировка WS по funding flag сломала бы цель.
- Допустимая доработка позже: добавить более явное поле/сообщение в `trading_next_goal_step.ps1` или status output, что funding заблокирован, а WS collect разрешен только через visible confirmed run. Это косметическое улучшение, не blocker.

## Какие есть риски
- Ручной запуск funding wrapper напрямую вне status/preflight все еще возможен технически, но текущая цель и next-step scripts его не предлагают. Для полного запрета потребуется отдельный guard в funding wrappers, но это не должно блокировать WS ветку.
- Пользователь должен явно подтвердить видимый 6h WS collect; без этого нельзя начинать долгий прогон.

## Что нельзя потерять/исказить дальше
- Funding final-review/rank/backtest/paper-forward на dataset `funding_collect_7d_spotliq_visible_20260617_185732` запрещены из-за `min_min_rows_per_cycle`.
- WS collect не является доказательством стратегии; это только следующий сбор данных для proof pipeline.
- No live orders, no API keys, no leverage/margin, no investment advice.

## Решение
approve
