# 2026-06-21 20:32 - Codex - HH Booster local server started

## Исходный запрос пользователя

Продолжить активную цель: запустить и провести 14-дневный landing/concierge test HH Resume Booster с тремя офферами и сравнением paid intent.

## Краткий план

1. Проверить, свободен ли порт `8787`.
2. Запустить production server в видимом PowerShell-окне.
3. Выполнить local preflight и write-smoke.
4. Зафиксировать текущий launch-state.

## Что было сделано

- Проверено, что `http://127.0.0.1:8787/` до запуска не отвечал, а `Get-NetTCPConnection -LocalPort 8787` не показывал слушателя.
- Запущен видимый Windows PowerShell с командой:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\start-hh-booster-test.ps1" -Port 8787 -SkipBuild
```

- Start process PID: `25120`.
- После старта `http://127.0.0.1:8787/` вернул HTTP `200`.
- Local preflight прошел:
  - `dist/index.html` exists;
  - HTTP root `200`;
  - `GET /api/hh-booster/leads` ok;
  - `GET /api/hh-booster/experiment` ok, `startedAt=not started`;
  - warning по public URL ожидаемый: внешний URL не задан.
- Write-smoke прошел:
  - временный QA lead принят;
  - временный QA lead удален cleanup;
  - `hh-booster-leads.jsonl` остался пустым.
- Data quality audit после cleanup: `ok=true`, `total_rows=0`, `errors=0`, `warnings=0`.

## Текущее состояние

- Local operator UI: `http://127.0.0.1:8787/#hh-booster`
- Local public form: `http://127.0.0.1:8787/#hh-booster-public`
- Server process: PID `25120`, alive at verification time.
- Leads JSONL: `D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl`, size `0`.
- Experiment state: `startedAt=null`.
- Launch manifest: отсутствует.
- Public URL: отсутствует.

## Измененные файлы

- `docs/agent-log/2026-06-21-2032-codex-hh-booster-local-server-started.md`

## Проверки

- HTTP readiness loop до `200`.
- `preflight-hh-booster-test.ps1 -BaseUrl "http://127.0.0.1:8787"` - ok.
- `preflight-hh-booster-test.ps1 -BaseUrl "http://127.0.0.1:8787" -WriteSmoke` - ok, cleanup done.
- `GET /api/hh-booster/leads?limit=10` - `ok=true`, `count=0`.
- `hh_resume_booster_data_quality.py ... --json` - clean.

## Риски и ограничения

- Это локальный запуск. Внешней аудитории нельзя отправлять `127.0.0.1`.
- `Старт теста` не нажат, поэтому 14-дневное окно еще не началось.
- Public tunnel/domain не создан.
- Launch manifest не сохранен, потому что его нужно сохранять после `Старт теста` и с реальным public URL.

## Что должен проверить следующий агент

- Открыть `http://127.0.0.1:8787/#hh-booster`.
- Нажать `Старт теста`, если пользователь готов начать 14-дневное окно.
- Создать реальный public URL в видимом терминале.
- Запустить `prepare-hh-booster-public-launch.ps1 -PublicBaseUrl "<REAL_URL>"` и добиться `Status: GO`.
