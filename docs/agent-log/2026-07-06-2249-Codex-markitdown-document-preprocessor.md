# 2026-07-06 22:49 +03 Codex - MarkItDown document preprocessor

## Что сделано

- Из видео `Lj_dEwFJ0Gk` извлечен практический вывод: перед отправкой больших PDF/Office/HTML/медиа документов в LLM выгодно конвертировать их в чистый Markdown через Microsoft MarkItDown.
- Установлен изолированный Python venv: `C:\Users\koval\.markitdown-venv`.
- Установлены `markitdown 0.1.6`, `markitdown-mcp 0.0.1a4`, `imageio-ffmpeg 0.6.0`.
- Добавлены локальные команды:
  - `C:\Users\koval\bat\markitdown.cmd`
  - `C:\Users\koval\bat\markitdown-mcp.cmd`
  - `C:\Users\koval\bat\ffmpeg.exe`
- Добавлен skill `markitdown-document-preprocessor` в:
  - `C:\Users\koval\.codex\skills`
  - `C:\Users\koval\.agents\skills`
  - `C:\Users\koval\.claude\skills`
  - shared `agent-skills`

## Проверка

- `markitdown --version` вернул `markitdown 0.1.6`.
- `markitdown-mcp --help` работает; transport по умолчанию STDIO.
- `ffmpeg -version` работает.
- Smoke-test: `transcript.txt` из артефакта видео сконвертирован в `C:\Users\koval\Documents\Команда\artifacts\markitdown-smoke\lj_dewfj0gk-transcript.md`, размер 1339 bytes.
- Skill прошел `quick_validate.py`.

## Политика

MarkItDown MCP установлен, но не включен как HTTP-сервер. Для агентов использовать локальный CLI или STDIO MCP. Не запускать `markitdown-mcp --http` без явного подтверждения bind address/port/access boundary.

## Манифест

- `C:\Users\koval\Documents\Codex\2026-05-18\npx-skills-add-anthropics-claude-code\agent-skills\MARKITDOWN_INSTALL_MANIFEST.md`
- `C:\Users\koval\Documents\Codex\2026-05-18\npx-skills-add-anthropics-claude-code\agent-skills\markitdown-install-manifest.json`
