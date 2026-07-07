## Что было сделано

В `tools/trading_goal_status.ps1` и `tools/trading_next_goal_step.ps1` устранена ситуация, при которой легаси-алиас `visible_collect_command` указывал на funding-сбор, пока `funding_blocked_by_swarm=true`. Добавлены явные поля `visible_collect_command_legacy_resolution` и `visible_collect_legacy_resolution` с маркером `redirected_to_ws_collect_because_funding_blocked_by_swarm`. Funding-команды сохранены как отдельные non-primary поля (`funding_visible_collect_command`, `funding_visible_collect_after_approval`). Добавлен тест `test_visible_ws_collect_wrapper.py`.

## На чём основан вывод

- L1–L4 Antigravity/Codex цепочка: все уровни выдали `approve` с одинаковой мотивацией — risk — это был живой alias на заблокированный путь.
- Верификация выводов `trading_goal_status.ps1 -Json`, `trading_next_goal_step.ps1 -Json`, `trading_edge_preflight.ps1 -Json` и `start_ws_collect_visible.ps1 -Hours 6 -PlanOnly` даёт согласованный результат.
- 204 теста пройдено, `fail_count=0`, `warn_count=0`.

## Что получилось хорошо

- Легаси-алиас теперь детерминированно resolves в WS-коллект, а не в заблокированный funding путь — источник путаницы устранён.
- Funding-команды не удалены: они доступны как явные non-primary поля, что позволяет при необходимости разблокировать ветку без правок кода.
- `start_ws_collect_visible.ps1 -PlanOnly` подтверждает, что реальный запуск по-прежнему требует `-ConfirmedLongRun` — gate не ослаблен.
- Preflight остаётся на `ok=true` без новых предупреждений.

## Что требует доработки

- Нет критических gap. Единственное условие перехода к реальному 6h WS collect — явное подтверждение пользователя (`-ConfirmedLongRun`) с видимым терминалом/монитором. Это не баг реализации, а намеренный policy-барьер.

## Какие есть риски

- **Минимальные процедурные.** Если `funding_blocked_by_swarm` будет снят без прохождения `data_quality:min_min_rows_per_cycle` (min_rows_per_cycle=9), легаси-алиас автоматически вернётся к funding-пути — это ожидаемо, но нужно отслеживать при любом ручном изменении gate.
- Реальных торговых рисков нет: ни ордеров, ни ключей API, ни плеча в цепочке нет.

## Что нельзя потерять/исказить дальше

- Маркер `funding_blocked_by_swarm=true` должен остаться в gate до явного прохождения `data_quality` guard.
- `funding_visible_collect_command` должен сохраняться как отдельное поле — это единственный путь вернуть funding ветку без хардкодинга.
- `requires_confirmed_long_run=true` в `start_ws_collect_visible.ps1` не трогать без явного решения уровня L2+.

## Решение

**approve**
