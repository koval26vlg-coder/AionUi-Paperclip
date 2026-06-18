# codex — 2026-06-11T06:07:25.108Z

## Запрос
automation-3: записать в Google Sheet метрику Bitrix `Счет отправлен, %` за предыдущий рабочий день.

## План
SML/preflight -> календарь таблицы -> Bitrix расчет -> service-account write -> проверка -> журнал.

## Результат
Выполнено за запуск 2026-06-11: целевая дата 2026-06-10, лист `Июнь 2026 ОП`, колонка `V`. Записано и проверено: V15=133%, V29=пусто, V45=50%, V61=пусто, V78=40%, V93=71%, V108=67%, V123=57%. Пустые значения связаны с new_deals=0. Исправлен proxy-bypass в Bitrix REST расчете и контроль exit code в wrapper.

## Изменённые файлы
- automations/conversion_invoices/calc_invoice_conversion.py
- automations/conversion_invoices/run_daily.ps1
- .codex/automations/automation-3/memory.md
- docs/agent-log/2026-06-11-konversiya-po-schetam.md

## Риски и ограничения
VibeCode preflight падает через локальный proxy, но automation-3 использует Bitrix REST. Динамический поиск строк метрики еще не реализован.

## Что следующему агенту
Сделать единый run_and_write_daily.ps1 и проверить другие Bitrix-клиенты на `trust_env=False`.
