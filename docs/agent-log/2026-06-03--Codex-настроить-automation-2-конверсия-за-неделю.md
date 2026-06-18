# Codex — 2026-06-03

## Запрос
Настроить automation-2 `Конверсия за неделю`: Bitrix24 `6. Оплата получена, %` по категориям/менеджерам в Google Sheets, один чат, переименовать чат.

## План
Проверить preflight/SML/automation.toml; обновить `automation-2`; переименовать чат; записать docs agent-log и память.

## Результат
Preflight первым шагом: ok=true. Существующая `automation-2` обновлена без дубля: cron -> heartbeat, ACTIVE, target thread 019e8e44-e621-7321-abb0-e655a9af75e3. Чат переименован в `Конверсия за неделю - автоматизация`. Prompt закрепляет календарь рабочих дат таблицы, категории 1/2/4 месяца, фильтры АРТ/MAX, Bitrix REST + stage-history и compact batchUpdate Sheets.

## Изменённые файлы
- C:/Users/koval/.codex/automations/automation-2/automation.toml
- C:/Users/koval/.codex/automations/automation-2/memory.md
- C:/Users/koval/Documents/ОК.ру/docs/agent-log/2026-06-03-konversiya-za-nedelyu-automation-2-setup.md

## Риски и ограничения
Праздники обрабатываются внутренней проверкой календаря таблицы, не одним RRULE. Google Sheets может давать 429, поэтому нужны минимальные чтения и одна batchUpdate-запись.

## Что следующему агенту
Следующий запуск: preflight -> SML; если день не первый рабочий по таблице, пропуск; если подходит, использовать успешный маршрут 2026-06-01.
