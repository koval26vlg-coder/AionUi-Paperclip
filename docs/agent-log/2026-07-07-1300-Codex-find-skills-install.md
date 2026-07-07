# 2026-07-07 13:00 +03 Codex - find-skills install after YouTube Short XfifNCHY93I

## Исходный запрос

Пользователь дал YouTube Short `https://www.youtube.com/shorts/XfifNCHY93I` и попросил посмотреть и принять решение.

## Что найдено в видео

Ролик продвигает идею "последнего ручного скилла" для Claude Code: `Open Skills` / `find-skills`, который ищет подходящие agent skills в open skills ecosystem вместо ручного перебора GitHub README.

## Решение

Принято: установить `find-skills` из `vercel-labs/skills`, но использовать его только как discovery/ranking слой. Не разрешать слепую автоустановку найденных skills без проверки источника, install count, репозитория, scripts/MCP/network behavior и локальной пользы.

## Что сделано

- Выполнен video-watch разбор с transcript, agy и frames.
- Установлен `find-skills` командой:
  `npx skills add vercel-labs/skills --skill find-skills -g -a claude-code -a codex -a cursor -a opencode -y`
- Синхронизирован skill в `.agents`, `.claude`, `.codex` и shared `agent-skills`.
- `agent-workflow-router` обновлен: добавлен `Skill Discovery Route Detail` и route через `find-skills`.
- Созданы manifest-файлы:
  - `agent-skills\FIND_SKILLS_INSTALL_MANIFEST.md`
  - `agent-skills\find-skills-install-manifest.json`

## Проверка

- `npx skills --version` вернул `1.5.15`.
- `npx skills find react` вернул ранжированные результаты.
- `quick_validate.py` прошел для `find-skills` и `agent-workflow-router` в основных roots.

## Ограничения

Команда `npx skills find --help` в текущей CLI версии ведет себя как поиск по `help`, а не как справка. Для справки использовать README/доки или `npx skills find <query>`.
