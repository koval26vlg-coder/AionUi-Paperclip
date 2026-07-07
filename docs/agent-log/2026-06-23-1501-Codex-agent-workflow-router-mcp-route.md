# 2026-06-23 15:01 +03 - Codex - agent-workflow-router MCP route update

## Исходный запрос

Пользователь добавил к рабочему протоколу три MCP: Context7 для свежей документации, GitHub MCP для репозиториев/PR/issues/comments и Playwright MCP для браузерного тестирования и сбора данных со страниц.

## Что сделано

- `agent-workflow-router` обновлен: добавлен тип `MCP-assisted work`.
- В route table добавлена строка для library/API docs, external repositories, browser testing и web inspection.
- Добавлен раздел `MCP Route Detail`:
  - Context7 MCP использовать для актуальной документации библиотек/SDK/API/CLI/cloud services.
  - GitHub MCP использовать для repo/issue/PR/commit/code-search контекста, не печатать токены.
  - Playwright MCP использовать для браузерной проверки UI, screenshot/responsive/console/form flows и web inspection.
- Eval-набор расширен четвертым сценарием, который требует Context7 + GitHub MCP + Playwright MCP.
- Копии синхронизированы в Codex, Claude Code, `.agents` и shared `agent-skills`.

## Проверки

- Claude MCP health-check показал `plugin:context7:context7` и `plugin:playwright:playwright` как Connected.
- GitHub MCP в прямом `claude mcp list` показал transient `Failed to connect`; раньше verify-script подтверждал GitHub token/API, но на этот запуск нужно учитывать текущий health-check.
- `codex mcp list` сейчас не стартует из-за `C:\Users\koval\.codex\config.toml`: `service_tier = default` больше не принимается CLI, ожидаются `fast` или `flex`. Конфиг не менялся в этом шаге.

## Следующий агент

При задачах с документацией библиотек использовать Context7. При GitHub-задачах сначала проверить MCP auth/health. При UI/browser задачах использовать Playwright MCP и не заявлять browser-backed evidence без успешного запуска.

