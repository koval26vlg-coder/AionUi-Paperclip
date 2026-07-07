## Что было сделано
Проведен аудит рекомендации уровня L1 (research review) с точки зрения технических и архитектурных ограничений этапа L2. Проверен механизм блокировки сбора данных фандинга (`funding_blocked_by_swarm=true`) и оценен риск несоответствия legacy-поля `visible_collect_command` в `tools/trading_goal_status.ps1` безопасному WS-пути. Определена необходимость выравнивания статуса и сформированы требования к верификационным тестам для Codex без проведения долгосрочных запусков.

## На чем основан вывод
- `funding_collect_7d_spotliq_visible_20260617_185732` заблокирован из-за низкого качества данных (`data_quality:min_min_rows_per_cycle`).
- Поле `visible_collect_command` в статусном скрипте `tools/trading_goal_status.ps1` при `funding_blocked_by_swarm=true` выдает команду на запуск старого сбора фандинга. Это противоречит Active Run Gate Rule и может спровоцировать ошибочный запуск.
- Шаг `trading_next_goal_step.ps1` корректно ведет к `start_ws_collect_visible.ps1 -Hours 6 -PlanOnly`. Следовательно, `tools/trading_goal_status.ps1` должен возвращать эту же безопасную/guard команду или статус `blocked/deprecated` при `funding_blocked_by_swarm=true`.

## Что получилось хорошо
- Логика блокировки фандинга по флагу `funding_blocked_by_swarm=true` надежно изолирует заблокированный датасет от процессов постобработки и бэктестинга.
- Использование режима `-PlanOnly` в `start_ws_collect_visible.ps1` исключает несанкционированные сетевые запросы и сбор без явного флага `-ConfirmedLongRun`.

## Что требует доработки
- В скрипте `tools/trading_goal_status.ps1` необходимо внедрить проверку флага `funding_blocked_by_swarm`. Если он равен `true`, значение `visible_collect_command` должно быть перенаправлено на безопасный WS-путь (`start_ws_collect_visible.ps1 -Hours 6 -PlanOnly`) или помечено как заблокированное/устаревшее.
- Требуется провести верификационные тесты:
  1. *Тест 1 (Swarm Blocked Status Test)*: Убедиться, что при `funding_blocked_by_swarm=true` вывод `visible_collect_command` переключается на безопасную WS-команду или возвращает статус блокировки.
  2. *Тест 2 (Integration Consistency Test)*: Проверить, что вывод `trading_next_goal_step.ps1` согласован со значением `visible_collect_command` в `tools/trading_goal_status.ps1`.
  3. *Тест 3 (No Side-Effects Test)*: Убедиться, что запуск статусных скриптов не приводит к фактическому сетевому сбору данных.

## Какие есть риски
- Риск человеческой или системной ошибки, если статус-скрипт выдаст неактуальную/опасную команду сбора фандинга, а автоматизация выполнит ее без guard-проверки.
- Риск нарушения Visible Run Rule при отсутствии синхронизации выходов утилит `trading_goal_status.ps1` и `trading_next_goal_step.ps1`.

## Что нельзя потерять/исказить дальше
- Ограничение на проведение транзакций (research-only, отсутствие API-ключей, плеча и реальных сделок).
- Запрет на запуск любых collectors/backtests/replay/long runs без явного подтверждения пользователя и параметра `-ConfirmedLongRun`.
- Исходную причину блокировки фандинга (`data_quality:min_min_rows_per_cycle`).

## Решение
approve
