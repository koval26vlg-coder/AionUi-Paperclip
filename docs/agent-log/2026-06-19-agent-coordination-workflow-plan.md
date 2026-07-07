# 2026-06-19 - План связанной схемы агентов

## Запрос
Пользователь спросил, как реализовать рабочую схему, где Codex, Claude Code и Gemini CLI взаимосвязаны, ждут ответов друг друга и не продолжают работу без нужного решения/проверки.

## Сделано
- Проверен active-run gate: долгий сбор `funding_collect_7d_spotliq_visible_20260617_185732` все еще `RUNNING`, поэтому инженерные шаги по trading_mvp не запускались.
- Подтянут SML/context bootstrap по теме координации агентов.
- Создан план внедрения: `D:\AionUi-Paperclip\docs\plans\2026-06-19-agent-coordination-workflow.md`.
- Схема основана на общем workflow-контракте, state machine, required gates, allowed_next_agents и event log.

## Ключевое решение
Начинать не с OpenClaw-first, а с локального координатора поверх уже активной связки `Codex + Claude Code + Gemini CLI`:

- Codex: исполнитель, интегратор, тесты, автоматизация.
- Gemini CLI: независимый large-context review и альтернативное мнение.
- Claude Code: архитектурный/лид-синтез и финальное решение по спорным изменениям.
- SML и файлы workflow: единый источник состояния, кто сейчас должен отвечать и какие gate уже закрыты.

## Следующие шаги
1. Реализовать Tasks 1-3 из плана: документация workflow, `tools/agent_workflow.py`, команды `new/claim/request-review/submit-review/approve/block/status`.
2. После MVP добавить видимый monitor-скрипт и VS Code task.
3. Для trading/collectors/backtests добавить обязательный risk gate и запрет live-money действий без явного решения пользователя.

## Риски
- Агент не должен "ждать" через скрытый фоновой процесс: ожидание должно быть явным состоянием workflow и видимым монитором.
- Нельзя давать всем агентам одинаковые права на запись/секреты/запуски. Нужны роли, gate и audit log.
