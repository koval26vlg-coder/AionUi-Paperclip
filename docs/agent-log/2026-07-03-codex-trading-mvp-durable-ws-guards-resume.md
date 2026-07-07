# 2026-07-03 - Codex - trading_mvp durable WS guards/resume

Implemented guarded visible durable WS wrapper in `C:\Users\koval\Documents\ZolotyayLopata`.

Key files:
- `tools/start_ws_collect_durable.ps1`
- `tools/watch_ws_collect_durable.ps1`
- `tools/check_active_run_gate.ps1`
- `trading_mvp/src/ws_durable_collector.py`
- `trading_mvp/tests/test_ws_durable_collector.py`
- `docs/ws-durable-collect-runbook.md`
- `docs/agent-log/2026-07-03-trading-mvp-durable-ws-guards-resume.md`

Behavior:
- No hidden/detached default long run.
- Actual run requires `-ConfirmedLongRun`.
- Current `STOPPED_INCOMPLETE` requires explicit `-ReplaceStoppedIncomplete` before starting a replacement durable verification/72h run.
- On stop, wrapper writes `STOPPED_INCOMPLETE.txt`, `notification_required`, `alert_path`, `resume_command`.
- Resume command: `tools/start_ws_collect_durable.ps1 -RunId <run_id> -Resume -ConfirmedLongRun`.
- Resume skips completed segment manifests and archives incomplete retry target dirs.

Verification:
- `tools/run_trading_tests.ps1` passed: 294 tests OK, 8 skipped.
- No market collector/backtest/postprocess was started.

Next command after user confirmation:
`pwsh -NoProfile -ExecutionPolicy Bypass -File C:\Users\koval\Documents\ZolotyayLopata\tools\start_ws_collect_durable.ps1 -TotalSec 7200 -SegmentSec 3600 -Exchanges "mexc,gateio" -UniversePath "C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\universe\no_binance_dense_ws_sweep_20260628.csv" -MaxSymbols 300 -MaxPairsPerExchange 16 -UpdateInterval "100ms" -ConfirmedLongRun -ReplaceStoppedIncomplete`
