# Agent Log: Drift dashboard idle jitter removed

## Дата и агент

- Дата: 2026-06-20 19:50 Europe/Volgograd
- Агент: Codex

## Исходный запрос пользователя

Пользователь попросил убрать дергание машин, потому что оно выглядит неестественно, и предложить другие варианты визуального оживления.

## Что было сделано

- Удален `IdleCarVibration` из `DriftWorkflowDashboard.tsx`.
- Удалены `idleCarRegions`, `.arena-idle-car` и `@keyframes arena-idle-vibration`.
- Оставлен только мягкий `SmokeLayer` у центральной машины.

## Проверки

- `rg "IdleCarVibration|idleCarRegions|arena-idle-car|arena-idle-vibration" apps/aion-vision/src` - совпадений нет.
- `npm run lint` - passed.
- `npm run build` - passed; остался стандартный Vite warning о крупном chunk.
- Screenshot: `C:/Users/koval/Documents/Команда/drift-dashboard-smoke-no-jitter-v1.png`.

## Рекомендация

Для стоящих заведенных машин не использовать прямую тряску кузова на bitmap. Более естественные варианты: выхлоп/тепловое марево, пульс подсветки, мягкое мерцание фар/стопов, движение бликов по полу, анимация индикаторов вокруг машин.
