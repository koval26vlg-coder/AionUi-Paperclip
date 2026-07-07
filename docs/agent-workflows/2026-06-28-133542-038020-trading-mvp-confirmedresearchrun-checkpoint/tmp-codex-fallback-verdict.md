## Что было сделано
Codex выполнил ручной fallback после недоступности Antigravity L1 и проверил текущий ConfirmedResearchRun по фактическим артефактам.

## На чем основан вывод
- ws_replay_validation_ws_confirmed_research_6h_20260628_103700.json: ok=true.
- sweep_reversal_acceptance_ws_confirmed_research_6h_20260628_103700_gatefixed.json: accepted=false, paper_forward_allowed=false, fail_count=15.
- WS grid: eligible_combinations=0/96; best config trades=11, win_rate=0.545, net_pnl_quote=0.0294, profit_factor=1.565, rejected by min_trades and min_win_rate.
- Event diagnostics: total_sweeps=43 < 1000, target_before_stop_rate=0.382 < 0.6, false_sweep_rate=0.698 > 0.5.
- OOS/walk-forward/stress rejected.

## Что получилось хорошо
- Research guard did not allow paper/live on weak evidence.
- Positive PF/net PnL in best WS config was not overclaimed because sample size and winrate fail gates.
- Gate false RUNNING from -NoExit was fixed with regression coverage.

## Что требует доработки
- Current spot_maker_liquidity_sweep_reversal cannot be treated as edge.
- If kept, it is only a hypothesis and needs an independent dense WS/perp dataset plus OOS/walk-forward/stress proof.
- Need stronger sample size and fill/queue realism before any paper-forward readiness.

## Какие есть риски
- Thin sample and overfit: 11 WS trades and 43 diagnostic events are far below proof thresholds.
- Fill/queue/adverse-selection risk: maker fills may concentrate in bad states.
- Liquidity risk: current best result appears concentrated in gateio:HYPE_USDT.
- Cost risk: maker assumptions do not prove taker or real venue economics.

## Что нельзя потерять/исказить дальше
- Verdict remains reject/no-paper-forward.
- No live orders, API keys, leverage, margin, or investment advice.
- Binance remains exclusion/reference only, not execution venue.
- New long collect must be visible and user-approved.

## Решение
revise
