# 2026-06-21 17:42 - Codex - HH Booster launch preflight

## Исходный запрос пользователя

Продолжить активную цель: сделать landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack` и затем сравнить paid intent.

## Краткий план

- Проверить текущие HH Booster запускатели и API.
- Добавить preflight script для проверки production-сервера перед раздачей ссылок.
- Проверить offline и running-safe сценарии.
- Обновить runbook и общий контекст.

## Что было сделано

- Добавлен `apps/aion-vision/scripts/preflight-hh-booster-test.ps1`.
- Скрипт проверяет `dist/index.html`, HTTP root, `GET /api/hh-booster/leads`, `GET /api/hh-booster/experiment`, public URL risk/reachability.
- По умолчанию preflight ничего не пишет.
- Опциональный `-WriteSmoke` отправляет временную QA-заявку и очищает ее через `tools/hh_resume_booster_data_admin.py` с backup.
- `apps/aion-vision/scripts/start-hh-booster-test.ps1` теперь печатает preflight команды после старта сервера.
- Runbook, `docs/current-context.md` и `docs/tasks.md` обновлены.

## Какие файлы были изменены

- `apps/aion-vision/scripts/preflight-hh-booster-test.ps1`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-1742-codex-hh-booster-launch-preflight.md`

## Проверки

- PowerShell parser smoke: `parse-ok`.
- Offline smoke against `http://127.0.0.1:9`: `ok=false`, expected HTTP/API failures, no writes.
- In-process server read-only smoke: `read_ok=true`, exit `0`.
- In-process server write-smoke: `write_ok=true`, `write_smoke_post:pass`, `write_smoke_cleanup:pass`, `remaining_after_cleanup=0`.

## Риски и ограничения

- Реальный 14-дневный сбор данных еще не проведен, цель не завершена.
- `-WriteSmoke` все равно пишет временную QA-заявку; использовать только перед запуском, когда понятно, что это тест.
- Если preflight проверяет удаленный публичный URL, local JSONL cleanup сработает только для локального server data path.
- Active-run gate в `trading_mvp` остается `RUNNING`; эта работа не трогала `trading_mvp`.

## Что должен проверить следующий агент

- После запуска сервера выполнить:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\preflight-hh-booster-test.ps1" -BaseUrl "http://127.0.0.1:8787"
```

- Если нужен полный intake smoke перед раздачей:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\preflight-hh-booster-test.ps1" -BaseUrl "http://127.0.0.1:8787" -WriteSmoke
```
