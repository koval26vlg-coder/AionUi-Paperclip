Проверить и утвердить/исправить цель v2 для trading_mvp.

Контекст:
- Пользователь хочет найти, доказать или честно отбросить рабочий trading edge для non-Binance markets.
- Новая цель должна оптимизировать net expectancy after all costs, а не win rate.
- Высокий winrate без положительной expectancy, profit factor, drawdown control, sample size и OOS устойчивости не считается edge.
- Taker cost-gate обязателен: если round-trip costs заранее больше target bps, сигнал kill by construction.
- Обязательны data-quality gate, cost gate, OOS, walk-forward, stress, economics, paper-forward before live.
- Live orders, API keys, leverage/margin и инвестсовет запрещены.
- Приоритетные ветки: funding/basis carry, slower structural edge, thin-market maker/post-only inefficiencies, listing/event effects. HFT-scalping on public API считать низкоприоритетным из-за fee/latency disadvantage.

Текущий run:
- active-run-gate синхронизирован в STOPPED_INCOMPLETE.
- run_id: ws_collect_72h_sweep_visible_20260702_012710.
- Manifest: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\raw\ws_collect_20260702_054555.json.
- Requested: 72h / 259200 sec.
- Actual: ~26274.98 sec / 7.3h.
- total_events: 7,716,396.
- error_count: 9.
- Stop reason: collector_exited_before_requested_duration_after_reconnect_failures.
- Do not run postprocess/grid/replay on this incomplete dataset unless explicitly accepted as incomplete research sample; default decision should be resume/clean-run vs discard.

Задачи Роя:
1. Проверить формулировку цели v2: она должна быть строгой, измеримой и не подменять expectancy winrate-ом.
2. Проверить текущий STOPPED_INCOMPLETE dataset и решить: resume same run, clean 72h rerun, or mark incomplete and use only for tooling QA.
3. Сформировать gate matrix: data quality, cost, OOS, walk-forward, stress, economics, paper-forward, risk/counterparty, security/API custody.
4. Определить ближайший инженерный шаг, который реально приближает доказательство или отбраковку edge и не жжет лимиты впустую.
5. Зафиксировать запреты: no channel analysis, no P2P/off-ramp/custody/legal content for this objective, no live trading before paper-forward acceptance.

Ожидаемый результат: краткий L1 handoff/recommendation, что делать дальше и какие branch kill/continue criteria применить.
