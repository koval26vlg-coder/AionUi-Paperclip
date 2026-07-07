# 2026-06-30 12:18 +03 - Codex - agent-loops skill

## Исходный запрос

Пользователь попросил реализовать практический вывод по loops.elorm.xyz: сделать локальный `agent-loops` или расширить `agent-workflow-router`, добавив режимы `verify`, `ci-until-green`, `post-edit-tests`, `docs-sync`, `security-audit`, `deploy-smoke`.

## План

1. Проверить общий Aion-контекст и текущий `agent-workflow-router`.
2. Создать локальный skill `agent-loops` в активных skill roots.
3. Обновить `agent-workflow-router`, чтобы он направлял повторяющиеся check-fix-check задачи в `agent-loops`.
4. Проверить наличие `SKILL.md` и маршрута.

## Что сделано

- Создан новый skill `agent-loops` в:
  - `C:\Users\koval\.codex\skills\agent-loops\SKILL.md`
  - `C:\Users\koval\.agents\skills\agent-loops\SKILL.md`
  - `C:\Users\koval\.claude\skills\agent-loops\SKILL.md`
  - `C:\Users\koval\Documents\Codex\2026-05-18\npx-skills-add-anthropics-claude-code\agent-skills\agent-loops\SKILL.md`
- Skill описывает безопасные bounded loops:
  - `verify`
  - `ci-until-green`
  - `post-edit-tests`
  - `docs-sync`
  - `security-audit`
  - `deploy-smoke`
- Обновлены все четыре копии `agent-workflow-router\SKILL.md`:
  - description теперь упоминает loops/repeated verification;
  - route table добавляет строку для repeated check-fix-check work;
  - добавлен раздел `Agent Loops Route Detail`.

## Проверки

- Проверено, что все четыре `agent-loops\SKILL.md` существуют и не пустые.
- Проверено, что все четыре router-файла содержат `agent-loops` и раздел `Agent Loops Route Detail`.

## Риски и ограничения

- Сторонние hook bundles с loops.elorm.xyz не устанавливались намеренно. Используется безопасная локальная инструкция, а project hooks можно ставить отдельно только после просмотра файлов и явного решения пользователя.
- Benchmark/eval viewer для skill не запускался, потому что задача была практической установкой локального workflow skill; выполнена файловая валидация.

## Следующий агент

При задачах вида "доведи CI до зеленого", "проверь после правок", "обнови доки после изменений", "проверь деплой" или "security loop" сначала использовать `agent-workflow-router`, затем `agent-loops` и доменный skill по задаче.
