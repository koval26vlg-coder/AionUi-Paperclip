# 2026-06-23 15:48 +03 - Codex - Claude GitHub MCP env fix

## Исходный запрос

Пользователь попросил исправить Claude MCP health-check: Context7/Playwright/SML/Snyk были подключены, но `plugin:github:github` показывал `Failed to connect`; Google Drive ранее тоже мог падать, Microsoft 365 показывал `Needs authentication`.

## Диагностика

- `GITHUB_PERSONAL_ACCESS_TOKEN` был сохранен в Windows User env, но отсутствовал в текущем process env.
- GitHub API с user-level token работает для `koval26vlg-coder`.
- `claude mcp list` без token в process env давал `plugin:github:github ... Failed to connect`.
- После временного импорта user-level token в process env `plugin:github:github` становился `Connected`.

## Что сделано

- Создан backup `C:\Users\koval\bat\claude.cmd.backup.20260623-154410`.
- Обновлен `C:\Users\koval\bat\claude.cmd`: если `GITHUB_PERSONAL_ACCESS_TOKEN` не задан в текущем process env, shim читает значение из `HKCU\Environment` через `%SystemRoot%\System32\reg.exe` и задает его только для дочернего `claude.exe`.
- Токен не записывался в файл и не печатался.

## Проверки

- `cmd /v:on ... call C:\Users\koval\bat\claude.cmd --version` подтвердил `wrapper-token-imported`.
- `claude mcp list` при очищенном process env показал:
  - `claude.ai Google Drive` - Connected
  - `plugin:github:github` - Connected
  - `plugin:context7:context7` - Connected
  - `plugin:playwright:playwright` - Connected
  - `sml` - Connected
  - `snyk-security` - Connected
  - `claude.ai Microsoft 365` - Needs authentication

## Осталось

Microsoft 365 требует отдельную OAuth-авторизацию в Claude; это не локальная проблема PAT/GitHub. Google Drive на финальной проверке подключен.

