# Agent Report

## Дата и время

2026-06-21 19:30 +03:00

## Агент

Codex

## Исходный запрос пользователя

Продолжить активную цель: подготовить и провести 14-дневный `HH Resume Booster` landing/concierge test с тремя офферами и сравнением paid intent.

## Краткий план

- Не поднимать публичный tunnel скрыто, потому что это открывает локальный сервер наружу.
- Добавить helper, который безопасно доводит публикацию до launch manifest и prelaunch GO/NO-GO.
- Подключить helper к стартовому скрипту и runbook.
- Проверить Windows PowerShell поведение.

## Что было сделано

- Добавлен `apps/aion-vision/scripts/prepare-hh-booster-public-launch.ps1`.
- Helper без `-PublicBaseUrl` печатает видимые варианты tunnel и возвращает `NO-GO`.
- Helper с реальным `-PublicBaseUrl` печатает/выполняет:
  - `tools/hh_resume_booster_launch_manifest.py --public-base-url ... --out ...`
  - `tools/hh_resume_booster_prelaunch_check.py --operator-base-url ... --public-base-url ...`
- Placeholder/test URL блокируются до записи manifest.
- `apps/aion-vision/scripts/start-hh-booster-test.ps1` теперь печатает helper-команду.
- Runbook `docs/experiments/hh-resume-booster-validation.md` дополнен helper-командами.

## Какие файлы были изменены

- `apps/aion-vision/scripts/prepare-hh-booster-public-launch.ps1`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-1930-codex-hh-booster-public-launch-helper.md`

## Проверки выполнены

- PowerShell parser для `prepare-hh-booster-public-launch.ps1`.
- Windows PowerShell 5.1: `prepare-hh-booster-public-launch.ps1 -PrintOnly` возвращает exit code `0`, печатает `NO-GO`, tunnel-варианты и команду rerun.
- Windows PowerShell 5.1: `prepare-hh-booster-public-launch.ps1 -PublicBaseUrl "https://example.test"` возвращает exit code `2` и блокирует placeholder.
- Windows PowerShell 5.1: `prepare-hh-booster-public-launch.ps1 -PublicBaseUrl "https://hh-booster.ngrok-free.app" -PrintOnly` печатает manifest/prelaunch команды и ничего не пишет.
- Windows PowerShell 5.1: `start-hh-booster-test.ps1 -PrintOnly` печатает `prepare-hh-booster-public-launch.ps1`.
- Проверено, что `apps/aion-vision/data/hh-booster-launch-manifest.md` не был записан тестами helper.

## Риски и ограничения

- Helper не запускает внешний tunnel сам. Это намеренно: tunnel должен запускаться пользователем в видимом терминале.
- Реальный 14-дневный сбор paid intent еще не начат и не завершен.
- Сейчас без реального public URL и `Старт теста` prelaunch остается `NO-GO`.

## Что должен проверить следующий агент

- Получить от пользователя разрешение/выбор способа публикации: реальный домен, cloudflared/ngrok/localtunnel/localhost.run.
- После появления real public URL выполнить helper с `-PublicBaseUrl`.
- Нажать `Старт теста` в операторской панели, сохранить launch manifest и пройти prelaunch GO/NO-GO.
