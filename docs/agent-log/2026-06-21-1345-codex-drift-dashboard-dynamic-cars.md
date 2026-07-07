# Agent Report

Дата и время: 2026-06-21 13:45 Europe/Volgograd

Агент: Codex

## Исходный запрос пользователя

Пользователь указал, что при смене `current_level` должна реально меняться активная машина, а не оставаться старый Nissan из центрального PNG. Требуемые машины: `L1.0` tuned kei, `L1.1` AE86, `L2` 180SX; также нужно добавить остальные новые машины по закрепленной car policy.

## Краткий план

1. Подтянуть SML-контекст и проверить active-run gate.
2. Найти источник визуала `Drift Workflow Control`.
3. Добавить динамический слой активной машины поверх арены.
4. Привязать выбор машины к `active`/`next`/`current_level`.
5. Проверить сборку и визуальный screenshot.

## Что сделано

- В `DriftWorkflowDashboard.tsx` добавлен `DynamicActiveCar`.
- Добавлена нормализация текущего уровня: если workflow стоит на `L1`, UI выбирает активный/следующий `L1.0` или `L1.1`, а не случайный fallback.
- Центральный активный автомобиль теперь выбирается по `activeAgent.carCode`: `kei`, `AE86`, `180SX`, `JZX100`, `S15`, `A80`.
- В `index.css` добавлены отдельные стили для tuned kei, AE86, 180SX, JZX100, S15 и A80.
- Добавлена размытая дорожная подложка, которая гасит старый центральный Nissan из фонового PNG, чтобы он не воспринимался как источник текущего состояния.
- Обновлены `docs/current-context.md` и `docs/tasks.md`.

## Измененные файлы

- `apps/aion-vision/src/components/dashboard/DriftWorkflowDashboard.tsx`
- `apps/aion-vision/src/index.css`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-1345-codex-drift-dashboard-dynamic-cars.md`

## Проверки

- `npm run lint` в `apps/aion-vision`
- `npm run build` в `apps/aion-vision`
- `apps/aion-vision/scripts/export-drift-workflow.py --json`
- Playwright screenshot через установленный Microsoft Edge:
  `C:/Users/koval/Documents/Команда/drift-dashboard-dynamic-cars-v4.png`

## Риски и ограничения

- Фоновый PNG `drift-arena-tuned-kei-ru.png` все еще физически содержит старую центральную машину; теперь она перекрывается динамическим слоем, но полностью удалить ее можно только новым bitmap-render/edit ассетом.
- Динамические машины сейчас CSS-стилизованы, а не фотореалистичные 3D/PNG-спрайты. Для следующего качества уровня reference-render лучше заменить этот слой на набор прозрачных car sprites или новый отрендеренный arena asset.

## Что должен проверить следующий агент

- Визуально подтвердить, что `drift-dashboard-dynamic-cars-v4.png` соответствует ожиданию пользователя.
- Если пользователь хочет еще ближе к reference-render, следующий шаг: подготовить набор прозрачных PNG/WebP-спрайтов машин под `carCode`, чтобы заменить CSS-стилизацию без повторной правки workflow-state логики.
