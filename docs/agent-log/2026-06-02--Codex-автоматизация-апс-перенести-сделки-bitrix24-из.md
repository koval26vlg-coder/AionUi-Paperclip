# Codex — 2026-06-02

## Запрос
Автоматизация АПС: перенести сделки Bitrix24 из воронки ОП в Google Sheets по критериям квалификации автоматизации, тех. пресейла и суммы >=100000, обновлять существующие строки и общий смысл.

## Результат
Префлайт ok=true. Dry-run прошел: fetched_deals=1373, matched_deals=194. После добавления retry/backoff для Bitrix REST и Google Sheets API боевой write прошел успешно: fetched_deals=1395, matched_deals=199, updated_rows=72, inserted_rows=127, prepared_cell_updates=720. State обновлен до 2026-06-02T12:03:36Z. В таблице Лист1 подтверждены 281 уникальный ID сделки.

## Изменённые файлы
- C:\Users\koval\Documents\ОК.ру\automations\aps\sync_bitrix_to_sheet.py
- C:\Users\koval\Documents\ОК.ру\docs\agent-log\2026-06-02-aps-bitrix-google-sheets-sync.md
- C:\Users\koval\Documents\ОК.ру\docs\decisions.md
- C:\Users\koval\Documents\ОК.ру\docs\tasks.md

## Риски и ограничения
Google Drive MCP/OAuth снова вернул 429 RATE_LIMIT_EXCEEDED; для automation-5 пока надежнее service account. Bitrix verify_ssl=false остается текущим сетевым компромиссом.

## Что следующему агенту
На следующем daily использовать service account write-путь и актуальный state, что должно сократить окно чтения и время запуска. Отдельно решить запуск через Планировщик задач Windows.
