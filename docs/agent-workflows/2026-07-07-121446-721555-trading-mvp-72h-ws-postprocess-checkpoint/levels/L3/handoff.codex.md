# L3 Codex Handoff: 72h WS Postprocess Result

## Decision
block_replay_pending_gap_audit

## What was executed
- Confirmed active-run gate was READY_FOR_POSTPROCESS for ws_durable_72h_20260704_000015.
- Confirmed stitched manifest is final/completed: 24/24 segments, 76,011,803 raw events, stop_condition=duration_sec.
- Ran visible guarded ws-postprocess with label $label.
- No live orders, API keys, leverage, margin, or investment advice.

## Artifacts
- Manifest: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\raw-durable\ws_durable_72h_20260704_000015\ws_collect_ws_durable_72h_20260704_000015.json
- Normalized: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\normalized\ws_normalized_ws_collect_ws_durable_72h_20260704_000015_postprocess_20260707_124007.jsonl
- Quality: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\backtests\ws_data_quality_ws_collect_ws_durable_72h_20260704_000015_postprocess_20260707_124007.json
- Postprocess: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\backtests\ws_postprocess_ws_collect_ws_durable_72h_20260704_000015_postprocess_20260707_124007.json
- Console log: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\run\ws_postprocess_ws_collect_ws_durable_72h_20260704_000015_postprocess_20260707_124007.console.log

## Metrics
- replay_allowed: false
- rejection reasons: max_gap_sec
- raw_rows: 76,011,803
- normalized_rows: 76,024,970
- decode_error_count: 0
- malformed_rows: 0
- parse_error_rate: 0.0
- exchanges: 2
- markets: 32
- span_hours: 79.90
- duration_ratio: 1.110
- max_market_event_share: 0.113
- max_gap_sec: 28,492.1 (~7.91h)
- markets_with_gap_over_limit: 32
- manifest_error_count: 0

## Required next step
Do not run replay/grid/search yet. Perform a gap audit:
1. Break down gaps by exchange/market/event_kind.
2. Distinguish collector/data outages from natural no-trade/no-update intervals on thin markets.
3. Decide whether the quality gate should use per-event-kind rules, contiguous-window slicing, or market eligibility filtering.
4. Only if a defensible clean slice exists, run replay-validation PlanOnly against that slice.
5. If gaps indicate collector reliability failure, mark this dataset unsuitable for proving edge and collect a cleaner dataset after monitor/progress improvements.

## Notes
The postprocess terminal is still open because it was launched with -NoExit; worker child finished and output artifacts exist. User can close that window.
