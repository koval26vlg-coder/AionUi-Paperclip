# Отчет агента

## Дата и время

2026-06-21 22:32 +03

## Агент

Codex

## Исходный запрос пользователя

Активная цель: запустить и провести HH Resume Booster landing/concierge test на 14 дней с тремя офферами и последующим сравнением paid intent.

## Контекст перед началом

Fresh rehearsal guard уже был добавлен в launch helper, но visible monitor не показывал, свежая ли day-0 rehearsal metadata для текущего temporary public URL. При проверке обнаружилась несовместимость PowerShell версий: Windows PowerShell 5.1 видел fresh metadata, а PowerShell 7 показывал `missing`, потому что `ConvertFrom-Json` по-разному парсит `generatedAt`.

## План

1. Добавить fresh rehearsal status в `watch-hh-booster-test.ps1`.
2. Исправить timestamp parsing в monitor и launch helper.
3. Проверить одинаковое поведение в Windows PowerShell 5.1 и `pwsh`.
4. Убедиться, что `startedAt` не записан.

## Что сделано

- `watch-hh-booster-test.ps1` теперь принимает `-FreshRehearsalMinutes` с default `15`.
- Monitor показывает для temporary public URL:
  - `Rehearsal: fresh/stale/missing`;
  - age;
  - metadata path;
  - next action для rerun day-0 rehearsal before Start test, если metadata нет или она stale.
- В `watch-hh-booster-test.ps1` и `prepare-hh-booster-public-launch.ps1` добавлен robust timestamp parser:
  - если `generatedAt` уже `DateTime`, используется `ToUniversalTime()`;
  - иначе пробует `DateTimeOffset.Parse`;
  - fallback на `LastWriteTime` metadata-файла.
- Runbook `docs/experiments/hh-resume-booster-validation.md` обновлен.

## Измененные файлы

- `apps/aion-vision/scripts/watch-hh-booster-test.ps1`
- `apps/aion-vision/scripts/prepare-hh-booster-public-launch.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/tasks.md`
- `docs/current-context.md`
- `docs/agent-log/2026-06-21-2232-codex-hh-booster-monitor-fresh-rehearsal.md`

## Проверки

- Windows PowerShell 5.1 monitor на `https://eighty-boats-work.loca.lt` показал `Rehearsal: fresh`.
- `pwsh` monitor на том же URL показал `Rehearsal: fresh`.
- `prepare-hh-booster-public-launch.ps1 ... -PrintOnly` продолжает работать.
- `pwsh prepare-hh-booster-public-launch.ps1 ... -FreshRehearsalMinutes 1 -StartExperiment` заблокировал stale rehearsal и не записал `startedAt`.
- `hh_resume_booster_experiment_state.py status --json`: `startedAt=null`, `total_leads=0`.

## Решения

- Visible monitor должен быть источником launch readiness для оператора перед реальным стартом.
- Для temporary tunnel свежесть rehearsal должна быть видна в status screen, а не только скрыта внутри launch helper.

## Риски и ограничения

- Реальный 14-дневный сбор еще не начат.
- `https://eighty-boats-work.loca.lt` временный и может умереть.
- Даже fresh rehearsal не заменяет final prelaunch `Status: GO` после `StartExperiment` и launch manifest.

## Что должен проверить следующий агент

- Если пользователь готов начать сбор, rerun day-0 rehearsal с write-smoke, затем guarded launch в течение freshness window.
- После launch добиться prelaunch `Status: GO`, затем публиковать ссылки.
