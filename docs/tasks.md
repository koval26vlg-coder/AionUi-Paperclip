# Задачи

Только задачи инфраструктуры памяти, агентов и Aion Vision. Прикладные задачи внешних
проектов (Bitrix, betting, ТпБ) здесь не смешивать — см. раздел «Внешние проекты».

## Активные

### Инфраструктура агентов и памяти

- Поддерживать рабочий цикл `Grok Build (L1) + Antigravity CLI (L2) + Codex (L3/L4) + Claude Code (L5)`, Gemini Vertex как fallback `gemini-vertex`: один агент выполняет, другой проверяет через SML, итог фиксируется в SML и `docs/agent-log/`.
- Поддерживать иерархический workflow `docs/agent-workflows/`; дефолтный профиль `Роя` — `grok-antigravity`. Соблюдать `docs/agent-workflows/model-policy.md`: не подменять model alias тихо, mismatch фиксировать в handoff.
- Перезапустить MCP-сервер `sml` у активных агентов, чтобы нормализация `author_agent` применялась к новым записям (живой процесс держит старый код до перезапуска клиента).
- Заполнить `docs/agent-limits/limits-config.json` реальными лимитами и reset time для Codex, Claude Code, Antigravity и Grok, когда они известны.

### Открытые дефекты

- DEF-02: добавить guard в `tools/agent_workflow.py submit-work` для проверки ожидаемых `level`/`assignment` перед записью handoff.
- DEF-03: в `tools/agent_workflow.py status` и `tools/watch-agent-workflows.ps1` явно отделять active blockers от `resolved=true`.
- Antigravity L1/L2 runner: process-tree timeout, жёсткая session correlation, запрет tool-use/внешнего поиска в review-only режиме (историю блокера см. `docs/history/current-context-chronicle-2026-06-07.md`).

### Ждут решения пользователя

- HH Resume Booster — 14-дневный validation тест НЕ стартован; rehearsal-артефакты от 2026-06-21 протухли. Перед запуском нужен свежий day-0 rehearsal и явное решение начать сбор. Runbook: `docs/experiments/hh-resume-booster-validation.md`.
- Antigravity NOI VPS (`147.90.11.165`) недоступен по SSH (banner exchange fail) — нужен console/rescue recovery в панели VPS или отказ от NOI. Helpers: `tools/check-antigravity-noi.ps1`, `tools/start-antigravity-noi-auth.ps1`.
- Telegram-канал «ИИ в дело» (`@iivdelo_ai`) — органический outreach на паузе, ждёт подтверждений `JOIN`/текстов. Детали и статус: workflow `docs/agent-workflows/2026-06-23-135910-435048-локальный-launch-bundle-ии-в-дело/` и записи `docs/agent-log/`.

## Внешние проекты

- Bitrix/Bit.Newton аналитика — отдельный прикладной проект: `C:\Users\koval\bat\bitrix24-automation`. Backlog и риски: `docs/projects/bitrix24-automation.md`.
- MVP ROI-радара банкротных торгов — `C:\Users\koval\Documents\ТпБ` (offline-core phase finalized).
- Betting decision-support MVP — `C:\Users\koval\Documents\New project`.

## Завершенные

Полный архив завершённых задач (2026-05..2026-06) вынесен в
`docs/history/completed-tasks-2026-05-06.md`.

## Отложенные

- Продолжить MVP ROI-радара банкротных торгов в `C:\Users\koval\Documents\ТпБ`: следующий шаг — offline/read-only source adapter fixture для одного реального источника (сохранённый export/snapshot ЕФРСБ или ГИС Торги) с mapping tests. Перед длительными сборщиками проверять active-run gate и запускать только через visible monitor.
- Добавить selector workflow id в `Drift Workflow Control` или query param `/api/drift-workflow?workflow_id=...` для переключения workflow без правки кода.
- Добавить static export `public/drift-workflow-data.json` для offline-просмотра без dev/serve API.
- Настроить регулярный аудит качества записей SML.

## Устаревшие

- Настроить автоматические Kiro hooks поверх SML — неактуально, пока Kiro не входит в активную схему.
