Проверить 7d funding/basis результат trading_mvp как независимый Рой-checkpoint.

Контекст:
- Репозиторий: C:\Users\koval\Documents\ZolotyayLopata
- Goal: найти/доказать/отбросить high-winrate edge без live orders/API keys/leverage.
- Dataset: exports/trading-mvp/funding/funding_collect_7d_spotliq_visible_20260617_185732.jsonl
- Manifest: exports/trading-mvp/funding/funding_collect_7d_spotliq_visible_20260617_185732.manifest.json
- Gate: READY_FOR_POSTPROCESS, final=true, 2016/2016 cycles, 50583 rows, 657 errors.
- Strict final-review artifact: exports/trading-mvp/funding/funding_final_review_funding_collect_7d_spotliq_visible_20260617_185732_final_review_20260627_094801.json
- Strict final-review blocked on data_quality:min_min_rows_per_cycle: min_rows_per_cycle=9 vs strict threshold=20.
- Diagnostic relaxed rank artifact: exports/trading-mvp/funding/funding_rank_funding_collect_7d_spotliq_visible_20260617_185732_relaxed_quality_diag_20260627_095113.json
- Diagnostic rank result: rank_eligible=0; top markets fail expected_edge/risk_adjusted_edge/break_even/spot_liquidity.

Задача Роя:
1. Независимо проверить, корректен ли текущий вывод: funding carry branch не принят для paper-forward.
2. Проверить, является ли strict quality blocker реальной причиной остановки или вторичной проблемой, учитывая rank_eligible=0 в relaxed diagnostic.
3. Предложить следующий инженерный шаг: collector coverage fix, maker/fee-tier economics, alternative edge family, or branch rejection.
4. Не предлагать live trading, API keys, leverage, margin or investment advice.
5. Если лимиты агентов не позволяют выполнить workflow, зафиксировать swarm_limited; Codex продолжит вручную.
