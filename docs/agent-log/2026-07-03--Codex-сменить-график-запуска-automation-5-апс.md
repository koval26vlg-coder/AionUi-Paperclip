# Codex — 2026-07-03

## Запрос
Сменить график запуска automation-5 АПС на режим по запросу.

## Результат
automation-5 (АПС) переведена в status=PAUSED через automation_update. Автоматические heartbeat-запуски отключены; запуск остается ручным по прямому запросу пользователя в этом чате.

## Изменённые файлы
- C:\Users\koval\Documents\ОК.ру\docs\agent-log\2026-07-03-aps-schedule-on-request.md
- C:\Users\koval\.codex\automations\automation-5\automation.toml

## Риски и ограничения
rrule сохранен как историческое расписание, но при status=PAUSED не должен запускаться автоматически.

## Что следующему агенту
При ручном запросе запустить текущий маршрут automation-5: SML -> preflight -> run_sync_with_env.ps1 -Write -> dry-run -> compact audit -> лог/SML.
