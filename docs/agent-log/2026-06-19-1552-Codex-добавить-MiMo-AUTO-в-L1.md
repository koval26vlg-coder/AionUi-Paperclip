# 2026-06-19 15:52 - Codex - добавить MiMo AUTO в L1

## Исходный запрос пользователя

Пользователь попросил добавить MIMO от Xiaomi в режиме AUTO на самый первый нижний уровень `L1` иерархической схемы agent-workflows.

## Краткий план

1. Сохранить прошлое решение: старые проектные MiMo-конфиги и запускатели не возвращать.
2. Добавить `MiMo AUTO` как отдельный подшаг `L1.0` перед `Gemini CLI`.
3. Обновить CLI, тесты, README/schema и общую память.
4. Проверить unit/smoke-тесты и синтаксис скриптов.

## Что сделано

- `tools/agent_workflow.py` расширен под подшаги внутри уровня.
- Новый workflow стартует с `current_level="L1"`, `current_subrole="L1.0"`, `allowed_next_agents=["MiMo AUTO"]`.
- `L1` теперь состоит из:
  - `L1.0 MiMo AUTO` — нижний AUTO-проход, первичные зацепки, гипотезы и риски;
  - `L1.1 Gemini CLI` — проверка MiMo AUTO, расширение фактов и чистый L1-handoff.
- `approve-level` теперь умеет продвигать workflow сначала между подшагами внутри L1, затем на L2.
- `tools/watch-agent-workflows.ps1` показывает `current_subrole`.
- Документы обновлены: `AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `README.md`, `docs/current-context.md`, `docs/tasks.md`, `docs/agents.md`, `docs/local-environment.md`, `docs/agent-memory-bootstrap.md`, `docs/agent-workflows/README.md`, `schema.example.json`, `README-smoke.md`, `docs/memory/layers/constraints.md`, `docs/context-index.md`, `docs/decisions.md`.

## Измененные файлы

- `tools/agent_workflow.py`
- `tools/sml/tests/test_agent_workflow.py`
- `tools/watch-agent-workflows.ps1`
- `docs/agent-workflows/README.md`
- `docs/agent-workflows/schema.example.json`
- `docs/agent-workflows/README-smoke.md`
- `docs/plans/2026-06-19-agent-coordination-workflow.md`
- `AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `README.md`
- `docs/current-context.md`, `docs/tasks.md`, `docs/agents.md`, `docs/local-environment.md`, `docs/context-index.md`, `docs/agent-memory-bootstrap.md`, `docs/memory/layers/constraints.md`, `docs/decisions.md`

## Проверки

- `python -m pytest tools\sml\tests\test_agent_workflow.py -v` — 7 passed.
- `python -m pytest tools\sml\tests -q` — 170 passed.
- `python -m py_compile tools\agent_workflow.py` — успешно.
- PowerShell parse-check `tools\watch-agent-workflows.ps1` — успешно.

## Риски и ограничения

- `MiMo AUTO` добавлен как логическое имя участника workflow. Старые `.mimocode/`, `OPEN-MIMO-SML.cmd`, `CHECK-MIMO-SML.cmd` не восстановлены.
- Для живого запуска MiMo потребуется отдельная проверка доступности провайдера/Auto-режима, если пользователь захочет выполнять L1.0 не вручную, а через настоящий MiMo CLI.
- Старые уже завершенные workflow могут иметь прежнюю структуру без `current_subrole`; CLI сохраняет совместимость с ними.

## Что должен проверить следующий агент

- При первой реальной задаче проверить, что `MiMo AUTO` может фактически выполнить `L1.0` и оставить handoff в требуемом формате.
- Если MiMo CLI нужно запускать интерактивно, не возвращать проектные конфиги без отдельного решения пользователя и не хранить секреты в `docs/` или SML.
