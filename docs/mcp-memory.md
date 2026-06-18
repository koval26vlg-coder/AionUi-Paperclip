# MCP-память проекта

Основной сервер памяти проекта:

```text
sml
```

`sml` — это Shared_Memory_Layer из `tools/sml/`. Он заменяет старый `aion-file-memory` как основной канал чтения и записи памяти для активной связки Codex + Gemini CLI.

## Что делает SML

SML работает локально в `D:\AionUi-Paperclip` и использует:

- SQLite WAL для долговременных `Memory_Record`;
- LanceDB для векторного индекса;
- Ollama `bge-m3` для русскоязычных эмбеддингов;
- файлы `docs/` и `AGENTS.md` как человекочитаемый источник истины.

Файлы остаются главным контролируемым слоем. SML индексирует их, ускоряет поиск, хранит связи, актуальность, журнал операций и semantic search.

## MCP-инструменты

Активные инструменты:

- `sml.ping` — проверить доступность сервера;
- `sml.startup_pack` — получить стартовый пакет контекста;
- `sml.semantic_query` — найти память по смыслу на русском языке;
- `sml.temporal_query` — получить состояние памяти с учетом времени;
- `sml.read` — прочитать запись по `id`;
- `sml.write` — добавить `Memory_Record`;
- `sml.supersede` — атомарно заменить устаревшие записи новой;
- `sml.add_log` — создать запись журнала агента и файл в `docs/agent-log/`;
- `sml.add_decision` — добавить решение в `docs/decisions.md`;
- `sml.build_context_pack` — пересобрать `docs/context-packs/context-pack-latest.md`.

## Где подключен

Codex CLI:

```text
C:\Users\koval\.codex\config.toml
```

Cursor:

```text
.cursor/mcp.json
```

Kiro:

```text
.kiro/settings/mcp.json
```

Все три клиента должны видеть сервер с именем `sml`.

## Как агент должен использовать память

Перед любой содержательной задачей агент должен:

1. вызвать `sml.startup_pack`;
2. выполнить `sml.semantic_query` по теме запроса;
3. при необходимости выполнить дополнительный `sml.semantic_query` по ключевым сущностям;
4. использовать найденный контекст перед ответом или правками.

После важной работы агент должен:

1. вызвать `sml.add_log`;
2. при необходимости вызвать `sml.write` для факта, предпочтения, ограничения или события;
3. при архитектурном решении вызвать `sml.add_decision`;
4. при отмене старой записи вызвать `sml.supersede`.

## Проверка

Быстрая проверка ядра:

```powershell
& "C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -ExecutionPolicy Bypass -File "D:\AionUi-Paperclip\tools\sml\start-sml.ps1" --selfcheck
```

Ожидаемый вывод:

```text
sml-selfcheck-ok
```

Проверка тестов:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" -m pytest "D:\AionUi-Paperclip\tools\sml\tests" -q
```

Ожидаемый результат на текущем состоянии:

```text
141 passed
```

Проверка Ollama:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -Method Get
```

В списке должна быть модель:

```text
bge-m3:latest
```

## Legacy: aion-file-memory

Старый сервер:

```text
tools/aion_memory_mcp.py
```

Статус: legacy/reference. Он больше не должен быть основным сервером памяти в активной конфигурации Codex + Gemini. Исторические конфиги Cursor/Kiro могут оставаться в проекте как резерв, но не считаются текущим рабочим путем.

Исторически он предоставлял инструменты:

- `read_context_pack`;
- `search_memory`;
- `add_memory`;
- `add_agent_log`;
- `create_handoff`;
- `build_context_pack`.

Карта замены:

- `read_context_pack` → `sml.startup_pack`;
- `search_memory` → `sml.semantic_query`;
- `add_memory` → `sml.write`;
- `add_agent_log` → `sml.add_log`;
- `build_context_pack` → `sml.build_context_pack`.

Новые задачи и новые агенты должны использовать только `sml`, а не `aion-file-memory`.
