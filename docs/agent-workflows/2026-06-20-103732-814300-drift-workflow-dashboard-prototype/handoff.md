# L4 Handoff: архитектурный синтез Drift Workflow Dashboard

## Что было сделано

L4 проверил L1-L3 цепочку как архитектурный уровень:

- сверил `brief.md`, `contract.json`, `events.jsonl`, L1/L2/L3 handoff и свежий agent-log по русскому PNG;
- проверил, что workflow был продвинут через `tools/agent_workflow.py`, а не ручной правкой `contract.json`;
- оценил финальную форму продукта: `Drift Workflow Control` как read-only dashboard, где arena/cars являются визуальной сценой, а реальные workflow-метрики вынесены в правые панели и compact markers;
- проверил, что последний спорный motion-layer удален, а английские zone labels заменены в raster asset, а не перекрыты React-плашками;
- подтвердил, что L3 прошел `npm run lint`, `npm run build` и Playwright visual screenshots.

После L5 revision request от 2026-06-20 18:36 L4 исправил car-role mismatch:

- закрепил линейку машин: `L1.0` tuned kei scout, `L1.1` Toyota AE86 Trueno, `L2` Nissan 180SX Type X, `L3` Toyota Chaser JZX100, `L4` Nissan Silvia S15, `L5` Toyota Supra A80;
- обновил typed snapshot в `apps/aion-vision/src/lib/driftWorkflowData.ts`;
- добавил `carCode` в `apps/aion-vision/src/types/driftWorkflow.ts` и compact model codes в `DriftWorkflowDashboard.tsx`;
- пересобрал arena asset `apps/aion-vision/public/drift-arena-car-policy-ru.png`;
- синхронизировал dashboard state: текущий уровень теперь `L4`, L3 помечен как `готово`, L4 как `работает`;
- исправил позицию L1.0 marker, чтобы он был на kei scout, а не на JZX100.

## На чем основан вывод

Основание проверки:

- исходная постановка в `brief.md`;
- approved L1.0/L1.1/L2 handoff;
- L3 handoff `levels/L3/handoff.md`;
- события `events.jsonl`, включая `level_submitted` и `level_approved` для L3;
- файлы реализации:
  - `apps/aion-vision/src/components/dashboard/DriftWorkflowDashboard.tsx`;
  - `apps/aion-vision/src/lib/driftWorkflowData.ts`;
  - `apps/aion-vision/src/index.css`;
  - `apps/aion-vision/public/drift-arena-tuned-kei-ru.png`;
  - `apps/aion-vision/public/drift-arena-car-policy-ru.png`;
- контрольный screenshot `C:/Users/koval/Documents/Команда/drift-dashboard-russian-image-replace-v3.png`.
- контрольный screenshot после car policy revision: `C:/Users/koval/Documents/Команда/drift-dashboard-car-policy-v3.png`.

## Что получилось хорошо

- Схема остается иерархической: L1/L2/L3/L4/L5 передают работу по contract/events/handoff, а не работают как один prompt в несколько моделей.
- Dashboard не мутирует workflow state из UI. Это правильно для текущего этапа: отображение отдельно, управление через CLI отдельно.
- Визуальный язык теперь ближе к выбранному render: русские zone labels находятся внутри изображения, без чужеродных overlay-плашек.
- Пользовательские ограничения соблюдены: `Drift Workflow Control` не переведен, имена агентов и моделей не переименованы.
- Неподтвержденные лимиты не выдумываются: remaining/reset остаются `неизвестно`.
- L3 не скрывает диагностические хвосты: fixture/live-reader gap и Antigravity `DEF-04` явно переданы выше.

## Что требует доработки

- `DRIFT_WORKFLOW_SNAPSHOT` все еще fixture. Следующий технический этап должен заменить его read-only adapter, который читает `contract.json`, `events.jsonl`, последний `handoff.md`, screenshots/QA metadata и usage snapshots.
- Русский arena asset сейчас статичен. Если роли/зоны будут меняться часто, нужен либо генератор PNG labels, либо code-native canvas/WebGL слой, который не будет выглядеть как отдельные плашки.
- Нужно обновить `design-qa.md`: там остались рекомендации про `Clean`/presentation mode, которые уже не совпадают с последним решением пользователя.
- Vite build проходит, но сохраняет warning о крупном chunk. Для прототипа это не блокер, для production стоит сделать code splitting.
- L5 должен честно указать, что Claude Code runtime найден, но финальный отчет собирается через локальный workflow с `--executor Codex`; если Claude CLI не пройдет smoke-test, это нужно фиксировать как runtime mismatch.
- Claude Code `--print` доступен, но предыдущая попытка L5 с бюджетом `$0.30` завершилась `Exceeded USD budget`; финализацию нужно повторять с достаточным бюджетом или фиксировать лимит как runtime/cost constraint.

## Какие есть риски

- Raster-first подход хорошо попадает в выбранный render, но усложняет будущую динамическую локализацию, замену car models и live state updates.
- Текущая замена машин в raster asset является прототипной: роли читаются (`JZX100`, `S15`, `180SX`), но это не полноценный фотореалистичный inpaint. Следующий дизайн-этап может потребовать генерации нового render целиком.
- Если оставить fixture надолго, dashboard может начать расходиться с реальным `contract.json/events.jsonl`.
- Финальный отчет не должен утверждать, что L1/L2 были полноценными независимыми model review без оговорки: Antigravity ранее имел диагностированный `DEF-04`, а L1/L2 проходили controlled fallback через Codex executor.
- Активный gate `trading_mvp` сейчас `RUNNING`; он не относится к Aion dashboard, но L5 не должен предлагать запускать долгие процессы или постпроцессинг по trading.

## Что нельзя потерять/исказить дальше

- Главный продуктовый смысл: это визуализация иерархического workflow отделов и handoff-цепочки, а не мульти-модельный broadcast.
- Управление workflow остается через `tools/agent_workflow.py`; UI пока read-only.
- Нельзя скрывать различие между подтвержденными проверками и fixture/demo данными.
- Нельзя возвращать декоративные fake charts без чисел и источников.
- Нельзя снова накладывать крупные UI-плашки поверх машин, если пользователь просит замену внутри render.
- Нельзя возвращать GT-R как Codex L3: L3 закреплен как Toyota Chaser JZX100.
- Нельзя оставлять L4 как generic coupe: L4 закреплен как Nissan Silvia S15.

## Решение

approve
