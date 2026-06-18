# codex — 2026-06-18T06:25:40.444Z

## Запрос
automation-3: daily Bitrix `Счет отправлен, %` -> Google Sheet за предыдущий рабочий день.

## План
SML/preflight -> pending check -> writer calendar -> Bitrix cohort расчет -> service-account write -> verify -> журнал.

## Результат
2026-06-18 выполнено: target 2026-06-17, лист `Июнь 2026 ОП`, колонка `AC`. Записано и проверено: AC15=50%, AC29=67%, AC45=43%, AC61=50%, AC78=33%, AC93=33%, AC108=67%, AC123=50%. Расчет шел по cohort-формуле: 32 новых сделки, 16 дошли до `C1:UC_9NU15J`; 5 stage-history переходов вне периода создания отсечены.

## Изменённые файлы
- .codex/automations/automation-3/memory.md
- docs/agent-log/2026-06-18-konversiya-po-schetam.md
- exports/sheets/automation-3-conversion-invoices-2026-06-18.json

## Риски и ограничения
Ранее записанные июньские daily-колонки до коррекции формулы могут быть завышены; нужен ретро-аудит. Строки метрики пока статические.

## Что следующему агенту
Провести ретро-аудит колонок до AB по cohort-формуле; добавить unknown_assigned_by и единый run_and_write_daily.ps1.
