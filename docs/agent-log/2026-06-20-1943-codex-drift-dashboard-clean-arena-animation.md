# Agent Log: Drift dashboard clean arena and motion pass

## Дата и агент

- Дата: 2026-06-20 19:43 Europe/Volgograd
- Агент: Codex

## Исходный запрос пользователя

Пользователь указал, что картинка dashboard выглядит неаккуратно: все съехало и появились непонятные фигуры. Затем попросил анимировать дым из-под колес, а остальные машины слегка трясти как заведенные.

## Что было сделано

- Live adapter `apps/aion-vision/scripts/export-drift-workflow.py` переключен с `drift-arena-car-policy-ru.png` на чистый asset `drift-arena-tuned-kei-ru.png`.
- Fallback data `apps/aion-vision/src/lib/driftWorkflowData.ts` также переключен на чистый asset.
- Убрана причина визуального шума: больше не используется raster asset с дорисованными техническими кузовами/полосами.
- В `DriftWorkflowDashboard.tsx` добавлены:
  - `SmokeLayer` для мягкого дыма у центральной машины;
  - `IdleCarVibration` для легкой вибрации остальных машин через clipped overlay самой картинки.
- В `index.css` добавлены `arena-wheel-smoke` и `arena-idle-vibration`, с учетом `prefers-reduced-motion`.

## Измененные файлы

- `apps/aion-vision/scripts/export-drift-workflow.py`
- `apps/aion-vision/src/lib/driftWorkflowData.ts`
- `apps/aion-vision/src/components/dashboard/DriftWorkflowDashboard.tsx`
- `apps/aion-vision/src/index.css`

## Проверки

- `python apps/aion-vision/scripts/export-drift-workflow.py --json` - `referenceRender=/drift-arena-tuned-kei-ru.png`.
- `npm run lint` - passed.
- `npm run build` - passed; остались предупреждения Vite/Rolldown о chunk/plugin timings.
- `pytest tools/sml/tests/test_export_drift_workflow.py` - 2 passed.
- Screenshot: `C:/Users/koval/Documents/Команда/drift-dashboard-smoke-idle-v1.png`.

## Риски и ограничения

- Дрожание машин реализовано через небольшие clipped overlays поверх bitmap, потому что машины не являются отдельными слоями исходного изображения.
- Если пользователю нужна полноценная физическая анимация каждой машины, потребуется генерация/нарезка отдельных transparent PNG sprites или Canvas/WebGL scene.
