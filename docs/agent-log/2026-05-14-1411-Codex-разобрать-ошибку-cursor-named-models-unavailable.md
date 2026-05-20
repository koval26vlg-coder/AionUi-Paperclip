# Codex — 2026-05-14T14:11:13.450Z

## Запрос
Разобрать ошибку Cursor: Named models unavailable при выборе Gemini 3.1 Pro.

## План
Объяснить ограничение Cursor Free, обновить документацию по Gemini в Cursor, сохранить вывод в SML.

## Результат
Ошибка означает, что текущий бесплатный план Cursor разрешает только модель Auto и блокирует named models вроде Gemini 3.1 Pro. Это не ошибка SML и не Gemini CLI. Документы docs/cursor-gemini-model.md и docs/gemini-sml.md обновлены: для работы внутри Cursor выбрать Auto или перейти на платный Cursor; если нужен именно Gemini, запускать Gemini CLI из терминала Cursor.

## Изменённые файлы
- D:\AionUi-Paperclip\docs\cursor-gemini-model.md
- D:\AionUi-Paperclip\docs\gemini-sml.md
- D:\AionUi-Paperclip\docs\context-packs\context-pack-latest.md

## Риски и ограничения
Даже с Google API key Cursor Free может не дать выбрать конкретную модель. SML должен продолжать работать в Auto, если MCP подключен.

## Что следующему агенту
В Cursor выбрать Auto и повторить запрос SML. Для Gemini-specific ревью запустить gemini -p из терминала Cursor.
