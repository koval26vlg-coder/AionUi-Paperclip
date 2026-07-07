Задача: независимый checkpoint по trading_mvp после ConfirmedResearchRun ws_confirmed_research_6h_20260628_103700.

Цель проекта: найти, доказать или честно отбросить рабочий high-winrate edge для non-Binance markets через данные, replay/backtest, OOS, walk-forward, stress, economics и paper-forward gates. Research-only: live orders/API keys/leverage/margin запрещены.

Факты текущего запуска:
- Gate был ложно RUNNING из-за оставленного pwsh -NoExit, дочерний grid-search завершился; gate переведен в READY_FOR_POSTPROCESS.
- Validation summary: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\backtests\ws_replay_validation_ws_confirmed_research_6h_20260628_103700.json, ok=true.
- Event quality: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\backtests\event_quality_ws_confirmed_research_6h_20260628_103700.json.
- Event validation: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\backtests\event_validation_ws_confirmed_research_6h_20260628_103700.json.
- Grid: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\backtests\ws_grid_search_ws_confirmed_research_6h_20260628_103700.json.
- Corrected acceptance gate: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\backtests\sweep_reversal_acceptance_ws_confirmed_research_6h_20260628_103700_gatefixed.json.

Ключевые результаты:
- sweep acceptance accepted=false, decision=SWEEP_REVERSAL_RESEARCH_NOT_ACCEPTED_NEEDS_INDEPENDENT_DATA, paper_forward_allowed=false, fail_count=15.
- Event diagnostics: total_sweeps=43 < 1000, target_before_stop_rate=0.382 < 0.6, false_sweep_rate=0.698 > 0.5.
- Event validation accepted=false: no_train_eligible_slice, train_selected_rejected, oos_rejected, walk_forward_rejected, stress_rejected.
- WS grid: total_combinations=96, eligible_combinations=0. Best config has trades=11, win_rate=0.545, net_pnl_quote=0.0294, profit_factor=1.565, but fails min_trades and min_win_rate.
- Perp/grid referenced by acceptance: trades=3, win_rate=0.667, positive expectancy/PF, but fails min_trades.

Запрос к Рою:
1. Проверить, корректен ли verdict reject/no-paper-forward по текущим evidence.
2. Сказать, ветку spot_maker_liquidity_sweep_reversal надо отбросить сейчас или оставить как research hypothesis, требующую независимого dense WS/perp collect.
3. Сформулировать следующий инженерный шаг, который максимально двигает цель high-winrate edge без live/API/leverage/margin.
4. Явно указать approve/revise/block и риски overfit/thin sample/cost/fill/liquidity.
