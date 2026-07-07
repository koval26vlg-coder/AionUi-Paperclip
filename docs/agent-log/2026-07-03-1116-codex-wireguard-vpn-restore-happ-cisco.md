# 2026-07-03 11:16 Codex - WireGuard VPN restore Happ/Cisco

Контекст: после добавления кнопок `Погасить Happ/Cisco` и `Погасить и включить` пользователь попросил оставить обратную возможность включать Happ/Cisco, потому что остановленные службы и адаптеры сами не возвращались.

Сделано:
- добавлен `C:\Users\koval\Documents\WireGuard VPN\tools\vpn\restore_local_vpn_blockers.ps1`;
- добавлен `C:\Users\koval\Documents\WireGuard VPN\RESTORE_LOCAL_VPN_BLOCKERS.cmd`;
- в панель добавлена кнопка `Вкл. Happ/Cisco`;
- restore-команда по умолчанию останавливает `ZLSSHVPN`, включает адаптеры Happ/Cisco, запускает `HappService`, `csc_vpnagent`, `csc_iseagent` и открывает UI клиентов, если exe найден;
- `stop_local_vpn_blockers.ps1` больше не отключает все адаптеры с описанием `sing-tun`, чтобы не задевать `ZLSSHVPN`;
- self-elevation в `stop_local_vpn_blockers.ps1` и `start_clean_system_vpn.ps1` переведена на quoted argument string, чтобы путь `WireGuard VPN` не ломал запуск.

Проверка:
- PowerShell parser OK для `restore_local_vpn_blockers.ps1`, `stop_local_vpn_blockers.ps1`, `start_clean_system_vpn.ps1`, `vpn_control_panel.ps1`;
- `vpn_control_panel.ps1 -SelfTest` OK;
- `tools\check-vpn-health.ps1` OK, Windows public IP `147.90.11.165`;
- панель перезапущена, процесс `powershell` PID `22856`, окно `ZolotayaLopata VPN Control Panel` отвечает;
- restore-скрипт намеренно не запускался верификацией, чтобы не выключить рабочий `ZLSSHVPN`.

Текущее состояние после работы:
- `ZLSSHVPN` adapter `Up`;
- `Cisco AnyConnect Virtual Miniport` disabled до ручного restore;
- внешний IP Windows `147.90.11.165`.
