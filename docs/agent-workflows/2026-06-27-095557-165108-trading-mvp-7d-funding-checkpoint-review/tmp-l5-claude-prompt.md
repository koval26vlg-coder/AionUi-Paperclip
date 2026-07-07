Ты Claude Code в L5 финальной инстанции workflow Роя. Ответь по-русски, как независимый technical verifier/final decision writer. Не запускай команды, не редактируй файлы, не давай инвестсовет.

Задача: проверить связность L1-L4 и сформировать final-report для пользователя.

Контекст:
- Проект: C:\Users\koval\Documents\ZolotyayLopata / trading_mvp.
- Цель: найти, доказать или честно отбросить high-winrate trading edge через данные/backtest/OOS/walk-forward/stress/economics/paper-forward gates.
- Ограничения: no live orders, no API keys, no leverage/margin, no investment advice, no hidden/background long runs, no new channel/P2P/off-ramp analysis.
- Active gate: READY_FOR_POSTPROCESS; 2016/2016 cycles, 50583 rows, 657 errors.
- Funding carry: blocked by 7d evidence and Рой L1/L2; relaxed diagnostic rank_eligible=0; no non-secret fee-tier evidence.
- L3 selected next research branch only: spot_maker_liquidity_sweep_reversal_event_quality. Not a strategy.
- L4 added read-only gate: tools/sweep_reversal_acceptance_gate.ps1.
- Gate artifact: exports/trading-mvp/analysis/sweep_reversal_acceptance_gate_20260627.json.
- Gate result: accepted=false; decision=SWEEP_REVERSAL_RESEARCH_NOT_ACCEPTED_NEEDS_INDEPENDENT_DATA; fail_count=14; warn_count=0.
- Key failures: target_before_stop_rate=0.367 < 0.60; false_sweep_rate=0.741 > 0.50; avg favorable 18.15 bps vs adverse abs 20.04 bps; liquidity_sweep_reversal_v2 maker 10 trades, 10% winrate, net_pnl=-0.3901, PF=0.0878; older positive slices have only 2-3 trades; OOS/walk-forward/stress missing.
- Verification: trading_edge_preflight ok=true fail_count=0 warn_count=0; branch selector and next-goal/status controllers now expose sweep_reversal_acceptance_gate command.

Нужно выдать final-report с разделами:
1. Итоговое решение
2. Почему это решение корректно
3. Что сейчас разрешено
4. Что запрещено
5. Следующий правильный шаг

Решение должно быть: approve L4 conclusion, but block paper/live; continue research-only with OOS/walk-forward/stress tooling before any visible user-approved long collect.
