# Локальное окружение

Дата последнего обновления: 2026-06-17

## Рабочая папка

```text
D:\AionUi-Paperclip
```

## Найденные приложения и инструменты

| Инструмент | Путь или состояние | Комментарий |
| --- | --- | --- |
| VS Code | `C:\Users\koval\AppData\Local\Programs\Microsoft VS Code\Code.exe` | Установлен, версия `1.124.2`; общая IDE-оболочка для `D:\AionUi-Paperclip`, SML, терминалов Codex/Claude/Gemini и VS Code Tasks. Команда `code` не найдена в PATH текущей PowerShell-сессии |
| Codex CLI | `C:\Users\koval\AppData\Roaming\npm\codex.cmd` и `C:\Users\koval\AppData\Local\OpenAI\Codex\bin\codex.exe` | Версия проверялась: `codex-cli 0.128.0` |
| Cursor | `C:\Users\koval\AppData\Local\Programs\cursor\resources\app\bin\cursor.cmd` | Исторически настроен, но не активен в текущей схеме |
| Kiro | `C:\Users\koval\AppData\Local\Programs\Kiro\Kiro.exe` | Исторически настроен, но не активен в текущей схеме |
| Gemini CLI | `C:\Users\koval\AppData\Roaming\npm\gemini.cmd` | Проверено: `0.42.0`, авторизован, MCP `sml` подключен и показывает `Connected` |
| MiMo Code | `C:\Users\koval\AppData\Roaming\npm\mimo.cmd` | Установлен, версия `0.1.1`; проектный MCP `sml` подключен, но `mimo providers list` показывает `0 credentials` |
| OpenCode | Установлен ранее, версия проверялась как `1.14.33` | Может зависеть от PATH текущей сессии |
| Hermes | Удален/отключен | Не используется в новой архитектуре |
| AionUi | Удален пользователем | Не используется |
| Paperclip | Удален пользователем | Не используется |

## Важное ограничение

Подписки и лимиты могут меняться. Поэтому общая память не должна зависеть от одного приложения или одной модели.

Главная долговременная память сейчас:

- `docs/current-context.md`
- `docs/tasks.md`
- `docs/decisions.md`
- `docs/agent-log/`
- `docs/memory/layers/`
- `docs/context-packs/context-pack-latest.md`

## MCP-память

Основной MCP-сервер памяти `sml` подключен к активным инструментам:

- Codex CLI через `C:\Users\koval\.codex\config.toml`;
- Gemini CLI через `C:\Users\koval\.gemini\settings.json` и `D:\AionUi-Paperclip\.gemini\settings.json`.
- MiMo Code через `D:\AionUi-Paperclip\.mimocode\mimocode.json`.

Исторические конфиги остаются в проекте:

- Cursor через `.cursor/mcp.json`;
- Kiro через `.kiro/settings/mcp.json`.

Сервер запускается через:

```text
C:\Program Files\PowerShell\7\pwsh.exe -NoProfile -File D:\AionUi-Paperclip\tools\sml\start-sml.ps1
```

Для Kiro исторически были выставлены:

- пользовательская локаль `ru`;
- `kiroAgent.configureMCP = Enabled`;
- проектный steering на русском языке.
- установлен русский языковой пакет `ms-ceintl.vscode-language-pack-ru`;
- рабочий запускатель: `D:\AionUi-Paperclip\OPEN-KIRO-RU.cmd`;
- активный MCP-конфиг Kiro: `D:\AionUi-Paperclip\.kiro\settings\mcp.json`.

Старый `aion-file-memory` оставлен только как legacy/reference в `tools/aion_memory_mcp.py` и не должен быть основным сервером в конфигурациях агентов.

## Gemini CLI

Добавлены запускатели:

- `D:\AionUi-Paperclip\OPEN-GEMINI-SML.cmd`;
- `D:\AionUi-Paperclip\CHECK-GEMINI-SML.cmd`.

Подробная инструкция по запуску и проверке находится в `D:\AionUi-Paperclip\docs\gemini-sml.md`.

Отдельная инструкция для подключения Gemini как модели внутри Cursor находится в `D:\AionUi-Paperclip\docs\cursor-gemini-model.md`.

## VS Code

VS Code используется как общая IDE-оболочка проекта памяти, а не как отдельный агент.

Добавлены:

- `D:\AionUi-Paperclip\OPEN-VSCODE-SML.cmd`;
- `D:\AionUi-Paperclip\CHECK-VSCODE-SML.cmd`;
- `D:\AionUi-Paperclip\.vscode\settings.json`;
- `D:\AionUi-Paperclip\.vscode\tasks.json`;
- `D:\AionUi-Paperclip\docs\vscode-sml.md`.

Запуск:

```powershell
D:\AionUi-Paperclip\OPEN-VSCODE-SML.cmd
```

Проверка:

```powershell
D:\AionUi-Paperclip\CHECK-VSCODE-SML.cmd
```

Внутри VS Code использовать `Terminal -> Run Task...` и задачи `SML:*` / `Claude:*`.

## MiMo Code

MiMo Code установлен как экспериментальный агент поверх SML.

Файлы:

- `D:\AionUi-Paperclip\.mimocode\mimocode.json`;
- `D:\AionUi-Paperclip\.mimocode\agents\sml-review.md`;
- `D:\AionUi-Paperclip\.mimocode\agents\sml-plan.md`;
- `D:\AionUi-Paperclip\.mimocode\agents\sml-build.md`;
- `D:\AionUi-Paperclip\OPEN-MIMO-SML.cmd`;
- `D:\AionUi-Paperclip\CHECK-MIMO-SML.cmd`;
- `D:\AionUi-Paperclip\docs\mimo-code-integration.md`.

Проверка:

```powershell
D:\AionUi-Paperclip\CHECK-MIMO-SML.cmd
```

Запуск:

```powershell
D:\AionUi-Paperclip\OPEN-MIMO-SML.cmd
```

Важно: провайдеры MiMo пока не авторизованы (`0 credentials`). Первый интерактивный запуск должен выбрать MiMo Auto, Xiaomi MiMo Platform, импорт Claude Code или custom provider. API-ключи не хранить в проектных файлах.

### VS Code IDE integration

Для использования Gemini CLI как IDE-инструмента в VS Code установлено расширение:

```text
Google.gemini-cli-vscode-ide-companion@0.20.0
```

Установлено командой:

```powershell
code --install-extension Google.gemini-cli-vscode-ide-companion --force
```

После установки нужно перезапустить окно VS Code и в Gemini CLI выполнить:

```text
/ide enable
```

Проектные правила для Gemini CLI находятся в:

```text
D:\AionUi-Paperclip\GEMINI.md
```

Gemini CLI должен автоматически загружать их при запуске из рабочей папки. После изменения правил выполнить:

```text
/memory reload
```

Для надежного режима, в котором SML-контекст вставляется в prompt технически до ответа модели, добавлены:

```text
D:\AionUi-Paperclip\tools\gemini-sml-context.ps1
D:\AionUi-Paperclip\.gemini\commands\sml\task.toml
D:\AionUi-Paperclip\.gemini\commands\sml\review.toml
```

В Gemini CLI использовать:

```text
/commands reload
/sml:task <задача>
/sml:review <что проверить>
```

## Автосинхронизация памяти

Задача Windows Task Scheduler `Aion File Memory Auto` переустановлена на запуск через PowerShell 7:

```text
C:\Program Files\PowerShell\7\pwsh.exe
```

Это важно для русских UTF-8 строк в `.ps1`.

## SML

Локальный виртуальный Python-интерпретатор для слоя общей памяти агентов (Shared_Memory_Layer, спека `agents-shared-memory-layer`).

| Параметр | Значение |
| --- | --- |
| Каталог venv | `D:\AionUi-Paperclip\.venv-sml` |
| Интерпретатор | `D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe` |
| Версия Python | `Python 3.13.7` (удовлетворяет требованию ≥ 3.11) |
| Скрипт активации | `D:\AionUi-Paperclip\.venv-sml\Scripts\Activate.ps1` |
| Оболочка запуска | `C:\Program Files\PowerShell\7\pwsh.exe -NoProfile` |
| Базовый Python | `python --version` в PATH → `Python 3.13.7` |

Активация в PowerShell 7:

```powershell
C:\Program Files\PowerShell\7\pwsh.exe -NoProfile -Command ". .\.venv-sml\Scripts\Activate.ps1; python --version"
```

Каталог `.venv-sml/` исключён из индексации git через `.gitignore` в корне репозитория.

### Ollama (эмбеддер для SML)

Локальная LLM-служба для расчёта векторов bge-m3 (Embedding_Engine). Установлена через native Windows installer, без Docker и без JVM.

| Параметр | Значение |
| --- | --- |
| Версия | `0.23.2` |
| Путь бинаря | `C:\Users\koval\AppData\Local\Programs\Ollama\ollama.exe` |
| Endpoint | `http://127.0.0.1:11434` (loopback-only) |
| `OLLAMA_HOST` | `127.0.0.1` (установлено через `setx` для текущего пользователя) |
| Служба | Автозапуск для текущего пользователя (установщик Ollama) |

Примечание: `ollama.exe` может быть не виден в PATH обычной PowerShell-сессии. Полный путь:

```text
C:\Users\koval\AppData\Local\Programs\Ollama\ollama.exe
```

Проверка доступности (Req 10.4):

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:11434/api/version -UseBasicParsing
```

Внешний интерфейс (по hostname) корректно недоступен — служба слушает только loopback.
