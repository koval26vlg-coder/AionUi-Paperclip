# Codex — 2026-06-23

## Запрос
Реализовать Real-Forecast слой для Telegram-прогнозов.

## План
match_intelligence + CLI; Telegram /forecast,/best,/match,/health; visible run-wc-model; tests/docs.

## Результат
Готово. Добавлен sports_betting_analytics intelligence: пишет data/intel/match_context.json и out/wc_real_forecast.md. Telegram /forecast теперь: лучший прогноз периода + 3 кандидата + реальный контекст; /best и /match показывают контекст перед рынками. Confidence снижается при low data_quality. Добавлены FIFA tie-break mini-table, freshness gates, expert scorecard, injury/suspension deltas. run-wc-model.ps1 запускает intelligence видимым шагом. Проверка: py_compile OK, unittest discover 64 OK.

## Изменённые файлы
- New project/src/sports_betting_analytics/match_intelligence.py
- New project/src/sports_betting_analytics/cli.py
- New project/src/sports_betting_analytics/telegram_bot.py
- New project/tools/run-wc-model.ps1
- New project/tests/test_real_forecast.py
- New project/README.md
- New project/КАК_РАБОТАТЬ.md

## Риски и ограничения
v1 без скрытых сетевых collectors; при отсутствии составов/травм quality low.

## Что следующему агенту
Добавить видимый collector при наличии API_FOOTBALL ключа/HTML snapshots; вести expert_scorecard.csv после исходов.
