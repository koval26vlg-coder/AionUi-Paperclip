# Отчет агента: HH Resume Booster public rehearsal

Дата и время: 2026-06-21 20:40 +03:00

Агент: Codex

## Исходный запрос пользователя

Продолжать активную цель: подготовить landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack`, сравнить paid intent и понять, оставлять ли аватарку как лид-магнит или делать модулем большого продукта.

## Краткий план

- Подтянуть Aion SML-контекст и проверить active-run gate.
- Проверить живы ли старые HH production server и tunnel.
- Перезапустить server и tunnel видимо, если они остановлены.
- Прогнать preflight/prelaunch/data-quality и не запускать 14-дневное окно без готовности к публикации.
- Зафиксировать состояние в памяти проекта.

## Что было сделано

- SML bootstrap выполнен по теме HH booster landing/concierge test.
- Active-run gate показывает `RUNNING` для отдельного `trading_mvp` collector; trading не трогался.
- Старые PID `25120` и `30948` оказались остановлены.
- Запущен новый HH production server в видимом PowerShell-окне:
  - PID: `28024`
  - URL: `http://127.0.0.1:8787/#hh-booster`
- Запущен новый public localtunnel в видимом PowerShell-окне:
  - PID: `4380`
  - URL: `https://huge-moons-fail.loca.lt/#hh-booster-public`
  - лог: `apps/aion-vision/data/hh-booster-public-tunnel-20260621-203648.log`
- Усилен preflight/prelaunch guard:
  - `preflight-hh-booster-test.ps1` теперь печатает public form на внешнем host при `-PublicBaseUrl`;
  - проверяет public API endpoints;
  - блокирует localtunnel interstitial/password page;
  - `hh_resume_booster_prelaunch_check.py` делает те же public HTTP/API проверки при `--check-public-http`.

## Измененные файлы

- `apps/aion-vision/scripts/preflight-hh-booster-test.ps1`
- `tools/hh_resume_booster_prelaunch_check.py`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-2040-codex-hh-booster-public-tunnel-prelaunch.md`

## Проверки

- `py_compile tools/hh_resume_booster_prelaunch_check.py` прошел.
- Local server/API:
  - `GET http://127.0.0.1:8787/#hh-booster` вернул `200`;
  - `GET /api/hh-booster/leads` вернул `200`;
  - `GET /api/hh-booster/experiment` вернул `startedAt=null`.
- Public preflight:
  - `https://huge-moons-fail.loca.lt` вернул app shell;
  - public `GET /api/hh-booster/leads` прошел;
  - public `GET /api/hh-booster/experiment` прошел;
  - `0` fail, `0` warnings.
- Public write-smoke:
  - временная QA-заявка принята через public tunnel;
  - cleanup удалил ее из локального JSONL с backup.
- Data quality:
  - `rows=0`, `errors=0`, `warnings=0`.
- Watch:
  - `Public URL: ready`;
  - `Started: no`;
  - `Manifest: missing`.
- Prelaunch GO/NO-GO:
  - ожидаемо `NO-GO` по двум пунктам: `experiment_started` и `launch_manifest`.

## Риски и ограничения

- 14-дневное окно не стартовало: `startedAt=null`.
- Launch manifest не создан намеренно: helper должен писать его только после старта experiment.
- Public localtunnel временный; URL может измениться после перезапуска tunnel.
- Не публиковать candidate links, пока prelaunch не вернет `Status: GO`.

## Что должен проверить следующий агент

- Если пользователь готов реально начать сбор, открыть `http://127.0.0.1:8787/#hh-booster`, нажать `Старт теста`, затем выполнить `prepare-hh-booster-public-launch.ps1 -PublicBaseUrl "https://huge-moons-fail.loca.lt"`.
- После manifest снова запустить `hh_resume_booster_prelaunch_check.py --operator-base-url "http://127.0.0.1:8787" --public-base-url "https://huge-moons-fail.loca.lt" --check-public-http`.
- Только при `Status: GO` публиковать ссылки кандидатам.
