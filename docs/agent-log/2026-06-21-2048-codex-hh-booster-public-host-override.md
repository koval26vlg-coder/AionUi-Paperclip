# Отчет агента: HH Resume Booster public host override

Дата и время: 2026-06-21 20:48 +03:00

Агент: Codex

## Исходный запрос пользователя

Продолжать активную цель: подготовить 14-дневный landing/concierge test для трех офферов `avatar-only`, `full resume audit`, `vacancy response pack` и сравнить paid intent.

## Краткий план

- Проверить состояние server/tunnel/experiment/manifest.
- Не стартовать 14-дневное окно без явного готового запуска.
- Закрыть UX-риск раздачи локальных `127.0.0.1` ссылок из операторской панели.
- Проверить сборку и рендер.

## Что было сделано

- Подтянут Aion SML-контекст.
- Проверено, что server PID `28024` и tunnel PID `4380` живы.
- Проверено, что `startedAt=null`, `hh-booster-launch-manifest.md` отсутствует, JSONL пустой.
- Запущены watch/prelaunch/data-quality/status проверки; prelaunch ожидаемо `NO-GO` только из-за `experiment_started` и `launch_manifest`.
- В `HhBoosterValidation.tsx` добавлен `publicBaseUrl` override:
  - query params `publicBaseUrl` / `public_base_url`;
  - сохранение в `localStorage` key `aion.hhResumeBooster.publicBaseUrl.v1`;
  - поле `Public host для candidate links` в блоке `Ссылки и тексты`;
  - warning при localhost;
  - channel/offer links и outreach texts строятся от public host.
- Открыта операторская панель:
  - `http://127.0.0.1:8787/?publicBaseUrl=https%3A%2F%2Fhuge-moons-fail.loca.lt#hh-booster`

## Измененные файлы

- `apps/aion-vision/src/components/dashboard/HhBoosterValidation.tsx`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-2048-codex-hh-booster-public-host-override.md`

## Проверки

- `npm run lint` прошел.
- `npm run build` прошел.
- Playwright/Edge smoke через bundled runtime прошел:
  - public host control виден;
  - `https://huge-moons-fail.loca.lt/#hh-booster-public` отображается в блоке ссылок;
  - offer+channel links содержат public host;
  - warning `Это локальный host` отсутствует.
- Screenshot: `C:/Users/koval/Documents/Команда/hh-booster-public-host-override-v1.png`.

## Риски и ограничения

- 14-дневное окно не стартовало: `startedAt=null`.
- Launch manifest еще не создан.
- Public localtunnel временный; после перезапуска нужен новый `publicBaseUrl`.
- Не публиковать candidate links до `Status: GO` в prelaunch.

## Что должен проверить следующий агент

- После ручного `Старт теста` выполнить:
  `apps/aion-vision/scripts/prepare-hh-booster-public-launch.ps1 -PublicBaseUrl "https://huge-moons-fail.loca.lt"`.
- Затем выполнить prelaunch с `--check-public-http`.
- Только при `Status: GO` публиковать candidate links.
