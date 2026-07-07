# 2026-06-22 13:29 +03 — Codex — Telegram reports dashboard

## Исходный запрос

Пользователь попросил, чтобы вся информация была в Telegram.

## Что сделано

- Учтено актуальное состояние после Claude: основной конвейер `tools/run-wc-model.ps1`, отчеты `out/wc_watchlist.md`, `out/wc_compare.md`, `out/wc_markets_compare.md`, тестовый набор 42+.
- В `src/sports_betting_analytics/telegram_bot.py` добавлены команды:
  - `/report` и `/reports` — отправляют watchlist + 1X2 compare + markets compare;
  - `/watchlist` — отправляет `out/wc_watchlist.md`;
  - `/compare` — отправляет `out/wc_compare.md`;
  - `/markets` — отправляет `out/wc_markets_compare.md`;
  - `/health` — состояние bot/report файлов;
  - `/model` и `/refresh` — объясняют видимый запуск `tools/run-wc-model.ps1`.
- Добавлен splitter длинных Telegram-сообщений, чтобы Markdown-отчеты уходили частями и не превышали лимит Telegram.
- README и `КАК_РАБОТАТЬ.md` обновлены новыми Telegram-командами.
- Дочерний `python.exe` monitor перезапущен, новый PID `33256`; monitor PID остался `31956`.
- В Telegram отправлен вводный текст и полный `/report`-эквивалент.

## Проверки

- `py_compile` для `telegram_bot.py` и `tests/test_core.py`: OK.
- `python -m unittest discover -s tests`: 45 tests OK.
- `tools/check-telegram-bot-health.ps1 -Json`: `OK`, monitor PID `31956`, python PID `33256`.
- Прямой send через Telegram API: `telegram-report-sent`.

## Ограничения

- Запуск модели остается видимым через `tools/run-wc-model.ps1`, потому что он обновляет линию, ходит в сеть и пишет артефакты.
- Telegram-команды отправляют уже собранные отчеты. После нового видимого прогона модели пользователь может вызвать `/report`.
