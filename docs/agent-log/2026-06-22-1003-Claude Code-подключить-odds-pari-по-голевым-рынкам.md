# Claude Code — 2026-06-22T10:03:22.695Z

## Запрос
Подключить odds pari по голевым рынкам для сравнения БК vs модель.

## Результат
Маппинг factor ID -> рынок верифицирован по каталогу pari (factorsCatalog/sportBasicFactors): тотал over=930.., under=931..; фора ФОРА1/ФОРА2; ИТ1/ИТ2; BTTS 4241/4242. В pari_fetcher добавлены наборы ID, extract_event_markets (тотал/фора/инд.тоталы/BTTS с линией из pt), команда export-markets -> data/manual/pari_markets.csv (1848 строк). tools/build_markets_compare.py показывает БК% (без маржи) vs наша% (Пуассон от xG) по тоталу 2.5, BTTS, форе -1.5, ИТ 1.5. Подключено в run-wc-model.ps1. Ключевое расхождение Португалия-Узбекистан: BTTS да БК40%/наша59%, фора -1.5 БК59%/наша37% — последовательно по всем рынкам. 42 теста OK (добавлен тест на верность over/under маппинга).

## Изменённые файлы
- src/sports_betting_analytics/pari_fetcher.py
- tools/build_markets_compare.py
- tools/run-wc-model.ps1
- tests/test_core.py
- data/manual/pari_markets.csv

## Что следующему агенту
Полный конвейер: tools/run-wc-model.ps1 показывает 1X2 (build_compare) и голевые рынки (build_markets_compare). Отчёты в out/wc_compare.md, wc_markets_compare.md.
