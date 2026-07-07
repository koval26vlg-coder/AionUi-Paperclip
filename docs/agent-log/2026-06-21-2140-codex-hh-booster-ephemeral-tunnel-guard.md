# Отчет агента

## Дата и время

2026-06-21 21:40 +03

## Агент

Codex

## Исходный запрос пользователя

Продолжить активную цель: подготовить 2-недельный landing/concierge test HH Resume Booster с тремя офферами и сравнением paid intent.

## Контекст перед началом

- Актуальный rehearsal использует public localtunnel `https://tangy-peaches-like.loca.lt`.
- Localtunnel подходит для проверки формы и API, но является временной ссылкой и рискован для 14-дневного теста.
- До этого prelaunch показывал только ожидаемые blockers `experiment_started` и `launch_manifest`, но не выделял риск временного tunnel.
- `startedAt` был и остается `null`; 14-дневный сбор не начат.

## План

1. Добавить определение временных tunnel hosts в launch manifest.
2. Показать warning в prelaunch GO/NO-GO.
3. Показать предупреждение в publish kit до копирования ссылок.
4. Перегенерировать publish kit.
5. Проверить CLI и обновить общий контекст.

## Что сделано

- В `tools/hh_resume_booster_launch_manifest.py` добавлена функция `is_ephemeral_tunnel_url`.
- Launch manifest теперь включает `status.ephemeral_url_warning`.
- `tools/hh_resume_booster_prelaunch_check.py` добавляет check `ephemeral_public_url` со статусом `warn` для временных tunnel hosts:
  - `*.loca.lt`;
  - `*.ngrok-free.app`;
  - `*.trycloudflare.com`;
  - `*.localhost.run`.
- Prelaunch next actions теперь отдельно рекомендует стабильный domain или повторную public API/prelaunch проверку прямо перед публикацией.
- `tools/hh_resume_booster_publish_kit.py` показывает `Ephemeral tunnel: yes` и добавляет правило перепроверки temporary tunnel перед рассылкой.
- `apps/aion-vision/data/hh-booster-publish-kit.md` перегенерирован под текущий `https://tangy-peaches-like.loca.lt` уже с предупреждением.

## Измененные файлы

- `tools/hh_resume_booster_launch_manifest.py`
- `tools/hh_resume_booster_prelaunch_check.py`
- `tools/hh_resume_booster_publish_kit.py`
- `apps/aion-vision/data/hh-booster-publish-kit.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-2140-codex-hh-booster-ephemeral-tunnel-guard.md`

## Проверки

- `python -m py_compile tools/hh_resume_booster_launch_manifest.py tools/hh_resume_booster_prelaunch_check.py tools/hh_resume_booster_publish_kit.py` — pass.
- Launch manifest JSON для `https://tangy-peaches-like.loca.lt` показывает `public_url_ready=true` и `ephemeral_url_warning=true`.
- Prelaunch JSON с `--check-public-http` вернул `Status: NO-GO`, `failed=2`, `warnings=1`; failures остались только `experiment_started` и `launch_manifest`, warning — `ephemeral_public_url`.
- Publish kit readback показывает `Ephemeral tunnel: yes`.
- Inline smoke `ephemeral_url_cases_ok` подтвердил matching временных и стабильных hosts.
- Финальная свежая проверка в 21:44 подтвердила, что temporary runtime уже протух: PIDs `21428/11932` не найдены, порт `8787` свободен, public API `https://tangy-peaches-like.loca.lt/api/hh-booster/experiment` вернул `503 Service Unavailable`, prelaunch показывает server/public failures.

## Решения

- Temporary tunnel не блокирует rehearsal, но должен быть видимым warning перед реальной рассылкой.
- Не запускать `-StartExperiment` автоматически.
- Не сохранять launch manifest до фактического старта, чтобы не получить stale launch freeze.

## Риски и ограничения

- `https://tangy-peaches-like.loca.lt` может измениться или умереть; перед публикацией нужно повторить public API/prelaunch.
- Текущий `https://tangy-peaches-like.loca.lt` уже нельзя использовать без нового visible tunnel: последняя проверка вернула `503`.
- Для настоящих 14 дней лучше стабильный public domain.
- Реальный paid-intent сбор еще не начат, leads JSONL пустой.

## Что должен проверить следующий агент

- Перед стартом заново проверить public API и prelaunch.
- Если пользователь подтверждает старт на temporary tunnel, явно принять риск смены ссылки.
- После старта сохранить launch manifest и добиться prelaunch `Status: GO` перед рассылкой.
