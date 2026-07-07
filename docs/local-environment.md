# Локальное окружение

Дата последнего обновления: 2026-07-03

## Рабочая папка

```text
D:\AionUi-Paperclip
```

## Найденные приложения и инструменты

| Инструмент | Путь или состояние | Комментарий |
| --- | --- | --- |
| VS Code | `C:\Users\koval\AppData\Local\Programs\Microsoft VS Code\Code.exe` | Установлен, версия `1.124.2`; общая IDE-оболочка для `D:\AionUi-Paperclip`, SML, терминалов Codex/Claude/Antigravity и VS Code Tasks. Команда `code` не найдена в PATH текущей PowerShell-сессии |
| Codex CLI | `C:\Users\koval\AppData\Roaming\npm\codex.cmd` и `C:\Users\koval\AppData\Local\OpenAI\Codex\bin\codex.exe` | Версия проверялась: `codex-cli 0.128.0` |
| Cursor | `C:\Users\koval\AppData\Local\Programs\cursor\resources\app\bin\cursor.cmd` | Исторически настроен, но не активен в текущей схеме |
| Kiro | `C:\Users\koval\AppData\Local\Programs\Kiro\Kiro.exe` | Исторически настроен, но не активен в текущей схеме |
| Gemini CLI | Удален | 2026-06-19 удалены `@google/gemini-cli`, `codex-gemini-helper`, npm shims `gemini`/`ask-gemini`, проектная `.gemini/`, `GEMINI.md`, Gemini launchers и root-файлы `C:\Users\koval\.gemini` без удаления `antigravity-cli` |
| Gemini Vertex | Google ADC + `google-genai`; `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` | Резервный L1/L2 route для agent-workflows через `tools/gemini_vertex_workflow_review.py`; smoke на `gemini-2.5-flash` проходил 2026-07-02 |
| Antigravity / `agy` CLI | `C:\Users\koval\AppData\Local\Programs\Antigravity\Antigravity.exe`; `C:\Users\koval\AppData\Local\agy\bin\agy.exe` | Дефолтный L2 route для `Рой` через isolated runner `tools/antigravity_workflow_review.py`; свежий smoke проходил 2026-07-03, при повторном runtime blocker использовать fallback `gemini-vertex` |
| Grok Build | `grok` / `@xai-official/grok@0.2.87` | Дефолтный L1 route для `Рой` через `tools/grok_build_workflow_review.py`; auth и `grok-build` smoke подтверждены 2026-07-06 |
| MiMo Code / MiMo AUTO | Удален из активного CLI | Исторически устанавливался; проектная интеграция выведена 2026-06-18. Решением 2026-06-24 отменено прежнее исключение `MiMo AUTO L1.0`, удален глобальный npm-пакет `@mimo-ai/cli`, команда `mimo` больше не резолвится |
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

- Codex через `C:\Users\koval\.codex\AGENTS.md`, skill `C:\Users\koval\.codex\skills\sml-memory-bootstrap` и проектные файлы `AGENTS.md`/SML;
- Claude Code через проектный `.mcp.json`, `C:\Users\koval\.claude\CLAUDE.md` и user-scope MCP `sml`;
- Grok Build через `grok`, `.grok/config.toml`, bootstrap SML и файлы `docs/agent-workflows/`, как дефолтный L1 profile.
- Antigravity CLI через `agy`, `C:\Users\koval\.gemini\antigravity-cli\settings.json`, bootstrap SML и файлы `docs/agent-workflows/`, как дефолтный L2 profile после smoke.
- Gemini Vertex через Google ADC, `tools/gemini_vertex_workflow_review.py`, bootstrap SML и файлы `docs/agent-workflows/`, как fallback profile `gemini-vertex`;

Исторические конфиги Cursor/Kiro/MiMo удалены из активного проекта. Историческая память о них хранится в `docs/agent-log/`, SML и `docs/specs/`. С 2026-06-24 `MiMo AUTO` больше не используется в новых agent-workflow.

Глобальный bootstrap для агентов:

```powershell
& "D:\AionUi-Paperclip\tools\agent-memory-bootstrap.ps1" -Agent "<имя агента>" -Query "<тема>"
```

Старый `aion-file-memory` оставлен только как legacy/reference в `tools/aion_memory_mcp.py` и не должен быть основным сервером в конфигурациях агентов.

## Gemini Vertex

Default route для `L1/L2` в новых agent-workflows:

```powershell
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\gemini_vertex_workflow_review.py <workflow-id> --task "<задача уровня>" --out <handoff-draft.md>
```

Требует Google ADC, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` и Python package `google-genai`. Текущая модель: `gemini-2.5-flash`.

## Antigravity CLI

`agy` установлен и добавлен в пользовательский PATH командой:

```powershell
C:\Users\koval\AppData\Local\agy\bin\agy.exe install
```

Проверка:

```powershell
agy --version
agy --help
```

На 2026-06-19 подтверждено: `agy --version` возвращает `1.0.10`; live smoke-test авторизовался через keyring и сделал `streamGenerateContent`. Ограничение: `agy --print "Return exactly OK."` завершился с кодом 0, ответ `OK` найден в conversation DB, но stdout пустой. На 2026-07-02 OAuth восстанавливался, но model-call smoke блокировался `FAILED_PRECONDITION (code 400): User location is not supported for the API use`. Этот статус superseded успешным smoke 2026-07-03 и решением 2026-07-07: новые workflow используют default `grok-antigravity`, где Antigravity является `L2`; `gemini-vertex` остается fallback.

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

## Выведенные агенты

Cursor, Kiro, Gemini CLI, проектный MiMo Code и `MiMo AUTO` не входят в активный рабочий цикл. Их старые настройки считаются историей и не должны использоваться как текущие инструкции запуска.

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
