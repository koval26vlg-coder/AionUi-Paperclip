# 2026-06-21 17:21 - Codex - HH Booster visible launch script

## Исходный запрос пользователя

Продолжить активную цель: сделать landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack`, затем сравнить paid intent.

## Краткий план

- Проверить текущий HH Booster и runbook.
- Добавить видимый production launch script для 14-дневного теста.
- Проверить dry-run, lint/build и команду метрик.
- Обновить общий контекст и список задач.

## Что было сделано

- Добавлен `apps/aion-vision/scripts/start-hh-booster-test.ps1`.
- Скрипт печатает операторскую ссылку, публичную форму, канальные URL, путь к `apps/aion-vision/data/hh-booster-leads.jsonl`, команду ежедневных метрик и tunnel-подсказки.
- Скрипт не запускает public tunnel скрыто и не уводит сервер в фон; production-сервис стартует в текущем терминале и останавливается через `Ctrl+C`.
- В runbook `docs/experiments/hh-resume-booster-validation.md` добавлена основная команда запуска и правило `-PublicBaseUrl` для внешней аудитории.
- Обновлены `docs/current-context.md` и `docs/tasks.md`.

## Какие файлы были изменены

- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-1721-codex-hh-booster-visible-launch-script.md`

## Проверки

- `pwsh -NoProfile -ExecutionPolicy Bypass -File apps/aion-vision/scripts/start-hh-booster-test.ps1 -PrintOnly -PublicBaseUrl "https://example.test" -Port 8787`
- PowerShell parser smoke: `parse-ok`
- `npm run lint`
- `npm run build`
- CLI metrics missing-JSONL smoke: `jsonl-missing-ok`

## Риски и ограничения

- Реальный 14-дневный сбор данных еще не проведен, цель не завершена.
- На машине не найден `cloudflared`, `ngrok`, `lt` или `localtunnel`; для удаленной аудитории нужен внешний домен/tunnel, переданный через `-PublicBaseUrl`.
- Active-run gate в `trading_mvp` остается `RUNNING`, но эта работа не запускала collectors/postprocess и не трогала `trading_mvp`.

## Что должен проверить следующий агент

- Запустить тест в видимом терминале командой:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\start-hh-booster-test.ps1" -Port 8787
```

- Если нужен внешний сбор, сначала поднять публичный URL/tunnel вручную и перезапустить script с `-PublicBaseUrl`.
- После старта теста ежедневно считать `apps/aion-vision/data/hh-booster-leads.jsonl` через `tools/hh_resume_booster_metrics.py`.
