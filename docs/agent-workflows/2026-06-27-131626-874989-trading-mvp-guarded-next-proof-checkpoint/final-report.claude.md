Проверка завершена. Все заявленные факты и артефакты подтверждены независимым чтением. Привожу финальное заключение L5.

## Что было сделано
- Прочитаны `brief.md`, `contract.json`, `events.jsonl` и все handoff L1→L4 рабочего процесса `2026-06-27-131626-...-trading-mvp-guarded-next-proof-checkpoint`.
- Независимо (только чтение) сверены с реальными файлами проекта `ZolotyayLopata` заявления L3/L4 об инженерных правках.
- Проверена цепочка решений gate: `funding_final_review_guard_stop_verify_20260627.json` → `trading_next_goal_step.ps1` → `start_ws_collect_visible.ps1 -PlanOnly`.
- Проверена логика early density guard и schema probe в WS-обёртке, а также readback-проверки в preflight и регресс-тест.

## На чем основан вывод
- **Guard-артефакт подтверждён:** `funding_final_review_guard_stop_verify_20260627.json` содержит `data_quality.accepted=false`, `metrics.min_rows_per_cycle=9` при `config.min_min_rows_per_cycle=20`, `ready_for_postprocess=false`, `verdict=wait_for_final_dataset`. Датасет — именно `funding_collect_7d_spotliq_visible_20260617_185732`. Совпадает с brief и фактами задачи.
- **Решение gate корректно:** `trading_next_goal_step.ps1:128` выдаёт `SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT` только внутри ветки `research_only_no_accepted_strategy` + `fundingBlockedBySwarm` без fee-evidence; `primary_command` = `... start_ws_collect_visible.ps1 -Hours 6 -PlanOnly`. Прямого пути к funding rank/backtest/postprocess из этой ветки нет.
- **Stale next-step нейтрализован:** в state выводятся `gate_postprocess_block`, `gate_raw_next_step_after_ready` (строки 183–185); preflight (`trading_edge_preflight.ps1:192–197`) падает в `fail`, если эти доказательства блока не сохранены.
- **WS-обёртка безопасна:** `start_ws_collect_visible.ps1:99` бросает исключение без `-ConfirmedLongRun` и без `-PlanOnly`; PlanOnly возвращает `would_start=false`, `requires_confirmed_long_run=true` (185–187).
- **Guards реально останавливают сбор:** schema probe (294–304) и early density (308–328) вызывают `Stop-Process -Force` и `break`; финальный статус становится `STOPPED_INCOMPLETE` со `stop_reason=schema_probe_failed`/`early_density_guard_failed` (345–360); `READY_FOR_POSTPROCESS` ставится только при отсутствии rejection и наличии манифеста.
- **Регресс-тест валиден:** `test_visible_ws_collect_wrapper.py` проверяет наличие всех нужных маркеров; грепом подтверждено, что эти маркеры присутствуют в обоих скриптах. Codex-репортинг `202 OK` правдоподобен (тест по сути читает текст файлов).

## Что получилось хорошо
- Stale funding-route защищён двумя независимыми слоями: gate readback + preflight regression — рассогласование выявится автоматически.
- Early density guard и schema probe экономят до 6 часов при явной деградации потока и ловят поломку схемы почти сразу.
- Все правки research-only: нет live orders, API-ключей, leverage/margin; фактический long-run требует и видимого терминала, и `-ConfirmedLongRun`.
- Handoff L1→L4 согласованы между собой, с brief и с events; искажения «испорченного телефона» не обнаружено.

## Что требует доработки
- **Полностью «мёртвый» поток:** schema probe требует `rawLineCount>0`, а early density срабатывает только на 60-й минуте. Если биржа не отдаёт ни строки, до 60 минут уйдёт впустую. L4 это осознанно зафиксировал, но перед реальным запуском стоит рассмотреть быстрый «zero-lines после N минут» abort (не блокер).
- **Пороги по умолчанию** `600 lines / 60 min / 10 lines/min` — минимальный sanity-порог, не доказательство качества. Перед фактическим collect пользователю надо осознанно подтвердить/поднять `EarlyDensityMinLinesPerMinute`.
- Early density основан на raw line count как proxy, не на качестве per-cycle/микроструктуры; финальная пригодность определяется только postprocess data-quality + OOS/walk-forward/stress.

## Какие есть риски
- Risk gate в контракте всё ещё `pending` (trading + long_running = true). Решение L5 = approve относится к **плану и инженерным правкам**, но НЕ авторизует запуск 6h collect — он по-прежнему требует отдельного явного подтверждения пользователя.
- `Stop-Process -Force` оставляет датасет в `STOPPED_INCOMPLETE` без манифеста — ожидаемое поведение, но downstream обязан трактовать это как «не готово», а не как пустой успех.
- Повторный dense collect снова может провалить quality gate; в этом случае ветку нужно честно признавать нежизнеспособной на текущих источниках, а не молча ослаблять пороги.

## Что нельзя потерять/исказить дальше
- `funding_collect_7d_spotliq_visible_20260617_185732` с `min_rows_per_cycle=9` остаётся **rejected**: никакого funding rank/backtest/paper-forward.
- Actual long run — только в видимом терминале/monitor и только после явного подтверждения пользователя и `-ConfirmedLongRun`.
- Replay/grid — только после guarded WS postprocess с `replay_allowed=true` и явным `ExpectedManifestPath`.
- High winrate сам по себе не acceptance: обязательны expectancy, net PnL after costs, PF, drawdown, sample size, liquidity/fill risk, OOS/walk-forward/stress.
- Запрет на live trading / API keys / leverage / margin как следующий шаг сохраняется.

## Решение
approve
