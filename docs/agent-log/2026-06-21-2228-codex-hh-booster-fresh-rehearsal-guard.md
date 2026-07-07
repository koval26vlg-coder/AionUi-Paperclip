# Отчет агента

## Дата и время

2026-06-21 22:28 +03

## Агент

Codex

## Исходный запрос пользователя

Активная цель: довести HH Resume Booster landing/concierge test до реального 14-дневного запуска и затем сравнить paid intent по трем офферам.

## Контекст перед началом

На 22:20 была успешная day-0 rehearsal с временным `loca.lt` URL `https://eighty-boats-work.loca.lt`, но такой URL может быстро протухнуть. Нужно не дать helper-у записать `startedAt`, если перед запуском нет свежей успешной rehearsal для того же public URL.

## План

1. Проверить текущий state и live runtime.
2. Добавить guard в `prepare-hh-booster-public-launch.ps1`.
3. Обновить publish kit, чтобы команда запуска явно показывала fresh rehearsal check.
4. Проверить guard без записи `startedAt`.
5. Зафиксировать результат в общей памяти.

## Что сделано

- В `apps/aion-vision/scripts/prepare-hh-booster-public-launch.ps1` добавлены:
  - `-FreshRehearsalMinutes` с default `15`;
  - `-SkipFreshRehearsalCheck` для ручного осознанного bypass;
  - `Is-EphemeralTunnelUrl`;
  - `Get-FreshRehearsalMetadata`.
- При `-StartExperiment` на временных tunnel hosts helper теперь требует metadata `hh-booster-day0-rehearsal-*.json` для того же `PublicBaseUrl` со статусом `ready_for_launch`, без `blockingFailures` и не старше заданного окна.
- `tools/hh_resume_booster_publish_kit.py` обновлен: one-command launch теперь явно включает `-FreshRehearsalMinutes 15`.
- Текущий `apps/aion-vision/data/hh-booster-publish-kit.md` перегенерирован под `https://eighty-boats-work.loca.lt`.

## Измененные файлы

- `apps/aion-vision/scripts/prepare-hh-booster-public-launch.ps1`
- `tools/hh_resume_booster_publish_kit.py`
- `apps/aion-vision/data/hh-booster-publish-kit.md`
- `docs/tasks.md`
- `docs/current-context.md`
- `docs/agent-log/2026-06-21-2228-codex-hh-booster-fresh-rehearsal-guard.md`

## Проверки

- Windows PowerShell 5.1 `prepare-hh-booster-public-launch.ps1 ... -PrintOnly` прошел.
- `pwsh prepare-hh-booster-public-launch.ps1 ... -PrintOnly` прошел.
- `python -m py_compile tools/hh_resume_booster_publish_kit.py` прошел.
- Fake URL test: `https://fresh-missing.loca.lt -StartExperiment -SkipServerCheck` вернул `NO-GO` из-за отсутствия fresh rehearsal metadata; experiment не стартовал.
- Stale window test: текущий `https://eighty-boats-work.loca.lt -FreshRehearsalMinutes 1 -StartExperiment` вернул `NO-GO`; experiment не стартовал.
- `hh_resume_booster_experiment_state.py status --json`: `startedAt=null`, `total_leads=0`.

## Решения

- Для временных tunnels реальный `-StartExperiment` должен быть близко по времени к successful day-0 rehearsal.
- Default freshness window: 15 минут.
- Bypass есть, но намеренно явный: `-SkipFreshRehearsalCheck`.

## Риски и ограничения

- Реальный 14-дневный сбор все еще не начат.
- `https://eighty-boats-work.loca.lt` временный и может умереть.
- Даже после fresh rehearsal перед публикацией ссылок нужен final prelaunch `Status: GO`.

## Что должен проверить следующий агент

- Если пользователь готов начать сбор, сначала при необходимости повторить:
  `start-hh-booster-day0-rehearsal.ps1 -PublicBaseUrl "https://eighty-boats-work.loca.lt" -SkipBuild -WriteSmoke`
- Затем выполнить guarded launch с `-FreshRehearsalMinutes 15`.
- Не публиковать ссылки до prelaunch `Status: GO`.
