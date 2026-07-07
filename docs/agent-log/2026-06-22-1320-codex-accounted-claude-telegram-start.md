# 2026-06-22 13:20 +03 — Codex — Accounted Claude changes and Telegram start

## Исходный запрос

Пользователь сообщил, что проект не запускается и нужно автоматизировать через Telegram, затем попросил учесть все изменения Claude.

## Что учтено

- Claude добавил текущий рабочий конвейер `tools/run-wc-model.ps1`.
- Новые компоненты проекта:
  - `src/sports_betting_analytics/pari_fetcher.py`
  - `src/sports_betting_analytics/xg_model.py`
  - `src/sports_betting_analytics/markets.py`
  - `src/sports_betting_analytics/adjustments.py`
  - `tools/build_compare.py`
  - `tools/build_markets.py`
  - `tools/build_markets_compare.py`
  - `tools/build_watchlist.py`
  - `tools/run-wc-model.ps1`
  - `КАК_РАБОТАТЬ.md`
- Текущий `data/signals/current_signal.json`: `Аргентина - Австрия`, PARI event `64971867`, `П1 Аргентина`, вход `1.45+`.
- Тестовый набор теперь 42 tests.

## Что сделано

- Health-check сначала показал `NO_PYTHON_CHILD`: monitor PID `26184` был жив, но без дочернего `python.exe`, state heartbeat stale.
- Исправлен `tools/start-telegram-bot-monitor-visible.ps1`: если metadata указывает на monitor без `python.exe`, launcher теперь заменяет такой процесс автоматически, а не считает его нормальным состоянием.
- Запущен новый visible monitor через:

```powershell
& "C:\Users\koval\Documents\New project\tools\start-telegram-bot-monitor-visible.ps1" -ForceRestart
```

- Новый monitor PID `31956`, child `python.exe` PID `32376`.
- Health после полного polling-интервала: `OK`.
- Проверен актуальный Claude-конвейер:

```powershell
& "C:\Users\koval\Documents\New project\tools\run-wc-model.ps1" -SkipLineRefresh
```

Результат: команда успешно собрала `out/wc_compare.md`, `out/wc_markets_compare.md`, `out/wc_watchlist.md`; 96 сигналов, 0 candidate, 5 longshot_watch.

## Проверки

- `python -m unittest discover -s tests`: 42 tests OK.
- `tools/start-telegram-bot-monitor-visible.ps1` parser: OK.
- `tools/check-telegram-bot-health.ps1 -Json`: `OK`, monitor PID `31956`, python PID `32376`.

## Следующему агенту

- Не использовать старую картину проекта до Claude; актуальная инструкция — `КАК_РАБОТАТЬ.md`.
- Для проекта: `tools/run-wc-model.ps1`.
- Для Telegram runtime: `tools/start-telegram-bot-monitor-visible.ps1`, затем `tools/check-telegram-bot-health.ps1`.
- Если health показывает `NO_PYTHON_CHILD`, перезапускать через launcher; скрипт уже умеет заменить такой monitor.
