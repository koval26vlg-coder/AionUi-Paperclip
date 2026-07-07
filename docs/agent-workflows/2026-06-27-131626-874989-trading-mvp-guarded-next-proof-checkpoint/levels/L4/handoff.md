## Что было сделано
- Проведен L4 architecture/risk review после L3 implementation.
- Проверена связка: `check_active_run_gate.ps1` -> `trading_next_goal_step.ps1` -> `start_ws_collect_visible.ps1 -PlanOnly` -> future `run_ws_postprocess_visible.ps1` -> future `run_ws_replay_validation_visible.ps1 -PlanOnly`.
- Подтверждено, что новые early-density/schema guards не запускают market collect сами и работают только внутри confirmed visible wrapper.
- Подтверждено, что PlanOnly остается non-invasive: `would_start=false`, `requires_confirmed_long_run=true`.

## На чем основан вывод
- `tools\start_ws_collect_visible.ps1 -Hours 6 -PlanOnly` вернул JSON plan с `early_density_guard.enabled=true` и `schema_probe.enabled=true`.
- `tools\trading_edge_preflight.ps1 -Json` вернул `READY_FOR_EDGE_PROOF_STEP`, `fail_count=0`, `warn_count=0`.
- `tools\trading_next_goal_step.ps1 -Json` вернул `SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT` и сохранил `state.gate_postprocess_block`.
- `python -m unittest discover -s trading_mvp/tests` прошел: `202 OK`.

## Что получилось хорошо
- Stale funding route теперь защищен двумя слоями: active gate readback и preflight regression.
- Future WS collect имеет early-stop на разреженных/сломанных данных, чтобы не сжигать 6 часов впустую.
- Schema probe проверяет raw writer contract до postprocess, снижая риск позднего обнаружения несовместимого JSONL.
- Все изменения research-only, без live orders/API keys/leverage/margin.

## Что требует доработки
- До actual collect пользователь должен явно подтвердить запуск visible 6h run.
- Перед запуском можно поднять `EarlyDensityMinLinesPerMinute`, если цель - жестче отсеивать малоплотные рынки; текущий default намеренно минимальный sanity threshold, а не доказательство качества.
- После collect все равно обязателен `ws-postprocess` data-quality gate; early guard не заменяет OOS/walk-forward/stress.

## Какие есть риски
- Early guard использует raw line count как быстрый proxy, а не качество microstructure-событий по рынкам; финальная пригодность определяется только postprocess quality/replay gates.
- Если биржа медленно начинает отдавать поток, schema probe дождется первых строк, а early density проверит только через 60 минут; это осознанный компромисс между false stop и wasted runtime.
- L5 Claude/risk gate может быть недоступен по лимитам; если так, нужно зафиксировать `swarm_limited` и продолжить ручное Codex-управление по тем же правилам.

## Что нельзя потерять/исказить дальше
- Funding dataset с `min_rows_per_cycle=9` остается rejected, не использовать для rank/backtest/paper-forward.
- Actual long run только в видимом терминале/monitor и только после явного подтверждения пользователя.
- Replay/grid только после postprocess artifact с `replay_allowed=true` и явным `ExpectedManifestPath`.
- High winrate сам по себе не acceptance; обязательны expectancy, net PnL after costs, PF, drawdown, sample size, liquidity/fill risk, OOS/walk-forward/stress.

## Решение
approve
