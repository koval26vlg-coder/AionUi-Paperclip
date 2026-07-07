# 2026-06-23 14:00 +03 - Codex - agent-workflow-router skill

## Исходный запрос

Пользователь согласился сделать общий локальный skill/протокол, который выбирает, когда использовать frontend-design, Superpowers/TDD/debugging/code review, verification-before-completion, security-аудит и skill-creator.

## План

1. Подтянуть Aion memory bootstrap и проверить active run gate.
2. Прочитать `skill-creator`.
3. Создать локальный `agent-workflow-router`.
4. Установить его в Codex, Claude Code, `.agents` и shared `agent-skills`.
5. Проверить наличие файлов и валидность JSON.

## Что сделано

- Создан skill `agent-workflow-router`.
- Skill установлен в:
  - `C:\Users\koval\.codex\skills\agent-workflow-router`
  - `C:\Users\koval\.claude\skills\agent-workflow-router`
  - `C:\Users\koval\.agents\skills\agent-workflow-router`
  - `C:\Users\koval\Documents\Codex\2026-05-18\npx-skills-add-anthropics-claude-code\agent-skills\agent-workflow-router`
- Добавлены:
  - `SKILL.md`
  - `metadata.json`
  - `evals\evals.json`
- Обновлены shared manifests:
  - `agent-skills\INSTALL_MANIFEST.md`
  - `agent-skills\install-manifest.json`

## Проверки

- `SKILL.md` найден во всех четырех целевых директориях.
- `evals.json` валиден через `ConvertFrom-Json`.
- `install-manifest.json` валиден через `ConvertFrom-Json`.
- В `SKILL.md` проверены ключевые маршруты: `frontend-design`, `systematic-debugging`, `skill-creator`, `verification-before-completion`.

## Ограничения

- Полный eval-loop с subagent baseline не запускался; создан lightweight eval-набор для будущей проверки триггеров.
- Активный gate `trading_mvp` оставался `RUNNING`; код и постобработка этого проекта не трогались.

## Следующий агент

При инженерных задачах сначала учитывать `agent-workflow-router`: выбрать минимальный достаточный route, затем загрузить только нужные downstream skills и перед финальным ответом выполнить свежую verification-проверку.

