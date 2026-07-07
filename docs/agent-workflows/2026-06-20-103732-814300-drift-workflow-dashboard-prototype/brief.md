Пользователь выбрал drift-arena reference render и попросил: заменить белый спорткар на легенду дрифта, маленькие машинки внутри арены заменить на тюнинговые kei cars, затем перейти к рабочему прототипу и использовать hierarchical Workflow для обкатки/диагностики/развития инструмента.

Входные материалы:
- Исходный выбранный render: C:/Users/koval/AppData/Local/Temp/codex-clipboard-5fcef762-97f8-4d09-8ed3-b743384b910b.png
- Отредактированный render: docs/agent-workflows/2026-06-20-091104-901407-drift-agent-dashboard-reference-renders/renders/drift-arena-tuned-kei-edit.png
- Предыдущий completed workflow: 2026-06-20-091104-901407-drift-agent-dashboard-reference-renders

Цель прототипа:
- Реализовать рабочий read-only dashboard в apps/aion-vision: drift-agent workflow visualization на основе выбранного arena/relay визуального языка.
- Видно кто сейчас работает, кто следующий, кто ждет, какие subagents внутри уровня, blockers/revision/done, audit events и usage/limits panel.
- Прототип должен читать реальные или fixture workflow данные без права мутировать workflow state.
- Использовать существующий стек React/Vite/Tailwind/lucide в apps/aion-vision.
- Проверить сборку/линт/визуал, запустить локальный dev server и дать URL.

Критерии готовности:
1. Есть отдельная route/view или экран в Aion Vision для Drift Workflow Dashboard.
2. Есть детерминированный code-native UI, не статичный PNG-скриншот; PNG используется только как design reference/asset preview.
3. State mapping явно связан с workflow contract/events/fixtures: active, next, waiting, blocked, revision, done.
4. Subagents показаны как tuned kei/micro cars или escort cars.
5. Есть audit panel, handoff timeline и usage/limits panel с честным указанием observed usage / unknown remaining-reset.
6. Build/lint/визуальная проверка выполнены; найденные workflow issues зафиксированы в handoff/agent-log.
