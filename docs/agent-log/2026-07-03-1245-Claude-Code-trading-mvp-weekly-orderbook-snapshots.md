# trading_mvp: стаканы watchlist добавлены в weekly forward

Дата: 2026-07-03 ~12:45 +03
Агент: Claude Code

## Исходный запрос

«Да делай» — добавить снятие стаканов кандидатов в еженедельную обёртку для усреднения ёмкости по времени.

## Что сделано

1. `trading_mvp/src/execution_gate.py`: добавлена `select_candidates()` — динамический watchlist из свежего pairs-отчёта (E-ноги ≥20%/год со спотом MEXC, max 8 + G-спреды ≥15%/год с consistency ≥0.75, max 6, dedup) и флаг `--auto-candidates`. Watchlist эволюционирует с данными, а не зафиксирован на сегодняшних именах.
2. `tools/run_weekly_forward_collect.ps1`: третий шаг — execution_gate с `--auto-candidates` по свежему pairs JSON; артефакт `exports/trading-mvp/analysis/execution_gate_forward_<дата>.json`; вывод включён в weekly md-отчёт (секции Funding pairs / Execution gate); gate_exit учитывается в exit code.
3. Тесты: +3 на select_candidates (отбор/dedup/капы/пусто), всего 11 OK в test_execution_gate.
4. Проверки: авто-отбор на реальном pairs-отчёте даёт 11 разумных кандидатов (BROCCOLIF3B, SKYAI, ESPORTS, BEAT, EVAA, BAS, PIPPIN, TAC, RAVE, M, NOM); сквозной smoke обёртки (2 символа) прошёл с exit 0, включая граничный случай пустого watchlist; smoke-артефакты удалены.

## Как использовать накопленное

Через 3–4 недели: усреднить capacity/spread по `execution_gate_forward_*.json` вместо одноточечного снапшота; сверить деградацию funding-кандидатов по `funding_pairs_forward_*.json`; заменить persistence haircut 0.5 фактом.

## Статус установки

Scheduled task по-прежнему ждёт двойного клика пользователя по `INSTALL_WEEKLY_FORWARD_COLLECT.cmd` (понедельник 09:05).

## Изменённые файлы

- `trading_mvp/src/execution_gate.py`, `trading_mvp/tests/test_execution_gate.py`
- `tools/run_weekly_forward_collect.ps1`
