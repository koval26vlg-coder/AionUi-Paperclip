# VS Code в общей памяти SML

VS Code в этой системе не является отдельным агентом. Это рабочая IDE-оболочка для общей папки `D:\AionUi-Paperclip`, через которую можно запускать терминалы, Codex/Claude/Gemini CLI, проверять SML, читать context-pack и работать с файлами общей памяти.

## Роль

VS Code используется как:

- единая рабочая оболочка для проекта общей памяти;
- место, где открыты `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `docs/context-packs/context-pack-latest.md` и журналы;
- терминальная среда для запуска Codex, Claude Code, SML-скриптов и проверок;
- быстрый доступ к задачам `.vscode/tasks.json`.

VS Code не заменяет SML и не хранит память сам. Источник истины остается в `docs/`, SML, context-pack и relationship-map.

## Запуск

Основной запускатель:

```powershell
D:\AionUi-Paperclip\OPEN-VSCODE-SML.cmd
```

Прямой запуск:

```powershell
& "C:\Users\koval\AppData\Local\Programs\Microsoft VS Code\Code.exe" "D:\AionUi-Paperclip"
```

Команда `code` может быть не видна в PATH текущей PowerShell-сессии, поэтому в запускателях используется прямой путь к `Code.exe`.

## Проверка

```powershell
D:\AionUi-Paperclip\CHECK-VSCODE-SML.cmd
```

Проверка должна показать:

- найден ли `Code.exe`;
- открыта ли рабочая папка `D:\AionUi-Paperclip`;
- есть ли `.vscode/tasks.json`;
- доступен ли context-pack;
- доступна ли relationship-map;
- видит ли Claude Code MCP-сервер `sml`, если Claude установлен.

## VS Code Tasks

В VS Code открыть:

```text
Terminal -> Run Task...
```

Доступные задачи:

- `SML: status memory auto` — статус фоновой памяти.
- `SML: rebuild context pack` — ручная пересборка context-pack.
- `SML: rebuild relationship map` — ручная пересборка карты связей.
- `SML: query relationship map` — быстрый поиск по карте связей.
- `Claude: auth status` — проверка авторизации Claude Code.
- `Claude: mcp list` — проверка MCP-серверов Claude Code.
- `MiMo: version` — проверка версии MiMo Code.
- `MiMo: mcp list` — проверка MCP-серверов MiMo Code.

Обычно эти задачи не нужно запускать вручную каждый раз: watcher памяти пересобирает context-pack и relationship-map автоматически. Tasks нужны для диагностики и ручной проверки.

## Правило для агентов

Если агент работает через VS Code, он должен считать рабочей папкой именно `D:\AionUi-Paperclip` и перед содержательной задачей использовать общий автопротокол памяти:

1. прочитать `AGENTS.md`;
2. прочитать `docs/context-packs/context-pack-latest.md`;
3. проверить SML, если MCP доступен;
4. использовать relationship-map через `tools/query-relationship-map.py`;
5. после работы оставить запись в `docs/agent-log/`.
