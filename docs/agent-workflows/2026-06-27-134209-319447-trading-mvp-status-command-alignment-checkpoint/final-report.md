## Что было сделано

В `tools/trading_goal_status.ps1` и `tools/trading_next_goal_step.ps1` устранена ситуация, при которой легаси-алиас `visible_collect_command` указывал на funding-сбор, пока `funding_blocked_by_swarm=true`. Добавлены явные поля `visible_collect_command_legacy_resolution` и `visible_collect_legacy_resolution` с маркером `redirected_to_ws_collect_because_funding_blocked_by_swarm`. Funding-команды сохранены как отдельные non-primary поля (`funding_visible_collect_command`, `funding_visible_collect_after_approval`). Добавлен тест `test_visible_ws_collect_wrapper.py`.

## На чём основан вывод

- L1–L4 Antigravity/Codex цепочка: все уровни выдали `approve` с одинаковой мотивацией — risk — это был живой alias на заблокированный путь.
- Верификация выводов `trading_goal_status.ps1 -Json`, `trading_next_goal_step.ps1 -Json`, `trading_edge_preflight.ps1 -Json` и `start_ws_collect_visible.ps1 -Hours 6 -PlanOnly` даёт согласованный результат.
- 204 теста пройдено, `fail_count=0`, `warn_count=0`.

## Что получилось хорошо

- Легаси-алиас теперь детерминированно resolves в WS-коллект, а не в заблокированный funding путь — источник путаницы устранён.
- Funding-команды не удалены: они доступны как явные non-primary поля, что позволяет при необходимости разблокировать ветку без правок кода.
- `start_ws_collect_visible.ps1 -PlanOnly` подтверждает, что реальный запуск по-прежнему требует `-ConfirmedLongRun` — gate не ослаблен.
- Preflight остаётся на `ok=true` без новых предупреждений.

## Что требует доработки

- Нет критических gap. Единственное условие перехода к реальному 6h WS collect — явное подтверждение пользователя (`-ConfirmedLongRun`) с видимым терминалом/монитором. Это не баг реализации, а намеренный policy-барьер.

## Какие есть риски

- **Минимальные процедурные.** Если `funding_blocked_by_swarm` будет снят без прохождения `data_quality:min_min_rows_per_cycle` (min_rows_per_cycle=9), легаси-алиас автоматически вернётся к funding-пути — это ожидаемо, но нужно отслеживать при любом ручном изменении gate.
- Реальных торговых рисков нет: ни ордеров, ни ключей API, ни плеча в цепочке нет.

## Что нельзя потерять/исказить дальше

- Маркер `funding_blocked_by_swarm=true` должен остаться в gate до явного прохождения `data_quality` guard.
- `funding_visible_collect_command` должен сохраняться как отдельное поле — это единственный путь вернуть funding ветку без хардкодинга.
- `requires_confirmed_long_run=true` в `start_ws_collect_visible.ps1` не трогать без явного решения уровня L2+.

## Решение

**approve**

## История прохождения уровней

- L1 Исследовательский отдел: status=approved, agent=Antigravity CLI, handoff=levels/L1/handoff.md
  - subagent antigravity-source-verifier: Проверяющий фактов - Сверить brief, handoff, события и доступные источники перед передачей на инженерную проверку. [Antigravity CLI AUTO / High]
  - subagent antigravity-context-expander: Расширитель контекста - Добавить недостающие альтернативы, ограничения, зависимости и edge cases. [Antigravity CLI AUTO / Low]
  - subagent antigravity-noise-filter: Фильтр шума - Убрать неподтвержденные или лишние идеи, чтобы L1 не передал искажение выше. [Antigravity CLI AUTO / Low]
  - subagent antigravity-handoff-editor: Редактор L1-handoff - Собрать проверенный handoff с явным решением approve/revise/escalate/block. [Antigravity CLI AUTO / Medium]
- L2 Инженерная проверка: status=approved, agent=Antigravity CLI, handoff=levels/L2/handoff.md
  - subagent antigravity-engineering-reviewer: Инженерный ревьюер - Проверить применимость L1-выводов к реальной реализации. [Antigravity CLI AUTO / High]
  - subagent antigravity-constraint-checker: Проверяющий ограничений - Сверить решение с brief, контрактом, risk flags, allowed_next_agents и контекстными лимитами. [Antigravity CLI AUTO / High]
  - subagent antigravity-edge-case-scout: Разведчик крайних случаев - Найти скрытые сценарии, неполные данные, конфликтующие требования и слабые места. [Antigravity CLI AUTO / High]
  - subagent antigravity-revision-gate: Gate ревизии - Решить, можно ли передавать работу на Codex L3 или нужно вернуть на доработку. [Antigravity CLI AUTO / High]
- L3 Декомпозиция реализации, тесты и automation: status=approved, agent=Codex, handoff=levels/L3/handoff.md
  - subagent codex-implementation-decomposer: Декомпозитор реализации - Разбить задачу на исполнимые шаги, файлы, интерфейсы и критерии готовности. [codex-5.3 / xhigh]
  - subagent codex-test-planner: Планировщик тестов - Определить unit/smoke/integration проверки и негативные сценарии. [gpt-5.5 / xhigh]
  - subagent codex-automation-builder: Инженер automation - Предложить или реализовать CLI/скрипты/мониторы для повторяемого выполнения. [gpt-5.4 mini / xhigh]
  - subagent codex-integration-checker: Проверяющий интеграции - Проверить совместимость с существующей структурой, SML, файлами памяти и политиками запуска. [gpt-5.4 / xhigh]
- L4 Архитектурный синтез: status=approved, agent=Codex, handoff=levels/L4/handoff.md
  - subagent codex-architecture-synthesizer: Архитектурный синтезатор - Собрать L1-L3 в целостное техническое решение без противоречий. [gpt-5.5 / xhigh]
  - subagent codex-contract-auditor: Аудитор контракта - Проверить, что contract, handoff, events и итоговые выводы согласованы. [gpt-5.5 / xhigh]
  - subagent codex-risk-gate: Risk gate - Отдельно оценить риски trading/long-running/secrets/external writes/destructive действий. [gpt-5.5 / xhigh]
  - subagent codex-maintainability-reviewer: Ревьюер сопровождения - Оценить простоту поддержки, расширения и передачи следующему агенту. [gpt-5.5 / xhigh]
- L5 Финальная инстанция для пользователя: status=approved, agent=Claude Code, handoff=final-report.md
  - subagent claude-executive-summarizer: Executive summarizer - Сжато объяснить пользователю итог, решение и оставшиеся риски. [Claude Opus 4.7 alias / xhigh]
  - subagent claude-technical-verifier: Финальный техпроверяющий - Независимо проверить техническую связность L1-L4 перед финальным отчетом. [Claude Haiku 4.5 alias / xhigh]
  - subagent claude-anti-distortion-auditor: Аудитор против искажения - Сверить final-report с brief, handoff и events, чтобы не было испорченного телефона. [Claude Sonnet 4.6 alias / xhigh]
  - subagent claude-final-decision-writer: Автор заключения - Сформировать final-report.md для пользователя с понятным решением approve/revise/escalate/block. [Claude Opus 4.8 alias / xhigh]
