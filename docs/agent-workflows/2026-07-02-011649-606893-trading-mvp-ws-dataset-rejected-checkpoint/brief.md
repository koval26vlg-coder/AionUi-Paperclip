trading_mvp checkpoint after visible WS collect/postprocess.

Current evidence:
- Repo: C:\Users\koval\Documents\ZolotyayLopata
- Active gate: READY_FOR_POSTPROCESS but replay_allowed=false.
- Manifest: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\raw\ws_collect_20260701_211647.json
- Postprocess: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\backtests\ws_postprocess_ws_collect_61h_sweep_20260701_211647.json
- Data quality: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\backtests\ws_data_quality_ws_collect_61h_sweep_20260701_211647.json
- Normalized: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\normalized\ws_normalized_ws_collect_61h_sweep_20260701_211647.jsonl

Postprocess result:
- replay_allowed=false
- data_quality.accepted=false
- reasons: min_duration_ratio, max_gap_sec
- normalized_rows=11,493,374
- MEXC rows=11,263,147; GateIO rows=230,227
- span_hours=16.1608 vs manifest duration 61.27h; duration_ratio=0.2638
- max_gap_sec=523.34; markets_with_gap_over_limit=16
- manifest_error_count=9

Task for swarm:
Independently review whether the dataset must be rejected for replay/grid, whether any safe partial analysis is allowed, and what the next proof-step should be toward finding or rejecting a high-winrate/non-Binance trading edge. Respect research-only mode: no live orders, API keys, leverage, margin, investment advice, or hidden long runs. Recommend either cleaner visible WS collect parameters, a different data branch (perp/funding), or discard this spot WS branch if evidence supports it.
