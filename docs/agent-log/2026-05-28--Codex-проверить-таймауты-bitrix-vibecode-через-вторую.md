# Codex — 2026-05-28

## Запрос
Проверить таймауты Bitrix/VibeCode через вторую сеть/VPN, прокси/HTTPS-inspection и повторить extract.

## Результат
Диагностика показала, что общий интернет работает, но доступ к online-kassa.bitrix24.ru и vibecode.bitrix24.tech уходит в timeout. Обнаружен активный full-tunnel через outline-tap0 (маршруты 0.0.0.0/1 и 128.0.0.0/1), запущены VanyaVPN/OutlineService. WinHTTP без прокси, WinINet proxy выключен, env-прокси отсутствуют. Контрольный extract не завершился из-за сетевого канала.

## Изменённые файлы
- C:/Users/koval/Documents/ОК.ру/docs/agent-log/2026-05-28-aps-timeouts-vpn-route-diagnostics.md

## Риски и ограничения
Пока full-tunnel/VPN путь активен и нестабилен, APS extract будет падать по timeout независимо от фильтров.

## Что следующему агенту
Отключить/обойти VPN full-tunnel на время прогона, проверить profile/me endpoint и сразу повторить extract_bitrix_for_mcp.py.
