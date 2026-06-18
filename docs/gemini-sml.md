# Gemini CLI и SML

Дата проверки: 2026-05-14.

## Статус

Gemini CLI установлен, авторизован и виден как версия `0.42.0`.

SML добавлен в конфигурацию Gemini CLI:

- пользовательский конфиг: `C:\Users\koval\.gemini\settings.json`;
- проектный конфиг: `D:\AionUi-Paperclip\.gemini\settings.json`;
- сервер: `sml`;
- запуск: `D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe -X utf8 -m tools.sml.mcp_adapter`;
- рабочая папка: `D:\AionUi-Paperclip`.

Проверено:

- `gemini mcp list` показывает `sml` как `Connected`;
- прямой MCP-тест SML проходит: `initialize`, `tools/list` и `sml.ping` отвечают корректно;
- живой тест через Gemini CLI проходит: Gemini вызывает `sml.ping` и `sml.startup_pack`, видит общий контекст и последние записи памяти.

## Исторический блокер

13 мая 2026 года вход через Google-аккаунт для Gemini CLI временно не проходил. Ошибка была:

```text
IneligibleTierError: Your current account is not eligible for Gemini Code Assist for individuals because it is not currently available in your location.
reasonCode: UNSUPPORTED_LOCATION
```

Это не было ошибкой SML. На 14 мая 2026 года связка Gemini CLI + SML проверена как рабочая.

По официальной документации Gemini CLI, для Google AI Pro и Ultra рекомендуется `Login with Google`. Но если этот способ недоступен из-за региона или типа аккаунта, остаются два рабочих варианта: API-ключ Google AI Studio или Vertex AI через Google Cloud.

## Если авторизация снова сломается: повторный вход через Google AI Pro

Использовать этот вариант, если подписка Google AI Pro оформлена на другой Google-аккаунт или если нужно явно перелогиниться.

Команда запуска:

```powershell
cd D:\AionUi-Paperclip
gemini
```

В интерфейсе Gemini выбрать `Login with Google` и войти именно в аккаунт с Google AI Pro.

Если Gemini продолжает использовать старый аккаунт, можно временно переименовать старые OAuth-файлы и войти заново:

```powershell
Rename-Item "$env:USERPROFILE\.gemini\oauth_creds.json" "oauth_creds.json.backup" -ErrorAction SilentlyContinue
Rename-Item "$env:USERPROFILE\.gemini\google_accounts.json" "google_accounts.json.backup" -ErrorAction SilentlyContinue
cd D:\AionUi-Paperclip
gemini
```

Если после повторного входа снова появляется `UNSUPPORTED_LOCATION`, значит этот способ на текущей машине или в текущем регионе снова не подходит.

## Если Google login недоступен: API-ключ Google AI Studio

Этот вариант не зависит от входа Gemini Code Assist через Google-аккаунт. Он использует `GEMINI_API_KEY`.

1. Открыть:

```text
https://aistudio.google.com/app/apikey
```

2. Создать API-ключ.

3. В PowerShell сохранить ключ в пользовательское окружение. Вместо `PASTE_KEY_HERE` вставить реальный ключ:

```powershell
$env:GEMINI_API_KEY = "PASTE_KEY_HERE"
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $env:GEMINI_API_KEY, "User")
```

4. Переключить Gemini CLI на API-ключ:

```powershell
$path = "$env:USERPROFILE\.gemini\settings.json"
$j = Get-Content -Raw $path | ConvertFrom-Json
if (-not $j.security) {
  $j | Add-Member -MemberType NoteProperty -Name security -Value ([pscustomobject]@{})
}
if (-not $j.security.auth) {
  $j.security | Add-Member -MemberType NoteProperty -Name auth -Value ([pscustomobject]@{})
}
$j.security.auth.selectedType = "gemini-api-key"
$j | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 $path
```

5. Открыть новое окно PowerShell и проверить:

```powershell
cd D:\AionUi-Paperclip
gemini mcp list
gemini -p "Проведи smoke-test MCP SML: вызови sml.ping и ответь кратко по-русски." --allowed-mcp-server-names sml --approval-mode yolo --skip-trust --output-format text
```

## Кнопки запуска

В корне папки добавлены:

- `OPEN-GEMINI-SML.cmd` — открыть Gemini CLI в общей рабочей папке;
- `CHECK-GEMINI-SML.cmd` — проверить список MCP-серверов и выполнить smoke-тест `sml.ping`.

`CHECK-GEMINI-SML.cmd` должен завершаться успешным ответом Gemini о доступности SML.

## IDE-режим в VS Code

VS Code установлен на компьютере и подходит как бесплатная IDE-оболочка для Gemini CLI.

Расширение Gemini CLI Companion установлено вручную:

```text
Google.gemini-cli-vscode-ide-companion@0.20.0
```

Если команда `/ide install` в Gemini CLI пишет:

```text
Failed to install VS Code companion extension
```

то расширение можно поставить вручную:

```powershell
code --install-extension Google.gemini-cli-vscode-ide-companion --force
```

После установки:

1. перезапустить окно VS Code;
2. открыть терминал в `D:\AionUi-Paperclip`;
3. запустить `gemini`;
4. выполнить:

```text
/ide enable
```

Если `/ide enable` снова пишет, что расширение не запущено, нужно выполнить `Developer: Reload Window` в VS Code и повторить `/ide enable`.

## Автоматические проектные правила

В корне проекта создан файл:

```text
D:\AionUi-Paperclip\GEMINI.md
```

Gemini CLI автоматически загружает `GEMINI.md` как проектный контекст при запуске из этой рабочей папки.

В этом файле закреплено:

- отвечать по-русски;
- перед содержательной задачей использовать `sml.startup_pack` и `sml.semantic_query`;
- после важной работы писать отчет через `sml.add_log`;
- использовать VS Code IDE-контекст после `/ide enable`;
- не сохранять секреты в документы, SML и журналы.

Проверить, что память загружена:

```text
/memory show
```

Перезагрузить правила после правки `GEMINI.md`:

```text
/memory reload
```

## Как снизить пропуски SML

Обычный `GEMINI.md` — это сильная инструкция, но не техническая гарантия. Чтобы Gemini не пропускал общий контекст, добавлены проектные команды:

```text
/sml:task
/sml:review
```

Они используют скрипт:

```text
D:\AionUi-Paperclip\tools\gemini-sml-context.ps1
```

Скрипт сам вызывает `sml.startup_pack` и `sml.semantic_query`, а затем вставляет найденный SML-контекст в prompt. Это надежнее, чем просто просить модель вызвать инструменты.

После добавления или изменения команд в Gemini CLI выполнить:

```text
/commands reload
```

Пример обычной задачи:

```text
/sml:task Проверь текущую настройку Gemini в VS Code и скажи, что еще нужно сделать.
```

Пример ревью:

```text
/sml:review Оцени последнюю работу Codex по настройке Gemini CLI.
```

Ограничение: это гарантирует предварительную загрузку SML-контекста в prompt. Запись `sml.add_log` после работы все равно выполняет сама модель, поэтому для критичных задач проверяй, что лог действительно появился.

## Использование Gemini из Cursor

Есть три уровня интеграции.

### 1. Через общую память SML

Это основной и самый надежный вариант.

Cursor и Gemini не обязаны быть встроены друг в друга. Оба агента читают и пишут в один SML:

- Cursor использует `.cursor/mcp.json`;
- Gemini использует `C:\Users\koval\.gemini\settings.json` и `.gemini/settings.json`;
- оба видят `sml.startup_pack`, `sml.semantic_query`, `sml.add_log` и остальные инструменты памяти.

Практический сценарий:

1. Cursor выполняет задачу.
2. Cursor пишет отчет в SML.
3. Gemini читает SML и дает второе мнение.
4. Cursor учитывает замечания Gemini и при необходимости исправляет.

### 2. Через терминал Cursor

В терминале Cursor можно запустить Gemini напрямую:

```powershell
cd D:\AionUi-Paperclip
gemini
```

Для одноразовой проверки:

```powershell
cd D:\AionUi-Paperclip
gemini -p "Прочитай общий контекст через SML. Оцени последние действия Cursor/Codex и дай краткое ревью по-русски." --allowed-mcp-server-names sml --approval-mode yolo --skip-trust --output-format text
```

### 3. Через Gemini как модель внутри Cursor

В Cursor можно добавить Google API key в настройках моделей и использовать Gemini как одну из моделей Cursor. Это отдельный путь от Gemini CLI и SML.

Ограничение: такой режим зависит от Google API key, возможностей Cursor и текущего плана Cursor. Если Cursor показывает `Named models unavailable. Free plans can only use Auto`, значит на текущем плане нельзя выбрать конкретную модель вроде `Gemini 3.1 Pro`; нужно выбрать `Auto` или перейти на платный план Cursor. Это не ломает SML.

Подробная инструкция: `docs/cursor-gemini-model.md`.

## Рекомендация для нашей схемы

Использовать Gemini из Cursor лучше не как "встроенный мозг Cursor", а как независимого проверяющего через общую память:

- Cursor делает правки в IDE;
- Gemini анализирует и критикует;
- Codex при необходимости делает глубокую инженерную проверку;
- SML хранит общий контекст и журнал.

## Что должен делать Gemini после подключения

Gemini должен работать как активный агент в той же системе, что Codex:

1. открыть папку `D:\AionUi-Paperclip`;
2. прочитать `AGENTS.md`, `docs/START-HERE.md`, `docs/context-packs/context-pack-latest.md`;
3. перед задачей использовать `sml.startup_pack` и `sml.semantic_query`;
4. после работы писать отчет через `sml.add_log` или в `docs/agent-log/`;
5. отвечать и фиксировать выводы на русском языке.
