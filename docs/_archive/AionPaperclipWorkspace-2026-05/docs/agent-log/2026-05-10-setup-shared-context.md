# Настройка общего контекста

## Дата и время

2026-05-10

## Агент

Codex

## Запрос пользователя

Настроить основу, чтобы Codex, Cursor и Kiro знали запросы и результаты друг друга, могли оценивать работу друг друга, а общий контекст сохранялся и был доступен каждой модели.

## Что сделано

Создана чистая структура рабочей области для трех агентов:

- общие правила `AGENTS.md`;
- правила Cursor в `.cursor/rules/`;
- steering-документы Kiro в `.kiro/steering/`;
- журнал агентов в `docs/agent-log/`;
- документы текущего контекста, решений и задач;
- описание будущей общей MCP-памяти.

## Измененные файлы

- `README.md`
- `AGENTS.md`
- `.cursor/rules/shared-context.mdc`
- `.cursor/rules/review-other-agents.mdc`
- `.kiro/steering/00-shared-context.md`
- `.kiro/steering/10-spec-workflow.md`
- `.kiro/hooks/README.md`
- `docs/current-context.md`
- `docs/decisions.md`
- `docs/tasks.md`
- `docs/how-to-use-agents.md`
- `docs/memory/README.md`
- `docs/agent-log/README.md`
- `docs/templates/agent-report.md`
- `docs/templates/review-report.md`
- `OPEN-AGENT-WORKSPACE.cmd`
- `tools/open-agent-workspace.ps1`
- `tools/new-agent-log.ps1`

## Проверки

Структура файлов создана. Следующий шаг - проверить, что Cursor и Kiro читают свои правила внутри IDE.

## Риски и ограничения

Общая MCP-память пока не подключена. До ее настройки источником истины являются файлы в `docs/`.

## Что проверить следующему агенту

Cursor должен проверить, что правила `.cursor/rules` применяются. Kiro должен проверить, что steering-документы видны в проекте.
