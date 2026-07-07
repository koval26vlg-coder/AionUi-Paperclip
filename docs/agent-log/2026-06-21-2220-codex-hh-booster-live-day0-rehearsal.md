# Отчет агента

## Дата и время

2026-06-21 22:20 +03

## Агент

Codex

## Исходный запрос пользователя

Активная цель: сделать 14-дневный HH Resume Booster landing/concierge test с тремя офферами (`avatar-only`, `full resume audit`, `vacancy response pack`) и затем сравнить paid intent.

## Контекст перед началом

До этого был подготовлен safe day-0 rehearsal launcher, но реальный 14-дневный тест не был начат: `startedAt=null`, лидов `0`, живого public URL не было. Следующий безопасный шаг — выполнить rehearsal без старта таймера.

## План

1. Проверить текущий experiment state и локальный порт.
2. Запустить day-0 rehearsal через видимый launcher.
3. Исправить обнаруженные wrapper/runtime ошибки.
4. Получить live public URL и readiness state.
5. Зафиксировать контекст для следующего шага.

## Что сделано

- Запущен `start-hh-booster-day0-rehearsal.ps1 -SkipBuild -WriteSmoke`.
- Первый auto-run поднял server PID `12736` и tunnel PID `27872`, но wrapper упал на Windows PowerShell 5.1 array splatting при передаче `PublicBaseUrl` в preflight.
- Исправлен `start-hh-booster-day0-rehearsal.ps1`:
  - вызов `preflight-hh-booster-test.ps1` переведен с array splatting на hashtable splatting;
  - failure path теперь пишет metadata перед выходом на preflight/publish-kit ошибках;
  - exit code сохраняется до записи metadata.
- Нестабильный tunnel `https://mighty-foxes-see.loca.lt` зафиксирован как runtime failure; metadata `apps/aion-vision/data/hh-booster-day0-rehearsal-20260621-221734.json`.
- Запущена повторная auto-rehearsal, которая дала новый URL `https://eighty-boats-work.loca.lt/#hh-booster-public`.
- Старый broken tunnel PID `27872` остановлен; живы server PID `12736` и новый tunnel PID `31096`.

## Измененные файлы

- `apps/aion-vision/scripts/start-hh-booster-day0-rehearsal.ps1`
- `apps/aion-vision/data/hh-booster-publish-kit.md`
- `apps/aion-vision/data/hh-booster-day0-rehearsal-20260621-221734.json`
- `apps/aion-vision/data/hh-booster-day0-rehearsal-20260621-221958.json`
- `docs/tasks.md`
- `docs/current-context.md`
- `docs/agent-log/2026-06-21-2220-codex-hh-booster-live-day0-rehearsal.md`

## Проверки

- Manual preflight на `https://mighty-foxes-see.loca.lt`: сначала проходил, затем начал timeout на public API.
- `start-hh-booster-day0-rehearsal.ps1 -PublicBaseUrl https://mighty-foxes-see.loca.lt -SkipBuild` после патча дошел до preflight и записал failure metadata при timeout.
- `start-hh-booster-day0-rehearsal.ps1 -SkipBuild -WriteSmoke -TimeoutSeconds 120` прошел успешно с новым URL `https://eighty-boats-work.loca.lt`.
- Public write-smoke принял временный QA lead и удалил его cleanup.
- `hh_resume_booster_experiment_state.py status --json`: `startedAt=null`, `total_leads=0`.
- `hh_resume_booster_prelaunch_check.py --operator-base-url http://127.0.0.1:8787 --public-base-url https://eighty-boats-work.loca.lt --check-public-http --json`: `NO-GO`, `failed=2`, `warnings=1`.

## Решения

- Текущий live rehearsal URL: `https://eighty-boats-work.loca.lt/#hh-booster-public`.
- Его можно использовать только после явного guarded start и повторного prelaunch, потому что это temporary tunnel.
- `https://mighty-foxes-see.loca.lt` не использовать: public API стал timeout.

## Риски и ограничения

- Реальный 14-дневный тест все еще не начат: `startedAt=null`.
- Launch manifest отсутствует, это штатный blocker до старта.
- Public URL временный (`*.loca.lt`), поэтому его нужно перепроверить прямо перед публикацией.
- Если нужен стабильный 14-дневный тест без смены ссылок, лучше заменить localtunnel на стабильный домен/reverse proxy.

## Что должен проверить следующий агент

- Если пользователь готов начать сбор, выполнить guarded launch:
  `& "D:\AionUi-Paperclip\apps\aion-vision\scripts\prepare-hh-booster-public-launch.ps1" -PublicBaseUrl "https://eighty-boats-work.loca.lt" -OperatorBaseUrl "http://127.0.0.1:8787" -CheckPublicHttp -StartExperiment`
- После старта сохранить/проверить launch manifest и добиться prelaunch `Status: GO`.
- Не публиковать candidate links, пока `experiment_started` и `launch_manifest` не пройдены.
