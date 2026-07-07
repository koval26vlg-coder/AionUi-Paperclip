# trading_mvp dense WS checkpoint review

Задача для Роя: независимо проверить текущий research checkpoint и следующий шаг по цели trading_mvp.

## Цель
Найти, доказать или честно отбросить высоко-винрейтную trading strategy/edge для non-Binance markets через данные, backtest, OOS, walk-forward, stress, economics и paper-forward gates.

## Ограничения
- Research-only.
- Не запускать live orders, API keys, leverage/margin.
- Не запускать новый collector/backtest/grid/paper-forward.
- Не анализировать канал/YouTube/P2P/off-ramp/custody/legal.
- Уважать Active Run Gate и Visible Run Rule.

## Текущее состояние по live evidence
- Project: C:\Users\koval\Documents\ZolotyayLopata
- Active gate: READY_FOR_POSTPROCESS for run_id=ws_confirmed_research_6h_20260628_103700.
- Manifest: exports/trading-mvp/raw/ws_collect_20260628_000346.json.
- Raw collect: 2,745,067 events, MEXC/Gate, 16 spot markets, 6h requested, errors=0.
- Data quality artifact: exports/trading-mvp/backtests/ws_data_quality_ws_collect_20260628_000346_postprocess_20260628_100805.json.
- Data quality accepted=true, rows=2,744,439, span_hours=5.99997, parse_error_rate=0, max_gap_sec=55.53.
- Replay validation: exports/trading-mvp/backtests/ws_replay_validation_ws_confirmed_research_6h_20260628_103700.json, ok=true.
- Acceptance gate: exports/trading-mvp/backtests/sweep_reversal_acceptance_ws_confirmed_research_6h_20260628_103700_gatefixed.json.

## Current result to verify
- Strategy is NOT accepted.
- sweep_reversal_acceptance accepted=false, fail_count=15.
- event_quality total_sweeps=43, target_before_stop_rate=0.38235, false_sweep_rate=0.69767.
- event_validation accepted=false; reasons include no_train_eligible_slice, train_selected_rejected, oos_rejected, walk_forward_rejected, stress_rejected.
- ws_grid eligible_combinations=0.
- best LSR config: 11 trades, win_rate=0.54545, net_pnl_quote=+0.029408, PF=1.565, but failed min_trades and min_win_rate.
- strategy_acceptance_gate accepted=false and live_orders=false.

## Decision under review
Current old/current dataset is rejected for strategy acceptance. Do not paper/live. The next useful step is a visible dense independent WS collect plan only; actual 6h collect requires explicit user confirmation and visible terminal/monitor.

## Review questions
1. Is the rejection defensible from artifacts and gates, or did Codex miss an acceptance-worthy signal?
2. Is the next step correctly limited to PlanOnly/visible dense WS collect, not paper/live or more tuning on the same thin sample?
3. Are any proof-pipeline guards missing before asking the user for explicit collect confirmation?
4. What exact artifact/metric should the next agent inspect before approving a new collection or replay-validation?

## Expected output
- approve/revise/block verdict.
- If revise/block: precise file/command/artifact gaps.
- Do not provide investment advice.
