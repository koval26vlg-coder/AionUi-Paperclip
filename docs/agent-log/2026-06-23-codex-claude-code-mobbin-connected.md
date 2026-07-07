# 2026-06-23 - Codex - Claude Code Mobbin connected

## Исходный запрос

Пользователь сообщил "готово" после интерактивной авторизации Mobbin MCP в Claude Code.

## Что сделано

- Проверен `active-run-gate`: `trading_mvp` остается `RUNNING`; проект не затрагивался.
- Проверен свежий статус Claude Code MCP.
- Обновлены:
  - `agent-skills/MCP_INSTALL_MANIFEST.md`
  - `agent-skills/mcp-install-manifest.json`

## Проверки

- `claude mcp get mobbin` показывает:
  - `Status: √ Connected`
  - `Type: http`
  - `URL: https://api.mobbin.com/mcp`
- `claude mcp list` показывает `mobbin: https://api.mobbin.com/mcp (HTTP) - √ Connected`.
- `codex mcp list` продолжает показывать `mobbin ... enabled OAuth`.
- `mcp-install-manifest.json` успешно распарсен как JSON и теперь содержит `claude_code: configured_connected`.

## Остатки

- Antigravity Mobbin все еще отмечен как требующий отдельной интерактивной OAuth-авторизации в Antigravity settings.
- ChatGPT/Codex App connector отмечен как подключенный по подтверждению пользователя, но это состояние не видно через локальный `codex mcp list`.
