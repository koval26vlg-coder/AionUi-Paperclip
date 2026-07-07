# Отчет агента: Telegram heartbeat и калибровка исходов

Дата и время: 2026-06-24 12:37 Europe/Volgograd
Агент: Codex

## Исходный запрос
Пользователь указал, что прогнозы по сильным фаворитам расходятся с фактическими исходами, и попросил научить систему предсказывать исходы матчей независимо от букмекерской линии. В ходе проверки также подтвердилось, что Telegram-бот снова выглядел зависшим из-за stale state.

## План
- Защитить главный прогноз от выбора голевых рынков вместо исхода 1X2.
- Добавить калибровку для сценария сильного фаворита при слабом контексте состава/травм.
- Исправить heartbeat Telegram poll loop, чтобы health не считал живой процесс зависшим при отсутствии новых updates.
- Проверить тестами и перезапустить видимый monitor.

## Что сделано
- В `src/sports_betting_analytics/telegram_bot.py` главный прогноз для `/forecast`, `/best` и блока матча ранжируется по 1X2-исходам; рынки тоталов/фор остаются в `/events` и списках рынков.
- Добавлен draw-trap профиль: при низком качестве контекста и непроверенных составах уверенность сильного фаворита ограничивается, а ничья получает осторожную поправку.
- В Telegram-тексте теперь показывается различие между модельной вероятностью и откалиброванной уверенностью, включая причину калибровки.
- В `run_bot` добавлен heartbeat state: `polling` перед запросом, `idle` после успешного цикла, `polling_error` при ошибке, `stopped` при остановке.
- Добавлены регрессионные тесты для heartbeat без новых Telegram updates и draw-trap калибровки.

## Измененные файлы
- `C:\Users\koval\Documents\New project\src\sports_betting_analytics\telegram_bot.py`
- `C:\Users\koval\Documents\New project\tests\test_core.py`
- `C:\Users\koval\Documents\New project\tests\test_real_forecast.py`

## Проверки
- Targeted unittest: heartbeat, 1X2 главный прогноз, full match 1X2, draw-trap калибровка — OK.
- `python -m py_compile src\sports_betting_analytics\telegram_bot.py` — OK.
- `python -m unittest discover -s tests -v` — 68 tests OK.
- Видимый Telegram monitor перезапущен через `tools/start-telegram-bot-monitor-visible.ps1 -ForceRestart`.
- `tools/check-telegram-bot-health.ps1 -Json` вернул `status: OK`, monitor PID `30000`, python PID `24856`, state age `0.31` minutes.

## Риски и ограничения
- Это не гарантирует угадывание исходов; правка снижает ложную уверенность, когда у модели нет свежего контекста.
- Для настоящего обучения нужна следующая итерация: журнал фактических результатов, post-match scorecard, calibration/backtest по 1X2, ничьим и low-scoring матчам.

## Что проверить следующему агенту
- Отправить в Telegram `/forecast 3`, `/best` и `/events` и убедиться, что главный прогноз идет по 1X2, а остальные рынки доступны отдельно.
- Начать отдельный слой post-match scorecard, чтобы модель училась на промахах вроде фаворит сыграл 0-0.
