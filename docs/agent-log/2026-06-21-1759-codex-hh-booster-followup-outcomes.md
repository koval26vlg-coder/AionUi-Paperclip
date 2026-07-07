# 2026-06-21 17:59 - Codex - HH Booster follow-up outcomes

## Исходный запрос пользователя

Продолжать активную цель: сделать landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack`, затем сравнить paid intent.

## Краткий план

1. Проверить текущий HH follow-up queue и формат лидов.
2. Добавить отдельный outcome tracker для ручной concierge-обработки.
3. Связать queue с outcome state, чтобы не обрабатывать закрытые лиды повторно.
4. Обновить runbook, `current-context.md` и `tasks.md`.

## Что было сделано

- Добавлен `tools/hh_resume_booster_followup_state.py`.
- Tracker ведет отдельный append-only файл:

```text
apps/aion-vision/data/hh-booster-followups.jsonl
```

- Исходный `apps/aion-vision/data/hh-booster-leads.jsonl` не меняется.
- Поддержаны команды:
  - `mark LEAD_ID --status ... --write`;
  - `summary`;
  - `list`.
- Поддержанные статусы:
  - `contacted`;
  - `responded`;
  - `confirmed_paid_intent`;
  - `paid`;
  - `declined`;
  - `no_response`;
  - `invalid`.
- `mark` по умолчанию dry-run и пишет только с `--write`.
- Контакты в выводе маскируются по умолчанию.
- `tools/hh_resume_booster_followup_queue.py` теперь читает follow-up state и скрывает closed-лиды (`paid`, `declined`, `no_response`, `invalid`) без `--include-closed`.
- `apps/aion-vision/scripts/start-hh-booster-test.ps1` печатает путь follow-ups и команды mark/summary.
- `docs/experiments/hh-resume-booster-validation.md` получил раздел `Concierge follow-up outcomes`.

## Измененные файлы

- `tools/hh_resume_booster_followup_state.py`
- `tools/hh_resume_booster_followup_queue.py`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-1759-codex-hh-booster-followup-outcomes.md`

## Проверки

- `python -m py_compile tools/hh_resume_booster_followup_queue.py tools/hh_resume_booster_followup_state.py tools/hh_resume_booster_metrics.py tools/hh_resume_booster_decision_report.py`
- PowerShell parser smoke для `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `start-hh-booster-test.ps1 -PrintOnly -Port 8787` печатает follow-up state path, mark command и summary command.
- Synthetic `mark --status paid --write --json` создает событие в temp JSONL.
- Synthetic `summary --json` считает `confirmed_paid_intent=1`, `paid=1`.
- Synthetic `list --status paid --json` возвращает latest paid state.
- Queue без `--include-closed` скрывает paid lead.
- Queue с `--include-closed` показывает paid lead со статусом `Оплатил`.
- Missing-state `summary --json` возвращает нули без ошибки.

## Риски и ограничения

- Outcome tracker не является платежной системой и не доказывает оплату сам по себе; он фиксирует ручной операционный факт.
- В `--note` не нужно писать лишние персональные данные.
- Primary decision gate остается прежним: 14 дней, 30+ лидов, 10+ strong paid intent, 2+ канала, 5+ ролей.
- Follow-up outcomes нужны как quality signal: если первичный intent высокий, а `confirmed_paid_intent/paid` низкий, оффер или цена требуют пересмотра.
- Реальный 14-дневный сбор и финальное сравнение paid intent еще не проведены.

## Что должен проверить следующий агент

1. В ежедневной работе сначала запускать queue:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_queue.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl"
```

2. После контакта отмечать исход:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_state.py" --leads "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" mark "LEAD_ID" --status confirmed_paid_intent --note "short non-sensitive note" --write
```

3. В конце дня смотреть summary:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_state.py" --leads "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" summary
```
