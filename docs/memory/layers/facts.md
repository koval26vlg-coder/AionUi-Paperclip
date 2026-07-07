# Долгосрочные факты

## Рабочая архитектура

- Основная папка: `D:\AionUi-Paperclip`.
- Главная цель: сделать агентов взаимозаменяемыми через общий файловый контекст.
- Основные агенты: Codex, Claude Code, Antigravity CLI (активная связка на 2026-06-24).
- Antigravity CLI использует `agy` и локальное состояние `C:\Users\koval\.gemini\antigravity-cli`; общая память SML (база данных SQLite `D:\AionUi-Paperclip\var\sml\state.db` и векторная Lance `D:\AionUi-Paperclip\var\sml\lance`) остается в `D:\AionUi-Paperclip`.
- AionUi, Paperclip и Hermes исключены из текущей основной схемы.
- Общая память реализована с помощью файлов Markdown и базы данных SML.
- MCP-память используется при доступности сервера, при его отсутствии агент работает напрямую с файлами и БД.

## Принцип взаимозаменяемости

Любой новый агент должен иметь возможность восстановить контекст через:

- `AGENTS.md`;
- `docs/START-HERE.md`;
- `docs/context-packs/context-pack-latest.md`;
- `docs/current-context.md`;
- `docs/tasks.md`;
- `docs/decisions.md`;
- `docs/agent-log/`.

## Принцип поиска памяти

Работа с памятью является поведением по умолчанию. Агент должен сам искать похожее по теме запроса перед содержательным ответом или действием.

## 2026-05-10 19:16:35 - kiro

Target_Repo `C:\Users\koval\bat\bitrix24-automation`: Git for Windows 2.51.0.windows.1 установлен в `C:\Program Files\Git\cmd\git.exe`, но по умолчанию НЕ в PATH сессии PowerShell внутри IDE (сам PATH усечён — нет даже System32). До починки PATH любые `git`-команды из спека bitrix24-automation-hygiene (1.1, 1.2, S1..S7) в этой сессии не работают. Варианты: добавить `C:\Program Files\Git\cmd` в User PATH, либо задавать `$env:PATH = 'C:\Program Files\Git\cmd;' + $env:PATH` в начале сессии.

## 2026-05-11 11:08:50 - kiro

D:\AionUi-Paperclip — самостоятельный проект, инфраструктура общего контекста и памяти для AI-агентов (Codex, Cursor, Kiro). Никакого отношения к Bitrix или любому другому продукту не имеет. Упоминания C:\Users\koval\bat\bitrix24-automation и spec-ов bitrix24-automation-hygiene / bitnewton-* — это прикладные работы, которые катятся через инфраструктуру, но не являются её частью. Код внешних проектов живёт в их собственных репозиториях; здесь остаются только spec-документы, журналы и память о ходе работы.
