# 2026-06-23 - Codex - Claude Code Mobbin auth attempt

## Исходный запрос

Пользователь попросил выполнить оставшийся шаг: авторизовать `mobbin` в Claude Code через `/mcp`.

## Что сделано

- Проверен `active-run-gate`: `trading_mvp` остается `RUNNING`; проект не затрагивался.
- Проверен статус Claude Code MCP:
  - `claude mcp get mobbin` показывает `Needs authentication`.
- Открыто видимое окно PowerShell с командой `claude /mcp`.
- После первой проверки статус не изменился.
- Открыто второе видимое окно обычной интерактивной Claude Code с инструкциями.
- В буфер обмена помещена команда `/mcp`, чтобы пользователь мог вставить ее в Claude Code.
- Проверено, что `claude -p '/mcp'` не подходит: выводит `/mcp isn't available in this environment.`

## Проверки

- Через 60 секунд после запуска интерактивного окна:
  - `claude mcp get mobbin` все еще показывает `Status: ! Needs authentication`.
  - `claude mcp list` все еще показывает `mobbin: https://api.mobbin.com/mcp (HTTP) - ! Needs authentication`.

## Ограничение

Claude Code не предоставляет отдельной CLI-команды `mcp login` для HTTP MCP, в отличие от Codex CLI. Авторизация Mobbin в Claude Code требует интерактивного шага внутри Claude Code: `/mcp` -> `mobbin` -> `Authenticate` -> browser OAuth.
