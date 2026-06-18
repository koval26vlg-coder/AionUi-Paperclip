# 2026-06-18 17:25 — Codex — очистка артефактов и Node PATH

## Контекст

Пользователь подтвердил решение: MiMo/Kiro/Cursor были срезаны осознанно, в этой части ничего не возвращать и не менять.

## Что сделано

- Оставлены технические улучшения SML/Aion Vision от Claude Code.
- Удалены только временные артефакты:
  - `D:\AionUi-Paperclip\.playwright-mcp`
  - `D:\AionUi-Paperclip\analytics-and-health.png`
  - `D:\AionUi-Paperclip\memory-search-result.png`
  - `D:\AionUi-Paperclip\apps\aion-vision\scripts\__pycache__`
- В `.gitignore` добавлены правила для генерируемых context-pack snapshot-файлов и временных browser/test артефактов.
- `START-AION-VISION.cmd` и `START-AION-VISION-SERVE.cmd` теперь явно используют `C:\Program Files\nodejs\npm.cmd`, если он найден, и заранее добавляют Node.js в `PATH`.

## Проверки

- `python -X utf8 -m tools.sml.core selfcheck` — успешно.
- `npm run build` для Aion Vision — успешно при том же PATH-режиме, который используют запускатели.

## Важно

Решение по удалению MiMo/Kiro/Cursor не откатывалось. `OPEN-KIRO-RU.cmd` остаётся удалённым как часть ранее принятого решения.
