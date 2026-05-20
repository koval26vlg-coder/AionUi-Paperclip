# Добавление агентонезависимой памяти

## Дата и время

2026-05-10

## Агент

Codex

## Исходный запрос пользователя

Сделать так, чтобы независимо от подписок, моделей и конкретных агентов все участники могли видеть общую базу того, что делали другие, и продолжать работу без потери контекста.

## Контекст перед началом

В папке `D:\AionUi-Paperclip` уже были базовые правила для Codex, Cursor и Kiro, но не было отдельного агентонезависимого контекстного слоя и единого файла быстрого входа для новых агентов.

## Что сделано

Добавлена файловая память v1:

- стартовый файл для любого агента;
- индекс общего контекста;
- реестр агентов;
- описание локального окружения;
- архитектура общей памяти;
- слои долговременной памяти;
- папка передач задач между агентами;
- шаблон handoff;
- генератор контекстного пакета;
- первый `docs/context-packs/context-pack-latest.md`.

## Измененные файлы

- `AGENTS.md`
- `README.md`
- `.cursor/rules/shared-context.mdc`
- `.kiro/steering/00-shared-context.md`
- `docs/START-HERE.md`
- `docs/context-index.md`
- `docs/agents.md`
- `docs/local-environment.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/memory/architecture.md`
- `docs/memory/layers/facts.md`
- `docs/memory/layers/preferences.md`
- `docs/memory/layers/timeline.md`
- `docs/memory/layers/constraints.md`
- `docs/handoffs/README.md`
- `docs/templates/handoff.md`
- `docs/context-packs/context-pack-latest.md`
- `tools/build-context-pack.ps1`
- `tools/new-handoff.ps1`

## Проверки

Проверен синтаксис новых PowerShell-скриптов. Сгенерирован первый контекстный пакет.

## Решения

Основной источник контекста остается файловым. MCP-память будет следующим уровнем, но не заменит файлы.

## Риски и ограничения

Файловая память требует дисциплины: каждый агент должен обновлять документы после работы. Автоматическая семантическая память пока не подключена.

## Что должен проверить следующий агент

Проверить, удобно ли читать `docs/context-packs/context-pack-latest.md` как единый входной файл. Затем можно переходить к подключению Graphiti MCP или Mem0/OpenMemory MCP.

