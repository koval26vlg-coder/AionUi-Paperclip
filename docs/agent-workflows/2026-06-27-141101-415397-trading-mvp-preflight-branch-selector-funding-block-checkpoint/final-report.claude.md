All L4 claims are independently verified against the actual artifacts. Here is my final L5 review-only conclusion.

## Verdict

Чекпойнт **подтверждается**. Я независимо (чтением артефактов, без запуска коллекторов) проверил всю цепочку и нашёл, что блокировка funding-датасета реальна и обоснована, а guard/readback/test-покрытие достаточны для перехода к research-only шагу. L1–L4 не исказили факты; более того, защита местами сильнее, чем описал L4.

## Evidence Reviewed

- **`docs/agent-log/active-run-gate.json`** — сырой статус `RUNNING`, run_id `funding_collect_7d_spotliq_visible_20260617_185732`, `monitor_pid 1464`, `process_ids [1464,7940]`, `next_step_after_ready` всё ещё указывает на funding-final-review.
- **`tools/check_active_run_gate.ps1`** — эффективный статус выводится по liveness PID + `manifest.final`, а не по сырому полю. При `final=true` и `completed≥total` → `READY_FOR_POSTPROCESS`; `Find-FundingPostprocessBlock` находит блок и **переопределяет** `next_step_after_ready`, сохраняя `raw_gate_next_step_after_ready`.
- **Manifest** `...185732.manifest.json` — `final: true`, `cycles: 2016`, `completed_cycles: 2016`, `rows: 50583`. → gate корректно резолвится в `READY_FOR_POSTPROCESS`.
- **`funding_final_review_..._20260627_120411.json`** (свежий) — `ok: false`, `status: not_ready_for_postprocess`, `data_quality.accepted: false`, reason `min_min_rows_per_cycle`, **`min_rows_per_cycle: 9`** при конфиге `min_min_rows_per_cycle: 20`; **`artifacts_created: []`** (rank/backtest/paper не созданы).
- **`tools/trading_branch_selector.ps1`** (стр. 157–166) — при `funding_blocked` сохраняет `original_scorecard_next_action`, ставит override `blocked_by_swarm_do_not_run_7d_funding_collect_or_final_review`, прокидывает `postprocess_block_reasons` и `min_rows_per_cycle`.
- **`tools/trading_edge_preflight.ps1`** — `branch_selector_funding_block_override` и `funding_postprocess_block_readback` грепают именно эти маркеры; источник им соответствует.
- **`tools/start_ws_collect_visible.ps1`** — hard `throw` без `-ConfirmedLongRun`/`-PlanOnly` (стр. 101–103); повторная проверка gate перед стартом (108–116); guard'ы zero-line / early-density / schema-probe; `-PlanOnly` → `would_start=false`.

## Findings

1. **Блокировка датасета подлинная, не формальная.** `min_rows_per_cycle = 9` против требуемых `20` — это плотность данных, а не косметика. Промежуточные циклы реально тонкие → rank/backtest/paper-forward на этом наборе были бы статистически невалидны. Блок корректен.
2. **Guard'ы funding сильнее, чем заявил L4.** L4 отнёс «wrapper final-review/rank/backtest должен сам отказываться» к будущему hardening, но артефакт доказывает, что final-review wrapper **уже** отказывается: `ok=false`, `artifacts_created=[]`. Defense-in-depth уже работает на этом слое.
3. **Эффективный статус fail-safe.** Даже если monitor_pid 1464 случайно жив (PID reuse), checker даст `RUNNING` → preflight заблокирует жёстче. Любое отклонение от заявленного `READY` идёт в консервативную сторону. Сама коллекция завершена (`final=true`), поэтому висящий монитор может только усилить блок, не ослабить.
4. **Единственная остаточная утечка stale-команды.** Сырой `active-run-gate.json` сохраняет `next_step_after_ready = "Run guarded funding-final-review..."`. Он нейтрализуется только на слое checker'а (override). Потребитель, читающий сырой файл напрямую, увидит устаревшую инструкцию — но даже её исполнение упрётся в отказ final-review wrapper (см. п.2). Утечка управляема, не блокер.
5. **WS-ветка как next step корректна.** Branch selector при `funding_blocked && !fee_tier_evidence` → `NEXT_BRANCH_SPOT_MAKER_LIQUIDITY_SWEEP_REVERSAL`, видимый 6h WS collect, `requires_user_approval=false` для планирования, но реальный запуск только по `-ConfirmedLongRun`.

## Required Before Next Run

- **Показать пользователю точную confirmed-команду** перед запуском (как и просил L4): `... start_ws_collect_visible.ps1 -Hours 6 -ConfirmedLongRun`. Подтверждение должно быть предметным.
- **Сначала `-PlanOnly`**, проверить `would_start=false` + branch/next_goal decision в выводе, затем явное «да» пользователя.
- **Gate должен быть не `RUNNING`** на момент старта (wrapper это перепроверяет — оставить как есть).
- **Не использовать** funding-датасет `...185732` для rank/backtest/paper-forward; не запускать новый funding collect первым; никакого анализа нового канального контента.
- **Рекомендация (не блокер):** обновить сырое `next_step_after_ready` в gate-файле на blocked-формулировку и/или добавить self-refuse в прямые funding rank/backtest/postprocess wrappers — закрыть остаточный вектор из Finding 4. Совпадает с future-hardening пунктом L4.
- **Граница:** результат WS collect — это только данные, не приёмка стратегии. Дальше — guarded postprocess → replay validation → OOS/walk-forward/stress/economics. No live orders, no API keys, no leverage/margin, no investment advice.

## Decision

approve
