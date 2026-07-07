# Claude Code — 2026-06-22T06:55:14.965Z

## Запрос
Улучшить модель ставок: сид Elo published-рейтингами, голевая разница, нейтральное поле, форма.

## Результат
core.py: добавлены сид initial_ratings, goal_difference_multiplier (World Football Elo), per-fixture neutral (Fixture.neutral), train_since фильтр. cli.py: --elo-seed, --train-since. Загружены реальные опубликованные Elo всех 48 сборных с eloratings.net -> data/manual/elo_seed.csv (RU имена). Решение: использовать published Elo напрямую (train_since в будущее), т.к. он уже включает голевую разницу и форму — переобучение было бы двойным счётом. РЕЗУЛЬТАТ: шум устранён. From-scratch давал 14-15 watch с абсурдным EV (Тунис-Нидерланды +314%); published Elo дал 0 кандидатов + всего 5 трезвых watch (EV 8-22%). Интересное расхождение: Колумбия(1998 Elo) выше Португалии(1967), рынок ставит Португалию. Единый запуск: tools/run-wc-model.ps1. 24 теста OK.

## Изменённые файлы
- src/sports_betting_analytics/core.py
- src/sports_betting_analytics/cli.py
- data/manual/elo_seed.csv
- tools/run-wc-model.ps1
- tools/build_watchlist.py
- tests/test_core.py
- out/wc_watchlist.md

## Что следующему агенту
Честно отказался имитировать травмы/составы/физуху из воздуха — для них нужен явный слой ручных поправок. Кандидатов нет: линия pari эффективна. Можно поднять alpha (доля Elo в смеси) для большего числа сигналов с большим риском.
