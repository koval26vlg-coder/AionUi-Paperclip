# Agent Report

Дата и время: 2026-06-21 13:58 Europe/Volgograd

Агент: Codex

## Исходный запрос пользователя

Пользователь резко отклонил центральный dynamic-car overlay в `Drift Workflow Control`: дополнительная машина/маска в центре выглядела как мусор и должна быть убрана. Требование: центр не должен закрываться наложенной фигурой; активность должна переезжать к машине/уровню, а не рисоваться поверх центра.

## Краткий план

1. Убрать `DynamicActiveCar` из React.
2. Удалить CSS для `.arena-active-car*`, `.arena-center-car-mask` и связанных keyframes.
3. Перенести `SmokeLayer` с фиксированных центральных координат к позиции активного агента.
4. Проверить сборку и снять новый screenshot.
5. Зафиксировать ограничение по bitmap asset: исходный PNG все еще содержит baked-in центральный Nissan.

## Что сделано

- Удален вызов `DynamicActiveCar` и сам компонент из `DriftWorkflowDashboard.tsx`.
- Удалены `carVariantMeta` и весь CSS-блок, который рисовал центральную CSS-машину, маску, подпись и дополнительные smoke-псевдоэлементы.
- `SmokeLayer` теперь принимает `activeAgent` и рассчитывает puff/wisp позиции относительно `hotspotPositions[agent.id]`, поэтому дым больше не прибит к центру.
- Сгенерированный экспериментальный `drift-arena-center-clear.png` удален, потому что bitmap-patch выглядел хуже исходника и не принят в UI.
- Документы `docs/current-context.md` и `docs/tasks.md` обновлены.

## Измененные файлы

- `apps/aion-vision/src/components/dashboard/DriftWorkflowDashboard.tsx`
- `apps/aion-vision/src/index.css`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-1358-codex-drift-dashboard-remove-center-overlay.md`

## Проверки

- `npm run lint`
- `npm run build`
- Playwright screenshot через Microsoft Edge:
  `C:/Users/koval/Documents/Команда/drift-dashboard-no-center-overlay-v1.png`

## Риски и ограничения

- В исходном `apps/aion-vision/public/drift-arena-tuned-kei-ru.png` центральный Nissan и дым уже baked-in. Код больше не добавляет ничего поверх центра, но полностью пустой центр требует нового качественного image-edit/render ассета.
- Попытка Photoshop MCP generative edit завершилась `403 Forbidden`.
- Локальный Pillow-патч был проверен и отклонен как визуально хуже исходника; не использовать его как production asset.

## Что должен проверить следующий агент

- Не возвращать центральную dynamic-car наклейку.
- Если пользователь снова требует именно пустой центр, делать это через нормальный новый background render/edit asset, а не CSS-маску или грубый inpaint.
