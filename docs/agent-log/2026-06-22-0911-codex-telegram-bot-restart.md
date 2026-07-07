# 2026-06-22 09:11 +03 — Codex — Telegram bot restart

## Исходный запрос

Пользователь спросил, как правильно запустить бота, и сообщил, что он снова не работает.

## Что сделано

- Проверен active-run gate: `trading_mvp` остается `RUNNING`; долгие collectors/backtests не запускались.
- Выполнен Aion bootstrap по теме запуска Telegram bot.
- Health-check показал `DEAD`: metadata monitor PID `11104` не жив, state heartbeat age около `22.77` минуты.
- Бот запущен корректным проектным launcher:

```powershell
& "C:\Users\koval\Documents\New project\tools\start-telegram-bot-monitor-visible.ps1"
```

- Новый monitor PID `33944`, child `python.exe` PID `36808`.
- Повторный health-check через 8 секунд показал `OK`.

## Правильные команды

Проверить:

```powershell
& "C:\Users\koval\Documents\New project\tools\check-telegram-bot-health.ps1"
```

Запустить:

```powershell
& "C:\Users\koval\Documents\New project\tools\start-telegram-bot-monitor-visible.ps1"
```

## Риск

Если закрыть видимое monitor-окно, бот остановится. Это ожидаемое ограничение текущего видимого режима; health-check покажет `DEAD`.
