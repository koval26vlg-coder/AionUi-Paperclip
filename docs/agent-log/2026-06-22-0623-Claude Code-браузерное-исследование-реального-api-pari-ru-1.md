# Claude Code — 2026-06-22T06:23:46.096Z

## Запрос
Браузерное исследование реального API pari.ru (категория 136181).

## Результат
pari.ru — client-side SPA, данные через REST API: host line-lb01-w.pb06e2-resources.com (резерв line-lb51-w), GET /events/listBase?lang=ru&scopeMarket=2300. events[] (id, sportId=ID категории, team1/team2, startTime unix), customFactors[] (e=eventId, factors[{f,v}]). 1X2: f921=П1, f922=X, f923=П2 (подтверждено Аргентина-Австрия 1.5/4.3/7.3). URL: pari.ru/sports/football/category/internationalteams/{sportId}/{eventId}. pari_fetcher.py переписан с парсинга HTML на прямой API + gzip-распаковка. Живой тест из Python: 34 матча найдено, search вернул верные коэффициенты. listBase публичный, авторизация не нужна.

## Изменённые файлы
- src/sports_betting_analytics/pari_fetcher.py
