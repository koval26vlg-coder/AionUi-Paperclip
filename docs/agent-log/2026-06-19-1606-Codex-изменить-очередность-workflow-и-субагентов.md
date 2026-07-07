# 2026-06-19 16:06 - Codex - изменить очередность workflow и субагентов

## Исходный запрос пользователя

Пользователь задал новую последовательность уровней:

```text
L1.0 MiMo AUTO
L1.1 Gemini CLI
L2 Gemini CLI
L3 Codex
L4 Codex
L5 Claude Code
```

Также попросил прописать субагентов под каждый уровень.

## Краткий план

1. Обновить `tools/agent_workflow.py` под новую очередность.
2. Добавить `subagents` в contract metadata для каждого уровня и подшага L1.
3. Обновить тесты smoke-path.
4. Обновить живые правила и документы памяти.
5. Прогнать проверки.

## Что сделано

- `L2` переведен на `Gemini CLI`.
- `L3` оставлен за `Codex` как декомпозиция реализации, тесты и automation.
- `L4` переведен на `Codex` как архитектурный синтез, contract audit, risk gate и maintainability review.
- `L5` переведен на `Claude Code` как независимая финальная техническая проверка и `final-report.md`.
- В `contract.json` новых workflow теперь пишутся субагенты:
  - `L1.0`: `mimo-intake-scanner`, `mimo-hypothesis-generator`, `mimo-risk-sentinel`;
  - `L1.1`: `gemini-source-verifier`, `gemini-context-expander`, `gemini-noise-filter`, `gemini-handoff-editor`;
  - `L2`: `gemini-engineering-reviewer`, `gemini-constraint-checker`, `gemini-edge-case-scout`, `gemini-revision-gate`;
  - `L3`: `codex-implementation-decomposer`, `codex-test-planner`, `codex-automation-builder`, `codex-integration-checker`;
  - `L4`: `codex-architecture-synthesizer`, `codex-contract-auditor`, `codex-risk-gate`, `codex-maintainability-reviewer`;
  - `L5`: `claude-executive-summarizer`, `claude-technical-verifier`, `claude-anti-distortion-auditor`, `claude-final-decision-writer`.
- `status` CLI теперь показывает субагентов текущего шага.
- Обновлены README/schema/smoke docs, `AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `README.md`, `docs/current-context.md`, `docs/tasks.md`, `docs/agents.md`, `docs/decisions.md`.

## Измененные файлы

- `tools/agent_workflow.py`
- `tools/sml/tests/test_agent_workflow.py`
- `docs/agent-workflows/README.md`
- `docs/agent-workflows/schema.example.json`
- `docs/agent-workflows/README-smoke.md`
- `docs/plans/2026-06-19-agent-coordination-workflow.md`
- `AGENTS.md`
- `GEMINI.md`
- `CLAUDE.md`
- `README.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agents.md`
- `docs/decisions.md`

## Проверки

- `python -m pytest tools\sml\tests\test_agent_workflow.py -v` — 7 passed.
- `python -m pytest tools\sml\tests -q` — 170 passed.
- `python -m py_compile tools\agent_workflow.py` — успешно.
- JSON parse `docs/agent-workflows/schema.example.json` — успешно.

## Риски и ограничения

- Субагенты являются role metadata, а не отдельными `allowed_next_agents`. Реальными отдельными подшагами остаются только `L1.0` и `L1.1`.
- Старый завершенный smoke workflow в `docs/agent-workflows/2026-06-19-140319-044554-smoke-test-agent-departments/` остается историческим артефактом со старой цепочкой; его events не переписывались.

## Что должен проверить следующий агент

- При создании нового workflow убедиться, что `contract.json` содержит новую цепочку и субагентов.
- Если нужен отдельный обязательный handoff для каждого субагента, это отдельное расширение CLI, потому что сейчас субагенты — роли внутри уровня.
