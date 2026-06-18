# codex — 2026-06-15T06:07:14.871Z

## Запрос
automation-3: daily Bitrix `Счет отправлен, %` -> Google Sheet за предыдущий рабочий день.

## План
SML/preflight -> pending check -> calendar fix/check -> Bitrix расчет -> service-account write -> verify -> журнал.

## Результат
2026-06-15 выполнено. 2026-06-12 пропущен как праздник/нерабочий день; целевая дата 2026-06-11, лист `Июнь 2026 ОП`, колонка `W`. Записано и проверено: W15=86%, W29=пусто, W45=29%, W61=50%, W78=75%, W93=50%, W108=40%, W123=100%. Пусто у Алены Ковалевой из-за new_deals=0. Исправлен календарный дефект write_daily.py: выходные и 2026-06-12 не выбираются как target.

## Изменённые файлы
- automations/conversion_invoices/write_daily.py
- .codex/automations/automation-3/memory.md
- docs/agent-log/2026-06-15-konversiya-po-schetam.md
- exports/sheets/automation-3-conversion-invoices-2026-06-15.json

## Риски и ограничения
Праздники пока заданы локальным списком в writer; нужен общий календарь проекта. Строки метрики июня пока статические.

## Что следующему агенту
Вынести календарь праздников в общий helper и сделать единый run_and_write_daily.ps1.
