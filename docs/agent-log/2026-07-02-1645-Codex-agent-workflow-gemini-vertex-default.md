# 2026-07-02 16:45 +03 - Codex - agent workflow Gemini Vertex default

## Исходный запрос
Пользователь попросил решить проблему Antigravity после успешного OAuth, но продолжающегося `FAILED_PRECONDITION (code 400): User location is not supported for the API use`, и сделать рабочий обход для `Рой`/agent-workflow.

## Краткий план
- Не пытаться считать proxy/OAuth достаточным обходом Antigravity eligibility.
- Перевести новые workflow на рабочий L1/L2 runtime через Gemini Vertex.
- Оставить Antigravity как явный optional profile после успешного smoke.
- Обновить CLI, launcher, docs, tests и зафиксировать проверку.

## Что сделано
- В `tools/agent_workflow.py` добавлены workflow profiles:
  - default `gemini-vertex`;
  - optional `antigravity`.
- Новый default chain:
  `L1 Gemini Vertex -> L2 Gemini Vertex -> L3 Codex -> L4 Codex -> L5 Claude Code`.
- В `contract.json` новых workflow добавляется `workflow_profile`.
- `Gemini Vertex` добавлен в review-only mutation agents: state mutations требуют `--executor Codex` или `--executor "Claude Code"`.
- `tools/start-agent-swarm.ps1` получил параметр `-Profile gemini-vertex|antigravity`, по умолчанию `gemini-vertex`.
- Добавлен isolated runner `tools/gemini_vertex_workflow_review.py`, который собирает packet из `brief.md`, `contract.json`, `handoff.md`, `events.jsonl`, вызывает Vertex Gemini и валидирует стандартные handoff headings.
- В `.venv-sml` установлен `google-genai`; зависимость добавлена в `tools/sml/requirements.txt`.
- Обновлены документы: `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/current-context.md`, `docs/tasks.md`, `docs/decisions.md`, `docs/agents.md`, `docs/local-environment.md`, `docs/agent-workflows/README.md`, `docs/agent-workflows/SWARM-COMMAND.md`, `docs/agent-workflows/model-policy.md`.

## Измененные файлы
- `tools/agent_workflow.py`
- `tools/start-agent-swarm.ps1`
- `tools/gemini_vertex_workflow_review.py`
- `tools/sml/requirements.txt`
- `tools/sml/tests/test_agent_workflow.py`
- `tools/sml/tests/test_gemini_vertex_workflow_review.py`
- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/decisions.md`
- `docs/agents.md`
- `docs/local-environment.md`
- `docs/agent-workflows/README.md`
- `docs/agent-workflows/SWARM-COMMAND.md`
- `docs/agent-workflows/model-policy.md`

## Проверки
- `python -m pytest tools/sml/tests/test_agent_workflow.py tools/sml/tests/test_antigravity_workflow_review.py tools/sml/tests/test_gemini_vertex_workflow_review.py -q` -> 17 passed.
- `python -m py_compile tools/agent_workflow.py tools/gemini_vertex_workflow_review.py tools/antigravity_workflow_review.py` -> OK.
- `tools/start-agent-swarm.ps1 -DryRun` -> показывает `Profile: gemini-vertex` и create command с `--profile gemini-vertex`.
- `tools/start-agent-swarm.ps1 -Profile antigravity -DryRun` -> показывает явный `--profile antigravity`.
- Live smoke в `tmp/gemini-vertex-workflow-smoke-20260702-163610`:
  - created workflow `2026-07-02-163610-307818-gemini-vertex-workflow-smoke`;
  - `gemini_vertex_workflow_review.py` вернул валидный L1 handoff через Vertex Gemini;
  - `claim` и `submit-work` прошли с `--agent "Gemini Vertex" --executor Codex`;
  - `approve-level` перевел workflow на `current_level: L2`, `allowed_next_agents: Gemini Vertex`.

## Риски и ограничения
- Antigravity CLI не удален: он остается optional profile, но нельзя считать его дефолтным runtime, пока fresh live smoke не пройдет без regional/eligibility error.
- Gemini CLI не возвращен в схему; используется именно Vertex AI runtime через `google-genai`.
- Gemini Vertex расходует Vertex/GCP quota и должен учитываться в лимит-мониторинге отдельно, если потребуется численный учет.

## Что проверить следующему агенту
- При команде `Рой:` новые workflow должны создаваться с `workflow_profile: gemini-vertex`.
- Для L1/L2 использовать `tools/gemini_vertex_workflow_review.py`, затем mutating команды через `--executor Codex`.
- Antigravity запускать только явным `-Profile antigravity` после свежего smoke.
