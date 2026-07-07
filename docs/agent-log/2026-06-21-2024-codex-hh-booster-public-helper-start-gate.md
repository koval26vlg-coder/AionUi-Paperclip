# 2026-06-21 20:24 - Codex - HH Booster public helper start gate

## Исходный запрос пользователя

Продолжить активную цель: подготовить реальный 14-дневный landing/concierge test HH Resume Booster с тремя офферами и сравнением paid intent.

## Краткий план

1. Проверить, не может ли public launch helper записать launch manifest до старта 14-дневного окна.
2. Заблокировать запись stale manifest при пустом `startedAt`.
3. Проверить helper в Windows PowerShell 5.1.
4. Обновить runbook и задачи.

## Что было сделано

- Найден зазор: `prepare-hh-booster-public-launch.ps1` с реальным `-PublicBaseUrl` сначала писал `hh-booster-launch-manifest.md`, а уже потом запускал prelaunch GO/NO-GO. Если `startedAt` пустой, это могло оставить manifest с незапущенным experiment state.
- Helper обновлен:
  - добавлены явные `$jsonlPath` и `$experimentPath`;
  - printed commands теперь используют explicit `--state` и `--data`;
  - non-PrintOnly перед записью manifest вызывает `hh_resume_booster_experiment_state.py --state ... --data ... status --json`;
  - если `startedAt` пустой, helper печатает `NO-GO`, не пишет manifest и возвращает exit `2`.
- Файл helper перекодирован/сохранен с UTF-8 BOM для Windows PowerShell 5.1.
- Runbook `docs/experiments/hh-resume-booster-validation.md` обновлен: helper сохраняет manifest только после старта experiment.
- `docs/tasks.md` обновлен записью о завершенном guard.

## Измененные файлы

- `apps/aion-vision/scripts/prepare-hh-booster-public-launch.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-2024-codex-hh-booster-public-helper-start-gate.md`

## Проверки

- Windows PowerShell 5.1 `prepare-hh-booster-public-launch.ps1 -PublicBaseUrl "https://hh-booster.ngrok-free.app" -SkipServerCheck -PrintOnly`:
  - печатает experiment path;
  - печатает status command;
  - печатает explicit `--state`;
  - не выполняет manifest/prelaunch.
- Windows PowerShell 5.1 non-PrintOnly с тем же URL при текущем `startedAt=null`:
  - `exit_code=2`;
  - `NO-GO: experiment is not started`;
  - `Launch manifest was not written`;
  - `hh-booster-launch-manifest.md` не создан.
- BOM check: первые байты `EF BB BF`.

## Риски и ограничения

- Реальный 14-дневный тест еще не стартовал.
- `https://hh-booster.ngrok-free.app` использовался как URL правильной формы для smoke; реальный tunnel/domain не подтвержден.
- Следующий запуск helper после `Старт теста` должен выполняться уже с живым production server и без `--skip-server-check`.

## Что должен проверить следующий агент

- После появления реального public URL: запустить production server видимо, нажать `Старт теста`, затем выполнить helper без `--skip-server-check`.
- Убедиться, что saved manifest содержит ненулевой `started_at` и prelaunch возвращает `Status: GO`.
