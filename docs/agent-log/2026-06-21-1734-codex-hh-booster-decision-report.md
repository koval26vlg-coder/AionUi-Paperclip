# 2026-06-21 17:34 - Codex - HH Booster decision report

## Исходный запрос пользователя

Продолжить активную цель: сделать landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack` и затем сравнить paid intent.

## Краткий план

- Проверить текущий metrics CLI и runbook.
- Добавить финальный decision report для paid intent.
- Проверить отчет на not-ready и ready synthetic данных.
- Обновить launch script, runbook и общий контекст.

## Что было сделано

- Добавлен `tools/hh_resume_booster_decision_report.py`.
- Скрипт читает те же JSON/CSV/JSONL и experiment state, что `tools/hh_resume_booster_metrics.py`.
- В strict mode скрипт возвращает exit code `2`, если `decision_ready=false`, и печатает blockers.
- С `--draft` отчет можно сгенерировать до завершения gate.
- При ready скрипт формирует Markdown-вывод: avatar standalone front-offer, avatar lead magnet/module, MVP вокруг аудита резюме или MVP вокруг отклика под вакансию.
- `apps/aion-vision/scripts/start-hh-booster-test.ps1` теперь печатает команды final report и draft report.
- Runbook, `docs/current-context.md` и `docs/tasks.md` обновлены.

## Какие файлы были изменены

- `tools/hh_resume_booster_decision_report.py`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-1734-codex-hh-booster-decision-report.md`

## Проверки

- `python -m py_compile tools/hh_resume_booster_decision_report.py`
- Not-ready synthetic smoke: exit code `2`, `Status: not_ready`, `Blockers`.
- Ready synthetic smoke: exit code `0`, `Status: ready`, decision `avatar_module_build_vacancy_response_pack`, winner `Отклик под вакансию`.

## Риски и ограничения

- Реальный 14-дневный сбор данных еще не проведен, цель не завершена.
- Отчет принимает paid intent как self-reported signal; он не заменяет платежи или фактическую оплату.
- Данные с контактами остаются в `apps/aion-vision/data/`, которое исключено из git.
- Active-run gate в `trading_mvp` остается `RUNNING`; эта работа не трогала `trading_mvp`.

## Что должен проверить следующий агент

- После 14 дней и выполнения gate запустить:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_decision_report.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --out "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-decision-report.md"
```

- Если gate еще не готов, использовать `--draft` только как промежуточный отчет, не как финальное решение.
