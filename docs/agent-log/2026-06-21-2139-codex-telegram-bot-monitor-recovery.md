# 2026-06-21 21:39 +03 — Codex — Telegram bot monitor recovery

## Исходный запрос

Пользователь сообщил: "ОПЯТЬ ЗАВИС БОТ".

## Краткий план

1. Проверить active-run gate и не трогать долгий `trading_mvp` collector.
2. Проверить реальное состояние Telegram bot PID из metadata.
3. Воспроизвести polling через короткий one-shot запуск.
4. Перевести Telegram bot в видимый monitor-режим с авто-рестартом.
5. Защитить `/signal` от повторного показа уже поставленного события.

## Что сделано

- Active-run gate проверен: `trading_mvp` остался в статусе `RUNNING`; collectors/backtests/postprocess не запускались.
- Старый metadata PID `2064` был мертв, дочернего `python.exe` не было.
- `tools/run-telegram-bot-visible.ps1 -Once` успешно обработал `17 update(s)` и поднял state offset до `722049890`, поэтому проблема была не в Telegram API/токене, а в умершем постоянном процессе.
- Добавлен `C:\Users\koval\Documents\New project\tools\run-telegram-bot-monitor-visible.ps1`.
- Monitor запущен в видимом окне: PID `29788`; дочерний `python.exe` после reload `9236`; metadata обновлена в `C:\Users\koval\Documents\New project\data\telegram_bot_run_metadata.json`.
- README обновлен: добавлена команда `.\tools\run-telegram-bot-monitor-visible.ps1`.
- Бот отправил пользователю Telegram-сообщение о восстановлении monitor-режима.
- Обнаружено, что `Уругвай - Кабо-Верде` уже записан как pending manual bet. В `telegram_bot.py` добавлена защита: `/signal` не показывает уже поставленный `current_signal`, а старая кнопка `ДА` не ведет к повторному подтверждению.
- Через реальный код `send_current_signal` отправлена проверка: текущий уже поставленный сигнал ушел без inline-кнопок.

## Измененные файлы

- `C:\Users\koval\Documents\New project\tools\run-telegram-bot-monitor-visible.ps1`
- `C:\Users\koval\Documents\New project\src\sports_betting_analytics\telegram_bot.py`
- `C:\Users\koval\Documents\New project\tests\test_core.py`
- `C:\Users\koval\Documents\New project\README.md`
- `C:\Users\koval\Documents\New project\data\telegram_bot_run_metadata.json`
- `D:\AionUi-Paperclip\docs\current-context.md`
- `D:\AionUi-Paperclip\docs\tasks.md`

## Проверки

- PowerShell parser для `run-telegram-bot-visible.ps1`: OK.
- PowerShell parser для `run-telegram-bot-monitor-visible.ps1`: OK.
- `py_compile` для `telegram_bot.py` и `tests/test_core.py`: OK.
- `python -m unittest discover -s tests`: 9 tests OK.
- Process check: monitor PID `29788` жив, под ним один `python.exe`.
- Telegram API sendMessage: `ok=True`.

## Риски и ограничения

- Бот не логинится в БК, не кликает ставки и не управляет деньгами.
- Если пользователь закроет видимое monitor-окно, bot остановится; это ожидаемое поведение.
- `Уругвай - Кабо-Верде` уже учтен как pending bet. Следующий betting-сигнал нужно рассчитывать отдельно по актуальной live-линии; текущий JSON повторять нельзя.
- Из-за active-run gate не запускались новые долгие аналитические прогоны или collectors.

## Что проверить следующему агенту

- Проверить статус командой:

```powershell
Get-Process -Id 29788
Get-CimInstance Win32_Process -Filter 'ParentProcessId=29788'
```

- Если нужен новый betting-сигнал, сначала проверить active-run gate, затем делать отдельную live-проверку линии и заменить `data/signals/current_signal.json` новым событием, не повторяя already placed `match_id`.
