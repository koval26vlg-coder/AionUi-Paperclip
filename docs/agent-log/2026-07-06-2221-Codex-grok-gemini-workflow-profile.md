# 2026-07-06 22:21 +03:00 — Codex — профиль Роя Grok -> Gemini -> Codex -> Claude

## Исходный запрос пользователя

Пользователь попросил не заменять существующих агентов Grok, а сделать его самым нижним уровнем в `Рое` с набором субагентов: первый уровень Grok, затем Gemini, затем Codex и последний Claude.

## Краткий план

- Проверить текущую реализацию workflow-профилей.
- Добавить отдельный профиль без поломки дефолтного `antigravity`.
- Дать Grok собственные L1-субагенты.
- Добавить runner для headless review-only вызова Grok.
- Обновить документы памяти и проверить dry-run/тесты.

## Что сделано

- Добавлен workflow profile `grok-gemini`.
- Цепочка профиля: `L1 Grok Build -> L2 Gemini Vertex -> L3 Codex -> L4 Codex -> L5 Claude Code`.
- Добавлены L1-субагенты Grok:
  - `grok-memory-bootstrapper`;
  - `grok-problem-framer`;
  - `grok-source-scout`;
  - `grok-handoff-editor`.
- `Grok Build` добавлен в review-only mutation agents: менять workflow state он может только через trusted executor `Codex` или `Claude Code`.
- Добавлен `tools/grok_build_workflow_review.py`, который запускает Grok в изолированном review-only packet режиме через `grok --no-auto-update -p`.
- `tools/start-agent-swarm.ps1` теперь принимает `-Profile grok-gemini`.

## Измененные файлы

- `tools/agent_workflow.py`
- `tools/start-agent-swarm.ps1`
- `tools/grok_build_workflow_review.py`
- `tools/sml/tests/test_agent_workflow.py`
- `tools/sml/tests/test_grok_build_workflow_review.py`
- `AGENTS.md`
- `docs/agents.md`
- `docs/agent-workflows/README.md`
- `docs/agent-workflows/SWARM-COMMAND.md`
- `docs/agent-workflows/model-policy.md`
- `docs/tasks.md`
- `docs/current-context.md`
- `docs/decisions.md`
- `docs/agent-log/2026-07-06-2221-Codex-grok-gemini-workflow-profile.md`

## Проверки выполнены

- `python -X utf8 -m pytest tools/sml/tests/test_agent_workflow.py tools/sml/tests/test_grok_build_workflow_review.py -q` — `17 passed`.
- `python -X utf8 -m py_compile tools/agent_workflow.py tools/grok_build_workflow_review.py` — успешно.
- `tools/start-agent-swarm.ps1 -Title "Тест Grok Gemini профиля" -Brief "Проверить создание профиля Grok Gemini без запуска моделей." -Profile grok-gemini -DryRun` — успешно; команда показала `Profile : grok-gemini` и корректный create command.
- `python -X utf8 -m tools.sml.core selfcheck` — `sml-selfcheck-ok`.
- `tools/build-context-pack.ps1` — context-pack пересобран вручную.
- `tools/build-relationship-map.ps1` — relationship-map пересобрана вручную.
- `query-relationship-map.py "grok-gemini Grok Gemini Codex Claude"` — находит `grok-gemini`, `--profile grok-gemini`, `grok-memory-bootstrapper` и этот agent-log.
- `Get-Command grok` — команда все еще не найдена в PATH.

## Риски и ограничения

- Superseded 2026-07-06 22:59 +03: локальный Grok runtime подтвержден в `docs/agent-log/2026-07-06-2259-Codex-grok-runtime-sml-smoke.md`.
- На момент этой записи live gate по Grok еще ожидал отдельной проверки PATH/auth/smoke; актуальный статус см. в новом логе 22:59.
- `grok-gemini` не сделан дефолтным профилем, чтобы не сломать обычный `Рой`.
- Перед живым использованием нужно пройти gate: `grok version`, auth, `grok inspect`, короткий smoke на русском из `D:\AionUi-Paperclip`.

## Что должен проверить следующий агент

- Superseded 2026-07-06 22:59 +03: установка/auth/smoke выполнены; смотреть `docs/agent-log/2026-07-06-2259-Codex-grok-runtime-sml-smoke.md`.
- После установки/auth Grok выполнить live smoke `tools/grok_build_workflow_review.py` на тестовом workflow.
- Если smoke успешен, решить с пользователем, оставлять `grok-gemini` явным профилем или делать его дефолтным.
