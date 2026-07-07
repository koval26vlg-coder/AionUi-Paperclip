# L5 Final Review — trading_mvp / «используй Рой»

## Что проверено
- **Запрос пользователя**: «используй Рой» → корректно развернут в иерархический workflow `2026-06-27-113313-505601-trading-mvp-visible-ws-collect-checkpoint` с прохождением L1→L4, все вернули `approve`.
- **Соответствие цели**: следующий шаг = видимый 6h dense WS collect по MEXC/Gate для spot maker liquidity sweep reversal, а **не** postprocess / live / paper-forward / acceptance стратегии. Совпадает с заявленной целью (свежий независимый dataset после rejection старых данных).
- **Active Run Gate**: `READY_FOR_POSTPROCESS`, `funding_collect_7d_spotliq_visible_20260617_185732`, live PIDs нет. Запуск нового collect гейт не нарушает.
- **Visible Run Rule**: фактический long collect не запускался; `would_start=false`, `requires_confirmed_long_run=true`, `next_goal_decision=SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT`.
- **PlanOnly ↔ next_goal_step** согласованы (L3 устранил неоднозначную reason-строку; `block` относится к funding-carry branch, не к WS checkpoint).

## Подтвержден ли следующий шаг
**Да, но только как research-only data-collection step.** `approve` всех уровней относится к запуску видимого 6h collect **после явного approval пользователя**, а не к принятию торговой стратегии и не к postprocess старого funding-датасета.

## Ограничения, которые нельзя нарушать
- Research-only: no live orders, no API keys (с торговыми правами), no leverage/margin, no investment advice.
- Только spot-пары MEXC и Gate; visible-run на весь процесс; никаких скрытых фоновых долгих процессов.
- Нет channel/P2P/off-ramp/custody/legal анализа в рамках цели.
- Funding-carry branch остается заблокированной (нет fee-tier evidence) — это отдельная ветка, не смешивать.
- Старый `READY_FOR_POSTPROCESS` датасет не «протаскивать» как замену свежему collect; partial ≠ final.

## Что сделать дальше
1. Запускать видимый 6h collect **только** после явного «да» пользователя командой с `-ConfirmedLongRun` (из PlanOnly).
2. До/в момент запуска убедиться, что monitor показывает: elapsed, ETA, rows, per-exchange/per-symbol counts, last write age, reconnect/errors.
3. После collect — обязательные data-quality gates (coverage, gaps, stale, density, malformed) до любого postprocess/OOS; недостаточный dataset → `inconclusive/rejected`, без подгонки параметров.
4. Если лимиты Роя недоступны на следующем checkpoint — фиксировать `swarm_limited` и продолжать Codex вручную.

## Решение
**approve** — следующий шаг (видимый 6h WS collect после явного approval пользователя) корректен и безопасен; принятие стратегии не одобрено и остается под строгими OOS/walk-forward/stress/net-PnL/sample-size gates.

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
