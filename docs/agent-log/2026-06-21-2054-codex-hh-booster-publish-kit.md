# Отчет агента: HH Resume Booster publish kit

Дата и время: 2026-06-21 20:54 +03:00

Агент: Codex

## Исходный запрос пользователя

Продолжать активную цель: подготовить 14-дневный landing/concierge test с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack` и сравнить paid intent.

## Краткий план

- Проверить live состояние server/tunnel/experiment.
- Не стартовать 14-дневное окно без готовности к публикации.
- Создать publish kit для текущего public URL, чтобы после старта сразу раздавать правильные материалы.
- Встроить команду publish kit в стартовый скрипт и runbook.

## Что было сделано

- Проверено:
  - server PID `28024` жив;
  - tunnel PID `4380` жив;
  - public URL `https://huge-moons-fail.loca.lt/#hh-booster-public` отдает Aion Vision app shell;
  - `startedAt=null`;
  - `hh-booster-leads.jsonl` пустой.
- Добавлен `tools/hh_resume_booster_publish_kit.py`.
- Сгенерирован текущий publish kit:
  - `apps/aion-vision/data/hh-booster-publish-kit.md`
  - public URL: `https://huge-moons-fail.loca.lt`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1` теперь печатает команду генерации publish kit.
- Runbook/current context/tasks обновлены.

## Измененные файлы

- `tools/hh_resume_booster_publish_kit.py`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-2054-codex-hh-booster-publish-kit.md`

## Проверки

- `py_compile tools/hh_resume_booster_publish_kit.py` прошел.
- Publish kit `--write` создал `apps/aion-vision/data/hh-booster-publish-kit.md`.
- Проверка содержимого:
  - `25` public-form ссылок на `https://huge-moons-fail.loca.lt/#hh-booster-public`;
  - есть `offer=avatar`, `offer=audit`, `offer=response`;
  - есть `Daily Control Loop`;
  - есть правило `Do not publish candidate links until prelaunch returns Status: GO`.
- `start-hh-booster-test.ps1 -PrintOnly -PublicBaseUrl "https://huge-moons-fail.loca.lt"` печатает publish kit command.
- Public preflight: `ok`, `0` fail, `0` warnings.
- Prelaunch: ожидаемо `NO-GO` по `experiment_started` и `launch_manifest`.

## Риски и ограничения

- 14-дневное окно еще не стартовало.
- Launch manifest еще не создан.
- Publish kit нужно пересобрать, если localtunnel URL изменится.
- Нельзя публиковать candidate links до `Status: GO`.

## Что должен проверить следующий агент

- После ручного `Старт теста` выполнить `prepare-hh-booster-public-launch.ps1 -PublicBaseUrl "https://huge-moons-fail.loca.lt"`.
- Затем выполнить prelaunch с `--check-public-http`.
- Если prelaunch даст `GO`, публиковать ссылки из `apps/aion-vision/data/hh-booster-publish-kit.md` или из операторской панели с тем же public host.
