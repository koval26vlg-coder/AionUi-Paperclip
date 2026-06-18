# codex — 2026-06-17T06:04:16.662Z

## Запрос
automation-3: daily Bitrix `Счет отправлен, %` -> Google Sheet за предыдущий рабочий день.

## План
SML/preflight -> pending check -> writer calendar -> Bitrix расчет -> service-account write -> verify -> журнал.

## Результат
2026-06-17 выполнено: target 2026-06-16, лист `Июнь 2026 ОП`, колонка `AB`. Записано и проверено: AB15=200%, AB29=67%, AB45=50%, AB61=25%, AB78=75%, AB93=67%, AB108=75%, AB123=88%. Все новые сделки CATEGORY_ID=1 входят в текущие 8 строк: new_deals_all=41 и subset=41. 200% у Юлианны допустимо по формуле, так как переходов больше, чем новых сделок.

## Изменённые файлы
- .codex/automations/automation-3/memory.md
- docs/agent-log/2026-06-17-konversiya-po-schetam.md
- exports/sheets/automation-3-conversion-invoices-2026-06-17.json

## Риски и ограничения
Строки метрики пока статические. Проценты могут быть >100%, потому что numerator=переходы в stage за день, denominator=новые сделки за день.

## Что следующему агенту
Добавить unknown_assigned_by в JSON-артефакт, общий календарь праздников и единый run_and_write_daily.ps1.
