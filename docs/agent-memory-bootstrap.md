# Agent Memory Bootstrap

Этот файл является единым правилом автоподхвата памяти для всех активных агентов.

## Назначение

Общая память проекта находится в `D:\AionUi-Paperclip`. Агент обязан подтягивать ее сам, даже если пользователь запустил агента из другой папки и отдельно не просил "посмотреть память".

Активная связка: Grok Build + Antigravity CLI + Codex + Claude Code. По решению пользователя от 2026-07-07 дефолтный `Рой` запускает `grok-antigravity` (`L1 Grok Build -> L2 Antigravity CLI -> L3 Codex -> L4 Codex -> L5 Claude Code`). Gemini Vertex остается резервным профилем `gemini-vertex`, если `agy`/Antigravity недоступен или явно нужен Vertex fallback. По решению 2026-06-24 `MiMo AUTO` выведен из новых `docs/agent-workflows/`; Cursor, Kiro, Gemini CLI и проектные конфиги MiMo Code остаются выведенными из общей схемы и не должны возвращаться без отдельного решения пользователя.

## Абсолютные пути

- Корень памяти: `D:\AionUi-Paperclip`
- Главные правила: `D:\AionUi-Paperclip\AGENTS.md`
- Сжатый контекст: `D:\AionUi-Paperclip\docs\context-packs\context-pack-latest.md`
- Текущий контекст: `D:\AionUi-Paperclip\docs\current-context.md`
- Задачи: `D:\AionUi-Paperclip\docs\tasks.md`
- Решения: `D:\AionUi-Paperclip\docs\decisions.md`
- Журнал агентов: `D:\AionUi-Paperclip\docs\agent-log`
- Карта связей: `D:\AionUi-Paperclip\docs\relationship-maps\graphify-sml-relationship-map.json`
- Bootstrap-команда: `D:\AionUi-Paperclip\tools\agent-memory-bootstrap.ps1`

## Правило перед задачей

Перед любой содержательной задачей агент должен:

1. Определить тему запроса.
2. Запустить bootstrap-команду из любой папки:

```powershell
& "D:\AionUi-Paperclip\tools\agent-memory-bootstrap.ps1" -Agent "<имя агента>" -Query "<тема запроса>"
```

3. Прочитать найденный контекст и только после этого отвечать или менять файлы.
4. Если доступен MCP-сервер `sml`, вызвать `sml.ping`, `sml.startup_pack` и `sml.semantic_query` по теме запроса.
5. Если MCP недоступен, использовать файлы `context-pack-latest.md`, `current-context.md`, `tasks.md`, `decisions.md`, `agent-log` и relationship-map.

## Правило после задачи

После важной работы агент должен:

1. Создать запись в `D:\AionUi-Paperclip\docs\agent-log`.
2. Обновить `docs/current-context.md`, если изменилась общая картина.
3. Обновить `docs/tasks.md`, если менялись задачи.
4. Обновить `docs/decisions.md`, если принято решение.
5. Если доступен `sml`, сохранить важные факты через `sml.write`, `sml.add_log` или `sml.add_decision`.

Фоновый watcher пересоберет context pack, карту связей, dashboard и backup. Но watcher не заменяет обязанность агента фиксировать смысл работы в документах или SML.

## Русский язык

Все ответы, выводы, решения, задачи, журналы и инструкции ведутся на русском языке. Исключения: код, команды, пути, API, логи ошибок и официальные названия.

## Безопасность

Не записывать секреты, API-ключи, пароли, OAuth-токены и приватные данные в `docs`, `AGENTS.md`, `CLAUDE.md`, `.mcp.json`, SML или agent-log.
