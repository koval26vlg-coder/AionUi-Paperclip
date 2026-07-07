# Реестр агентов

Этот файл описывает агентов, которых можно подключать к общей системе.

## Активная связка

Активная рабочая связка — Grok Build + Antigravity CLI + Codex + Claude Code. По решению пользователя от 2026-07-07 дефолтный `Рой` идет через `grok-antigravity`: `L1 Grok Build -> L2 Antigravity CLI -> L3 Codex -> L4 Codex -> L5 Claude Code`. Gemini Vertex сохранен как резервный profile `gemini-vertex` после успешной Vertex AI проверки. Агенты взаимозаменяемы: видят общий контекст через SML, документы и context-pack, проверяют работу друг друга.

| Агент | Роль | Статус | Главный вход в контекст |
| --- | --- | --- | --- |
| Grok Build 0.2.87 | Дефолтный `L1`: SML bootstrap, первичная постановка задачи, разведка контекста, source scout и L1-handoff для Antigravity CLI | Активен как дефолтный первый уровень `Рой`; live runtime подтвержден 2026-07-06 | `tools/grok_build_workflow_review.py`, `AGENTS.md`, `.grok/config.toml`, SML bootstrap, MCP `sml`, `docs/agent-log/` |
| Codex | `L3` декомпозиция/тесты/automation и `L4` архитектурный синтез; также инженерная реализация, анализ, ревью, автоматизации | Активен | `C:\Users\koval\.codex\AGENTS.md`, skill `sml-memory-bootstrap`, `AGENTS.md`, SML |
| Claude Code | `L5` финальная инстанция: независимая техпроверка, anti-distortion audit и final-report для пользователя | Активен | `C:\Users\koval\.claude\CLAUDE.md`, `CLAUDE.md`, user/project MCP `sml` |
| Antigravity CLI | Дефолтный `L2`; независимое ревью через `agy`, engineering review и revision gate; также явный profile `antigravity` без Grok | Активен | `agy`, `tools/antigravity_workflow_review.py`, `AGENTS.md`, `docs/agent-workflows/`, SML bootstrap |
| Gemini Vertex | Резервный `L1/L2` fallback; анализ контекста, независимое ревью, альтернативное мнение через Vertex AI | Доступен через явный `-Profile gemini-vertex` | `tools/gemini_vertex_workflow_review.py`, Google ADC, `AGENTS.md`, `docs/agent-workflows/`, SML bootstrap |

## Экспериментальные профили и резерв

| Агент | Возможная роль | Статус | Главный вход в контекст |
| --- | --- | --- | --- |
| Grok Build 0.2.87 | `L1` в legacy profile `grok-gemini`: L1-handoff для Gemini Vertex | Подтвержден live runtime 2026-07-06: `grok 0.2.87`, auth `grok.com`, модель `grok-build`, MCP `sml` через `sml_*` alias, L1 runner smoke OK | `tools/grok_build_workflow_review.py`, `AGENTS.md`, `.grok/config.toml`, SML bootstrap, MCP `sml`, `docs/agent-log/` |

## Рабочие оболочки

| Оболочка | Роль | Статус | Главный вход в контекст |
| --- | --- | --- | --- |
| VS Code | Общая IDE-оболочка для SML, документов, терминалов и задач проверки | Активна | `docs/vscode-sml.md`, `.vscode/tasks.json`, `AGENTS.md` |

## Выведены из схемы

Cursor, Kiro, Gemini CLI, MiMo AUTO и проектный MiMo Code больше не входят в систему. Их активные конфиги (`.cursor/`, `.kiro/`, `.mimocode/`, `.gemini/`) и запускатели (`OPEN-KIRO-RU.cmd`, `OPEN-MIMO-SML.cmd`, `CHECK-MIMO-SML.cmd`, `OPEN-GEMINI-SML.cmd`, `CHECK-GEMINI-SML.cmd`) удалены, чтобы не создавать путаницу в активной схеме.

Решение 2026-06-24: исключение для `MiMo AUTO L1.0` отменено, потому что пользователь решил убрать MiMo перед переходом на платный режим с 2026-06-25. Старые workflow с MiMo остаются историей и не являются шаблоном для новых задач.

Историческая память об их работе сохранена: записи этих инструментов остаются в SML и `docs/agent-log/` как контекст, а ценные спецификации из бывшего `.kiro/specs/` перенесены в `docs/specs/` (в т.ч. спецификация ядра SML `agents-shared-memory-layer`).

Вернуть любой из этих инструментов можно только по отдельному решению пользователя.

## Условия добавления нового агента

Нового агента можно добавить, если он умеет:

- читать файлы в рабочей папке;
- писать файлы в `docs/`;
- выполнять инструкции из `AGENTS.md`;
- оставлять отчет после работы.

Если агент не умеет писать файлы, он все равно может быть полезен как советник, но его вывод нужно вручную перенести в `docs/agent-log/`.

## Универсальная фраза для подключения нового агента

```text
Перед задачей подтяни общую память командой: `& "D:\AionUi-Paperclip\tools\agent-memory-bootstrap.ps1" -Agent "<имя агента>" -Query "<тема>"`. Затем учитывай `D:\AionUi-Paperclip\docs\agent-memory-bootstrap.md`, `AGENTS.md`, `docs/context-packs/context-pack-latest.md`, `docs/current-context.md`, `docs/tasks.md`, `docs/decisions.md` и последние записи `docs/agent-log`. Если доступен MCP-сервер `sml`, вызови `sml.startup_pack` и `sml.semantic_query`. Работай на русском языке. После работы оставь отчет в `docs/agent-log` и обнови общий контекст.
```
