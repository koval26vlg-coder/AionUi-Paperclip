# 2026-06-21 17:38 - Codex - HH Booster privacy data admin

## Исходный запрос пользователя

Продолжить активную цель: сделать landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack` и затем сравнить paid intent.

## Краткий план

- Проверить текущий privacy/delete контекст HH Booster.
- Добавить безопасный CLI для поиска, удаления и редактирования заявок в server JSONL.
- Проверить CLI на synthetic JSONL.
- Обновить runbook и общий контекст.

## Что было сделано

- Добавлен `tools/hh_resume_booster_data_admin.py`.
- По умолчанию tool делает read-only find и маскирует контакт в выводе.
- `--action delete --write` удаляет matching rows из JSONL.
- `--action redact --write` сохраняет агрегатную строку, но заменяет `contact` и `notes`, ставит `consentAccepted=false` и `deletedAt`.
- Перед любым write создается backup в `apps/aion-vision/data/backups/`.
- Поддерживаются target-параметры `--id`, `--contact`, `--contact-contains`.
- `start-hh-booster-test.ps1` теперь печатает privacy/delete dry-run и write команды.
- Runbook, `docs/current-context.md` и `docs/tasks.md` обновлены.

## Какие файлы были изменены

- `tools/hh_resume_booster_data_admin.py`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-1738-codex-hh-booster-data-admin.md`

## Проверки

- `python -m py_compile tools/hh_resume_booster_data_admin.py`
- Synthetic find: matched 1 row, contact masked.
- Synthetic delete write: row removed, backup created.
- Synthetic redact write: `contact`/`notes` redacted, `consentAccepted=false`, `deletedAt` present, backup created.

## Риски и ограничения

- Реальный 14-дневный сбор данных еще не проведен, цель не завершена.
- Backup-файлы могут содержать персональные данные; они лежат внутри `apps/aion-vision/data/`, который исключен из git.
- Удаление из exported CSV/JSON, если они уже отправлены вне `data/`, нужно выполнять отдельно.
- Active-run gate в `trading_mvp` остается `RUNNING`; эта работа не трогала `trading_mvp`.

## Что должен проверить следующий агент

- Перед публичным тестом оставить в тексте для участников обещание удаления через указанный контакт.
- При запросе удаления сначала выполнить dry-run:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_data_admin.py" --contact "CONTACT_OR_TELEGRAM"
```

- Затем выполнить `--action delete --write` или `--action redact --write` по ситуации.
