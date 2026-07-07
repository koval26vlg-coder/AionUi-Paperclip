# 2026-06-30 14:10 +03 - Codex - Antigravity NOI recovery attempt

## Request

Пользователь попросил выполнить следующий шаг по Antigravity: восстановить SSH/NOI, пройти OAuth и сделать smoke через сервер.

## Route

Agent coordination / tool setup / debugging. Проверялись только короткие диагностические команды и smoke-запуски; long-running процессы не запускались.

## What Was Checked

- Aion SML bootstrap по теме `восстановить SSH NOI Antigravity OAuth smoke`.
- `trading_mvp` active-run gate: `READY_FOR_POSTPROCESS`, без запуска trading collectors/replay/grid.
- Локальный `agy`: найден через `C:\Users\koval\bat\agy.cmd`, версия `1.0.14`.
- Локальный `agy --print` без proxy.
- Локальный `agy --print` через Frankfurt proxy `127.0.0.1:10809`.
- SSH к `root@147.90.11.165` через Windows OpenSSH.
- TCP/banner probes для `147.90.11.165:22`.
- Альтернативные SSH-порты `22`, `2222`, `443`, `2022`, `2200`.
- Старый Xray/REALITY NOI proxy helper.

## Result

Antigravity локально все еще blocked для live model call:

```text
FAILED_PRECONDITION (code 400): User location is not supported for the API use
```

Frankfurt proxy жив (`Germany / Frankfurt am Main`), но на текущем `agy 1.0.14` не снимает блокировку.

NOI/VPS сейчас недоступен для управления по SSH:

```text
TCP: connected
SSH banner: read failed
```

OpenSSH также возвращает:

```text
Connection timed out during banner exchange
```

Xray/REALITY путь к NOI не помог: локальный proxy принял `ifconfig.co:443`, но запрос ушел в timeout.

## Added Tools

Добавлены постоянные проектные helper-скрипты:

- `tools/check-antigravity-noi.ps1`
- `tools/start-antigravity-noi-auth.ps1`

Команда проверки после reboot/console recovery:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "D:\AionUi-Paperclip\tools\check-antigravity-noi.ps1"
```

После восстановления SSH и успешной версии `agy`:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "D:\AionUi-Paperclip\tools\start-antigravity-noi-auth.ps1"
pwsh -NoProfile -ExecutionPolicy Bypass -File "D:\AionUi-Paperclip\tools\check-antigravity-noi.ps1" -Smoke
```

## Next Step

Нужен reboot/console recovery VPS `147.90.11.165` из панели провайдера или out-of-band console. Пока SSH banner не возвращается, OAuth и remote smoke выполнить нельзя.

## Reboot Follow-Up

2026-06-30 после сообщения пользователя `перезагрузил` выполнена повторная проверка:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "D:\AionUi-Paperclip\tools\check-antigravity-noi.ps1"
```

Результат не изменился:

```text
TCP: connected
SSH banner: read failed
```

Также исправлен bug в helper-скриптах: PowerShell 7 с `Set-StrictMode` падал на `.Source`, если `ssh.exe` не найден через `Get-Command`. Теперь `tools/check-antigravity-noi.ps1` и `tools/start-antigravity-noi-auth.ps1` корректно fallback-ят на `C:\Windows\System32\OpenSSH\ssh.exe`.

Следующий шаг уже не обычный reboot, а console/rescue diagnostics у провайдера: проверить `sshd`, firewall и загрузку ОС с консоли VPS.

## HAPP Follow-Up

2026-06-30 после сообщения пользователя, что HAPP-профиль переключен, проверены оба локальных proxy:

```text
127.0.0.1:10808 -> United States / Los Angeles / 24SHELLS
127.0.0.1:10809 -> United States / Los Angeles / 24SHELLS
```

Через `HTTP_PROXY/HTTPS_PROXY=http://127.0.0.1:10809` запущено видимое OAuth-окно для локального `agy`. OAuth успешно восстановлен для текущего аккаунта, но короткий smoke `agy --print "Ответь ровно одним словом: ok"` снова завершился:

```text
FAILED_PRECONDITION (code 400): User location is not supported for the API use
```

OAuth URL из локального test-лога был редактирован как sensitive auth artifact. Вывод: текущий HAPP US-route не снимает regional/eligibility блок Antigravity API. Antigravity остается недоступным как надежный L1/L2 runtime до другого supported route/account либо восстановления NOI через console/rescue.
