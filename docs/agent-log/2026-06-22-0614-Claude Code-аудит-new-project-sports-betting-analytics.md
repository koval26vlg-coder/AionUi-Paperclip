# Claude Code — 2026-06-22T06:14:49.338Z

## Запрос
Аудит New project (sports betting analytics) + интеграция pari.ru

## Результат
5 дефектов исправлено: (1) DEFAULT_SETTINGS bankroll 10000→1000; (2) мёртвый код в telegram_bot.py удалён; (3) crash-guard для missing chat.id в handle_message/callback; (4) save_state стала атомарной (tmp+replace); (5) cli.py теперь кидает FileNotFoundError на явно несуществующий config. Создан pari_fetcher.py с fetch_event, fetch_odds_from_event_url, check_line_threshold, build_signal_json, CLI. Инструменты: pari-check-line.ps1, pari-search-event.ps1. 20 тестов, все OK.

## Изменённые файлы
- src/sports_betting_analytics/core.py
- src/sports_betting_analytics/telegram_bot.py
- src/sports_betting_analytics/cli.py
- src/sports_betting_analytics/pari_fetcher.py
- tools/pari-check-line.ps1
- tools/pari-search-event.ps1
- tests/test_core.py

## Что следующему агенту
Проверить реальный ответ pari.ru через DevTools Network → найти API-endpoint → подставить в PARI_CATEGORY_URL. Затем: pyproject.toml (P3-1) и новый current_signal.json.
