## Что было сделано

L2 engineering review выполнен в controlled fallback режиме из-за `DEF-04` Antigravity print instability. Codex executor зафиксировал инженерные ограничения для реализации рабочего прототипа в `apps/aion-vision`.

Решение L2:

- внедрить прототип как отдельный экран Aion Vision, а не отдельный новый frontend;
- сделать dashboard read-only;
- использовать code-native React/Tailwind/SVG/CSS, без WebGL;
- edited PNG `drift-arena-tuned-kei-edit.png` использовать как reference/preview asset, не как весь интерфейс;
- сохранить существующий SML dashboard доступным через переключатель view.

## На чем основан вывод

Основано на current brief, L1.0 handoff, L1.1 diagnostic handoff, текущем стекe `apps/aion-vision`:

- React 19;
- Vite;
- Tailwind;
- lucide-react;
- framer-motion;
- существующая структура `DashboardLayout`, `components/dashboard`, `lib/dashboardData`.

## Что получилось хорошо

- У проекта уже есть подходящая dashboard shell: темная индустриальная палитра, боковая навигация, header/status, SML data panels.
- Визуальный стиль drift-arena render совпадает с текущей палитрой Aion Vision: dark graphite, cyan/amber accents, compact panels.
- Можно реализовать прототип без дополнительных зависимостей.

## Что требует доработки

L3 должен реализовать:

- `src/components/dashboard/DriftWorkflowDashboard.tsx`;
- `src/lib/driftWorkflowData.ts`;
- `src/types/driftWorkflow.ts`;
- обновление `DashboardLayout.tsx`, чтобы переключать `overview` и `drift`;
- обновление `App.tsx`, чтобы первый экран открывал Drift Workflow Dashboard, а SML обзор оставался вторым view;
- копию reference PNG в `public/` или явный path asset для просмотра.

Функциональные требования:

- arena/track map с 6 уровнями: L1.0, L1.1, L2, L3, L4, L5;
- центр: активная drift car;
- tuned kei cars как subagents вокруг активного уровня;
- final bay: drift legend car;
- audit timeline/events;
- limit panel с honest labels: `observed`, `remaining unknown`, `reset unknown`;
- Clean/Performance toggle, отключающий дым/анимации.

## Какие есть риски

- Существующий `DashboardLayout` сейчас статичен; если просто поменять NavItem без props, можно сломать обзор SML.
- Tailwind динамические классы должны быть статически перечислены, иначе purge/JIT может не собрать нужные цвета.
- Изображение reference render большое; если выводить его full-size внутри UI, нужно ограничить размер, чтобы не перегрузить first viewport.
- Дым/анимации должны уважать `prefers-reduced-motion`.
- Antigravity L1.1/L2 runtime не подтвержден; это отдельный workflow defect, не frontend blocker.

## Что нельзя потерять/исказить дальше

- UI должен быть рабочим прототипом, а не статичным скриншотом.
- Прототип не должен мутировать `contract.json`/`events.jsonl`.
- Состояния агентов должны быть явно видны: active, next, waiting, blocked, revision, done.
- Drift legend final car и tuned kei cars должны быть представлены в code-native визуальном языке.
- DEF-04 нужно упомянуть в L3/L4/final report как найденный diagnostic issue.

## Решение

approve
