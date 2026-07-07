Ты Claude Code L5 final reviewer в hierarchical workflow. Не используй инструменты. Проверь только пакет ниже и верни короткий markdown final-report на русском.

Задача: пользователь попросил использовать Рой для trading_mvp. Нужно финально проверить, что Codex не исказил цель и не принял торговую стратегию без доказательств.

Критичные факты:
- Goal: найти/доказать/честно отбросить high-winrate trading edge для non-Binance markets через data/backtest/OOS/walk-forward/stress/economics/paper-forward gates.
- Restrictions: no live orders, no API keys, no leverage/margin, no investment advice, no hidden long runs, no new channel/P2P/off-ramp analysis.
- Active-run gate: READY_FOR_POSTPROCESS, 2016/2016 cycles, 50583 funding rows, 657 errors.
- L1 Antigravity: approve next step event_validation_report + data quality diagnostics + acceptance gate.
- L2 Antigravity: approve local research-only implementation; require strict acceptance thresholds and separate data-quality diagnostics.
- L3 Codex implemented:
  - trading_mvp/src/event_validation.py
  - CLI `event-validation-report`
  - run_mvp.ps1 action `event-validation-report`
  - sweep_reversal_acceptance_gate.ps1 now reads real validation artifact
  - generated event_validation_6h_duration_20260614_181422.json
  - generated funding_collect_diagnostics_7d_spotliq_visible_20260617_185732.json
  - updated branch artifact and proof plan
- Tests: `C:\Program Files\Python313\python.exe -m unittest discover -s trading_mvp/tests` -> 194 tests OK.
- Event validation result: accepted=false; reasons=oos_rejected, walk_forward_rejected, stress_rejected.
- Sweep acceptance gate result: accepted=false; fail_count=15; decision=SWEEP_REVERSAL_RESEARCH_NOT_ACCEPTED_NEEDS_INDEPENDENT_DATA.
- Key current data failures:
  - event target_before_stop_rate=0.367 < 0.60
  - false_sweep_rate=0.741 > 0.50
  - OOS selected_events=7, target_before_stop_rate=0.5, false_sweep_rate=0.571
  - walk-forward accepted_windows=0/4
  - stress target_before_stop_rate=0.0
  - execution v2 trades=10, winrate=0.1, net_pnl=-0.3901, PF=0.0878
- Next-step controller now says: SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT. Primary command only PlanOnly: start_ws_collect_visible.ps1 -Hours 6 -PlanOnly. Long collect requires explicit user approval.

Верни final-report с разделами:
# Final Report
## Решение
Одно слово: approve / revise / block.
## Проверка
## Что важно дальше
## Запрещено
## Итог для пользователя
