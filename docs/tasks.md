# Задачи

## Активные

- Поддерживать устойчивый рабочий цикл Codex + Claude Code + Gemini CLI: один агент выполняет задачу, другой проверяет через SML, итог фиксируется в SML и `docs/agent-log/`.
- Перезапустить MCP-сервер `sml` у активных агентов, чтобы нормализация `author_agent` применялась к новым записям (живой процесс держит старый код до перезапуска клиента).

## Внешние проекты

- Bitrix/Bit.Newton аналитика ведётся как отдельный прикладной проект: `C:\Users\koval\bat\bitrix24-automation`.
- Backlog и риски по нему вынесены в `docs/projects/bitrix24-automation.md`.
- Общий список задач `D:\AionUi-Paperclip` должен содержать только задачи инфраструктуры памяти, агентов и Aion Vision. Прикладные задачи Bitrix не смешивать с активными задачами SML.

## Завершенные

- 2026-06-18 (Claude Code) Aion Vision: постоянный HTTP-сервис `serve-sml.py` (stdlib) для прод-режима — статика `dist/` + API без dev-сервера; запускатель `START-AION-VISION-SERVE.cmd`. Проверено curl + Playwright (поиск «конверсия за неделю» → 10 результатов, 0 console errors).
- 2026-06-18 (Claude Code) Aion Vision «мощнее»: живые данные через `/api/sml-dashboard` (откат на снимок) и семантический поиск по памяти прямо из UI (`/api/search` + `search-sml.py` с FTS5-фоллбэком, компонент `MemorySearch`). ESLint + build зелёные.
- 2026-06-18 (Claude Code) Надёжность топ-3: FTS5-фоллбэк семантического поиска без Ollama (миграция БД v2, `mode=text`); heartbeat watcher + тревога в `status-memory-auto`; verify бэкапа (integrity + сверка записей); CI на GitHub Actions + unit-тест `normalize_author`. 163 теста зелёные.
- 2026-06-18 (Claude Code) Аудит проекта + правки P0/P1/P2/P3: подключён экспорт дашборда и ежедневный бэкап БД к watcher; нормализованы имена агентов в SML (7→4 автора); расширен цветовой код типов и защищён NexusGraph в Aion Vision; убран мёртвый API-endpoint; достроен CLI ядра SML (`stats/ping/selfcheck`); выведены Cursor/Kiro/MiMo, их спецификации сохранены в `docs/specs/`.

- Проверено наличие и содержание `.cursor/rules/`. Правило `shared-context.mdc` обновлено для использования SML вместо устаревшего `aion-file-memory`.
- Gemini CLI авторизован и успешно прошел smoke-test SML (ping, startup_pack, semantic_query, add_log).
- Запущен `CHECK-GEMINI-SML.cmd` (внутри текущей сессии), записан лог `019e20ff-8d86-73f8-9987-c280fd8e035b`.
- Создана чистая рабочая структура для Codex, Cursor и Kiro.
- Добавлены общие правила для агентов.
- Добавлены правила Cursor.
- Добавлены steering-документы Kiro.
- Добавлены документы текущего контекста, решений и задач.
- Добавлены запускатель `OPEN-AGENT-WORKSPACE.cmd`.
- Рабочая структура перенесена в `D:\AionUi-Paperclip`.
- Добавлены стартовый файл, индекс контекста, реестр агентов, локальное окружение, слои памяти и handoff-протокол.
- Добавлены скрипт генерации контекстного пакета.
- Сгенерирован первый `docs/context-packs/context-pack-latest.md`.
- Добавлены MCP-конфиги для Cursor и Kiro.
- Установлен и запущен автозапуск фонового наблюдателя памяти через Windows Task Scheduler.
- Проверено автоматическое обновление `docs/context-packs/context-pack-latest.md` после изменения документа.
- Добавлен автопротокол памяти: агенты должны сами искать похожее перед задачей.
- Kiro переведен на русский режим насколько это поддерживает приложение: установлен русский языковой пакет, включена локаль `ru`, добавлен русский steering.
- Проверено, что Kiro запускается в `D:\AionUi-Paperclip`.
- Убрано дублирование Kiro MCP-конфигов: активным оставлен проектный `.kiro/settings/mcp.json`.
- Реализован и подключен основной MCP-сервер памяти `sml`.
- Codex, Cursor и Kiro переведены на `sml` как основной сервер памяти.
- Gemini CLI установлен, SML прописан в пользовательском и проектном конфиге Gemini.
- Полный набор тестов SML проходит: `141 passed`.
- Доведено до рабочего состояния: повторный Google AI Pro login, `GEMINI_API_KEY` или Vertex AI (подтверждено активной сессией).
- После авторизации Gemini CLI запущен `CHECK-GEMINI-SML.cmd` и записан успешный `sml.add_log` от имени `Gemini CLI`.
- На 2026-05-27 активная рабочая схема сведена к Codex + Gemini; Cursor и Kiro исключены из обязательного рабочего цикла.
- Актуализированы ключевые документы под схему Codex + Gemini: `AGENTS.md`, `GEMINI.md`, `docs/current-context.md`, `docs/agents.md`, `docs/tasks.md`, `docs/local-environment.md`, `docs/mcp-memory.md`, `docs/memory/layers/constraints.md`, `docs/decisions.md`.
- Добавлен постоянный Codex skill `relationship-map-builder` для Graphify-style карт связей, адаптированный под SML. Созданы `docs/relationship-maps.md`, `docs/relationship-maps/graphify-sml-relationship-map.md` и JSON-граф.
- Relationship-map подключен как автоматический слой памяти: watcher пересобирает карту вместе с context-pack, добавлены `tools/build-relationship-map.ps1` и `tools/query-relationship-map.py`.
- Claude Code добавлен в активную схему общей памяти: созданы `CLAUDE.md`, проектный `.mcp.json`, `OPEN-CLAUDE-SML.cmd` и `CHECK-CLAUDE-SML.cmd`; CLI версии `2.1.178` найден через `C:\Users\koval\AppData\Roaming\npm\claude.cmd`, `sml` в `claude mcp list` подключен, но живой prompt/smoke-test ожидает `claude auth login`.
- VS Code добавлен в общий контекст как IDE-оболочка SML: созданы `.vscode/settings.json`, `.vscode/tasks.json`, `OPEN-VSCODE-SML.cmd`, `CHECK-VSCODE-SML.cmd` и `docs/vscode-sml.md`; `Code.exe` версии `1.124.2` найден по прямому пути, но `code` не найден в PATH текущей PowerShell-сессии.
- MiMo Code установлен и подключен к SML как экспериментальный агент: создан `.mimocode/mimocode.json`, агенты `sml-review/sml-plan/sml-build`, `OPEN-MIMO-SML.cmd`, `CHECK-MIMO-SML.cmd`; `mimo mcp list` показывает `sml connected`, но `mimo providers list` показывает `0 credentials`.


## Отложенные

- Настроить регулярный аудит качества записей SML.

## Устаревшие

- Настроить автоматические Kiro hooks поверх SML — неактуально, пока Kiro не входит в активную схему.
