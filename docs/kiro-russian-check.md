# Проверка Kiro на русском языке

## Что настроено

Kiro найден локально:

```text
C:\Users\koval\AppData\Local\Programs\Kiro\Kiro.exe
```

Проверенная версия:

```text
Kiro 0.12.155
```

В установке Kiro есть русская Chromium/Electron-локаль:

```text
C:\Users\koval\AppData\Local\Programs\Kiro\locales\ru.pak
```

Пользовательская локаль выставлена:

```text
C:\Users\koval\AppData\Roaming\Kiro\User\locale.json
```

Содержимое:

```json
{
  "locale": "ru"
}
```

MCP включен в пользовательских настройках Kiro:

```json
"kiroAgent.configureMCP": "Enabled"
```

Установлен русский языковой пакет:

```text
ms-ceintl.vscode-language-pack-ru@1.106.0
```

Постоянная локаль также выставлена в:

```text
C:\Users\koval\.kiro\argv.json
```

Значение:

```json
"locale": "ru"
```

## Проектные русские правила

Русское поведение Kiro задают:

- `.kiro/steering/00-shared-context.md`
- `.kiro/steering/01-russian-language.md`
- `.kiro/steering/10-spec-workflow.md`

## Как запустить

Используй:

```text
OPEN-KIRO-RU.cmd
```

Или вручную:

```powershell
& "C:\Users\koval\AppData\Local\Programs\Kiro\Kiro.exe" --locale ru "D:\AionUi-Paperclip"
```

Проверенный статус запуска:

```text
Process Argv: --locale ru D:\AionUi-Paperclip
Window: AionUi-Paperclip - Kiro
```

## MCP-память

Активный MCP-сервер памяти для Kiro:

```text
sml
```

Активный конфиг:

```text
D:\AionUi-Paperclip\.kiro\settings\mcp.json
```

Команда запуска сервера:

```text
C:\Program Files\PowerShell\7\pwsh.exe -NoProfile -File D:\AionUi-Paperclip\tools\sml\start-sml.ps1
```

Историческая проблема, найденная до миграции: Kiro запускал `aion-file-memory`, но соединение уходило в таймаут из-за несовпадения stdio-framing. Это исправлено в legacy-сервере `tools/aion_memory_mcp.py`, но основной путь после миграции — `sml`.

Проверка SML:

```text
sml.ping
sml.startup_pack
sml.semantic_query
```

## Тестовый запрос

В Kiro напиши:

```text
Используй MCP-сервер sml: сначала вызови sml.ping, затем sml.startup_pack и sml.semantic_query по запросу "автоматизация памяти". Ответь по-русски, что нашел.
```

Ожидаемое поведение:

1. Kiro отвечает на русском.
2. Kiro учитывает `docs/memory-autoprotocol.md`.
3. Kiro использует `sml`.
4. Kiro упоминает `context-pack-latest.md`, `docs/agent-log/`, `docs/memory/layers/` и SML.

Дополнительный тест записи:

```text
Создай через sml.add_log короткую тестовую запись: "Kiro UI smoke-test SML прошел".
```

## Важное ограничение

Интерфейс Kiro может быть не полностью русским. Базовая Electron-локаль `ru.pak` есть, но расширение `kiro.kiro-agent` не содержит найденного русского `l10n`-пакета. Поэтому полностью русскими мы можем гарантировать:

- ответы агента;
- specs;
- steering;
- задачи;
- выводы;
- журналы;
- контекст и память.

Полный перевод всех кнопок и внутренних надписей Kiro зависит от поддержки локализации самим Kiro.
