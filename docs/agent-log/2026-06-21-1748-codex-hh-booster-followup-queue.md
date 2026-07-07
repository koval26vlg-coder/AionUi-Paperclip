# 2026-06-21 17:48 - Codex - HH Booster follow-up queue

## Исходный запрос пользователя

Продолжать активную цель: сделать landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack`, затем сравнить paid intent.

## Краткий план

1. Проверить текущий формат HH Booster лидов и существующие CLI метрик.
2. Добавить read-only очередь concierge follow-up.
3. Проверить очередь на synthetic JSONL.
4. Обновить runbook, текущий контекст и задачи.

## Что было сделано

- Добавлен `tools/hh_resume_booster_followup_queue.py`.
- CLI читает JSON, CSV и server JSONL.
- По умолчанию показывает только actionable intents: `ready` и `maybe`.
- Сортирует `Готов оплатить` выше `Интересно`, затем по времени.
- Маскирует контакты по умолчанию; реальные контакты раскрываются только через `--show-contact`.
- Поддерживает фильтры:
  - `--intent ready,maybe,not_now,all`;
  - `--offer avatar,audit,response,all`;
  - `--channel`;
  - `--role-contains`;
  - `--days`;
  - `--limit`;
  - `--oldest-first`.
- Поддерживает text, Markdown и JSON вывод.
- Для каждого лида показывает suggested action: запрос ссылки на вакансию, аудит профиля, фото-разбор, уточнение возражения или отказ от продажи.
- `apps/aion-vision/scripts/start-hh-booster-test.ps1` теперь печатает команды follow-up queue рядом с daily metrics.
- `docs/experiments/hh-resume-booster-validation.md` получил раздел `Concierge follow-up queue`.
- `docs/current-context.md` и `docs/tasks.md` обновлены.

## Измененные файлы

- `tools/hh_resume_booster_followup_queue.py`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-1748-codex-hh-booster-followup-queue.md`

## Проверки

- `python -m py_compile tools/hh_resume_booster_metrics.py tools/hh_resume_booster_decision_report.py tools/hh_resume_booster_data_admin.py tools/hh_resume_booster_followup_queue.py`
- PowerShell parser smoke для `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- PowerShell parser smoke для `apps/aion-vision/scripts/watch-hh-booster-test.ps1`
- Synthetic JSONL text smoke: default queue показал `ready/maybe`, замаскировал контакты и поставил `ready` первым.
- Synthetic JSONL `--intent ready --show-contact --json`: показал только ready-лид и раскрыл контакт по явному флагу.
- Synthetic JSONL Markdown smoke.
- Synthetic JSONL `--intent all --offer audit --show-contact --json`: проверен фильтр not_now/audit.
- Missing-data smoke: если JSONL еще не создан, CLI показывает пустую очередь без stack trace.
- `start-hh-booster-test.ps1 -PrintOnly -Port 8787`: launch script печатает команды concierge queue рядом с daily metrics и не стартует сервер.

## Риски и ограничения

- Очередь не заменяет юридическую privacy policy; это операционный read-only инструмент для concierge-теста.
- `--show-contact` нужно использовать только когда реально пишем кандидату.
- Скрипт не меняет JSONL и не отмечает статус follow-up; если нужен статус `contacted/responded/converted`, потребуется отдельный state-файл или CRM-таблица.
- Реальный 14-дневный сбор и сравнение paid intent еще не проведены, цель не завершена.

## Что должен проверить следующий агент

1. При запуске production-теста использовать `start-hh-booster-test.ps1`, затем каждый день запускать:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_queue.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl"
```

2. Для реальной обработки готовых к оплате лидов использовать явный режим:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_queue.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --intent ready --show-contact
```

3. После накопления фактических данных считать метрики и финальный decision report, не принимать решение до прохождения 14-дневного gate.
