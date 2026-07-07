# Отчет агента

## Дата и время

2026-06-21 18:57 +03:00

## Агент

Codex

## Исходный запрос пользователя

Пользователь попросил настроить систему прогнозов и аналитики, чтобы вручную делать ставки.

## Контекст перед началом

- Использован предыдущий workflow `sports-betting-automation-risk-bounded-workflow`, где разрешен только analytics/paper-trading/manual decision-support контур.
- Active run gate по `trading_mvp` оставался `RUNNING`; новые long-running collectors/backtests/grid-search/paper-forward не запускались.
- Рабочая папка `C:\Users\koval\Documents\New project` была пустой, кроме `.git`.

## План

1. Создать локальный MVP без bookmaker integration.
2. Использовать ручные CSV как входы.
3. Считать no-vig probabilities, простой Elo-shrinkage, EV и risk gates.
4. Генерировать CSV/HTML отчет для ручного решения.
5. Добавить ledger для ручного учета фактических ставок.

## Что сделано

- Создан Python package `src/sports_betting_analytics`.
- Добавлены CSV-шаблоны `fixtures.csv`, `results.csv`, `odds_1x2.csv`, `manual_bets.csv`.
- Реализованы no-vig baseline, Elo update, market/model probability mix, EV, Kelly fraction, stake cap, статусы `candidate`, `longshot_watch`, `skip`.
- Добавлен HTML report `out/report.html` и signals CSV `out/signals.csv`.
- Добавлен manual ledger CLI с `out/ledger_summary.csv`.
- Добавлен PowerShell запускатель `tools/run-manual-signals.ps1`.
- Добавлены unit tests.

## Измененные файлы

- `C:\Users\koval\Documents\New project\README.md`
- `C:\Users\koval\Documents\New project\config\default.json`
- `C:\Users\koval\Documents\New project\data\manual\*.csv`
- `C:\Users\koval\Documents\New project\src\sports_betting_analytics\*.py`
- `C:\Users\koval\Documents\New project\tests\test_core.py`
- `C:\Users\koval\Documents\New project\tools\run-manual-signals.ps1`
- `D:\AionUi-Paperclip\docs\current-context.md`
- `D:\AionUi-Paperclip\docs\tasks.md`
- `D:\AionUi-Paperclip\docs\agent-log\2026-06-21-1857-codex-manual-betting-analytics-mvp.md`

## Проверки

- `$env:PYTHONPATH="src"; & "C:\Users\koval\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m unittest discover -s tests` - 5 tests OK.
- `.\tools\run-manual-signals.ps1` - созданы `out/signals.csv` и `out/report.html`, 6 sample-сигналов.
- `python -m sports_betting_analytics ledger --bets data/manual/manual_bets.csv --output out/ledger_summary.csv` - создан ledger summary.

## Решения

- Использовать bundled Python, потому что системный `python` не найден в PATH.
- Держать MVP на standard library без внешних зависимостей и API keys.
- Не подключать реальные БК, не хранить bookmaker credentials и не автоматизировать размещение ставок.

## Риски и ограничения

- Sample CSV не является реальным прогнозом; пользователь должен заменить строки на реальные данные из легального источника.
- Elo-shrinkage - базовая модель, пригодная как стартовый baseline, но не как доказанный edge.
- Live-сценарии требуют отдельного разрешенного data feed и сначала paper-mode.
- Это не юридическая, финансовая или азартно-игровая рекомендация.

## Что должен проверить следующий агент

- Если пользователь даст реальные CSV, сначала валидировать данные и не запускать долгий backtest без visible run rule.
- Следующий технический шаг: добавить отдельный `validate` CLI и поддержку 1X2 snapshots по нескольким букмекерам с выбором лучшего odds per selection.
- Не двигаться в сторону auto-click или bookmaker writes без отдельного legal/compliance gate.
