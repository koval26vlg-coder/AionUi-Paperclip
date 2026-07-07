# 2026-06-21 17:27 - Codex - HH Booster server experiment state

## Исходный запрос пользователя

Продолжить активную цель: сделать landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack` и затем сравнить paid intent.

## Краткий план

- Проверить текущие метрики и формат данных HH Booster.
- Убрать зависимость финального подсчета от браузерного `localStorage`.
- Синхронизировать дату старта/пороги теста в server-side файл.
- Проверить CLI, серверные helper-функции и frontend build.

## Что было сделано

- В `apps/aion-vision/scripts/serve-sml.py` добавлены `GET /api/hh-booster/experiment` и `POST /api/hh-booster/experiment`.
- Production-сервис хранит дату старта и пороги в `apps/aion-vision/data/hh-booster-experiment.json`.
- Операторская панель `#hh-booster` при `Старт теста` синхронизирует experiment state на сервер в production-режиме.
- Кнопка `Сервер` теперь импортирует не только заявки из JSONL, но и server experiment state.
- `tools/hh_resume_booster_metrics.py` при подсчете `hh-booster-leads.jsonl` автоматически ищет соседний `hh-booster-experiment.json`; также добавлен параметр `--experiment-state`.
- `start-hh-booster-test.ps1` теперь печатает путь к experiment state.
- Runbook обновлен.

## Какие файлы были изменены

- `apps/aion-vision/scripts/serve-sml.py`
- `apps/aion-vision/src/components/dashboard/HhBoosterValidation.tsx`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `tools/hh_resume_booster_metrics.py`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-1727-codex-hh-booster-server-experiment-state.md`

## Проверки

- `python -m py_compile apps/aion-vision/scripts/serve-sml.py tools/hh_resume_booster_metrics.py`
- `npm run lint`
- `npm run build`
- Synthetic JSONL + `hh-booster-experiment.json` smoke: CLI вернул `decision_ready=true`, когда все пороги искусственно выполнены.
- Server helper smoke через importlib и временную директорию: запись/чтение experiment state работает без записи в реальные `data/`.
- `start-hh-booster-test.ps1 -PrintOnly -Port 8787` печатает путь к `hh-booster-experiment.json`.

## Риски и ограничения

- Реальный 14-дневный сбор данных еще не проведен, цель не завершена.
- Для внешней аудитории все еще нужен публичный URL или tunnel через `-PublicBaseUrl`; локальный `127.0.0.1` не публиковать.
- Server experiment state хранится локально и не должен попадать в git вместе с контактами.
- Active-run gate в `trading_mvp` остается `RUNNING`; эта работа не трогала `trading_mvp`.

## Что должен проверить следующий агент

- Запустить production-сервис видимо через `start-hh-booster-test.ps1`.
- Нажать `Старт теста` в `#hh-booster` и проверить, что создан `apps/aion-vision/data/hh-booster-experiment.json`.
- После первых реальных заявок считать `apps/aion-vision/data/hh-booster-leads.jsonl` через `tools/hh_resume_booster_metrics.py` и убедиться, что `started_at` не `n/a`.
