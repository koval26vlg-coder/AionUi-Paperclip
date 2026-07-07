# 2026-07-06 22:02 +03:00 — Codex — Grok Build 0.2.87 как кандидат SML-агента

## Исходный запрос пользователя

Пользователь сообщил: «у нас еще появился один агент Grok 0.2.87».

## Краткий план

- Подтянуть SML-память по теме Grok.
- Проверить, виден ли Grok локально как CLI.
- Сверить публичное описание Grok Build с требованиями SML-схемы.
- Зафиксировать статус в документах памяти без преждевременного включения в активный workflow.

## Что сделано

- Выполнен SML bootstrap по теме `Grok 0.2.87 новый агент интеграция в общую память SML`.
- Проверены типовые локальные места запуска: `%USERPROFILE%\AppData\Roaming\npm`, `%USERPROFILE%\.local\bin`, `%USERPROFILE%\bat`.
- Проверен глобальный npm-реестр через `npm list -g --depth=0`.
- Проверена команда `grok --version`: в текущем PATH команда не найдена.
- По официальной странице xAI CLI зафиксировано, что Grok Build поддерживает `AGENTS.md`, MCP servers, skills, hooks и memory, поэтому архитектурно совместим с SML-подходом после локальной установки и проверки.

## Измененные файлы

- `AGENTS.md`
- `docs/agents.md`
- `docs/tasks.md`
- `docs/current-context.md`
- `docs/decisions.md`
- `docs/agent-log/2026-07-06-2202-Codex-grok-build-candidate.md`

## Проверки

- `Get-Command grok` — не найден.
- `grok --version` — не найден.
- Поиск `*grok*` в `%USERPROFILE%\AppData\Roaming\npm`, `%USERPROFILE%\.local\bin`, `%USERPROFILE%\bat` — не найден.
- `npm list -g --depth=0` — Grok не найден.

## Риски и ограничения

- Grok пока не считается рабочим участником активной связки: нет локального CLI, auth и smoke-теста.
- Нельзя включать Grok в дефолтный `Рой` до проверки `grok --version`, чтения `AGENTS.md`, SML bootstrap/MCP и записи отчета.
- Секреты/auth-данные Grok нельзя сохранять в `docs/`, SML, `AGENTS.md` или `.mcp.json`.

## Что должен проверить следующий агент

- Найти фактический путь установки Grok Build или установить официальный CLI.
- Подтвердить `grok --version`.
- Выполнить auth без утечки секретов.
- Запустить короткий smoke из `D:\AionUi-Paperclip` на русском языке.
- Проверить, видит ли Grok `AGENTS.md`, SML bootstrap и MCP `sml`.
- После успешного smoke решить, нужен ли отдельный workflow profile для Grok.
