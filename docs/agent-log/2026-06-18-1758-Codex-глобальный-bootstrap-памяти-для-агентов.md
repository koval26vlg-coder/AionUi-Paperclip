# 2026-06-18 17:58 — Codex — глобальный bootstrap памяти для агентов

## Запрос пользователя

Пользователь попросил заложить каждому агенту skill/инструкцию/правило, чтобы агент подтягивал общую память автоматически, а не только при запуске из `D:\AionUi-Paperclip` или после отдельной просьбы.

## План

- Сделать абсолютный bootstrap общей памяти из любой папки.
- Подключить правило к активным агентам: Codex, Claude Code, Gemini CLI.
- Не возвращать Cursor, Kiro и MiMo Code.
- Проверить запуск из внешней папки и валидность skill.

## Что сделано

- Добавлен `docs/agent-memory-bootstrap.md` — каноническое правило автоподхвата памяти.
- Добавлен `tools/agent-memory-bootstrap.ps1` — команда, которая из любой папки показывает статус памяти, делает relationship-map query и выводит excerpt context-pack.
- Добавлен `LOAD-SML-MEMORY.cmd` для ручной проверки.
- В `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` добавлен абсолютный bootstrap-путь.
- В глобальные инструкции добавлено правило:
  - `C:\Users\koval\.codex\AGENTS.md`
  - `C:\Users\koval\.claude\CLAUDE.md`
  - `C:\Users\koval\.gemini\GEMINI.md`
- Создан Codex skill `C:\Users\koval\.codex\skills\sml-memory-bootstrap`.
- Для Claude Code добавлен user-scope MCP `sml` через `claude mcp add --scope user`.
- Актуализированы `docs/current-context.md`, `docs/tasks.md`, `docs/agents.md`, `docs/local-environment.md`, `docs/decisions.md`.

## Проверки

- `tools\agent-memory-bootstrap.ps1` успешно запущен из `C:\Users\koval\Documents\Bitrix24`.
- Bootstrap нашел `D:\AionUi-Paperclip`, context-pack и relationship-map.
- `quick_validate.py` подтвердил: `Skill is valid!`
- `claude mcp list` из внешней папки показывает `sml` как `Connected`.

## Ограничения

- Это не заставляет веб-версии Claude/ChatGPT автоматически читать локальные файлы без локального инструмента.
- Автоматический подхват зависит от того, читает ли конкретный агент свои глобальные инструкции.
- Cursor, Kiro и MiMo Code этим шагом не возвращались.

## Следующий шаг

При новом запуске Codex, Claude Code или Gemini CLI проверить коротким запросом, что агент сам упоминает bootstrap/SML без отдельной просьбы пользователя.
