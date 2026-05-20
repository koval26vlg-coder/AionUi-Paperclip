# Codex — 2026-05-14T13:59:03.413Z

## Запрос
Можно ли пользоваться Gemini из Cursor?

## План
Проверить Cursor MCP/SML, добавить правило Cursor для использования Gemini как второго ревьюера, обновить документацию.

## Результат
Можно. Основной способ: Cursor и Gemini работают через общий SML. Из терминала Cursor можно запускать Gemini CLI командой gemini или gemini -p. Добавлено правило .cursor/rules/use-gemini-from-cursor.mdc и раздел в docs/gemini-sml.md.

## Изменённые файлы
- D:\AionUi-Paperclip\.cursor\rules\use-gemini-from-cursor.mdc
- D:\AionUi-Paperclip\docs\gemini-sml.md
- D:\AionUi-Paperclip\docs\context-packs\context-pack-latest.md

## Риски и ограничения
Не использовать Gemini как единственный источник истины или основной исполнитель рискованных правок. Через Cursor Settings > Models можно подключить Gemini по Google API key, но это отдельный путь от Gemini CLI/SML.

## Что следующему агенту
В Cursor открыть D:\AionUi-Paperclip, попросить Cursor использовать правило Gemini или запустить Gemini из встроенного терминала.
