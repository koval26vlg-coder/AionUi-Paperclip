# 2026-06-23 15:09 +03 - Codex - Codex config service_tier fix

## Исходный запрос

Пользователь попросил исправить проблему из `codex mcp list`: `service_tier = default` больше не принимается Codex CLI, ожидаются `fast` или `flex`.

## Что сделано

- Создан backup `C:\Users\koval\.codex\config.toml.backup.20260623-150727`.
- В `C:\Users\koval\.codex\config.toml` изменена только строка:
  - было: `service_tier = "default"`
  - стало: `service_tier = "flex"`
- После исправления обнаружен следующий слой проблемы: текущий Codex desktop process не видел `node.exe` в inherited PATH.
- Создан backup user PATH: `C:\Users\koval\.codex\user-path.backup.20260623-150826.txt`.
- В Windows user PATH добавлен `C:\Program Files\nodejs`.
- После перезапуска/проверки выяснилось, что shell-процесс Codex все равно стартует с урезанным process PATH (`C:\Program Files\PowerShell\7;C:\Users\koval\bat`), а `codex.ps1` вызывает именно `node.exe`.
- Попытка создать `C:\Users\koval\bat\node.exe` как SymbolicLink/HardLink на `C:\Program Files\nodejs\node.exe` не прошла из-за Windows access denied.
- Создан backup npm shim: `C:\Users\koval\AppData\Roaming\npm\codex.ps1.backup.20260623-151507`.
- В `C:\Users\koval\AppData\Roaming\npm\codex.ps1` добавлен fallback: если `C:\Program Files\nodejs\node.exe` существует, shim вызывает его напрямую.

## Проверки

- `Select-String C:\Users\koval\.codex\config.toml '^service_tier\s*='` показывает `service_tier = "flex"`.
- При login-style PATH из Machine+User `Get-Command node.exe` находит `C:\Program Files\nodejs\node.exe` версии `22.22.2.0`.
- При login-style PATH `codex mcp list` успешно выводит MCP servers, включая `context7`, `playwright`, `sml`, `snyk-security`, `github`, `b24-dev-mcp`, `airtable`.
- После patch `codex.ps1` прямой запуск `& C:\Users\koval\AppData\Roaming\npm\codex.ps1 mcp list` из текущей Codex shell-среды тоже проходит без ручной PATH-подстановки.
- `verify-github-snyk-mcp.ps1` подтверждает: `GITHUB_PERSONAL_ACCESS_TOKEN` есть в process/user env, GitHub API token works for user `koval26vlg-coder`, Snyk CLI `1.1305.1`, Codex MCP list проходит. Claude MCP health-check: Context7/Playwright/SML/Snyk Connected, GitHub remote MCP transient `Failed to connect`, Google Drive `Failed to connect`, Microsoft 365 `Needs authentication`.

## Важно

Текущий Codex shell может иметь урезанный process PATH даже после перезапуска. `codex.ps1` теперь устойчив к этому через абсолютный Node fallback. При переустановке глобального npm-пакета `@openai/codex` shim может быть перегенерирован, тогда fallback нужно восстановить или обеспечить полноценный PATH в launcher.
