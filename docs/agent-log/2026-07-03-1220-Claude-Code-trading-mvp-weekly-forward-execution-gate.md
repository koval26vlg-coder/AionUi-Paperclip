# trading_mvp: weekly forward настроен (ждёт клика установки) + execution gate v1 выполнен

Дата: 2026-07-03 ~12:20 +03
Агент: Claude Code

## Исходный запрос

Пользователь подтвердил план: (1) еженедельный scheduled forward-сбор, (2) execution gate по топ-кандидатам carry.

## Что сделано

### Weekly forward collect

- `tools/run_weekly_forward_collect.ps1` — обёртка: daily_collector (top-200, 200 дней, run-id `daily_forward_<дата>`) → funding_pairs пересчёт → md-отчёт в `docs/analysis/funding-forward/` → лог в `logs/weekly-forward/`. Smoke-тест прошёл (BTC/ETH, basis std ~1bps подтверждает валидность метрики); smoke-артефакты удалены.
- Прямая регистрация scheduled task заблокирована auto-mode классификатором (persistence требует явной авторизации) — сделано по конвенции проекта: `INSTALL_WEEKLY_FORWARD_COLLECT.cmd` (понедельник 09:05), `UNINSTALL_...cmd`, `STATUS_...cmd`. **Ожидает двойного клика пользователя по INSTALL.**
- Метаданные по Visible Run Rule: команда `pwsh -NoProfile -File tools\run_weekly_forward_collect.ps1`, cwd = корень проекта, ожидаемая длительность ~4-6 мин, выходы: manifest в `exports/trading-mvp/daily/daily_forward_*/`, отчёт `docs/analysis/funding-forward/funding_forward_*.md`, лог `logs/weekly-forward/*.log`. Проверка статуса: `STATUS_WEEKLY_FORWARD_COLLECT.cmd`.

### Execution gate v1

- Модуль `trading_mvp/src/execution_gate.py` + `tests/test_execution_gate.py` (8 OK). Стаканы MEXC spot/perp + Gate perp, полосы ±25/50/100 bps, ёмкость = min(20% глубины ±50bps, 0.5% оборота), экономика с persistence haircut 0.5 и спред-издержками 12 циклов/год.
- Прогон по 9 кандидатам без ошибок: `exports/trading-mvp/analysis/execution_gate_v1_20260703_091623.json`.
- **Ключевой вывод**: net-проценты живут (13-70%/год), но консервативная ёмкость крошечная ($74-$3.5K на имя); потолок 9-именного портфеля ~$1.5-3K/год. Масштаб — шириной (77 кандидатов → портфель 30-50 имён = $10-30K/год потенциала) либо признанием менее консервативной exit-модели (объёмный лимит BEAT $85K). RAVE/BROCCOLIF3B — только G-конструкция (спот мёртв).
- Документ: `docs/analysis/2026-07-03-execution-gate-v1.md`.

## Изменённые файлы

- `tools/run_weekly_forward_collect.ps1`, `INSTALL/UNINSTALL/STATUS_WEEKLY_FORWARD_COLLECT.cmd` (новые)
- `trading_mvp/src/execution_gate.py`, `trading_mvp/tests/test_execution_gate.py` (новые)
- `exports/trading-mvp/analysis/execution_gate_v1_20260703_091623.json`
- `docs/analysis/2026-07-03-execution-gate-v1.md`

## Риски и ограничения

- Scheduled task НЕ активен до клика пользователя по INSTALL.
- Execution gate v1 — один снапшот стакана; maker-fill не моделируется; haircut 0.5 — допущение до forward-факта.
- Live orders/API keys/leverage не затрагивались.

## Что дальше

1. Пользователь: двойной клик INSTALL_WEEKLY_FORWARD_COLLECT.cmd.
2. Добавить снятие стаканов кандидатов в weekly-обёртку (усреднение ёмкости по времени).
3. Через 3-4 недели forward: пересчёт персистентности, дизайн портфельного carry-контура (30-50 имён) как спецификация перед paper-forward.
