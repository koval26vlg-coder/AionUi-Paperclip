# 2026-07-06 22:59 +03:00 — Codex — Grok Build runtime, SML MCP и L1 smoke

## Исходный запрос пользователя

Пользователь подтвердил: добавить Grok 0.2.87 как нижний уровень Роя не вместо других агентов, а в цепочке `Grok -> Gemini -> Codex -> Claude`, и довести подключение до рабочего состояния.

## Краткий план

- Подтянуть SML-контекст.
- Установить и авторизовать Grok CLI.
- Подключить SML MCP для Grok.
- Исправить совместимость имен SML tools с Grok.
- Проверить model smoke, SML smoke и L1 workflow runner.
- Обновить документы памяти.

## Что сделано

- Установлен npm-пакет `@xai-official/grok@0.2.87`.
- `grok version` подтвердил `grok 0.2.87 (0ae0bf47e5)`.
- Через видимое PowerShell-окно завершен `grok login --device-auth`; `grok models` показывает `grok-composer-2.5-fast` и `grok-build`.
- В `D:\AionUi-Paperclip\.grok\config.toml` добавлен MCP server `sml`.
- В `tools/sml/mcp_adapter.py` добавлен режим `SML_MCP_TOOL_NAME_MODE=grok-safe`, чтобы Grok видел SML tools как `sml_ping`, `sml_startup_pack`, `sml_semantic_query` и т.д. Старые dotted names остаются default для Codex/Claude/Cursor/Kiro.
- В `tools/grok_build_workflow_review.py` добавлен fallback на `C:\Users\koval\AppData\Roaming\npm\grok.cmd`, PATH-prepend для Git/Node/Windows, `SML_MCP_TOOL_NAME_MODE=grok-safe`, запуск через `grok-build` и `--prompt-file`, а также фильтр внешнего MCP stderr-шума на успешном запуске.
- Создан smoke workflow `2026-07-06-225247-147230-smoke-grok-gemini` через `-Profile grok-gemini`.
- Grok L1 runner сформировал валидный русский handoff, сохраненный в `docs/agent-workflows/2026-07-06-225247-147230-smoke-grok-gemini/grok-l1-handoff.md`.
- Через trusted executor Codex выполнены `claim` и `submit-work` за `Grok Build`; workflow перешел в `waiting_for_approval`, следующий разрешенный агент — `Gemini Vertex`.

## Измененные файлы

- `AGENTS.md`
- `docs/agents.md`
- `docs/agent-workflows/README.md`
- `docs/agent-workflows/model-policy.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/decisions.md`
- `docs/agent-log/2026-07-06-2259-Codex-grok-runtime-sml-smoke.md`
- `docs/agent-workflows/2026-07-06-225247-147230-smoke-grok-gemini/grok-l1-handoff.md`
- `D:\AionUi-Paperclip\.grok\config.toml`
- `tools/grok_build_workflow_review.py`
- `tools/sml/mcp_adapter.py`
- `tools/sml/tests/test_grok_build_workflow_review.py`
- `tools/sml/tests/test_mcp_adapter.py`

## Проверки выполнены

- `grok version` — `grok 0.2.87`.
- `grok models` — logged in with `grok.com`, доступен `grok-build`.
- `grok mcp doctor` — `sml` handshake OK, 10 tools discovered.
- `grok --model grok-build -p "Ответь ровно одним словом: OK"` — `OK`.
- Grok prompt с `sml_ping` — `SML OK`, `ok=true`, `version sml-0.1.0`, `degraded=false`.
- `python -X utf8 -m pytest tools/sml/tests/test_grok_build_workflow_review.py tools/sml/tests/test_mcp_adapter.py tools/sml/tests/test_agent_workflow.py -q` — `41 passed`.
- `python -X utf8 -m py_compile tools/sml/mcp_adapter.py tools/grok_build_workflow_review.py tools/agent_workflow.py` — успешно.
- `tools/grok_build_workflow_review.py 2026-07-06-225247-147230-smoke-grok-gemini ...` — валидный L1 handoff с `approve`.
- `agent_workflow.py status 2026-07-06-225247-147230-smoke-grok-gemini` — `state: waiting_for_approval`, `allowed_next_agents: Gemini Vertex`.

## Риски и ограничения

- `grok-gemini` остается экспериментальным явным профилем и не заменяет дефолтный `antigravity`.
- `grok mcp doctor` может возвращать общий exit code 1 из-за внешних GitHub/Mobbin MCP из глобальных совместимых конфигов; это не блокирует SML.
- Grok Build является review-only участником: state mutations делает Codex/Claude через `--executor`.
- Не запускать Grok на долгие задачи скрыто; действует Visible Run Rule.

## Что должен проверить следующий агент

- Для реальной задачи запускать `grok-gemini` только явно через `-Profile grok-gemini`.
- L1 Grok handoff получать через `tools/grok_build_workflow_review.py`, затем submit через `agent_workflow.py ... --executor Codex`.
- Если нужен полный прогон цепочки, следующий шаг после L1 — ревью `Gemini Vertex`, а не повторный Grok.
