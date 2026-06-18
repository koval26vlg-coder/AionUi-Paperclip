# Codex — 2026-06-09

## Запрос
Разобрать, почему Bitrix24 Automation 2026-06-09 не завершался, и убрать browser fallback из основного маршрута.

## Результат
Причина `ConnectTimeout` найдена: preflight выставляет BITRIX24_SOURCE_IP только в своем процессе, а отдельный CLI-запуск шел без bind и падал на profile. Подтверждено: без source_ip profile timeout, с source_ip ответ успешен. Дополнительно: `--use-vibecode` без `--bitrix-source vibecode` не создает VibeCode-клиент. Актуализированы automation.toml, memory.md и agent-log.

## Изменённые файлы
- C:\Users\koval\.codex\automations\automation\automation.toml
- C:\Users\koval\.codex\automations\automation\memory.md
- C:\Users\koval\Documents\ОК.ру\docs\agent-log\2026-06-09-bitrix-connecttimeout-root-cause.md

## Риски и ограничения
Browser fallback больше не должен быть частью основного маршрута; использовать только по явному разрешению пользователя. Последний JSON-отчет без браузера содержит OK=0 ERR=13 и пока оставлен pending.

## Что следующему агенту
На следующем прогоне экспортировать BITRIX24_SOURCE_IP и VIBECODE_SOURCE_IP в тот же CLI-процесс, запускать с `--bitrix-source vibecode`, не включать `--ui-download`, а profile-check делать только перед единственным retry.
