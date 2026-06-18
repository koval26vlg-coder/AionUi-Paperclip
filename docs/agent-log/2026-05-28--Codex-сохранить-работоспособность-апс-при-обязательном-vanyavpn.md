# Codex — 2026-05-28

## Запрос
Сохранить работоспособность АПС при обязательном VanyaVPN и устранить Bitrix/VibeCode timeout.

## Результат
Реализована привязка исходящих запросов к локальному Wi-Fi IP через env (BITRIX24_SOURCE_IP/VIBECODE_SOURCE_IP). Изменены внешние клиенты bitrix24_api.py/vibecode_api.py и APS-скрипты extract/sync. Добавлен helper run_extract_with_vpn.ps1. Live smoke через helper успешен: fetched_deals=41, matched_deals=7.

## Изменённые файлы
- C:/Users/koval/bat/bitrix24-automation/bitrix24_api.py
- C:/Users/koval/bat/bitrix24-automation/vibecode_api.py
- C:/Users/koval/Documents/ОК.ру/automations/aps/extract_bitrix_for_mcp.py
- C:/Users/koval/Documents/ОК.ру/automations/aps/sync_bitrix_to_sheet.py
- C:/Users/koval/Documents/ОК.ру/automations/aps/config.json
- C:/Users/koval/Documents/ОК.ру/automations/aps/config.example.json
- C:/Users/koval/Documents/ОК.ру/automations/aps/README.md
- C:/Users/koval/Documents/ОК.ру/automations/aps/run_extract_with_vpn.ps1
- C:/Users/koval/Documents/ОК.ру/docs/agent-log/2026-05-28-aps-vpn-source-ip-bind.md

## Риски и ограничения
Полный первичный backfill остается длительным по объему данных; для быстрого daily старта нужен актуальный state. GOOGLE_SERVICE_ACCOUNT_FILE пока не задан для write-фазы sync.

## Что следующему агенту
Запускать extract через run_extract_with_vpn.ps1; при необходимости задать GOOGLE_SERVICE_ACCOUNT_FILE и выполнить sync --dry-run/--write.
