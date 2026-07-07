Пользователь попросил: "используй Рой".

Текущая цель: trading_mvp должен найти, доказать или честно отбросить рабочую высоко-винрейтную trading strategy/edge для non-Binance markets через данные, backtest, OOS, walk-forward, stress, economics и paper-forward gates.

Текущий confirmed state Codex:
- Active run gate: READY_FOR_POSTPROCESS по funding_collect_7d_spotliq_visible_20260617_185732; live PIDs нет.
- Предыдущий Рой workflow 2026-06-27-110635-774802-trading-mvp-oos-stress-checkpoint завершен и не принял стратегию: sweep_reversal accepted=false; текущие старые данные rejected.
- Следующий допустимый шаг: только PlanOnly/approval checkpoint для видимого dense WS collect, без скрытого фонового запуска.
- tools/start_ws_collect_visible.ps1 -Hours 6 -PlanOnly должен показывать next_goal_decision=SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT и команду с -ConfirmedLongRun только после явного approval пользователя.

Задача Роя:
1. Независимо проверить, что следующий шаг цели корректен: видимый 6h WS collect по MEXC/Gate для spot maker liquidity sweep reversal/event-quality, а не postprocess/live/paper-forward.
2. Проверить риски: trading research-only, no live orders, no API keys, no leverage/margin, no investment advice, no channel/P2P/off-ramp analysis.
3. Проверить, не нарушает ли запуск collect active-run gate и visible-run rule.
4. Дать handoff: запускать ли видимый 6h collect после явного approval пользователя, какие параметры/acceptance gates должны быть зафиксированы, и что делать если агентские лимиты/Рой недоступны.

Не запускать торговые операции, API keys, live orders, margin/leverage или скрытые долгие процессы.
