# Задачи

Только задачи инфраструктуры памяти, агентов и Aion Vision. Прикладные задачи внешних
проектов (Bitrix, betting, ТпБ) здесь не смешивать — см. раздел «Внешние проекты».

## Активные

### Инфраструктура агентов и памяти

- Поддерживать рабочий цикл `Grok Build (L1) + Antigravity CLI (L2) + Codex (L3/L4) + Claude Code (L5)`, Gemini Vertex как fallback `gemini-vertex`: один агент выполняет, другой проверяет через SML, итог фиксируется в SML и `docs/agent-log/`.
- Поддерживать иерархический workflow `docs/agent-workflows/`; дефолтный профиль `Роя` — `grok-antigravity`. Соблюдать `docs/agent-workflows/model-policy.md`: не подменять model alias тихо, mismatch фиксировать в handoff.
- Перезапустить MCP-сервер `sml` у активных агентов, чтобы нормализация `author_agent` применялась к новым записям (живой процесс держит старый код до перезапуска клиента).
- NOI VPS (`147.90.11.165`) восстановлен 2026-07-07 как резервный зарубежный Antigravity-роут: SSH работает, `agy 1.0.16`, OAuth пройден, live smoke возвращает `ok`. Использовать как fallback, если региональный блокер вернётся и локальный Antigravity + `gemini-vertex` откажут. Проверка: `tools/check-antigravity-noi.ps1 -Smoke`.

### Открытые дефекты

- Antigravity L1/L2 runner: process-tree timeout, жёсткая session correlation, запрет tool-use/внешнего поиска в review-only режиме (историю блокера см. `docs/history/current-context-chronicle-2026-06-07.md`).

### Ждут решения пользователя

- Telegram-канал «ИИ в дело» (`@iivdelo_ai`) — органический outreach на паузе, ждёт подтверждений `JOIN`/текстов. Детали и статус: workflow `docs/agent-workflows/2026-06-23-135910-435048-локальный-launch-bundle-ии-в-дело/` и записи `docs/agent-log/`.

## Внешние проекты

- Bitrix/Bit.Newton аналитика — отдельный прикладной проект: `C:\Users\koval\bat\bitrix24-automation`. Backlog и риски: `docs/projects/bitrix24-automation.md`.
- MVP ROI-радара банкротных торгов — `C:\Users\koval\Documents\ТпБ` (offline-core phase finalized).
- Betting decision-support MVP — `C:\Users\koval\Documents\New project`.

## Завершенные

Полный архив завершённых задач (2026-05..2026-06) вынесен в
`docs/history/completed-tasks-2026-05-06.md`.

## Отложенные

- HH Resume Booster — 14-дневный validation тест отложен (решение 2026-07-07). Инфраструктура готова, но запуск требует 14 дней ручного outreach; стартовать только при явной готовности вести ежедневную concierge-работу. Rehearsal-артефакты от 2026-06-21 протухли — перед стартом нужен свежий day-0 rehearsal. Runbook: `docs/experiments/hh-resume-booster-validation.md`.
- Продолжить MVP ROI-радара банкротных торгов в `C:\Users\koval\Documents\ТпБ`: следующий шаг — offline/read-only source adapter fixture для одного реального источника (сохранённый export/snapshot ЕФРСБ или ГИС Торги) с mapping tests. Перед длительными сборщиками проверять active-run gate и запускать только через visible monitor.
- Добавить selector workflow id в `Drift Workflow Control` или query param `/api/drift-workflow?workflow_id=...` для переключения workflow без правки кода.
- Добавить static export `public/drift-workflow-data.json` для offline-просмотра без dev/serve API.
- Настроить регулярный аудит качества записей SML.

## Устаревшие

- Настроить автоматические Kiro hooks поверх SML — неактуально, пока Kiro не входит в активную схему.
