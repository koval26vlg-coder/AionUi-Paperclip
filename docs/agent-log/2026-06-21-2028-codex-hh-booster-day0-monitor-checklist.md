# 2026-06-21 20:28 - Codex - HH Booster day-0 monitor checklist

## Исходный запрос пользователя

Продолжить активную цель: подготовить и провести 14-дневный landing/concierge test HH Resume Booster с тремя офферами и сравнением paid intent.

## Краткий план

1. Проверить, достаточно ли visible monitor показывает launch blockers до публикации ссылок.
2. Расширить monitor day-0 checklist без сетевых вызовов и без записей.
3. Синхронизировать start script и runbook.
4. Прогнать Windows PowerShell smoke.

## Что было сделано

- `apps/aion-vision/scripts/watch-hh-booster-test.ps1` получил параметры:
  - `-ManifestPath`;
  - `-OperatorBaseUrl`;
  - `-PublicBaseUrl`.
- Monitor теперь показывает:
  - operator/public links;
  - наличие `hh-booster-launch-manifest.md`;
  - готовность public URL: `missing`, `not ready`, `ready`;
  - нажата ли кнопка `Старт теста` (`startedAt`);
  - launch checklist и следующий безопасный шаг.
- `apps/aion-vision/scripts/start-hh-booster-test.ps1` теперь печатает monitor/watch команды с `-OperatorBaseUrl` и `-PublicBaseUrl`, если публичный URL задан.
- `docs/experiments/hh-resume-booster-validation.md` обновлен: описан monitor с public URL и новые пункты day-0 checklist.
- `docs/tasks.md` обновлен записью о завершенном monitor-checklist слое.

## Измененные файлы

- `apps/aion-vision/scripts/watch-hh-booster-test.ps1`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-2028-codex-hh-booster-day0-monitor-checklist.md`

## Проверки

- Windows PowerShell 5.1 `watch-hh-booster-test.ps1` без URL:
  - `Launch checklist` есть;
  - `Public URL : missing`;
  - `Manifest : missing`;
  - next action указывает нажать `Start test`.
- Windows PowerShell 5.1 `watch-hh-booster-test.ps1 -PublicBaseUrl "https://PUBLIC_HOST"`:
  - `Public URL : not ready`;
  - `Manifest : missing`;
  - `Started : no`.
- Windows PowerShell 5.1 `watch-hh-booster-test.ps1 -PublicBaseUrl "https://hh-booster.ngrok-free.app"`:
  - `Public URL : ready`;
  - next action по-прежнему требует `Start test`.
- Windows PowerShell 5.1 `start-hh-booster-test.ps1 -PublicBaseUrl "https://hh-booster.ngrok-free.app" -PrintOnly`:
  - печатает monitor command с `-PublicBaseUrl`;
  - печатает watch command с `-Watch`.
- BOM check: `watch-hh-booster-test.ps1` и `start-hh-booster-test.ps1` сохранены с UTF-8 BOM.

## Риски и ограничения

- Monitor не делает сетевой prelaunch и не заменяет `tools/hh_resume_booster_prelaunch_check.py`.
- Реальный 14-дневный тест не стартовал: `startedAt=null`, лидов `0`.
- Public URL `https://hh-booster.ngrok-free.app` использовался только как URL правильной формы для smoke, не как подтвержденный живой tunnel.

## Что должен проверить следующий агент

- Когда будет реальный public URL: поднять production server в видимом терминале, нажать `Старт теста`, запустить monitor с `-PublicBaseUrl`, затем public launch helper/prelaunch без `--skip-server-check`.
- Candidate links публиковать только после `Status: GO`.
