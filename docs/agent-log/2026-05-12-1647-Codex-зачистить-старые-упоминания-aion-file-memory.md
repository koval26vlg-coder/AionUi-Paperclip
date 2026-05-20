# Codex — 2026-05-12T16:47:12.593Z

## Запрос
Зачистить старые упоминания aion-file-memory и привести документы к линии SML = основная память

## Результат
Документы START-HERE, current-context, mcp-memory, local-environment, kiro-russian-check, tasks, decisions и rollback-sml обновлены под SML. Исправлена опечатка slayer -> слоя. Найден и исправлен баг TemporalStore.supersede с коллизией records_history.valid_from в одной миллисекунде. Добавлена обработка notifications/initialized без ошибочного ответа. Полный pytest: 141 passed.

## Изменённые файлы
- docs/START-HERE.md
- docs/current-context.md
- docs/mcp-memory.md
- docs/local-environment.md
- docs/kiro-russian-check.md
- docs/tasks.md
- docs/decisions.md
- docs/rollback-sml.md
- .kiro/specs/agents-shared-memory-layer/tasks.md
- tools/sml/temporal_store.py
- tools/sml/mcp_adapter.py
- tools/sml/tests/test_mcp_adapter.py

## Риски и ограничения
Живой smoke-тест Cursor UI требует запуска внутри Cursor, из командной строки проверены MCP stdio и конфиги.

## Что следующему агенту
Открыть Cursor и Kiro UI, вызвать sml.ping, sml.startup_pack, sml.semantic_query и sml.add_log из каждого интерфейса.
