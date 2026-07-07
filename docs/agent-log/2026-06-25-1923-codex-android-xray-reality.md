# Agent Log: Android VPN switched to Xray REALITY

## Date
2026-06-25 19:23 Europe/Volgograd

## Agent
Codex

## User request
User reported that the Android VPN still did not work after prior WireGuard/OpenVPN/Shadowsocks attempts and asked to stop looping.

## Context
Previous Android tests showed WireGuard/OpenVPN handshakes and server-side traffic, but phone pages still did not load. Shadowsocks was active on TCP/UDP 443 but did not provide a confirmed stable phone path.

## Work done
- Added `tools/vpn/deploy_android_xray_reality.ps1`.
- Added `tools/vpn/watch_android_xray_reality.ps1`.
- Installed Xray on VPS `147.90.11.165`.
- Replaced the Android mobile service on TCP 443 with VLESS REALITY.
- Stopped/disabled `shadowsocks-libev` for port 443.
- Kept WireGuard `wg0` active as reserve/diagnostic mode.
- Generated local Android import artifacts:
  - `C:\Users\koval\Desktop\zl-android-vless-reality-link.txt`
  - `C:\Users\koval\Desktop\zl-android-vless-reality-qr.png`
  - `C:\Users\koval\Desktop\zl-android-vless-reality-summary.txt`

## Verification
- `xray` service: active.
- TCP 443 listener: `xray`.
- Xray config test: `Configuration OK`.
- VPS external IP check: `147.90.11.165`.
- `wg-quick@wg0`: active.

## Notes
- Do not print the VLESS link or QR in shared logs; they are secret credentials.
- Android must use a VLESS REALITY capable app such as v2rayNG or Hiddify Next, not the WireGuard app and not OpenVPN Connect.
- If the phone still does not work, run `tools/vpn/watch_android_xray_reality.ps1` while enabling the profile on the phone and inspect TCP 443 established sessions plus Xray journal.
