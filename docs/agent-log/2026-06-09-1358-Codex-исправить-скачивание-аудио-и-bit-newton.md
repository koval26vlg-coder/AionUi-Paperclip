# Codex — 2026-06-09T13:58:18.389Z

## Запрос
Исправить скачивание аудио и Bit.Newton ASR без браузера.

## План
Добавить source-IP bind в download_resolver и Bit.Newton клиенты, проверить smoke и retry.

## Результат
Исправлено: download_resolver берет BITRIX24_SOURCE_IP; bit_newton_asr.py и bit_new_ton_asr.py берут BITNEWTON_SOURCE_IP или fallback BITRIX24_SOURCE_IP. Тесты source_ip: 3 passed. Smoke без браузера: profile ok, audio/mpeg 3551904 bytes, Bit.Newton token ok. Retry отчета 20260609_145249 без --ui-download: новый отчет 20260609_165440, OK=13 ERR=0. Выполнен --ack-current: pending_score=0, pending_crm=0.

## Изменённые файлы
- download_resolver.py
- bit_newton_asr.py
- bit_new_ton_asr.py
- tests/test_source_ip_binding.py
- memory.md
- docs/agent-log/2026-06-09-bitrix-no-browser-download-asr.md

## Риски и ограничения
BITNEWTON_TOKEN истекает 2026-06-11; source-IP нужен в том же процессе CLI.

## Что следующему агенту
Основной маршрут: --bitrix-source vibecode --use-vibecode --use-bitnewton --vibecode-asr-fallback --no-vibecode-timeline-log, без --ui-download.
