# 2026-07-03 11:55 +03 - Codex - Antigravity access and RОЙ workflow check

## Исходный запрос
Пользователь попросил проверить доступ к Antigravity, проверить корректировки и настроить workflow с командой `РОЙ`.

## Краткий план
- Подтянуть SML-контекст и правила workflow-router.
- Проверить локальный `agy` и wrapper `tools/antigravity_print.py`.
- Проверить создание workflow через `tools/start-agent-swarm.ps1`.
- Проверить optional `antigravity` profile через isolated runner.
- Обновить stale-документы и глобальные правила Codex/Claude.

## Что было сделано
- Выполнен Aion SML bootstrap по теме `Antigravity доступ workflow команда РОЙ`.
- Прочитан skill `agent-workflow-router`.
- Подтвержден `agy.exe`: `C:\Users\koval\AppData\Local\agy\bin\agy.exe`.
- `tools/check-agent-runtimes.ps1` видит `cmd`, `where`, `node`, `npm`, `claude`, `agy`.
- `tools/antigravity_print.py --process-timeout-seconds 90 "Ответь ровно одним словом: OK"` вернул `OK`.
- Создан temp workflow default profile: `tmp/swarm-command-smoke/2026-07-03-114824-153545-рой-smoke-default`, статус `workflow_profile=gemini-vertex`, `current_level=L1`, `allowed_next_agents=["Gemini Vertex"]`.
- Создан temp workflow optional profile: `tmp/swarm-antigravity-smoke/2026-07-03-114820-511481-antigravity-profile-smoke`, статус `workflow_profile=antigravity`, `allowed_next_agents=["Antigravity CLI"]`.
- `tools/antigravity_workflow_review.py` на optional profile вернул валидный L1 handoff с `## Решение approve`.
- Команда `РОЙ` закреплена как case-insensitive alias рядом с `Рой`.

## Измененные файлы
- `AGENTS.md`
- `docs/agent-workflows/SWARM-COMMAND.md`
- `docs/agent-workflows/README.md`
- `docs/agents.md`
- `docs/agent-memory-bootstrap.md`
- `docs/current-context.md`
- `docs/decisions.md`
- `docs/memory/layers/constraints.md`
- `docs/context-packs/context-pack-latest.md`
- `tools/start-agent-swarm.ps1`
- `C:\Users\koval\.codex\AGENTS.md`
- `C:\Users\koval\.claude\CLAUDE.md`

## Проверки
- `python -m pytest tools/sml/tests/test_agent_workflow.py tools/sml/tests/test_antigravity_print.py tools/sml/tests/test_antigravity_workflow_review.py tools/sml/tests/test_gemini_vertex_workflow_review.py tools/sml/tests/test_agent_limit_monitor.py -q` -> 28 passed.
- `tools/start-agent-swarm.ps1 -Title "РОЙ trigger verification" -Brief "..." -DryRun` показывает примеры `Рой:` и `РОЙ,` и не создает workflow.
- `rg` по stale-формулировкам `новые workflow стартуют с L1 Antigravity`, `blocked для L1/L2`, `не считать надежным L1/L2` в активных правилах после пересборки context-pack не нашел актуальных совпадений.

## Риски и ограничения
- Antigravity доступен сейчас, но остается optional profile, не дефолтным runtime. Причина: дефолтный `gemini-vertex` стабильнее для `Рой`, имеет usage log и не зависит от Antigravity stdout/DB quirks.
- Raw `agy --print` не использовать как workflow-контроль. Для handoff применять только `tools/antigravity_workflow_review.py`, затем Codex выполняет state mutation через `--executor Codex`.
- Numeric token usage/remaining/reset для Antigravity локально не найден; монитор видит только conversation DB и quota refresh events.

## Следующий агент
Для обычного запуска пользователь пишет `РОЙ: <задача>` или `Рой: <задача>`. Codex должен создать workflow через `tools/start-agent-swarm.ps1` с дефолтом `-Profile gemini-vertex`. Для Antigravity L1/L2 нужен явный `-Profile antigravity`.
