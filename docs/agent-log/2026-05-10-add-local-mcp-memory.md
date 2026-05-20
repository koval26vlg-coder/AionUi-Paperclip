# Добавление локальной MCP-памяти

## Дата и время

2026-05-10

## Агент

Codex

## Исходный запрос пользователя

Продолжить настройку общей базы контекста так, чтобы разные агенты и модели могли использовать одну память и быть взаимозаменяемыми.

## Контекст перед началом

Файловая память v1 уже была создана, но агенты могли работать с ней только как с файлами. Нужен был следующий слой, который можно подключить через MCP.

## Что сделано

Добавлен локальный MCP-сервер `aion-file-memory`.

Сервер работает поверх файлов в `D:\AionUi-Paperclip` и предоставляет инструменты:

- `read_context_pack`
- `search_memory`
- `add_memory`
- `add_agent_log`
- `create_handoff`
- `build_context_pack`

Добавлены MCP-конфиги для Cursor и Kiro.

`aion-file-memory` добавлен в глобальный конфиг Codex CLI через `codex mcp add`.

## Измененные файлы

- `tools/aion_memory_mcp.py`
- `.cursor/mcp.json`
- `.kiro/settings/mcp.json`
- `C:\Users\koval\.codex\config.toml`
- `docs/mcp-memory.md`
- `docs/memory/architecture.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/memory/layers/timeline.md`
- `docs/agent-log/2026-05-10-add-local-mcp-memory.md`

## Проверки

Проверен синтаксис Python-сервера.

Проверена валидность JSON-конфигов Cursor и Kiro.

Выполнен реальный MCP-handshake:

- `initialize` вернул сервер `aion-file-memory`;
- `tools/list` вернул список инструментов;
- `tools/call search_memory` успешно нашел записи по запросу `Codex Cursor Kiro`.

Проверен `codex mcp list`: сервер `aion-file-memory` отображается со статусом `enabled`.

## Решения

Так как Docker/Podman не найдены, Graphiti MCP не устанавливался сейчас. Вместо этого создан легкий локальный MCP-сервер на файлах, который не зависит от подписок, API-ключей и внешней базы данных.

## Риски и ограничения

Это не графовая память и не семантическая база. Поиск пока простой текстовый. Для следующего уровня можно подключить Graphiti MCP или Mem0/OpenMemory.

## Что должен проверить следующий агент

Открыть Cursor и Kiro, проверить, видят ли они MCP-сервер `aion-file-memory`, и выполнить в них тестовый запрос к памяти.
