# Отчет агента

Дата и время: 2026-07-03 12:09 +03

Агент: Codex

## Исходный запрос пользователя

Сделать дефолтным запуск `Рой` через `agy`/Antigravity, а Gemini Vertex оставить запасным вариантом.

## Краткий план

1. Переключить default workflow profile с `gemini-vertex` на `antigravity`.
2. Обновить тесты и документацию, чтобы `Gemini Vertex` остался явным fallback.
3. Проверить unit/smoke сценарии и записать итог в память.

## Что сделано

- `tools/agent_workflow.py` теперь использует `DEFAULT_WORKFLOW_PROFILE = "antigravity"`.
- `tools/start-agent-swarm.ps1` теперь без явного `-Profile` создает workflow с `Profile: antigravity`.
- Тесты workflow перестроены: default проверяет `Antigravity CLI`, отдельный тест проверяет fallback `gemini-vertex`.
- Обновлены проектные и глобальные правила: `AGENTS.md`, `CLAUDE.md`, `C:\Users\koval\.codex\AGENTS.md`, `C:\Users\koval\.claude\CLAUDE.md`.
- Обновлены рабочие документы: `docs/agent-workflows/README.md`, `docs/agent-workflows/SWARM-COMMAND.md`, `docs/agent-workflows/model-policy.md`, `docs/agents.md`, `docs/agent-memory-bootstrap.md`, `docs/current-context.md`, `docs/tasks.md`, `docs/decisions.md`, `docs/local-environment.md`, `docs/memory/layers/constraints.md`.

## Проверки

- `py_compile`: `tools/agent_workflow.py`, `tools/antigravity_workflow_review.py`, `tools/gemini_vertex_workflow_review.py` — OK.
- `pytest`: `tools/sml/tests/test_agent_workflow.py`, `test_antigravity_print.py`, `test_antigravity_workflow_review.py`, `test_gemini_vertex_workflow_review.py` — `24 passed`.
- Smoke default: `tools/start-agent-swarm.ps1` без `-Profile` создал workflow `workflow_profile: antigravity`, `allowed_next_agents: Antigravity CLI`.
- Smoke fallback: `tools/start-agent-swarm.ps1 -Profile gemini-vertex` создал workflow `workflow_profile: gemini-vertex`, `allowed_next_agents: Gemini Vertex`.
- Live Antigravity smoke: `tools/antigravity_print.py --process-timeout-seconds 90 "Ответь ровно одним словом: OK"` вернул `OK`.

## Риски и ограничения

- Antigravity остается review-only для state mutations: `agy` не должен сам вызывать `agent_workflow.py` и менять workflow state.
- При повторном runtime blocker Antigravity конкретный workflow нужно запускать с fallback `-Profile gemini-vertex`.
- Старые agent-log и старые workflow могут содержать исторический default `gemini-vertex`; их не переписывать.

## Что должен проверить следующий агент

- При новом `Рой: <задача>` убедиться, что `contract.json.workflow_profile` равен `antigravity`.
- Если нужен Vertex fallback, использовать только явный `-Profile gemini-vertex` / `--profile gemini-vertex`.
