# 2026-07-03 09:32 Codex - WireGuard VPN health check

## Исходный запрос

Пользователь спросил: "что у нас с VPN ghjdthm" (прочитано как "проверь").

## Краткий план

- Подтянуть Aion/SML контекст.
- Проверить active-run gate.
- Запустить `C:\Users\koval\Documents\WireGuard VPN\tools\check-vpn-health.ps1`.
- Проверить внешний доступ к `147.90.11.165:22` и `147.90.11.165:443`.
- Если SSH доступен, сделать read-only проверку `xray` на VPS.

## Что сделано

- Aion bootstrap выполнен; memory watcher сейчас stale, но context-pack и relationship-map прочитались.
- Active-run gate сейчас `STOPPED_INCOMPLETE` для `trading_mvp`; VPN-проверка не трогала торговые прогоны.
- `check-vpn-health.ps1 -External` показал:
  - Desktop VLESS REALITY link/QR/summary существуют, обновлены 2026-07-02.
  - VLESS link structurally ok: `security=reality`, `flow=xtls-rprx-vision`, server `147.90.11.165:443`, SNI `www.apple.com`.
  - Внешний TCP check-host: `22/tcp` доступен `5/5`, `443/tcp` доступен `5/5`.
  - Локальный Windows default route идет через `happ-tun`; текущий внешний IP Windows `50.7.28.226`, то есть Windows не сидит на нашем VPS как основном выходе.
- `check-vpn-health.ps1 -Server` через SSH подтвердил:
  - `xray` active и enabled.
  - `*:443` слушает процесс `xray`.
  - `xray run -test -config /usr/local/etc/xray/config.json` возвращает `Configuration OK`.
  - `shadowsocks-libev` inactive.
  - `openvpn-server@android` inactive.
  - `wg-quick@wg0` active как резерв.
  - В `journalctl -u xray --since "15 minutes ago" -p warning` нет предупреждений.

## Файлы изменены

- Добавлен этот журнал.

## Проверки

- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\tools\check-vpn-health.ps1 -External -TimeoutMs 5000`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\tools\check-vpn-health.ps1 -Server -TimeoutMs 5000`

## Риски и ограничения

- Android end-to-end не подтвержден, потому что телефон не проверялся. Нужно включить профиль `ZL-REALITY-443` на Android и открыть `https://api.ipify.org`; ожидаемый IP `147.90.11.165`.
- Локальный Windows-трафик сейчас идет через Happ, а не через наш VPS. Это нормально для проверки Android, но не является подтверждением Windows VPN.

## Что должен проверить следующий агент

- Если пользователь говорит, что телефон не работает: запускать `tools\vpn\watch_android_xray_reality.ps1` и просить включить профиль на телефоне, чтобы увидеть established TCP сессии к `xray`.
- Не возвращаться к WireGuard/OpenVPN как основному Android пути без новых причин; текущий основной Android профиль - Xray VLESS REALITY.
