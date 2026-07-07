# Codex trading_mvp MEXC WS chunking readiness

Date: 2026-06-30 14:00 Europe/Volgograd
Agent: Codex

## User request
Continue the `trading_mvp` goal after rejected WS postprocess without wasting work while respecting visible-run and active-gate rules.

## Context
- `active-run-gate.json` status is `READY_FOR_POSTPROCESS`, but current WS postprocess is rejected: `replay_allowed=false` due `min_duration_ratio`.
- Replay/grid on the rejected artifact remain blocked.
- Next proof step is a new visible 72h dense WS collect only after explicit user approval.

## Work completed
- Added MEXC-safe WS subscription chunking in `trading_mvp/src/ws_collector.py`.
- MEXC now uses `max_channels_per_connection=30` and `channels_per_symbol=3`; `MaxPairsPerExchange=16` splits into safe chunks `10 + 6`.
- Added/updated tests and readiness/preflight checks so the 72h plan refuses unsafe no-chunk MEXC fanout.
- Did not start any long run.

## Verification
- `python -m unittest trading_mvp.tests.test_ws_collector trading_mvp.tests.test_active_run_gate trading_mvp.tests.test_visible_ws_collect_wrapper` -> 25 OK, 1 skipped.
- `tools/trading_edge_preflight.ps1 -Json` -> ok=true, fail_count=0, warn_count=0.
- `tools/trading_ws_collect_readiness.ps1 -Hours 72 -MaxPairsPerExchange 16 ... -RefreshPlan -Json` -> READY_FOR_VISIBLE_72H_WS_COLLECT_CONFIRMATION.
- `tools/check_active_run_gate.ps1 -Json` -> READY_FOR_POSTPROCESS, replay_allowed=false, explicit approval required for new collect.
- Full unittest discovery timed out after 120s; not counted as passed.

## Next step
If the user explicitly confirms `START72H`, launch only the guarded visible 72h dense WS collect through `tools/start_ws_collect_visible.ps1`. While it is running, only status/ETA checks are allowed. After completion, run guarded WS postprocess; only if `replay_allowed=true`, continue to replay/grid.
