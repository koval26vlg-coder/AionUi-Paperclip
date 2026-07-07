# 2026-06-23 - Codex - Mobbin ChatGPT connector user reported connected

## Исходный запрос

Пользователь сообщил "готово" после интерактивного подключения Mobbin в ChatGPT/Codex App.

## Что сделано

- Выполнен `active-run-gate`: `trading_mvp` остается `RUNNING`; проект не затрагивался.
- Проверен локальный Codex MCP статус.
- Обновлены:
  - `agent-skills/MCP_INSTALL_MANIFEST.md`
  - `agent-skills/mcp-install-manifest.json`

## Проверки

- `codex mcp list` показывает `mobbin https://api.mobbin.com/mcp enabled OAuth`.
- `mcp-install-manifest.json` успешно распарсен как JSON.
- Manifest теперь содержит `chatgpt_codex_app: user_reported_connected_not_locally_verifiable`.

## Ограничение

Состояние ChatGPT/Codex App connector хранится в аккаунте ChatGPT и не видно через локальный `codex mcp list`. Поэтому факт подключения зафиксирован как подтвержденный пользователем, а не как локально верифицированный CLI-статус.
