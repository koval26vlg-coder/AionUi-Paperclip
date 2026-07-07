# 2026-06-22 08:15 +03 — Codex — Project technical audit and bot recovery

## Исходный запрос

Пользователь сообщил, что бот снова завис, и попросил выполнить полный аудит проекта, подготовить файл с техническим описанием без указания функционального назначения процесса, проверить всё и найти баги.

## Краткий план

1. Проверить active-run gate и не запускать долгие collectors/backtests.
2. Подтянуть Aion/SML память по предыдущим запускам.
3. Снять фактическое состояние monitor/python процессов, metadata, state и event log.
4. Проверить код, PowerShell launchers, JSON/CSV данные, CLI и тесты.
5. Исправить подтвержденные дефекты с регрессионными тестами.
6. Запустить monitor через проектный launcher и зафиксировать health.
7. Создать технический audit-файл в проекте.

## Что сделано

- Active-run gate проверен: `trading_mvp` оставался `RUNNING`; новые collectors/backtests/postprocess не запускались.
- Установлено фактическое состояние отказа: metadata указывала на PID `29788`, но monitor/python процессов не было.
- `run-telegram-bot-visible.ps1 -Once` успешно обработал `9 update(s)` и обновил offset до `722049906`, то есть Telegram API/токен были живы.
- Исправлен stale callback bug: обработчик теперь сверяет `callback_data` signal_id с активным `current_signal`.
- Исправлено журналирование дублей: новые duplicate placed events пишутся как `placed_manual_duplicate_command` / `placed_manual_duplicate_button`.
- Исправлена обработка Telegram JSON `ok=false`.
- Добавлены проектные команды:
  - `tools/start-telegram-bot-monitor-visible.ps1`
  - `tools/check-telegram-bot-health.ps1`
- `tools/run-telegram-bot-monitor-visible.ps1` теперь пишет transcript в `data/telegram_bot_monitor_transcript.log`.
- Bankroll default синхронизирован до `1000` в `config/default.json` и `tools/run-manual-signals.ps1`.
- README обновлен командами launcher/health/transcript.
- Monitor запущен через новый launcher: PID `11104`, child `python.exe` PID `29600`.
- Создан отчет `C:\Users\koval\Documents\New project\PROJECT_TECHNICAL_AUDIT.md`.

## Измененные файлы

- `C:\Users\koval\Documents\New project\PROJECT_TECHNICAL_AUDIT.md`
- `C:\Users\koval\Documents\New project\src\sports_betting_analytics\telegram_bot.py`
- `C:\Users\koval\Documents\New project\tests\test_core.py`
- `C:\Users\koval\Documents\New project\tools\run-telegram-bot-monitor-visible.ps1`
- `C:\Users\koval\Documents\New project\tools\start-telegram-bot-monitor-visible.ps1`
- `C:\Users\koval\Documents\New project\tools\check-telegram-bot-health.ps1`
- `C:\Users\koval\Documents\New project\tools\run-manual-signals.ps1`
- `C:\Users\koval\Documents\New project\config\default.json`
- `C:\Users\koval\Documents\New project\README.md`
- `C:\Users\koval\Documents\New project\data\telegram_bot_run_metadata.json`
- `D:\AionUi-Paperclip\docs\current-context.md`
- `D:\AionUi-Paperclip\docs\tasks.md`

## Проверки

- `py_compile` по основным Python-модулям и тестам: OK.
- `python -m unittest discover -s tests`: 11 tests OK.
- PowerShell parser для всех `tools\*.ps1`: OK.
- CLI help: OK.
- CLI run: OK, созданы audit CSV/HTML.
- CLI ledger: OK, `3` rows, pending exposure `30.00`.
- JSON/CSV parse/schema checks: OK.
- One-shot Telegram polling: OK, `9 update(s)`.
- Health check после restart: `OK`, monitor PID `11104`, python PID `29600`.

## Риски и ограничения

- Видимое monitor-окно остается обязательным; если пользователь его закрывает, процесс остановится. Теперь это диагностируется health-check как `DEAD`.
- Исторические duplicate events в `data/telegram_events.jsonl` не переписывались, чтобы не менять audit trail.
- `data\signals\current_signal.json` технически stale, потому что его `match_id` уже есть в ledger; бот теперь suppress-ит повторный `/signal`, но файл нужно заменить новым валидным состоянием или явно перевести в inactive.
- Секреты не выводились и не записывались в docs.

## Что проверить следующему агенту

```powershell
& "C:\Users\koval\Documents\New project\tools\check-telegram-bot-health.ps1"
```

Если status не `OK`, запускать только видимо:

```powershell
& "C:\Users\koval\Documents\New project\tools\start-telegram-bot-monitor-visible.ps1"
```
