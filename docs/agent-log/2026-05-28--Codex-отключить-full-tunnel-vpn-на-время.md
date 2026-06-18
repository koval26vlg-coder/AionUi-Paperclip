# Codex — 2026-05-28

## Запрос
Отключить full-tunnel VPN на время прогона, проверить profile/me endpoint и повторить extract.

## Результат
Выполнена попытка временного отключения VPN со стороны процессов (VanyaVPN/OutlineService), но маршруты full-tunnel через outline-tap0 остались активны и процессы восстановились. Endpoint Bitrix profile.json и VibeCode /v1/me продолжают timeout. Повторный fail-fast запуск extract завершился Read timed out на crm.deal.list.

## Изменённые файлы
- C:/Users/koval/Documents/ОК.ру/docs/agent-log/2026-05-28-aps-vpn-check-and-rerun.md

## Риски и ограничения
При активном full-tunnel/автовосстановлении VPN APS extract продолжит падать по таймаутам.

## Что следующему агенту
Отключить туннель в UI VPN-клиента (снять full-tunnel/автоподъем), повторить проверки endpoint и затем штатный extract.
