# Final Report: Drift Workflow Control

## Решение

approve

Прототип можно считать рабочим для текущего этапа: `Drift Workflow Control` показывает иерархический workflow как drift-arena, не мутирует состояние из UI и сохраняет цепочку `brief -> handoff -> events -> final-report`.

## Проверено

- L1.0/L1.1/L2/L3/L4 прошли через `tools/agent_workflow.py`, а не через ручное продвижение `contract.json`.
- После замечания пользователя car policy исправлена: `L1.0` = tuned kei scout, `L1.1` = Toyota AE86 Trueno, `L2` = Nissan 180SX Type X, `L3` = Toyota Chaser JZX100, `L4` = Nissan Silvia S15, `L5` = Toyota Supra A80.
- Dashboard оставлен read-only: управление workflow остается в CLI, визуализация только отображает состояние.
- Убраны декоративные fake charts; оставлены arena, компактные markers, реальные workflow-метрики, handoff/audit и limits/usage panel с честным `unknown`, где нет источника данных.
- Проверки пройдены: `npm run lint`, `npm run build`, `python -m pytest tools/sml/tests/test_agent_workflow.py` = 10 passed.

## Что нельзя исказить

- Это не схема "один запрос в несколько моделей". Это последовательная иерархия отделов, где каждый уровень принимает handoff предыдущего уровня и фиксирует свое решение.
- `Drift Workflow Control` не переводить.
- Имена агентов, моделей и car policy не переименовывать без нового решения пользователя.
- Не возвращать большие overlay-плашки поверх машин и не добавлять бессмысленные графики без чисел и источников.
- Не утверждать, что fixture является live adapter: текущие данные dashboard еще статические.

## Остаточные риски

- `DRIFT_WORKFLOW_SNAPSHOT` пока fixture, поэтому следующий технический этап должен подключить read-only adapter к `contract.json`, `events.jsonl`, handoff и usage snapshots.
- PNG arena asset является прототипной технической заменой, а не полноценным фотореалистичным inpaint. Для production лучше сгенерировать новый цельный render или вынести роли в аккуратный canvas/WebGL слой.
- Claude Code runtime не прошел стабильный L5 smoke-test в этой итерации: одна попытка была остановлена бюджетом `$0.30`, короткая попытка `haiku` завершилась timeout за 124 секунды. Поэтому L5 фиксируется как `Claude Code` по контракту, но с `executor=Codex` и runtime/cost constraint в отчете.
- Vite build проходит, но оставляет warning о крупном chunk. Для прототипа это не блокер.

## Следующий шаг

Следующий полезный шаг: заменить fixture на live read-only adapter, чтобы dashboard показывал текущий workflow напрямую из файлов `docs/agent-workflows/<workflow>/contract.json`, `events.jsonl`, последнего `handoff.md` и `docs/agent-limits/limits-config.json`.

## История прохождения уровней

- L1 Нижний авто-уровень и исследовательский отдел: status=approved, agent=Antigravity CLI, handoff=levels/L1/L1.1/handoff.md
  - L1.0 AUTO-первичная разведка: status=approved, agent=MiMo AUTO, mode=AUTO, handoff=levels/L1/L1.0/handoff.md
    - subagent mimo-intake-scanner: Сканер постановки - Вытащить исходную цель, ограничения, входные данные и явные критерии успеха. [MiMo AUTO / AUTO / Xiaomi API AUTO]
    - subagent mimo-hypothesis-generator: Генератор первичных гипотез - Дать быстрые варианты решения, не выдавая их за проверенные выводы. [MiMo AUTO / AUTO / Xiaomi API AUTO]
    - subagent mimo-risk-sentinel: Сигнальщик очевидных рисков - Отметить пробелы, противоречия, опасные допущения и что нельзя потерять дальше. [MiMo AUTO / AUTO / Xiaomi API AUTO]
  - L1.1 Исследовательский lead: status=approved, agent=Antigravity CLI, mode=reviewed, handoff=levels/L1/L1.1/handoff.md
    - subagent antigravity-source-verifier: Проверяющий фактов - Сверить тезисы MiMo с brief, handoff, событиями и доступными источниками. [Antigravity CLI AUTO / High]
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
