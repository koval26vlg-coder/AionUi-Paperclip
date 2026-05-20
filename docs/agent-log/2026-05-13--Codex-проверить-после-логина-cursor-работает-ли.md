# Codex — 2026-05-13

## Запрос
Проверить после логина Cursor, работает ли связка общей памяти SML с Cursor/Kiro/Codex

## План
1. Проверить статус Cursor Agent и список MCP-инструментов. 2. Найти причину отклонения MCP-вызовов Cursor. 3. Исправить allowlist Cursor CLI. 4. Запустить Cursor headless smoke-test через sml.ping/startup_pack/semantic_query/add_log. 5. Проверить SML-журнал и Kiro-логи.

## Результат
Cursor Agent залогинен как koval26vlg@gmail.com, MCP-сервер sml в статусе ready, 10 инструментов доступны. Причина отказа была в Cursor CLI allowlist: был разрешён только Shell(ls). В C:\Users\koval\.cursor\cli-config.json добавлено разрешение Mcp(sml:*). После этого Cursor Agent успешно вызвал sml.ping, sml.startup_pack, sml.semantic_query и записал sml.add_log с agent=Cursor Agent. SML-журнал подтвердил запись record_id=019e20a3-285c-7b0a-befe-7c362e98b8d6. Kiro конфиг содержит sml, Kiro MCP Logs показывает успешное подключение и синхронизацию инструментов, а Kiro Logs показывает наличие mcp_sml_* в Tool selection; текущие ошибки Kiro относятся к Service temporarily unavailable/high traffic, не к SML.

## Изменённые файлы
- C:\Users\koval\.cursor\cli-config.json

## Риски и ограничения
Kiro UI smoke-test зависит от доступности облачного сервиса Kiro; по локальным логам MCP подключен, но ответ агента может падать из-за временной недоступности Kiro.

## Что следующему агенту
Для Kiro повторить ручной smoke-test в UI, когда сервис Kiro отвечает: попросить вызвать sml.ping, sml.startup_pack, sml.semantic_query и sml.add_log. Для Cursor использовать модель auto на бесплатном плане.
