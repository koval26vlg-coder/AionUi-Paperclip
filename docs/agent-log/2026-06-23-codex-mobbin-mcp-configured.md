# 2026-06-23 - Codex - Mobbin MCP setup

## Исходный запрос

Пользователь попросил настроить Mobbin MCP после внедрения `ai-design-workflow`.

## План

- Проверить официальную документацию Mobbin MCP.
- Зарегистрировать Mobbin MCP для Codex CLI и Claude Code.
- Добавить Mobbin MCP в Antigravity config.
- Проверить статусы без вывода секретов.
- Обновить MCP manifest.

## Что сделано

- Зарегистрирован Claude Code user-scope MCP:
  - `mobbin`
  - URL: `https://api.mobbin.com/mcp`
  - файл изменен командой `claude mcp add`: `C:\Users\koval\.claude.json`
- Зарегистрирован Codex CLI MCP:
  - `mobbin`
  - URL: `https://api.mobbin.com/mcp`
- Выполнен `codex mcp login mobbin`; Codex CLI показал `mobbin ... OAuth`.
- Добавлен `Mobbin` в Antigravity MCP config:
  - `C:\Users\koval\.gemini\config\mcp_config.json`
  - backup: `C:\Users\koval\.gemini\config\mcp_config.json.backup.20260623-191102`
- Обновлены:
  - `agent-skills/MCP_INSTALL_MANIFEST.md`
  - `agent-skills/mcp-install-manifest.json`

## Проверки

- `active-run-gate` проверен: `trading_mvp` остается `RUNNING`; эта работа не затрагивала проект.
- `codex mcp list` показал `mobbin https://api.mobbin.com/mcp enabled OAuth`.
- `claude mcp get mobbin` показал user-scope HTTP MCP, но статус `Needs authentication`.
- `C:\Users\koval\.gemini\config\mcp_config.json` успешно распарсен как JSON и содержит `Mobbin` с `serverUrl`.
- `agent-skills/mcp-install-manifest.json` успешно распарсен как JSON и содержит `mobbin`.

## Риски и ограничения

- Claude Code еще требует интерактивную авторизацию: открыть Claude Code, выполнить `/mcp`, выбрать `mobbin`, нажать `Authenticate`.
- Antigravity еще требует интерактивную авторизацию в настройках после Refresh MCP servers.
- Для Codex App официальная документация Mobbin говорит сначала подключить Mobbin в ChatGPT; Codex CLI уже авторизован отдельно.
- Mobbin MCP по официальной документации доступен на платных планах Mobbin и использует OAuth, не API key.
