# Текущий контекст

Дата создания: 2026-05-10

## Природа проекта

`D:\AionUi-Paperclip` — самостоятельный проект. Его единственная цель — быть инфраструктурой общего контекста и памяти для AI-агентов (сейчас активны Codex, Gemini CLI и Claude Code; будущие агенты могут быть добавлены позже).

Любые упоминания внешних репозиториев и прикладных задач (например, `C:\Users\koval\bat\bitrix24-automation` и его spec-ов вида `bitrix24-automation-hygiene`, `bitnewton-*`) — это работы, которые катятся через эту инфраструктуру, но не являются её частью. Код, тесты и артефакты таких внешних проектов живут в своих репозиториях; здесь остаются только spec-документы, журналы, решения и память о ходе работы.

Следующий агент не должен воспринимать bitrix24-automation или любой другой внешний проект как часть `D:\AionUi-Paperclip`.

Практическая граница:

- **Bitrix/Bit.Newton** — прикладной проект для анализа звонков, сделок, CRM-качества и отчетов. Рабочий код находится в `C:\Users\koval\bat\bitrix24-automation`.
- **Aion/SML** — инфраструктурный проект общей памяти агентов. Рабочая папка `D:\AionUi-Paperclip` содержит SML, документы контекста, agent-log и дашборд `apps/aion-vision`.
- **Aion Vision** показывает состояние общей памяти SML. Он может отображать записи о Bitrix как историю работы агентов, но не должен становиться интерфейсом Bitrix-аналитики.

## Рабочая схема

Актуальная рабочая связка на 2026-06-18:

- Codex
- Claude Code
- Gemini CLI

Cursor, Kiro и MiMo Code выведены из схемы 2026-06-18; их конфиги (`.cursor/`, `.kiro/`, `.mimocode/`) и запускатели удалены, чтобы не создавать путаницу. Историческая память об их работе сохранена в SML и `docs/agent-log/`, а ценные спецификации из `.kiro/specs/` перенесены в `docs/specs/`. Вернуть любой инструмент можно только по отдельному решению пользователя.

AionUi, Paperclip и Hermes больше не используются как основа текущей архитектуры.

Основной MCP-сервер памяти — **Shared_Memory_Layer (SML)** (`tools/sml/`). Старый `aion-file-memory` больше не является активным сервером памяти; он оставлен только как reference/legacy-код.

## Цель

Сделать так, чтобы разные агенты и модели работали в одной общей системе:

- знали запросы и результаты друг друга;
- могли оценивать работу друг друга;
- сохраняли общий контекст;
- фиксировали решения и задачи в документах;
- могли заменять друг друга при окончании подписки или лимитов;
- в будущем использовали общую MCP-память.

## Текущая структура

- Рабочая папка: `D:\AionUi-Paperclip`.
- `AGENTS.md` - единые правила для всех агентов.
- `CLAUDE.md` - проектные правила Claude Code.
- `.mcp.json` - проектное подключение SML для Claude Code и других MCP-клиентов, которые читают корневой MCP-конфиг.
- `.vscode/` - настройки и tasks для работы с общей памятью из VS Code.
- `.gemini/settings.json` - проектное подключение SML для Gemini CLI.
- `docs/agent-log/` - журнал работы агентов.
- `docs/decisions.md` - журнал решений.
- `docs/tasks.md` - список задач.
- `docs/memory/` - файловый источник истины для общей памяти.
- `docs/specs/` - спецификации проекта, в т.ч. ядра SML `agents-shared-memory-layer`.
- `docs/START-HERE.md` - первый файл для любого нового агента.
- `docs/context-index.md` - карта всех источников контекста.
- `docs/context-packs/` - собранные контекстные пакеты.
- `docs/relationship-maps.md` - стандарт построения карт связей и индекс текущих графов.
- `docs/relationship-maps/` - Markdown/JSON карты связей для SML, агентов, документов и инструментов.
- `docs/handoffs/` - передачи задач между агентами.
- `docs/agents.md` - реестр агентов.
- `docs/local-environment.md` - локальное окружение.
- `docs/vscode-sml.md` - роль VS Code как общей IDE-оболочки SML.
- `tools/sml/` - основной MCP-сервер Shared_Memory_Layer (CLI: `python -m tools.sml.core stats|ping|selfcheck`). Схема БД v2: FTS5-индекс `records_fts` даёт полнотекстовый фоллбэк семантического поиска, когда Ollama недоступна (`sml.semantic_query` отвечает `mode="text"`).
- `tools/aion_memory_mcp.py` - legacy/reference-сервер файловой памяти, не основной путь.
- `tools/watch-memory.ps1` - фоновый наблюдатель: context-pack, relationship-map, экспорт дашборда, бэкап БД и heartbeat (`logs/memory-auto.heartbeat`).
- `tools/status-memory-auto.ps1` - статус автоматизации, включая проверку свежести heartbeat.
- `tools/normalize-sml-authors.py` - нормализация имён агентов в SML.
- `tools/backup-sml.py` - бэкап БД SML с ротацией и `--verify` (integrity + сверка записей).
- `.github/workflows/ci.yml` - CI: selfcheck + pytest ядра SML на push/PR.
- `apps/aion-vision/` - дашборд SML: живые данные через `/api/sml-dashboard` и поиск по памяти `/api/search` (`scripts/search-sml.py`, семантика + FTS5-фоллбэк). Панели «Здоровье системы» (watcher/поиск/бэкап) и «Аналитика памяти» (тренды по неделям, разбивка по агентам/типам). Dev: `START-AION-VISION.cmd` (vite middleware). Прод: `START-AION-VISION-SERVE.cmd` → `scripts/serve-sml.py` (stdlib HTTP-сервис, отдаёт `dist/` + API без dev-сервера).
- `docs/HOW-TO-USE.md` - гайд для новичка: запуск агентов и панели, поиск по памяти, обслуживание, troubleshooting.
- Ollama опциональна: без неё поиск работает в режиме FTS5 (по словам); семантика — только при запущенной Ollama.
- `docs/memory-automation.md` - описание автоматизации памяти.
- `docs/memory-autoprotocol.md` - правило автоматического поиска похожего контекста перед задачей.

## Автоматизация

Фоновый наблюдатель памяти установлен в Windows Task Scheduler.

Имя задачи:

```text
Aion File Memory Auto
```

Назначение: автоматически пересобирать `docs/context-packs/context-pack-latest.md` при изменениях в общей базе.

## Выведенные инструменты (Cursor, Kiro, MiMo Code)

Cursor, Kiro и MiMo Code выведены из схемы 2026-06-18. Их конфиги (`.cursor/`, `.kiro/`, `.mimocode/`) и запускатели (`OPEN-KIRO-RU.cmd`, `OPEN-MIMO-SML.cmd`, `CHECK-MIMO-SML.cmd`) удалены, чтобы не создавать путаницу в активной схеме Codex + Claude Code + Gemini CLI.

Сохранено:

- историческая память об их работе — записи в SML и `docs/agent-log/`;
- ценные спецификации из бывшего `.kiro/specs/` перенесены в `docs/specs/` (в т.ч. спецификация ядра SML `agents-shared-memory-layer`, на которую ссылается `tools/sml/__init__.py`).

Вернуть любой из этих инструментов можно только по отдельному решению пользователя.

## Gemini CLI

Gemini CLI установлен, авторизован и подключен к SML.

Проверено:

- установлен пакет `@google/gemini-cli`;
- версия CLI: `0.42.0`;
- пользовательский конфиг: `C:\Users\koval\.gemini\settings.json`;
- проектный конфиг: `D:\AionUi-Paperclip\.gemini\settings.json`;
- MCP-сервер `sml` добавлен в оба конфига;
- `gemini mcp list` показывает `sml` как `Connected`;
- прямой stdio smoke-test SML через `tools.sml.mcp_adapter` проходит: `initialize`, `tools/list`, `sml.ping`;
- живой smoke-test через сам Gemini CLI проходит: Gemini вызывает `sml.ping` и `sml.startup_pack`, видит общий контекст и записи памяти.

Подробная инструкция: `docs/gemini-sml.md`.

## Claude Code

Claude Code — активный агент рядом с Codex и Gemini CLI.

Подготовлено:

- `CLAUDE.md` - правила Claude Code для русского языка, SML, relationship-map и журналирования;
- `.mcp.json` - проектный MCP-конфиг с сервером `sml`;
- `OPEN-CLAUDE-SML.cmd` - запуск Claude из рабочей папки;
- `CHECK-CLAUDE-SML.cmd` - базовая проверка auth/MCP после установки CLI.

Проверено:

- Claude Code установлен: `2.1.178`, авторизован, работает из `D:\AionUi-Paperclip`;
- `claude mcp list` показывает `sml` как `Connected`;
- 2026-06-18 Claude Code выполнил содержательную работу (аудит проекта + правки P0/P1/P2/P3) и записал отчёт в `docs/agent-log/` — живой рабочий цикл подтверждён.

Важно: Claude web, Claude Desktop projects/chats и OpenClaude/Cowork-сессии не получают общий SML-контекст автоматически. Общую память видит только тот Claude-клиент, который:

1. запущен из `D:\AionUi-Paperclip`;
2. читает `CLAUDE.md`;
3. видит проектный `.mcp.json`;
4. имеет подключенный MCP-сервер `sml`;
5. авторизован в Claude Code.

Если Claude говорит, что видит только локальные Cowork-сессии и не имеет доступа к проектам/чатам Claude, значит используется не наш локальный Claude Code-контур SML, а отдельная оболочка.

## VS Code

VS Code добавлен в общий контекст как рабочая IDE-оболочка, а не как отдельный агент. Он нужен, чтобы открывать `D:\AionUi-Paperclip`, держать рядом правила агентов, context-pack, SML-скрипты, журнал и терминалы Codex/Claude/Gemini.

Подготовлено:

- `.vscode/settings.json` - настройки рабочей папки, UTF-8 и исключения тяжелых каталогов;
- `.vscode/tasks.json` - задачи для проверки памяти, пересборки context-pack, пересборки relationship-map, поиска по карте и проверки Claude MCP;
- `OPEN-VSCODE-SML.cmd` - запуск VS Code в рабочей папке;
- `CHECK-VSCODE-SML.cmd` - проверка VS Code, общей памяти и Claude MCP;
- `docs/vscode-sml.md` - инструкция по роли VS Code.

Проверено: `Code.exe` найден по пути `C:\Users\koval\AppData\Local\Programs\Microsoft VS Code\Code.exe`, версия VS Code `1.124.2`, но команда `code` не найдена в PATH текущей PowerShell-сессии. Поэтому запускатели используют прямой путь к `Code.exe`.

## Поведение агентов по умолчанию

Агенты больше не должны ждать отдельной команды "посмотри в память".

Перед любой содержательной задачей агент сам:

1. определяет тему запроса;
2. вызывает `sml.startup_pack`;
3. ищет похожее через `sml.semantic_query`;
4. если SML недоступен, ищет по `docs/context-packs/context-pack-latest.md` и `docs/`;
5. учитывает найденное перед ответом или действием.

## Карты связей

Для построения и обновления карт связей добавлен постоянный Codex skill:

```text
C:\Users\koval\.codex\skills\relationship-map-builder
```

Текущая карта по Graphify/SML/Codex/Gemini находится в:

```text
docs/relationship-maps/graphify-sml-relationship-map.md
docs/relationship-maps/graphify-sml-relationship-map.json
```

Карты связей являются автоматическим производным слоем над SML и документами. Watcher памяти пересобирает их вместе с context-pack, а агенты используют `tools/query-relationship-map.py "<тема>"` как быстрый навигатор перед широким поиском по файлам. Этот слой помогает видеть центральные узлы и мосты, но не заменяет SML как основную память.

## Следующий шаг

Проверить новый рабочий цикл Codex + Gemini + Claude Code:

1. Codex выполняет небольшую инженерную задачу.
2. Gemini CLI через `/sml:review` читает SML и дает независимое ревью.
3. Claude Code читает `CLAUDE.md`, видит `sml` через `.mcp.json` и дает второе инженерное ревью.
4. Codex учитывает замечания и фиксирует итог через `sml.add_log`.
