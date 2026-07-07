# Codex — 2026-06-23

## Запрос
Реализовать Real-Forecast слой для Telegram-прогнозов: match_intelligence, контекст матча, источники/качество данных, Telegram блоки, visible pipeline и тесты.

## План
1. Добавить tests/test_real_forecast.py для мотивации, freshness, scorecard, deltas и Telegram карточек. 2. Реализовать src/sports_betting_analytics/match_intelligence.py и CLI intelligence. 3. Интегрировать контекст в /forecast, /best, /match и /health. 4. Подключить шаг к tools/run-wc-model.ps1. 5. Обновить README/КАК_РАБОТАТЬ и проверить тесты.

## Результат
Добавлен real-forecast слой. CLI sports_betting_analytics intelligence пишет data/intel/match_context.json и out/wc_real_forecast.md. Telegram /forecast показывает лучший прогноз периода + 3 кандидата и реальный контекст; /best и /match получают блок реального контекста перед рынками. Ранжирование снижает confidence при плохом data_quality и сортирует по скорректированной вероятности/качеству данных. Реализованы FIFA tie-break mini-table, freshness gates, expert scorecard и mapping injuries/suspensions to Adjustment. tools/run-wc-model.ps1 теперь видимо запускает intelligence как шаг 3/4. Сгенерированы текущие артефакты: 32 scheduled match contexts.

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
v1 не делает сетевой парсинг RotoWire/API-Football и не автокликает БК; при отсутствии составов/травм data_quality низкий и confidence снижается. Git не был в PATH, использован только абсолютный путь для статуса; репозиторий выглядит полностью untracked.

## Что следующему агенту
При появлении API_FOOTBALL ключа или устойчивых HTML snapshots добавить отдельный видимый collector/fixture parser. После реальных исходов начать заполнять expert_scorecard.csv и повышать вес источников только после накопленной проверки.
