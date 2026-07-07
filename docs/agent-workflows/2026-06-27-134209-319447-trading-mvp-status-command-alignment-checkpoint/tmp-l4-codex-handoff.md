## Что было сделано
Codex L4 выполнил архитектурную и risk-gate проверку результата L1-L3. Проверено, что изменение не запускает торговые процессы, не требует секретов, не меняет acceptance criteria и не ослабляет Active Run Gate Rule или Visible Run Rule. Изменение только выравнивает статусные команды, чтобы текущий default/legacy путь не возвращал оператора к заблокированному funding collect.

## На чем основан вывод
Фактическая проверка: `trading_goal_status.ps1 -Json` показывает `funding_blocked_by_swarm=true`, `visible_collect_command_legacy_resolution=redirected_to_ws_collect_because_funding_blocked_by_swarm`, `visible_collect_command == visible_ws_collect_command`, а `funding_visible_collect_command` остается отдельным explicit field. `trading_next_goal_step.ps1 -Json` показывает decision `SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT`, primary command `start_ws_collect_visible.ps1 -Hours 6 -PlanOnly`, и legacy `visible_collect_after_approval == visible_ws_collect_after_approval`. `trading_edge_preflight.ps1 -Json` вернул `READY_FOR_EDGE_PROOF_STEP`, `ok=true`, `fail_count=0`, `warn_count=0`. `start_ws_collect_visible.ps1 -Hours 6 -PlanOnly` вернул `would_start=false`, `requires_confirmed_long_run=true`, guards enabled. Full tests: `204 OK`.

## Что получилось хорошо
Статусные контроллеры теперь согласованы: preflight, next-goal и goal-status не дают разных default-путей. Risk снижён без удаления funding tooling: funding branch можно явно открыть позже только через fee/economics evidence, но legacy aliases не ведут туда автоматически.

## Что требует доработки
Если следующий пользовательский шаг будет фактический 6h WS collect, нужно запросить явное подтверждение и запускать только видимо. После collect нельзя сразу grid/replay; нужен guarded postprocess и `replay_allowed=true`.

## Какие есть риски
Риск не в коде, а в дальнейшем операторском действии: пользователь может попросить `запусти прогон`; тогда нужно сначала показать, что это actual long run и получить явное подтверждение, а не использовать скрытый фон. Risk flag trading остается true; live/API/leverage/margin остаются запрещены.

## Что нельзя потерять/исказить дальше
Нельзя интерпретировать эту правку как доказательство стратегии. Это только guard/command hygiene перед следующим сбором данных. Funding dataset остается rejected; current proof branch остается WS dense collect plan. Канальный анализ и P2P/off-ramp темы остаются вне цели.

## Решение
approve
