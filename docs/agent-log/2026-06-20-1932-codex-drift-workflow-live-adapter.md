# Agent Log: Drift Workflow Control live adapter

## Дата и агент

- Дата: 2026-06-20 19:32 Europe/Volgograd
- Агент: Codex

## Исходный запрос пользователя

Продолжить активную цель: заменить `DRIFT_WORKFLOW_SNAPSHOT` на live read-only adapter, чтобы dashboard читал реальные `contract.json`, `events.jsonl`, `handoff.md`, `final-report.md` и лимиты напрямую.

## Краткий план

1. Проверить active-run gate и Aion SML bootstrap.
2. Собрать live exporter по workflow-файлам и лимитам.
3. Подключить exporter в Vite dev API и standalone `serve-sml.py`.
4. Перевести React dashboard на async loader с fixture только как fallback.
5. Прогнать тесты, lint/build и визуальный screenshot.

## Что было сделано

- Добавлен `apps/aion-vision/scripts/export-drift-workflow.py`.
- Exporter читает:
  - `docs/agent-workflows/2026-06-20-103732-814300-drift-workflow-dashboard-prototype/contract.json`;
  - `events.jsonl`;
  - `last_handoff` из `contract.json`;
  - `final_report` из `contract.json`;
  - `docs/agent-limits/limits-config.json`;
  - `docs/agent-limits/latest.json` для observed usage.
- Добавлен dev API endpoint `/api/drift-workflow` в `apps/aion-vision/vite.config.ts`.
- Добавлен production/standalone endpoint `/api/drift-workflow` в `apps/aion-vision/scripts/serve-sml.py`.
- `DriftWorkflowDashboard` переведен на `loadDriftWorkflowSnapshot()`: сначала live API, затем статический `/drift-workflow-data.json`, затем `DRIFT_WORKFLOW_FALLBACK`.
- Добавлена панель `Источники данных`, где видно `live`, diagnostics и пути к `contract/events/final`.
- `DRIFT_WORKFLOW_SNAPSHOT` больше не используется как основной источник; статический объект переименован в `DRIFT_WORKFLOW_FALLBACK`.

## Измененные файлы

- `apps/aion-vision/scripts/export-drift-workflow.py`
- `apps/aion-vision/scripts/serve-sml.py`
- `apps/aion-vision/vite.config.ts`
- `apps/aion-vision/src/lib/driftWorkflowData.ts`
- `apps/aion-vision/src/types/driftWorkflow.ts`
- `apps/aion-vision/src/components/dashboard/DriftWorkflowDashboard.tsx`
- `tools/sml/tests/test_export_drift_workflow.py`
- `.gitignore` - добавлено исключение для `apps/aion-vision/src/lib/**`, потому что глобальное `lib/` скрывало frontend source files.
- `docs/current-context.md`
- `docs/tasks.md`

## Проверки

- `python apps/aion-vision/scripts/export-drift-workflow.py --json` - возвращает `state=done`, `currentLevel=L5`, diagnostics по `contract/events/handoff/final-report/limits`.
- `GET http://127.0.0.1:5174/api/drift-workflow` - возвращает live JSON.
- `python -m py_compile apps/aion-vision/scripts/serve-sml.py apps/aion-vision/scripts/export-drift-workflow.py` - passed.
- `python -m pytest tools/sml/tests/test_export_drift_workflow.py tools/sml/tests/test_agent_workflow.py tools/sml/tests/test_agent_limit_monitor.py` - 16 passed.
- `npm run lint` - passed.
- `npm run build` - passed; остался только Vite warning о chunk > 500 kB.
- Screenshot live adapter: `C:/Users/koval/Documents/Команда/drift-dashboard-live-adapter-v2.png`.

## Риски и ограничения

- Dashboard остается read-only. Мутации workflow по-прежнему только через `tools/agent_workflow.py`.
- `DRIFT_WORKFLOW_FALLBACK` оставлен только на случай недоступности API/статического JSON.
- Presentation mapping машин/цветов/позиций остается в exporter как UI metadata; статусы и события берутся из workflow-файлов.
- Claude Code L5 CLI runtime constraint остается актуальным и зафиксирован в final report.
- Active-run gate по внешнему `trading_mvp` остается `RUNNING`; Aion changes не затрагивают trading.

## Что должен проверить следующий агент

- При необходимости добавить selector workflow id в UI или query param `/api/drift-workflow?workflow_id=...`.
- Позже можно сделать static export `public/drift-workflow-data.json` для offline-просмотра без dev/serve API.
