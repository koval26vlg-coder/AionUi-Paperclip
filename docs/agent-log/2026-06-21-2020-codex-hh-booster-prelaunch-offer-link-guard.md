# 2026-06-21 20:20 - Codex - HH Booster prelaunch offer-link guard

## Исходный запрос пользователя

Продолжить активную цель: довести landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack` до практического запуска и сравнения paid intent.

## Краткий план

1. Снять day-0 readiness текущего HH Resume Booster.
2. Найти операционный зазор перед публикацией candidate links.
3. Усилить prelaunch GO/NO-GO, чтобы он проверял новую матрицу offer-specific links.
4. Прогнать smoke-проверки и зафиксировать состояние.

## Что было сделано

- Проверен текущий state:
  - `hh-booster-experiment.json`: `startedAt=null`;
  - `hh-booster-leads.jsonl`: существует, размер `0`;
  - summary: `total_leads=0`, `decision_ready=false`.
- Readiness smoke с `https://hh-booster.ngrok-free.app` и `--skip-server-check` показывает ожидаемый `NO-GO` только по:
  - `experiment_started`;
  - `launch_manifest`.
- `tools/hh_resume_booster_prelaunch_check.py` усилен:
  - добавлен парсинг hash-query ссылок;
  - проверяется `offer_links`: ровно 3 прямые ссылки, по одной на `avatar`, `audit`, `response`;
  - проверяется `offer_channel_links`: ровно 18 ссылок `3 оффера x 6 каналов`;
  - каждая matrix-ссылка должна сохранять и `channel`, и `offer`;
  - next actions теперь явно указывают, что сломанную матрицу candidate links нужно чинить до запуска.
- Runbook `docs/experiments/hh-resume-booster-validation.md` обновлен: prelaunch проверяет прямые offer-ссылки и матрицу `offer + channel`.
- `docs/tasks.md` обновлен записью о завершенном prelaunch guard.

## Измененные файлы

- `tools/hh_resume_booster_prelaunch_check.py`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-2020-codex-hh-booster-prelaunch-offer-link-guard.md`

## Проверки

- `python -m py_compile tools/hh_resume_booster_prelaunch_check.py` - прошло.
- Prelaunch smoke:
  - command: `hh_resume_booster_prelaunch_check.py --operator-base-url http://127.0.0.1:8787 --public-base-url https://hh-booster.ngrok-free.app --skip-server-check --json`;
  - result: `status=NO-GO`, `failed=2`;
  - `offer_links=pass`;
  - `offer_channel_links=pass`;
  - failures: `experiment_started`, `launch_manifest`.
- Placeholder smoke:
  - `https://PUBLIC_HOST` блокируется через `public_url=fail`;
  - offer-link checks при этом остаются pass, потому что они проверяют структуру ссылок, а не валидность хоста.

## Риски и ограничения

- Реальный 14-дневный тест не стартовал.
- Public URL `https://hh-booster.ngrok-free.app` использовался только как URL правильной формы для smoke; не подтвержден как реально поднятый tunnel/domain.
- Сохраненный launch manifest пока отсутствует намеренно: его лучше сохранять после реального `Старт теста` и перед публикацией ссылок.
- Trading active-run gate показывает RUNNING для другого проекта `trading_mvp`; этот поток не трогался.

## Что должен проверить следующий агент

- Перед публикацией: поднять production server видимо, получить реальный public URL, нажать `Старт теста`, сохранить launch manifest, пройти prelaunch GO/NO-GO без `--skip-server-check`.
- Не публиковать ссылки, пока `prelaunch_check.py` не покажет `Status: GO`.
