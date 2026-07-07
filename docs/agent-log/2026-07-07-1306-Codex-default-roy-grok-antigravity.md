# 2026-07-07 13:06 +03 - Codex - default РОЙ grok-antigravity

## Запрос
Пользователь попросил сделать так, чтобы команда `РОЙ` запускала цепочку:

```text
L1 Grok -> L2 Antigravity CLI -> L3 Codex -> L4 Codex -> L5 Claude Code
```

## Сделано
- `tools/agent_workflow.py`: добавлен profile `grok-antigravity`, он сделан `DEFAULT_WORKFLOW_PROFILE`.
- `tools/start-agent-swarm.ps1`: default `-Profile grok-antigravity`.
- `tools/grok_build_workflow_review.py`: Grok L1 handoff теперь ориентируется на L2 из `contract.json`, поэтому для default route пишет handoff под `Antigravity CLI L2`.
- Тесты обновлены под правило: следующий уровень оценивает предыдущий. После сдачи L1 решение принимает L2 `Antigravity CLI`, а не сам L1 `Grok Build`.
- Документы и глобальные правила Codex/Claude обновлены: активная связка `Grok Build + Antigravity CLI + Codex + Claude Code`; `Gemini Vertex` остается fallback, `antigravity` и `grok-gemini` остаются явными профилями.

## Проверка
- `py_compile` прошел для workflow CLI и review runners.
- `pytest` прошел: `33 passed`.
- Smoke без явного `-Profile`: `tmp/swarm-default-grok-antigravity-smoke/2026-07-07-130352-778636-рой-default-grok-antigravity-smoke`.
- Smoke contract:
  - `workflow_profile=grok-antigravity`
  - `current_level=L1`
  - `allowed_next_agents=Grok Build`
  - `L1=Grok Build`
  - `L2=Antigravity CLI`
  - `L3=Codex`
  - `L4=Codex`
  - `L5=Claude Code`

## Важное правило
`Grok Build`, `Antigravity CLI` и `Gemini Vertex` остаются review-only участниками для workflow state mutations. Их выводы получает isolated runner, а `Codex`/`Claude Code` выполняют `claim`, `submit-work`, `approve-level` как trusted executor.
