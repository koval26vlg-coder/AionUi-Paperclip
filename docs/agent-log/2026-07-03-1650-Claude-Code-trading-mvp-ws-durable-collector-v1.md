# trading_mvp: durable сегментированный WS-коллектор реализован и проверен kill-тестом

Дата: 2026-07-03 ~16:50 +03
Агент: Claude Code

## Исходный запрос

Пользователь одобрил реализацию hardening-плана после ревью падения ws_collect_72h_sweep_visible_20260702_101730 (см. `2026-07-03-1400-Claude-Code-review-codex-ws-collect-failure-analysis.md`): detached collector + child-owned manifest, сегментация со stitching/gap accounting, фикс footgun `_latest_ws_input`.

## Что сделано

### 1. `trading_mvp/src/ws_durable_collector.py` (новый)

- Сегментированный сбор: ран режется на сегменты (default 3ч), каждый — папка `seg_NNN/` с raw + собственным финальным manifest.json; переиспользует проверенный `ws_collector.collect_ws_markets`.
- Child-owned state: `state.json` атомарно (tmp+os.replace) каждые 30с — heartbeat, сегмент, размеры raw, ошибки; обработчики SIGINT/SIGTERM/SIGBREAK пишут `terminated_by_signal_*`.
- Stitching: run-manifest `ws_collect_<run_id>.json` с coverage_ratio, gaps между сегментами, `collector_exit_reason`.
- Постфактум `finalize`: собирает stitched manifest даже после смерти процесса; незавершённые сегменты учитываются по fs (raw без manifest); инференс причины: status=running + heartbeat старше 120с → `killed_externally_inferred_stale_heartbeat`.
- CLI: `collect` / `finalize` / `status`.

### 2. PowerShell-контур

- `tools/start_ws_collect_durable.ps1`: detached-запуск (жизнь коллектора не зависит от окон), `launch.json` с pid/command/paths/status_check/finalize_cmd, авто-открытие watcher-окна.
- `tools/watch_ws_collect_durable.ps1`: наблюдатель read-only по state.json, подсветка stale heartbeat; закрытие окна безвредно.

### 3. Фикс footgun `cli.py::_latest_ws_input`

Автовыбор входа для ws-normalize/ws-postprocess теперь отказывает при: (а) raw новее последнего manifest (сценарий partial run из инцидента), (б) manifest c completed=false. Явный input всегда работает.

### 4. Документация

`docs/ws-durable-collect-runbook.md` — архитектура, команды, интерпретация exit_reason, gate-протокол для durable-ранов.

## Проверки

- Юнит-тесты: 15 новых (stitch/gaps/инференс/парсинг/guard) + существующие ws-модули = 31 OK.
- **Verification run** `ws_durable_verify1` (2×60с, реальные WS mexc+gateio): completed=true, coverage 0.9984, 9,418 событий, оба сегментных manifest'а на месте. Попутно найден и исправлен баг порядка state→stitch в finally.
- **Kill test** `ws_durable_killtest` (3×60с, hard kill pid посреди сегмента 2 — имитация инцидента): state завис как running/unknown (как в реале), `finalize` постфактум дал `killed_externally_inferred_stale_heartbeat`, seg_001 сохранён как полные данные (3,981 событий), seg_002 честно incomplete, coverage 0.5238. Артефакты обоих ранов оставлены в `exports/trading-mvp/raw-durable/` как evidence.

## Изменённые файлы

- `trading_mvp/src/ws_durable_collector.py`, `trading_mvp/tests/test_ws_durable_collector.py` (новые)
- `trading_mvp/tests/test_cli_ws_input_guard.py` (новый)
- `trading_mvp/src/cli.py` (только `_latest_ws_input`)
- `tools/start_ws_collect_durable.ps1`, `tools/watch_ws_collect_durable.ps1` (новые)
- `docs/ws-durable-collect-runbook.md` (новый)

## Что осталось (для Codex/следующего шага)

1. Интеграция guards прежнего visible-контура (preflight, density, schema probe) в durable-путь.
2. Verification run 2–3ч (по рекомендации Codex) перед новым 72ч: `start_ws_collect_durable.ps1 -TotalSec 7200 -SegmentSec 3600` с боевым universe.
3. Обновить data-quality gate: принимать stitched manifest (coverage_ratio/gaps пороги).
4. Прежние TRADING_START_DENSE_WS_CONFIRMED.cmd — переключить на durable-путь после интеграции guards.

Live orders/API keys/leverage не затрагивались; research-only.
