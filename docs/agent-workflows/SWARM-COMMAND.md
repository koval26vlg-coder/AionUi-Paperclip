# Команда запуска роя агентов

Цель: запускать иерархический workflow одной понятной фразой, без ручного вспоминания всех уровней, файлов и команд.

Это не "один запрос во все модели". Команда создает управляемую задачу в `docs/agent-workflows/`, где агенты идут по уровням, читают общий brief, пишут handoff и не искажают результат.

## Чат-триггер

В любом чате с Codex можно писать:

```text
Рой: <задача>
Рой, <задача>
РОЙ: <задача>
РОЙ, <задача>
рой: <задача>
```

Регистр слова `Рой` не важен; команда `РОЙ` означает тот же запуск workflow.

Альтернативы:

```text
/swarm <задача>
Запусти рой: <задача>
Workflow: <задача>
```

Пример smoke-проверки распознавания:

```text
Рой, проверь задачу
```

Когда Codex видит такой триггер, он должен:

1. Выполнить Aion SML bootstrap.
2. Создать или продолжить workflow через `tools/agent_workflow.py`.
3. Зафиксировать исходную постановку в `brief.md` без пересказа "по памяти".
4. Проверить risk flags: `trading`, `writes_external_system`, `long_running`, `uses_secrets`, `destructive`.
5. Показать `workflow_id`, текущий уровень и кто ходит следующим.
6. Дальше вести задачу по цепочке `Grok Build L1 -> Antigravity CLI L2 -> Codex L3 -> Codex L4 -> Claude Code L5`. `Antigravity CLI L1/L2` оставить как явный профиль `--profile antigravity` / `-Profile antigravity`, `Gemini Vertex L1/L2` оставить как резервный профиль `--profile gemini-vertex` / `-Profile gemini-vertex`, старую цепочку `Grok Build L1 -> Gemini Vertex L2 -> Codex L3/L4 -> Claude Code L5` запускать только явно через `--profile grok-gemini` / `-Profile grok-gemini`.

## Терминальная команда

Из `D:\AionUi-Paperclip`:

```powershell
.\START-AGENT-SWARM.cmd -Title "Проверить идею продукта" -Brief "Нужно оценить спрос, риски, MVP и план проверки."
```

То же напрямую через PowerShell:

```powershell
& "D:\AionUi-Paperclip\tools\start-agent-swarm.ps1" -Title "Проверить идею продукта" -Brief "Нужно оценить спрос, риски, MVP и план проверки."
```

Резервный профиль Gemini Vertex:

```powershell
& "D:\AionUi-Paperclip\tools\start-agent-swarm.ps1" -Title "Проверить идею продукта" -Brief "..." -Profile gemini-vertex
```

Явный профиль без Grok:

```powershell
& "D:\AionUi-Paperclip\tools\start-agent-swarm.ps1" -Title "Проверить идею продукта" -Brief "..." -Profile antigravity
```

Legacy-профиль Grok -> Gemini:

```powershell
& "D:\AionUi-Paperclip\tools\start-agent-swarm.ps1" -Title "Проверить идею продукта" -Brief "..." -Profile grok-gemini
```

Dry-run без создания workflow:

```powershell
& "D:\AionUi-Paperclip\tools\start-agent-swarm.ps1" -Title "Проверка команды роя" -Brief "Тест запуска." -DryRun
```

С risk flags:

```powershell
& "D:\AionUi-Paperclip\tools\start-agent-swarm.ps1" -Title "Автоматизация внешней записи" -Brief "..." -RiskWritesExternalSystem -RiskLongRunning
```

Открыть видимый monitor после создания:

```powershell
& "D:\AionUi-Paperclip\tools\start-agent-swarm.ps1" -Title "..." -Brief "..." -OpenMonitor -Watch
```

Создать workflow и сразу выполнить первый шаг L1 в той же консоли:

```powershell
& "D:\AionUi-Paperclip\tools\start-agent-swarm.ps1" -Title "..." -Brief "..." -RunNext
```

Выполнить следующий шаг уже созданного workflow:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\AionUi-Paperclip\tools\run-agent-workflow-next.ps1 -Root D:\AionUi-Paperclip\docs\agent-workflows -WorkflowId <workflow-id>
```

## Что команда делает

- Создает новый workflow через `tools/agent_workflow.py new`.
- Записывает `contract.json`, `brief.md`, `handoff.md`, `events.jsonl`.
- Стартует с `current_level=L1`, `workflow_profile="grok-antigravity"`, `allowed_next_agents=["Grok Build"]` по умолчанию.
- Печатает status command, monitor command и `Run L1` command.
- Если указан `-RunNext`, выполняет первый шаг текущего уровня в этой же консоли через `tools/run-agent-workflow-next.ps1`.
- Не запускает долгие процессы скрыто.
- Не пишет во внешние системы без risk gate и явного подтверждения пользователя.

## Что команда не делает

- Не запускает все модели параллельно.
- Не прогоняет всю цепочку L1-L5 одним скрытым вызовом.
- Не обходит `allowed_next_agents`.
- Не делает Gemini Vertex, Antigravity или Grok Build владельцем workflow-state: они остаются review-only, state mutations делает Codex/Claude как trusted executor.
- Не считает задачу завершенной без `final-report.md` и проверки всех gates.

## Быстрое правило

Если задача обычная и не требует роя, не использовать workflow.

Если задача сложная, многошаговая, рискованная, требует проверки несколькими агентами или пользователь написал `Рой:`, использовать workflow.
