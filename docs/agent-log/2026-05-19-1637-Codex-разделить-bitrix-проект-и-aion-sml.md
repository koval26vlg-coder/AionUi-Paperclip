# Codex — 2026-05-19T16:37:36.866Z

## Запрос
Разделить Bitrix-проект и Aion/SML, потому что они начали смешиваться.

## План
Зафиксировать границу проектов, вынести Bitrix backlog из общих задач, убрать Bitrix-лейблы из Aion Vision, убрать temp-файлы из корня.

## Результат
Bitrix backlog вынесен в docs/projects/bitrix24-automation.md. docs/tasks.md теперь содержит только ссылку на внешний проект. README и current-context уточняют границу: AionUi-Paperclip = SML/Aion Vision, Bitrix = C:\Users\koval\bat\bitrix24-automation. В Aion Vision nav label Bitrix Data заменен на Memory Sources. constants.py.tmp и scoring_crm.py.tmp перенесены в docs/projects/_archive/bitrix-temp-code.

## Изменённые файлы
- docs/projects/bitrix24-automation.md
- docs/tasks.md
- docs/current-context.md
- README.md
- apps/aion-vision/src/components/layout/DashboardLayout.tsx
- docs/decisions.md

## Риски и ограничения
SML по смыслу все равно хранит историю работ по Bitrix; Aion Vision может показывать такие записи как agent-log, но это история памяти, не кодовое смешение.

## Что следующему агенту
При желании добавить в Aion Vision фильтр по проектам/источникам, чтобы записи Bitrix можно было скрывать из общей ленты.
