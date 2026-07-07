## Итог

Цепочка L1→L4 непротиворечива и сходится к единому verdict `approve`. Все уровни корректно фиксируют исходное состояние цели `trading_mvp` (research-only edge на non-Binance markets):

- funding-датасет `funding_collect_7d_spotliq_visible_20260617_185732` **отвергнут** data-quality guard (`min_rows_per_cycle=9 < 20`, `ok=false`, `not_ready_for_postprocess`) — никакой rank/backtest/paper-forward по нему не предлагается;
- next branch правильно переключён на `SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT`, а не на funding postprocess;
- первичный шаг — только `start_ws_collect_visible.ps1 -Hours 6 -PlanOnly` (PlanOnly вернул `would_start=false`, `requires_confirmed_long_run=true`);
- post-collect цепочка выражена явно: active-run gate → guarded WS postprocess на exact manifest → replay-validation PlanOnly с `-ExpectedManifestPath` → `-ConfirmedResearchRun` только после прохождения data-quality gate и явного review;
- L3 подтверждён прогонами (preflight `READY_FOR_EDGE_PROOF_STEP`, acceptance gate `research_only_no_accepted_strategy`, tests `198 OK`), L4 закрыл архитектурный/risk gate.

Все критичные правила соблюдены: нет live orders, API keys, leverage/margin, инвестсоветов; long-run требует видимого терминала и явного подтверждения.

## Проверка искажения

Искажения цели или подмены verdict между уровнями **не обнаружено**. Контрольные факты сохранены сквозь все уровни без дрейфа:

- funding rejection не «потерян» и нигде не переинтерпретирован как годный датасет;
- старый gate-status `READY_FOR_POSTPROCESS` корректно помечен как относящийся к отвергнутому funding run и не используется как разрешение (L4 явно даёт приоритет next-goal logic + guard artifact над строкой `next_step_after_ready`);
- ни на одном уровне нет скрытого повышения шага до фактического collect/replay/grid/postprocess;
- предыдущий workflow без risk-флагов (`2026-06-27-124834-...`) корректно исключён как источник решения.

Замечания (не блокеры, влияют на качество, а не на корректность):
- **L1 и L2 идентичны почти дословно** — L2 не добавил независимой ценности, фактически дублирует L1. Это снижает реальную глубину независимой перекрёстной проверки, но не искажает вывод.
- L3 отметил ~20s overhead PlanOnly из-за `trading_next_goal_step.ps1` — честно зафиксировано как UX-, а не safety-вопрос.

## Допустимый следующий шаг

Единственный разрешённый следующий шаг для Codex — **PlanOnly-превью без запуска долгого прогона**:

```
pwsh -NoProfile -ExecutionPolicy Bypass -File tools\start_ws_collect_visible.ps1 -Hours 6 -PlanOnly
```

(предварительно — `tools\check_active_run_gate.ps1`).

Далее строго по цепочке и только при явном подтверждении пользователя:
1. фактический 6h WS collect — **только в видимом терминале и только после явного `-ConfirmedLongRun`/подтверждения пользователя**;
2. после завершения — `run_ws_postprocess_visible.ps1` (guarded) на exact completed manifest;
3. `run_ws_replay_validation_visible.ps1 -PlanOnly -PostprocessPath <...> -ExpectedManifestPath <тот же manifest>`;
4. фактический replay/grid — только при `replay_allowed=true` после data-quality acceptance и отдельном `-ConfirmedResearchRun` с human review.

## Блокировки

- Запрет на старт нового long collector/backtest/replay/grid/paper-forward без явного подтверждения пользователя и видимого терминала.
- Funding 7d dataset остаётся заблокирован; rank/backtest/paper-forward по нему запрещены.
- Перед каждым шагом обязателен `check_active_run_gate.ps1`; при статусе `RUNNING` — только status/ETA.
- После нового WS collect необходимо убедиться, что active-run gate перезаписан WS-метаданными и не ссылается на старый funding run.
- Winrate не оптимизировать в отрыве от expectancy / net PnL after costs / PF / drawdown / sample size / liquidity-fill risk / OOS.
- Нет live orders, API keys, leverage/margin, инвестсоветов, внешних media/channel/P2P/off-ramp/custody/legal входов.

## Решение

approve

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
