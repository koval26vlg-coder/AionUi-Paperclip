## Что было сделано
- Проведен независимый анализ L1-чекпоинта `trading_mvp` по результатам 7-дневного сбора данных по финансированию/базису в файле [funding_collect_7d_spotliq_visible_20260617_185732.jsonl](file:///C:/Users/koval/Documents/ZolotyayLopata/exports/trading-mvp/funding/funding_collect_7d_spotliq_visible_20260617_185732.jsonl).
- Проверены строгие результаты финального ревью в [funding_final_review_funding_collect_7d_spotliq_visible_20260617_185732_final_review_20260627_094801.json](file:///C:/Users/koval/Documents/ZolotyayLopata/exports/trading-mvp/funding/funding_final_review_funding_collect_7d_spotliq_visible_20260617_185732_final_review_20260627_094801.json) и диагностические результаты с расслабленными критериями качества в [funding_rank_funding_collect_7d_spotliq_visible_20260617_185732_relaxed_quality_diag_20260627_095113.json](file:///C:/Users/koval/Documents/ZolotyayLopata/exports/trading-mvp/funding/funding_rank_funding_collect_7d_spotliq_visible_20260617_185732_relaxed_quality_diag_20260627_095113.json).

## На чем основан вывод
1. Ветка переноса финансирования (funding carry branch) должна быть **отклонена** для перехода к paper-forward торговле, так как топовые рынки не показывают никакого торгового преимущества (edge).
2. Строгий блокировщик качества данных `min_rows_per_cycle` (фактическое значение 9 против требуемого порога 20) является **вторичной** проблемой. Первичная проблема — экономическая несостоятельность ветки: при полностью отключенных ограничениях качества в диагностическом запуске количество подходящих рынков равно нулю (`rank_eligible=0`), поскольку все они не проходят проверки по `expected_edge`, `risk_adjusted_edge`, `break_even` и `spot_liquidity`.
3. Рекомендованный следующий шаг — **отклонение ветки** (branch rejection) или переход к исследованию альтернативного семейства стратегий (**alternative edge family**).

## Что получилось хорошо
- Сбор данных отработал в полном объеме: завершено 2016 из 2016 циклов, собрано 50583 строки при относительно небольшом количестве ошибок (657).
- Диагностический режим с расслабленными критериями качества позволил изолировать экономическую проблему от технических неполадок сбора данных.

## Что требует доработки
- Экономическая модель стратегии funding carry: текущий уровень комиссий и ликвидности делает стратегию нерентабельной.
- Покрытие коллектора: необходимо разобраться, почему среднее количество строк на цикл (`min_rows_per_cycle = 9`) значительно ниже установленного порога качества (20).

## Какие есть риски
- Риск продолжения разработки и тестирования стратегий переноса финансирования (funding carry) при заведомо неблагоприятной структуре комиссий и недостаточной ликвидности.
- Риск пропустить другие прибыльные направления из-за концентрации на неэффективной ветке.

## Что нельзя потерять/исказить дальше
- Собранный 7-дневный датасет [funding_collect_7d_spotliq_visible_20260617_185732.jsonl](file:///C:/Users/koval/Documents/ZolotyayLopata/exports/trading-mvp/funding/funding_collect_7d_spotliq_visible_20260617_185732.jsonl) и его манифест [funding_collect_7d_spotliq_visible_20260617_185732.manifest.json](file:///C:/Users/koval/Documents/ZolotyayLopata/exports/trading-mvp/funding/funding_collect_7d_spotliq_visible_20260617_185732.manifest.json), которые могут быть использованы для оффлайн-исследований других стратегий.
- Строгий порог `min_rows_per_cycle >= 20` для прохождения финального ревью, предотвращающий ложные выводы на неполных данных.

## Решение
block
