# Claude Code — 2026-06-22T06:23:38.911Z

## Запрос
Браузерное исследование реального API pari.ru для рабочей автоматизации (категория 136181).

## Результат
pari.ru — client-side SPA, данные через REST API на хосте line-lb01-w.pb06e2-resources.com (резерв line-lb51-w). Endpoint: GET /events/listBase?lang=ru&scopeMarket=2300. Структура: events[] (id, sportId=ID категории, team1, team2, startTime unix), customFactors[] (e=eventId, factors[{f,v}]). Факторы 1X2 подтверждены: f921=П1, f922=X, f923=П2 (Аргентина-Австрия 1.5/4.3/7.3). URL события: pari.ru/sports/football/category/internationalteams/{sportId}/{eventId}. pari_fetcher.py переписан на прямой вызов API (был парсинг __NEXT_DATA__ — не работал). Добавлена gzip-распаковка (API отдаёт gzip без заголовка). Живой тест из Python: list нашёл 34 матча категории 136181, search Аргентина/Австрия вернул верные коэффициенты. 20 тестов OK. listBase публичный — авторизация НЕ требуется.

## Изменённые файлы
- src/sports_betting_analytics/pari_fetcher.py

## Что следующему агенту
Опционально: добавить категории в KNOWN_CATEGORIES по мере появления других турниров (slug->sportId). Для регулярного мониторинга использовать tools/pari-check-line.ps1.
