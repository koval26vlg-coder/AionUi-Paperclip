# Отчет агента

## Дата и время

2026-06-23 16:51 +03

## Агент

Codex

## Исходный запрос пользователя

Пользователь спросил, можно ли придумать команду, чтобы чат понимал, что нужно запустить Codex и общий рой агентов, и запускать это одним написанием.

## Контекст перед началом

В проекте уже есть `tools/agent_workflow.py`, `docs/agent-workflows/`, `watch-agent-workflows.ps1`, модель уровней `MiMo AUTO L1.0 -> Antigravity CLI L1.1/L2 -> Codex L3/L4 -> Claude Code L5` и локальный `agent-workflow-router` skill. Не хватало короткого пользовательского триггера и терминального запускателя.

## План

1. Подтянуть Aion SML memory bootstrap и проверить active-run gate.
2. Проверить существующий workflow CLI и router skill.
3. Добавить короткий запускатель workflow.
4. Закрепить чат-триггеры в документации и глобальных правилах агентов.
5. Проверить dry-run, temp workflow creation и CMD wrapper.

## Что сделано

- Добавлен `tools/start-agent-swarm.ps1`.
- Добавлен корневой `START-AGENT-SWARM.cmd`.
- Добавлена документация `docs/agent-workflows/SWARM-COMMAND.md`.
- Обновлен `AGENTS.md`: триггеры `Рой:`, `/swarm`, `Запусти рой:`, `Workflow:`.
- Обновлен `docs/agent-workflows/README.md`.
- Обновлен глобальный `C:\Users\koval\.codex\AGENTS.md`.
- Обновлен глобальный `C:\Users\koval\.claude\CLAUDE.md`.
- Обновлены `docs/current-context.md`, `docs/tasks.md`, `docs/decisions.md`.

## Измененные файлы

- `tools/start-agent-swarm.ps1`
- `START-AGENT-SWARM.cmd`
- `docs/agent-workflows/SWARM-COMMAND.md`
- `AGENTS.md`
- `docs/agent-workflows/README.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/decisions.md`
- `docs/agent-log/2026-06-23-1651-codex-agent-swarm-trigger.md`
- `C:\Users\koval\.codex\AGENTS.md`
- `C:\Users\koval\.claude\CLAUDE.md`

## Проверки

- Windows PowerShell 5.1 parse:
  - `parse ok`
- Dry-run:
  - `start-agent-swarm.ps1 -Title "Проверка команды роя" -Brief "Тестовый dry-run запуска роя." -DryRun`
  - workflow не создан, команда `agent_workflow.py new` выведена корректно.
- Temp-root smoke creation:
  - workflow создан во временной папке;
  - `current_level=L1`;
  - `current_subrole=L1.0`;
  - `allowed_next_agents=MiMo AUTO`;
  - временная папка удалена после проверки.
- CMD wrapper:
  - `START-AGENT-SWARM.cmd -Title "CMD swarm smoke" -Brief "CMD wrapper dry run." -DryRun`
  - wrapper успешно вызвал PowerShell-скрипт.

## Решения

Официальный короткий чат-триггер: `Рой: <задача>`.

Терминальный запуск:

```powershell
.\START-AGENT-SWARM.cmd -Title "<название>" -Brief "<исходная задача>"
```

`/swarm` оставлен как ASCII-альтернатива для случаев, где кодировка терминала портит кириллицу.

## Риски и ограничения

- Команда создает workflow и запускает протокол, но не выполняет все уровни магически и не отправляет один prompt во все модели параллельно.
- Long-running, external-write, trading, secrets и destructive действия должны идти через risk flags и явное подтверждение пользователя.
- Antigravity остается review-only для state mutations: workflow-state должен менять trusted executor.

## Что должен проверить следующий агент

Если пользователь пишет `Рой: <задача>`, сразу использовать `tools/start-agent-swarm.ps1` или `tools/agent_workflow.py new`, показать `workflow_id` и вести работу через `contract.json`, `brief.md`, `handoff.md`, `events.jsonl`.
