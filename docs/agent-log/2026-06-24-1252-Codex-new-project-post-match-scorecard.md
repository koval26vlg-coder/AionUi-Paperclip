# Отчет агента: post-match scorecard для Telegram-прогнозов

Дата и время: 2026-06-24 12:52 Europe/Volgograd
Агент: Codex

## Исходный запрос
Пользователь попросил добавить реальное обучение после матчей: фиксировать фактические исходы, промахи фаворитов, ничьи и 0-0, чтобы будущие Telegram-прогнозы не просто повторяли линию/модель, а калибровали уверенность по закрытым ошибкам.

## План
- Добавить post-match scorecard из локального журнала прогнозов и фактических результатов.
- Подключить scorecard к Telegram-калибровке confidence.
- Добавить Telegram-команду `/scorecard`.
- Встроить сбор scorecard в видимый `tools/run-wc-model.ps1`.
- Проверить тестами и перезапустить видимый Telegram monitor.

## Что сделано
- Создан `src/sports_betting_analytics/scorecard.py`.
- Добавлен `data/intel/forecast_journal.csv` как журнал главных прогнозов, показанных через `/forecast`, `/best`, `/match`.
- Добавлен `data/intel/post_match_scorecard.csv` и `out/post_match_scorecard.md`.
- Реализована CLI-команда `sports_betting_analytics scorecard`.
- Scorecard помечает теги `overconfident_favorite_miss`, `draw_missed`, `nil_nil_missed`.
- Telegram-кандидаты теперь получают scorecard-калибровку: cap для переоцененных фаворитов и boost для ничьих, с явной заметкой `scorecard`.
- Добавлена команда `/scorecard` и включение scorecard в `/report`, `/help`, `/health`, `/model`.
- `tools/run-wc-model.ps1` теперь выполняет шаг `[4/5] Сбор post-match scorecard`.
- Обновлены `README.md` и `КАК_РАБОТАТЬ.md`.

## Измененные файлы
- `C:\Users\koval\Documents\New project\src\sports_betting_analytics\scorecard.py`
- `C:\Users\koval\Documents\New project\src\sports_betting_analytics\telegram_bot.py`
- `C:\Users\koval\Documents\New project\src\sports_betting_analytics\cli.py`
- `C:\Users\koval\Documents\New project\tests\test_real_forecast.py`
- `C:\Users\koval\Documents\New project\tests\test_core.py`
- `C:\Users\koval\Documents\New project\tools\run-wc-model.ps1`
- `C:\Users\koval\Documents\New project\README.md`
- `C:\Users\koval\Documents\New project\КАК_РАБОТАТЬ.md`
- `C:\Users\koval\Documents\New project\data\intel\post_match_scorecard.csv`
- `C:\Users\koval\Documents\New project\out\post_match_scorecard.md`

## Проверки
- Targeted tests по scorecard и Telegram-интеграции: 13 tests OK.
- `python -m py_compile src\sports_betting_analytics\telegram_bot.py src\sports_betting_analytics\scorecard.py src\sports_betting_analytics\cli.py` — OK.
- `python -m unittest discover -s tests -v` — 74 tests OK.
- `python -m sports_betting_analytics scorecard ...` — создал текущие файлы scorecard, сейчас `0 closed`, потому что новый journal еще не содержит закрытых прогнозов.
- Видимый Telegram monitor перезапущен через `tools/start-telegram-bot-monitor-visible.ps1 -ForceRestart`.
- Health: `status OK`, monitor PID `11280`, python PID `5572`, state age `0.23` minutes.

## Риски и ограничения
- Scorecard не подгружает результаты сам из интернета; он использует локальный `wc_results.csv`.
- На первом запуске scorecard пустой, пока бот не покажет прогноз и матч не появится в результатах.
- Калибровка меняет confidence и пояснение, а не сырую модельную вероятность.

## Что проверить следующему агенту
- В Telegram отправить `/forecast 3`, затем убедиться, что `data/intel/forecast_journal.csv` пополняется.
- После обновления фактических результатов запустить `tools/run-wc-model.ps1` и проверить `/scorecard`.
