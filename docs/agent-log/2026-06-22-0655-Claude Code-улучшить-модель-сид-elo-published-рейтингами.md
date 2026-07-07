# Claude Code — 2026-06-22T06:55:26.422Z

## Запрос
Улучшить модель: сид Elo published-рейтингами, голевая разница, нейтральное поле.

## Результат
core.py: initial_ratings сид, goal_difference_multiplier, Fixture.neutral, train_since. cli.py: --elo-seed, --train-since. Загружены реальные Elo всех 48 сборных с eloratings.net -> data/manual/elo_seed.csv. Published Elo используется напрямую (train_since в будущее), т.к. уже включает голевую разницу и форму. РЕЗУЛЬТАТ: from-scratch давал 14-15 watch с абсурдом (Тунис-Нидерланды +314%); published дал 0 кандидатов + 5 трезвых watch (EV 8-22%). Колумбия(1998) выше Португалии(1967) по Elo, рынок против. Запуск: tools/run-wc-model.ps1. 24 теста OK. Травмы/составы честно не имитируются — нужен ручной слой поправок.

## Изменённые файлы
- src/sports_betting_analytics/core.py
- src/sports_betting_analytics/cli.py
- data/manual/elo_seed.csv
- tools/run-wc-model.ps1
- tools/build_watchlist.py
- tests/test_core.py
