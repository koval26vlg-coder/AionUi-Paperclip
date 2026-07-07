# 2026-06-21 18:06 - Codex - HH Booster decision report follow-up outcomes

## Исходный запрос пользователя

Продолжать активную цель: сделать landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack`, затем сравнить paid intent.

## Краткий план

1. Проверить текущий `tools/hh_resume_booster_decision_report.py` и outcome tracker.
2. Добавить optional follow-up outcomes в финальный Markdown report.
3. Обновить launch script и runbook.
4. Проверить strict/draft synthetic scenarios.

## Что было сделано

- В `tools/hh_resume_booster_decision_report.py` добавлен параметр `--followup-state`.
- Если параметр не передан, CLI автоматически ищет соседний `hh-booster-followups.jsonl` рядом с `hh-booster-leads.jsonl`.
- В Markdown report добавлен раздел `Follow-up Outcomes`:
  - tracked;
  - confirmed paid intent;
  - paid;
  - declined;
  - open;
  - follow-up winner.
- Добавлен caveat, если follow-up winner расходится с primary form winner.
- Primary decision gate не изменен: 14 дней, 30+ лидов, 10+ `Готов оплатить`, 2+ канала, 5+ ролей.
- `apps/aion-vision/scripts/start-hh-booster-test.ps1` теперь печатает final/draft report commands с `--followup-state`.
- Runbook `docs/experiments/hh-resume-booster-validation.md` обновлен: финальный отчет использует follow-up state как quality signal.

## Измененные файлы

- `tools/hh_resume_booster_decision_report.py`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-1806-codex-hh-booster-decision-followup-outcomes.md`

## Проверки

- `python -m py_compile tools/hh_resume_booster_decision_report.py tools/hh_resume_booster_followup_state.py tools/hh_resume_booster_followup_queue.py`
- Synthetic ready strict report:
  - gate passed;
  - report includes `Follow-up Outcomes`;
  - response offer has `paid=1`;
  - strict mode exit code `0`.
- Synthetic not-ready draft report:
  - report status `not_ready`;
  - blockers preserved;
  - follow-up `confirmed_paid_intent` still shown as quality signal.
- PowerShell parser smoke для `apps/aion-vision/scripts/start-hh-booster-test.ps1`.

## Риски и ограничения

- Follow-up outcomes не заменяют primary gate и не доказывают оплату автоматически; это ручной операционный журнал.
- Если primary paid intent и follow-up outcome расходятся, итоговое решение нужно читать как требующее ручной продуктовой проверки.
- Реальный 14-дневный сбор и финальное сравнение paid intent еще не проведены.

## Что должен проверить следующий агент

1. После реального 14-дневного сбора запускать final report так:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_decision_report.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --followup-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-followups.jsonl" --out "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-decision-report.md"
```

2. До прохождения gate использовать `--draft`.
