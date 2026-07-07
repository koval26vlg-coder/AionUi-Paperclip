# 2026-06-21 17:31 - Codex - HH Booster visible status monitor

## Исходный запрос пользователя

Продолжить активную цель: сделать landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack` и затем сравнить paid intent.

## Краткий план

- Проверить актуальные HH Booster файлы и метрики.
- Добавить безопасный daily/status monitor для server JSONL и experiment state.
- Проверить monitor на пустом и synthetic состоянии.
- Обновить runbook и общий контекст.

## Что было сделано

- Добавлен `apps/aion-vision/scripts/watch-hh-booster-test.ps1`.
- По умолчанию скрипт делает один read-only статус и завершается.
- Для видимого наблюдения есть `-Watch -IntervalSeconds 60`.
- Monitor показывает наличие `hh-booster-experiment.json`, наличие/размер/line count/last write `hh-booster-leads.jsonl`, gate progress, темп, by-offer paid intent, последние дни и next action.
- `apps/aion-vision/scripts/start-hh-booster-test.ps1` теперь печатает команду разового статуса и watch-mode рядом с daily metrics command.
- Runbook, `docs/current-context.md` и `docs/tasks.md` обновлены.

## Какие файлы были изменены

- `apps/aion-vision/scripts/watch-hh-booster-test.ps1`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-1731-codex-hh-booster-visible-status-monitor.md`

## Проверки

- PowerShell parser smoke: `parse-ok`.
- Missing-data smoke: monitor корректно сообщает, что JSONL и experiment state еще не созданы.
- Synthetic JSONL + experiment smoke: monitor показывает `Ready: yes`, когда все пороги искусственно выполнены.
- `start-hh-booster-test.ps1 -PrintOnly -Port 8787` печатает команды monitor.

## Риски и ограничения

- Monitor ничего не пишет и не заменяет реальный сбор данных.
- Реальный 14-дневный сбор и сравнение paid intent еще не проведены.
- Для внешней аудитории по-прежнему нужен публичный URL или tunnel через `-PublicBaseUrl`.
- Active-run gate в `trading_mvp` остается `RUNNING`; эта работа не трогала `trading_mvp`.

## Что должен проверить следующий агент

- После запуска production-сервиса выполнить:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\watch-hh-booster-test.ps1"
```

- Для видимого наблюдения:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\watch-hh-booster-test.ps1" -Watch -IntervalSeconds 60
```

- Когда появятся реальные заявки, сверить, что `started_at` не `n/a`, `decision_ready=false` до завершения 14 дней, а daily pace показывает честный остаток.
