Пользователь попросил использовать Рой для продолжения цели trading_mvp.

Текущая цель: найти, доказать или честно отбросить рабочую high-winrate trading strategy/edge для non-Binance markets через данные, backtest, OOS, walk-forward, stress, economics и paper-forward gates.

Обязательные ограничения:
- research-only; без live orders, API keys, leverage/margin, инвестсоветов;
- не анализировать новые видео/канал/P2P/off-ramp/custody/legal;
- перед goal work проверять C:\Users\koval\Documents\ZolotyayLopata\tools\check_active_run_gate.ps1;
- RUNNING = только status; STOPPED_INCOMPLETE = видимый resume или признать dataset неполным; READY_FOR_POSTPROCESS = можно следующий шаг;
- длинные collect/backtest/replay/grid/paper-forward запускать только видимо или через видимый monitor, не в фоне;
- не стартовать новый 6h WS collect без явного подтверждения пользователя.

Факты текущего состояния:
- funding 7d collect завершен, но funding final-review отклонил dataset как blocked_by_data_quality: min_rows_per_cycle=9 < threshold 20, поэтому funding rank/backtest/OOS/paper-forward не создан и claims по PnL/winrate/ROI запрещены.
- выбранная ветка: NEXT_BRANCH_SPOT_MAKER_LIQUIDITY_SWEEP_REVERSAL / spot_maker_liquidity_sweep_reversal_event_quality.
- следующий реальный long-run: visible 6h WS collect, только после явного подтверждения.
- уже есть guarded WS postprocess wrapper: C:\Users\koval\Documents\ZolotyayLopata\tools\run_ws_postprocess_visible.ps1.

Задача Роя:
1. Независимо проверить, что следующий инженерный checkpoint должен быть guarded WS replay/validation wrapper после data-quality postprocess, а не live/paper-forward.
2. Проверить, какие gates обязаны блокировать replay/grid при плохом ws_postprocess artifact.
3. Дать approve/revise/block по плану Codex: добавить wrapper run_ws_replay_validation_visible.ps1 с PlanOnly, explicit PostprocessPath, refusal on active RUNNING/STOPPED_INCOMPLETE, replay_allowed gate, and ConfirmedResearchRun for actual replay/grid.
4. Не запускать collector/replay/grid/live orders. Только проверка плана и handoff.
