Провести независимую проверку trading_mvp checkpoint перед следующим proof step.

Контекст:
- Цель: найти/доказать/отбросить high-winrate trading edge для non-Binance markets через data/backtest/OOS/walk-forward/stress/economics/paper-forward gates.
- Live orders/API keys/leverage/margin запрещены; режим research-only.
- Active gate сейчас READY_FOR_POSTPROCESS, но текущий WS postprocess artifact rejected: replay_allowed=false, причина min_duration_ratio.
- Replay/grid/postprocess на rejected artifact запрещены.
- Следующий рыночный шаг разрешен только как visible 72h dense WS collect после явного START72H.
- Проверить файлы/команды: tools/check_active_run_gate.ps1, tools/trading_collect_approval_contract.ps1, tools/trading_edge_preflight.ps1, tools/start_ws_collect_visible.ps1, TRADING_START_DENSE_WS_CONFIRMED.cmd, exports/trading-mvp/analysis/trading_ws_collect_readiness_current.json.

Задача Роя:
1. Проверить, что текущий next step действительно gated START72H 72h dense WS collect, а не replay/grid на rejected artifact.
2. Проверить, что approval contract и visible-run правила достаточны перед запуском долгого сбора.
3. Найти пробелы в proof pipeline до запуска 72h collect: risk, data quality, MEXC/Gate fanout, postprocess readiness, OOS/walk-forward/stress readiness.
4. Не запускать collectors/backtests/replay/grid и не анализировать новый канал/YouTube/P2P/off-ramp/custody/legal.
5. Вернуть handoff с verdict: approve/revise/block next START72H step и конкретными правками, если нужны.
