# 2026-06-19 16:51 - Codex - закрепить model policy субагентов

## Исходный запрос пользователя

Пользователь задал точную модельную матрицу для каждого субагента workflow и попросил ее запомнить.

## Краткий план

1. Добавить model metadata к субагентам в `tools/agent_workflow.py`.
2. Обновить schema example и документацию model policy.
3. Записать решение в `docs/decisions.md`.
4. Прогнать тесты.

## Что сделано

- В `tools/agent_workflow.py` каждый субагент получил `model.provider`, `model.name`, `model.effort`, а для MiMo также `model.mode`.
- `status` и финальная история workflow теперь показывают модель субагента.
- Создан `docs/agent-workflows/model-policy.md` с полной матрицей:
  - `L1.0`: MiMo AUTO / Xiaomi API AUTO;
  - `L1.1`: Gemini 3.1 Pro / Gemini 3.5 Flash с High/Low/Medium;
  - `L2`: Gemini 3.5 Flash / High;
  - `L3`: codex-5.3, gpt-5.5, gpt-5.4 mini, gpt-5.4 / xhigh;
  - `L4`: gpt-5.5 / xhigh;
  - `L5`: Claude Opus 4.7 alias, Claude Haiku 4.5 alias, Claude Sonnet 4.6 alias, Claude Opus 4.8 alias / xhigh.
- `docs/agent-workflows/schema.example.json` обновлен из фактического генератора contract.
- `docs/agent-workflows/README.md`, `AGENTS.md`, `docs/current-context.md`, `docs/tasks.md`, `docs/decisions.md` обновлены под model policy.

## Измененные файлы

- `tools/agent_workflow.py`
- `tools/sml/tests/test_agent_workflow.py`
- `docs/agent-workflows/model-policy.md`
- `docs/agent-workflows/schema.example.json`
- `docs/agent-workflows/README.md`
- `AGENTS.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/decisions.md`

## Проверки

- `python -m pytest tools\sml\tests\test_agent_workflow.py -v` — 7 passed.
- `python -m pytest tools\sml\tests -q` — 170 passed.
- `python -m py_compile tools\agent_workflow.py` — успешно.
- JSON parse/assert для `docs/agent-workflows/schema.example.json` — успешно.

## Риски и ограничения

- Названия моделей сохранены как пользовательские aliases/target labels. Перед живым запуском нужно проверить, что конкретный CLI/провайдер реально принимает эти имена.
- Если alias недоступен, агент не должен молча подменять модель; mismatch нужно записать в handoff и запросить approved fallback.

## Что должен проверить следующий агент

- При первом реальном workflow проверить, что `contract.json` содержит `subagent.model`.
- Перед запуском Gemini/Codex/Claude/MiMo проверить соответствие aliases реальным model ids выбранного CLI/API.
