# Codex — 2026-06-23

## Запрос
Реализовать Real-Forecast слой для Telegram-прогнозов: контекст матча, качество данных, источники, Telegram блоки и visible pipeline.

## План
Добавить match_intelligence + CLI intelligence; подключить в /forecast, /best, /match, /health; обновить run-wc-model.ps1, тесты и docs.

## Результат
Готово: sports_betting_analytics intelligence пишет data/intel/match_context.json и out/wc_real_forecast.md. Telegram /forecast показывает лучший прогноз периода + 3 кандидата и реальный контекст; /best и /match показывают этот контекст перед рынками. Confidence снижается при низком data_quality. Добавлены FIFA tie-break mini-table, freshness gates, expert scorecard и injury/suspension deltas. run-wc-model.ps1 запускает intelligence видимым шагом 3/4. Сгенерировано 32 match contexts. Проверка: py_compile OK, unittest discover 64 tests OK.

## Изменённые файлы
- C:/Users/koval/Documents/New project/src/sports_betting_analytics/match_intelligence.py
- C:/Users/koval/Documents/New project/src/sports_betting_analytics/cli.py
- C:/Users/koval/Documents/New project/src/sports_betting_analytics/telegram_bot.py
- C:/Users/koval/Documents/New project/tools/run-wc-model.ps1
- C:/Users/koval/Documents/New project/tests/test_real_forecast.py
- C:/Users/koval/Documents/New project/README.md
- C:/Users/koval/Documents/New project/КАК_РАБОТАТЬ.md
- C:/Users/koval/Documents/New project/data/intel/match_context.json
- C:/Users/koval/Documents/New project/out/wc_real_forecast.md

## Риски и ограничения
v1 без скрытых сетевых collectors; RotoWire/API-Football пока только как source contract/links. Если составы/травмы отсутствуют, quality low и бот пишет риск.

## Что следующему агенту
При появлении API_FOOTBALL ключа или HTML snapshots добавить видимый collector. После исходов вести expert_scorecard.csv.
