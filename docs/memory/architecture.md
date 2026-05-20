# Архитектура общей памяти

## Цель

Память должна переживать:

- окончание подписки;
- удаление конкретного агента;
- смену модели;
- потерю истории чата;
- переход между Codex, Cursor, Kiro и другими агентами.

## Текущая реализация: файловая память v1

Сейчас память хранится в обычных Markdown-файлах.

Плюсы:

- работает без подписки;
- понятна человеку;
- доступна любому агенту;
- не зависит от конкретной модели;
- легко копируется и резервируется.

Минусы:

- агент должен дисциплинированно читать и обновлять файлы;
- нет автоматического семантического поиска;
- длинная история может разрастаться.

## Следующий уровень: MCP-память v2

Добавлена и введена в эксплуатацию MCP-память v2 — **Shared_Memory_Layer (SML)**, tools/sml/:

- код: `tools/sml/` (mcp_adapter, temporal_store, embedding_engine, writers, file_watcher, security, operation_log);
- запуск: `tools/sml/start-sml.ps1` (pwsh 7, UTF-8, автопроверка Ollama);
- хранилище: `var/sml/state.db` (SQLite WAL) + `var/sml/lance/` (LanceDB, 1024-dim float32);
- эмбеддер: Ollama `bge-m3` на `127.0.0.1:11434`;
- журнал: `logs/sml-operation-log.ndjson` (JSONL append-only, ротация по UTC-дням, TTL 30 дней);
- MCP-регистрация: `~/.codex/config.toml`, `.cursor/mcp.json`, `.kiro/settings/mcp.json` (имя сервера `sml`, параллельно со старым `aion-file-memory`);
- 10 инструментов: `sml.ping`, `sml.read`, `sml.write`, `sml.semantic_query`, `sml.temporal_query`, `sml.supersede`, `sml.add_decision`, `sml.add_log`, `sml.build_context_pack`, `sml.startup_pack`.

SML построен поверх файловой памяти: файлы `docs/` остаются источником истины (Req 8), при любом расхождении запись приводится к файлу. SyncService (`tools/sml/file_watcher.py::SyncService`) индексирует файлы в Memory_Record с маппингом типов из `design.md §7.4`.

Старый `aion-file-memory` оставлен в конфигах как fallback, пока идёт Фаза 1 миграции.

## Слои памяти

| Слой | Файл | Что хранит |
| --- | --- | --- |
| Текущая память | `docs/current-context.md` | Что происходит сейчас |
| Задачи | `docs/tasks.md` | Что нужно сделать |
| Решения | `docs/decisions.md` | Почему выбрали именно так |
| Журнал | `docs/agent-log/` | Что делали агенты |
| Передачи | `docs/handoffs/` | Что один агент передает другому |
| Долгосрочные факты | `docs/memory/layers/facts.md` | Устойчивые факты |
| Предпочтения | `docs/memory/layers/preferences.md` | Как пользователь хочет работать |
| Таймлайн | `docs/memory/layers/timeline.md` | Хронология важных событий |
| Ограничения | `docs/memory/layers/constraints.md` | Лимиты, подписки, запреты |
| Контекстный пакет | `docs/context-packs/context-pack-latest.md` | Сжатая сборка для быстрого входа |

## Правило записи

Если факт важен больше чем на одну сессию, его нужно записать в файл.

Если факт нужен только для текущей задачи, достаточно `docs/current-context.md` или записи в `docs/agent-log/`.

Если факт влияет на будущие решения, он должен быть в `docs/decisions.md` или `docs/memory/layers/facts.md`.
