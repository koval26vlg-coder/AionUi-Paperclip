# Отчёт агента

- Дата и время: 2026-06-18
- Агент: Claude Code

## Запрос пользователя

Сделать проект мощнее, надёжнее и стабильнее — начать с топ-3 рекомендаций.

## Краткий план

- #1 FTS5-фоллбэк семантического поиска (когда Ollama недоступна).
- #2 Heartbeat watcher + проверка свежести в статус-скрипте.
- #3 Verify бэкапа БД (integrity + сверка числа записей).
- #7/#8 CI на GitHub Actions + unit-тест `normalize_author`.

## Что сделано

- **FTS5-фоллбэк.** Миграция схемы БД v2: `records_fts` (FTS5, unicode61 remove_diacritics) + триггеры синхронизации по rowid. Метод `TemporalStore.text_search` с безопасным построением MATCH (`_build_fts_match`: префиксные термы в кавычках, защита от инъекций синтаксиса FTS5). В `mcp_adapter._tool_semantic_query` добавлена деградация: при `engine=None` или `IOErrorSML` в рантайме — текстовый поиск, ответ помечается `mode="text"`, `degraded=true`. Память остаётся искабельной без Ollama.
- **Heartbeat.** `tools/watch-memory.ps1` пишет `logs/memory-auto.heartbeat` (ISO 8601 UTC) каждый цикл. `tools/status-memory-auto.ps1` парсит метку и выдаёт OK/STALE/MISSING (порог 120 c).
- **Verify бэкапа.** `tools/backup-sml.py`: функция `verify_backup` (PRAGMA integrity_check + сверка `COUNT(*)`), флаг `--verify`. Watcher вызывает `--if-stale --verify`.
- **CI + тест.** `.github/workflows/ci.yml` (selfcheck + pytest на push/PR с фильтром путей). `tools/sml/tests/test_validation.py` — параметрический тест карты `normalize_author`.

## Изменённые файлы

- `tools/sml/temporal_store.py` (миграция v2, `text_search`, `_build_fts_match`)
- `tools/sml/mcp_adapter.py` (`_semantic_text_fallback`, деградация semantic_query)
- `tools/watch-memory.ps1` (heartbeat, backup --verify)
- `tools/status-memory-auto.ps1` (проверка heartbeat)
- `tools/backup-sml.py` (verify_backup, --verify)
- `tools/sml/tests/test_fts_fallback.py` (новый), `tools/sml/tests/test_validation.py` (новый)
- `tools/sml/tests/test_temporal_store.py` (миграции [1,2]), `tools/sml/tests/test_e2e.py` (нормализация — из прошлой сессии)
- `.github/workflows/ci.yml` (новый)
- `docs/decisions.md`, `docs/tasks.md`, `docs/current-context.md`

## Проверки

- `pytest tools/sml/tests` → **163 passed** (+21: 6 FTS, 5 validation, прочие)
- FTS5 на живой БД: миграция v2 применилась (227 строк индекса), русские запросы возвращают релевантные результаты
- `backup-sml.py --verify` → «227 записей, integrity ok»
- `status-memory-auto.ps1` → «Heartbeat: OK (age 41s)»
- `core.py selfcheck` → `sml-selfcheck-ok`

## Риски и ограничения

- Миграция v2 применяется к живой БД при следующем открытии store; у работающего MCP-сервера `sml` подхватится после перезапуска клиента (как и нормализация авторов).
- Синтетическая релевантность текстового фоллбэка (0.5–0.99 по позиции) — не косинус; для ранжирования это BM25 от FTS5, score только для совместимости формата.
- CI ставит lancedb/pyarrow (тяжёлые) — первый прогон может быть медленным; Ollama-тесты скипаются.

## Что проверить следующему агенту

- Перезапустить MCP `sml`, проверить `semantic_query` в обоих режимах (Ollama on/off → mode semantic/text).
- Убедиться, что GitHub Actions проходит на первом push (доступность зеркал pip для lancedb).
- Раз в день смотреть `STATUS-MEMORY-AUTO.cmd` на heartbeat OK.
