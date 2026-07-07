## Что было сделано
Codex L3 реализовал рекомендацию Роя L1/L2: выровнял legacy visible_collect aliases в `tools/trading_goal_status.ps1` и `tools/trading_next_goal_step.ps1`, чтобы при `funding_blocked_by_swarm=true` они резолвились в guarded WS path, а не в старый 7d funding collect. Явные funding-команды сохранены отдельно как `funding_visible_*`, чтобы не терять диагностический путь, но не смешивать его с текущей primary branch.

## На чем основан вывод
Проверен active-run gate: `READY_FOR_POSTPROCESS` только формально, funding postprocess заблокирован guard review по `data_quality:min_min_rows_per_cycle`, `min_rows_per_cycle=9`. Проверены текущие `trading_goal_status.ps1 -Json`, `trading_next_goal_step.ps1 -Json`, `trading_edge_preflight.ps1 -Json` и `start_ws_collect_visible.ps1 -Hours 6 -PlanOnly`. После правок legacy visible collect в goal status и next goal step указывает на `start_ws_collect_visible.ps1`, а explicit funding fields указывают на `start_funding_collect_visible.ps1`.

## Что получилось хорошо
Убран второй обходной путь к заблокированному funding collect из операторских/status outputs. Сохранена обратная совместимость legacy fields: старые потребители `visible_collect_*` получат актуальную WS-команду при заблокированном funding. Добавлены регрессионные проверки, которые читают JSON-вывод обоих контроллеров и проверяют это поведение.

## Что требует доработки
Перед фактическим 6h collect все еще нужно отдельное явное подтверждение пользователя. После завершения collect следующий шаг остается guarded WS postprocess, затем replay validation только при `replay_allowed=true` и отдельном подтверждении research run.

## Какие есть риски
Funding-команды сохранены в explicit `funding_visible_*`; оператор может увидеть их, но они больше не являются legacy/default current branch. Любой фактический long run по-прежнему требует visible terminal/monitor и `-ConfirmedLongRun`. Никакие collectors/backtests/replay/grid не запускались.

## Что нельзя потерять/исказить дальше
Датасет `funding_collect_7d_spotliq_visible_20260617_185732` остается rejected для rank/backtest/paper-forward. Текущая ветка цели: guarded visible 6h WS collect plan, не live trading. High winrate не считается edge без expectancy, net PnL after costs, profit factor, drawdown, sample size, liquidity/fill risk и OOS/walk-forward/stress.

## Решение
approve
