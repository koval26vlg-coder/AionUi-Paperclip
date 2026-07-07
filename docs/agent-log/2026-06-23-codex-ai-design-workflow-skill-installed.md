# 2026-06-23 - Codex - Установка ai-design-workflow skill

## Исходный запрос

Пользователь после изучения PDF `C:\Users\koval\Desktop\Дизайн нейросетью.pdf` попросил: "бери в работу".

## План

- Не менять сторонние vendor skills напрямую.
- Создать отдельный локальный skill `ai-design-workflow`.
- Установить его в Codex, Claude Code, `.agents` и общий `agent-skills`.
- Подключить skill к `agent-workflow-router` для UI/frontend задач.
- Обновить install manifest и проверить файлы.

## Что сделано

- Создан `ai-design-workflow/SKILL.md` в:
  - `C:\Users\koval\.codex\skills\ai-design-workflow`
  - `C:\Users\koval\.claude\skills\ai-design-workflow`
  - `C:\Users\koval\.agents\skills\ai-design-workflow`
  - `C:\Users\koval\Documents\Codex\2026-05-18\npx-skills-add-anthropics-claude-code\agent-skills\ai-design-workflow`
- Добавлены `metadata.json` и `evals/evals.json`.
- Обновлен `agent-workflow-router/SKILL.md` в четырех копиях, чтобы UI route использовал `ai-design-workflow`.
- Обновлены:
  - `agent-skills/INSTALL_MANIFEST.md`
  - `agent-skills/install-manifest.json`
- Перед изменением router-файлов созданы backup-копии с суффиксом `backup.20260623-185902`.

## Проверки

- `active-run-gate` проверен: `trading_mvp` остается `RUNNING`; эта работа не затрагивала проект.
- JSON-файлы `metadata.json`, `evals.json` и `install-manifest.json` успешно распарсены Python.
- `install-manifest.json` содержит `ai-design-workflow`.
- Четыре копии `SKILL.md` имеют одинаковый размер `6679` байт и SHA256 prefix `d9fdff4a8b8d4b0e`; `unique_hashes = 1`.
- `INSTALL_MANIFEST.md` содержит строку `ai-design-workflow` и `Last updated: 2026-06-23T18:59:00+03:00`.

## Риски и ограничения

- Скиллы в уже запущенных агентах могут подхватиться только после перезапуска Codex / Claude Code.
- Mobbin MCP не настраивался: skill только описывает, как использовать его при наличии доступа и ключа.
