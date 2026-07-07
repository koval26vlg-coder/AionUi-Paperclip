# 2026-07-03 10:08 Codex - WireGuard VPN local repair

## Исходный запрос

Пользователь попросил проверить логи, исправить ошибки и довести VPN до рабочего состояния. По панели было видно: системный VPN не включается, внешний IP не равен VPS, активен Cisco/Happ.

## Краткий план

- Проверить SML/Aion контекст и active-run gate.
- Собрать локальные логи, процессы, сервисы, маршруты и состояние VPS.
- Найти root cause в панели и стартовых скриптах.
- Исправить запуск и диагностику.
- Проверить внешний IP и серверное состояние.

## Что сделано

- Подтверждено, что VPS исправен: `xray active`, `xray enabled`, `*:443` слушает, `xray run -test` возвращает `Configuration OK`, предупреждений в `journalctl -u xray` нет.
- Найден локальный blocker: `happ-tun`/Cisco держали маршрут и мешали запуску `ZLSSHVPN`.
- Найден баг запуска `sing-box`: из-за пробела в пути `C:\Users\koval\Documents\WireGuard VPN` `Start-Process -ArgumentList @(...)` приводил к ошибке чтения `C:\Users\koval\Documents\WireGuard`.
- Исправлена передача аргументов в `singbox_ssh_socks_tun.ps1` и `singbox_wireguard_tun.ps1` через явное quoting/join.
- Добавлен cleanup: при неудачном старте TUN теперь убираются полусостояния `ssh -D` и pid-файлы.
- Панель теперь показывает blocker `Happ/Cisco`, не пишет ложное успешное состояние, и имеет кнопки `Погасить Happ/Cisco` и `Погасить и включить`.
- Добавлены скрипты `tools\vpn\stop_local_vpn_blockers.ps1`, `tools\vpn\start_clean_system_vpn.ps1`, `STOP_LOCAL_VPN_BLOCKERS.cmd`, `START_CLEAN_SYSTEM_VPN.cmd`.
- `tools\check-vpn-health.ps1` переведен на устойчивую проверку текущего IP через `curl.exe` с fallback.
- README обновлен с Windows-сценарием запуска и критерием готовности.

## Измененные файлы

- `C:\Users\koval\Documents\WireGuard VPN\README_RU.md`
- `C:\Users\koval\Documents\WireGuard VPN\START_CLEAN_SYSTEM_VPN.cmd`
- `C:\Users\koval\Documents\WireGuard VPN\STOP_LOCAL_VPN_BLOCKERS.cmd`
- `C:\Users\koval\Documents\WireGuard VPN\tools\check-vpn-health.ps1`
- `C:\Users\koval\Documents\WireGuard VPN\tools\vpn\singbox_ssh_socks_tun.ps1`
- `C:\Users\koval\Documents\WireGuard VPN\tools\vpn\singbox_wireguard_tun.ps1`
- `C:\Users\koval\Documents\WireGuard VPN\tools\vpn\start_clean_system_vpn.ps1`
- `C:\Users\koval\Documents\WireGuard VPN\tools\vpn\stop_local_vpn_blockers.ps1`
- `C:\Users\koval\Documents\WireGuard VPN\tools\vpn\vpn_control_panel.ps1`
- `C:\Users\koval\Documents\WireGuard VPN\vpn-control-panel.config.json`

## Проверки

- PowerShell syntax OK для всех измененных `.ps1`.
- `vpn_control_panel.ps1 -SelfTest` OK.
- `singbox_ssh_socks_tun.ps1 -Action check` OK, config path с пробелом проходит.
- `curl.exe -4 https://api.ipify.org` вернул `147.90.11.165`.
- `check-vpn-health.ps1 -Server -TimeoutMs 6000` показал текущий Windows IP `147.90.11.165`, `xray active/enabled`, `*:443` listener, `Configuration OK`.
- `check-vpn-health.ps1 -External -ExternalPorts 443 -TimeoutMs 6000` показал `443/tcp success_count=5/5` и текущий Windows IP `147.90.11.165`.
- Локальное состояние: `ZLSSHVPN` Up, `sing-box SSH TUN` running PID 9448, `SSH SOCKS` running PID 28492, `HappService` stopped, `csc_vpnagent` stopped, Cisco adapter disabled.

## Риски и ограничения

- Текущий режим является TCP-over-SSH TUN; UDP намеренно не является рабочей частью этого режима. Старые UDP block строки в логе не являются причиной неработающего TCP VPN.
- HOSTKEY API может быть полезен как аварийный серверный канал, но текущая поломка была локальной, не серверной.
- При следующем чистом запуске через `Погасить и включить` будет применен новый noisy-log filter/config.

## Что должен проверить следующий агент

- Если пользователь снова видит не-VPS IP, сначала нажать `Погасить и включить` в панели или запустить `START_CLEAN_SYSTEM_VPN.cmd`.
- Затем проверить `curl.exe -4 https://api.ipify.org`; ожидается `147.90.11.165`.
- Если `147.90.11.165` не возвращается, читать `ssh-tun-vpn-out\start-clean-system-vpn.log`, `local-vpn-blockers.log`, `singbox-ssh-socks-tun.stderr.log`.
