# Установка автоматизации памяти

## Дата и время

2026-05-10

## Агент

Codex

## Исходный запрос пользователя

Перейти ко второму уровню и сделать так, чтобы память сохранялась автоматически, без ручного нажатия, а агенты понимали общий контекст.

## Контекст перед началом

В проекте уже были файловая память v1, контекстный пакет и локальный MCP-сервер `aion-file-memory`. Но пересборка контекстного пакета после изменений была ручной или выполнялась только через MCP-инструменты.

## Что сделано

Добавлен фоновый наблюдатель памяти:

- `tools/watch-memory.ps1`
- `tools/run-memory-watcher.ps1`
- `tools/install-memory-autostart.ps1`
- `tools/uninstall-memory-autostart.ps1`
- `tools/status-memory-auto.ps1`

Добавлены CMD-файлы:

- `INSTALL-MEMORY-AUTO.cmd`
- `STATUS-MEMORY-AUTO.cmd`
- `UNINSTALL-MEMORY-AUTO.cmd`

Установлена и запущена задача Windows Task Scheduler:

```text
Aion File Memory Auto
```

## Измененные файлы

- `tools/watch-memory.ps1`
- `tools/run-memory-watcher.ps1`
- `tools/install-memory-autostart.ps1`
- `tools/uninstall-memory-autostart.ps1`
- `tools/status-memory-auto.ps1`
- `INSTALL-MEMORY-AUTO.cmd`
- `STATUS-MEMORY-AUTO.cmd`
- `UNINSTALL-MEMORY-AUTO.cmd`
- `docs/memory-automation.md`
- `AGENTS.md`
- `README.md`
- `docs/START-HERE.md`
- `docs/context-index.md`
- `docs/mcp-memory.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/memory/architecture.md`
- `docs/memory/layers/timeline.md`
- `docs/memory/layers/constraints.md`

## Проверки

Проверен синтаксис PowerShell-скриптов.

Проверена валидность MCP JSON-конфигов.

Задача `Aion File Memory Auto` установлена и запущена. Статус Task Scheduler: `Running`.

Была обнаружена несовместимость Windows PowerShell 5.1 с UTF-8 без BOM в `tools/build-context-pack.ps1`. Скрипт исправлен: служебные строки переведены в ASCII, чтение документов выполняется через `-Encoding UTF8`.

Проверено автоматическое обновление: после изменения `docs/memory-automation.md` наблюдатель сам пересобрал `docs/context-packs/context-pack-latest.md`.

## Решения

Автоматизация пересобирает `docs/context-packs/context-pack-latest.md` после изменений в общей базе. При этом агент все равно обязан записывать результат работы в `docs/agent-log/`, `docs/memory/layers/` или `docs/handoffs/`.

## Риски и ограничения

Фоновый наблюдатель не может автоматически извлекать закрытую историю чатов из приложений. Если агент ничего не записал в общую базу, сохранить смысл его работы невозможно.

## Что должен проверить следующий агент

Проверить, что после изменения любого файла в `docs/` контекстный пакет обновляется автоматически. Затем проверить использование MCP-сервера `aion-file-memory` внутри Cursor и Kiro.
