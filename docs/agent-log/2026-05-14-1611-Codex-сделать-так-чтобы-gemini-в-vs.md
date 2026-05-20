# Codex — 2026-05-14T16:11:11.658Z

## Запрос
Сделать так, чтобы Gemini в VS Code автоматически помнил наши правила и SML-протокол.

## План
Создать GEMINI.md, прописать русский язык, SML до задачи, SML-лог после работы, VS Code IDE-контекст и безопасность; проверить загрузку Gemini CLI.

## Результат
Создан D:\AionUi-Paperclip\GEMINI.md. Gemini CLI подтвердил, что проектный GEMINI.md загружен и видит правила: русский язык, sml.startup_pack/sml.semantic_query перед задачей, sml.add_log после работы. Документы и context-pack обновлены.

## Изменённые файлы
- D:\AionUi-Paperclip\GEMINI.md
- D:\AionUi-Paperclip\docs\gemini-sml.md
- D:\AionUi-Paperclip\docs\local-environment.md
- D:\AionUi-Paperclip\docs\context-packs\context-pack-latest.md

## Риски и ограничения
GEMINI.md повышает вероятность автоматического соблюдения протокола, но модель все равно может иногда не вызвать SML; для критичных задач проверять через /memory show и просить явно выполнить sml.*.

## Что следующему агенту
В VS Code после изменения GEMINI.md выполнить /memory reload в Gemini CLI. Для IDE-контекста выполнить /ide enable.
