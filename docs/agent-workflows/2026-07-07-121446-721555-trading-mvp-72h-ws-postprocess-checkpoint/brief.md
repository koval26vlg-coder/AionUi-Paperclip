Цель trading_mvp: найти, доказать или честно отбросить рабочий high-winrate / positive-expectancy trading edge для non-Binance markets через данные, backtest, OOS/walk-forward, stress, economics и paper-forward gates. Research-only: no live orders, no API keys, no leverage/margin, no investment advice.

Текущий checkpoint: завершен durable segmented 72h WS collect.
Run id: ws_durable_72h_20260704_000015
Manifest: C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\raw-durable\ws_durable_72h_20260704_000015\ws_collect_ws_durable_72h_20260704_000015.json
Gate: READY_FOR_POSTPROCESS
Manifest summary: schema=ws_collect_stitched_v1, completed=true, final=true, stop_condition=duration_sec, requested_duration_sec=259200, actual_duration_sec=259199.8, segments_total=24, segments_with_manifest=24, segments_incomplete=0, total_events=76011803, errors_count=0.

История: segment 20 падал из-за OSError [Errno 28] No space left on device. После освобождения места был выполнен visible resume с явными -TotalSec 259200 -SegmentSec 10800; итоговый stitched manifest final=true. Не использовать старую неудачную resume-попытку с default TotalSec=7200 как финальное состояние.

Задача Роя: независимо проверить checkpoint и дать handoff для следующего шага: guarded ws-postprocess по completed manifest, затем replay-validation PlanOnly и только после replay_allowed=true/quality accepted переход к replay/grid. Проверить риски: диск/размер данных, durable manifest consistency, inactive stale monitor, segment completeness, archived incomplete segment handling, whether postprocess should include/ignore archived seg_020_incomplete, and whether expected quality gate thresholds are appropriate for 72h dataset. Не запускать live orders, не трогать API keys, не давать инвестсовет.
