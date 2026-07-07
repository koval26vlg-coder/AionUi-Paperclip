# Финальный отчет: sports-betting-automation-risk-bounded-workflow

## Executive Summary

Workflow завершает задачу как архитектуру безопасной аналитической системы для спортивных прогнозов и paper-trading. Скрытое размещение денежных ставок, browser auto-click, обход правил букмекерских контор, KYC, CAPTCHA, лимитов, anti-bot, мультиаккаунтинг и credential sharing остаются заблокированными.

Разрешенная зона:

- decision-support;
- paper trading;
- alerting;
- backtest;
- probabilistic modeling;
- EV scanner;
- bankroll/risk controls;
- read-only dashboard.

## Проверка источников и текущего контекста

- FIFA World Cup 2026 идет с 11 июня по 19 июля 2026: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026
- 244-ФЗ регулирует азартные игры и интерактивные ставки: https://pravo.gov.ru/proxy/ips/?docbody=&nd=102111150
- ФНС публикует реестры лицензий и официальных сайтов букмекерских контор/тотализаторов: https://www.nalog.gov.ru/rn77/related_activities/registries/licence/
- ЕРАИ - единый регулятор азартных игр: https://erai.ru/
- Единый ЦУПИС описывает идентификацию, платежи и responsible-game контур: https://1cupis.ru/
- ЦУПИС "Ответственная игра" позволяет настраивать лимиты или полностью запретить переводы букмекерам: https://1cupis.ru/info/help/usloviya-perevodov-limity-komissii-sroki/otvetstvennaya-igra/

## Что реально можно автоматизировать

1. Сбор разрешенных данных:
   - календарь матчей, результаты, составы, травмы, новости;
   - историческая статистика команд/игроков;
   - odds snapshots только из легального источника: data provider, партнерский API, ручной CSV/export.
2. Прогнозирование:
   - baseline: no-vig market implied probability;
   - pre-match: Elo/Glicko, Poisson/Dixon-Coles, xG-based model, gradient boosting, Bayesian ensemble;
   - live: hazard/survival model для next goal/totals с учетом минуты, счета, xG, красных карточек, замен, темпа и свежести данных.
3. Поиск value:
   - `p_market_no_vig` после удаления маржи;
   - `p_model` после calibration;
   - `EV = p_model * decimal_odds - 1`;
   - alert только если EV, confidence, liquidity, latency и risk gates проходят.
4. Paper-trading:
   - локальная симуляция ставки;
   - запись model version, market, odds, timestamp, selection, hypothetical stake, result;
   - никакой записи в БК.
5. Risk management:
   - fractional Kelly cap;
   - max exposure per match/day/market;
   - stop-loss, cooldown;
   - responsible-game/self-limit checks.

## Что нельзя автоматизировать в текущем контуре

- Автоматический логин в БК и размещение ставки.
- Автоклик по сайту/приложению БК.
- Обход KYC/CAPTCHA/anti-bot/лимитов.
- Мультиаккаунтинг и credential sharing.
- Использование паролей/токенов БК в локальных агентах без отдельного legal/compliance решения.

## Главный технический вывод

Нужно оптимизировать не "максимальную угадываемость", а risk-adjusted positive expected value.

Высокая вероятность события часто уже заложена в низкий коэффициент. Высокий коэффициент обычно означает низкую вероятность. Ставочный edge появляется только если модель стабильно оценивает вероятность выше очищенной от маржи рыночной вероятности и это подтверждается на out-of-sample/backtest/CLV.

## Проверочный план

Перед любым live или real-money применением:

- walk-forward backtest;
- out-of-sample period;
- Brier score/log loss;
- calibration curves;
- CLV;
- paper ROI;
- max drawdown;
- latency rejection tests;
- no-lookahead tests;
- audit every signal.

## MVP Roadmap

1. Создать спецификацию:
   - `requirements.md`;
   - `data-contract.md`;
   - `compliance-gates.md`;
   - `backtest-plan.md`;
   - `mvp-roadmap.md`.
2. Начать с футбола ЧМ-2026:
   - pre-match рынки: 1X2, double chance, totals 2.5, BTTS;
   - live рынки только после легального live data feed.
3. Реализовать:
   - importer fixtures/results/odds snapshots;
   - market no-vig baseline;
   - Elo/Poisson baseline;
   - calibration;
   - EV scanner;
   - paper executor;
   - read-only dashboard.
4. Все длинные backtest/paper-forward запускать только по Visible Run Rule.

## Claude Code L5 Verification

Claude Code L5 summary:

- L1.0 MiMo заблокировал hidden real-money auto-betting and bookmaker KYC/CAPTCHA/limit/anti-bot bypass.
- Antigravity L1.1/L2 runtime failed; user-approved Codex fallback did not расширить периметр доступа.
- L3/L4 are read-only analytics/paper-trading.
- External bookmaker writes отсутствуют.
- Residual drift risk: future iterations must not add real credentials or bookmaker write endpoints without a new L1/risk gate.

## Risk Gate

Risk gate status: passed for analytics/paper-trading MVP only.

Not passed for real-money execution.

## Final Decision

approve

Аналитический и paper-trading MVP можно продолжать. Реально-денежная автоматизация ставок остается заблокированной до отдельного legal/compliance review, правил конкретной БК, разрешенного API/партнерского канала и ручного approval step.

Не является юридической, финансовой или игровой рекомендацией. Участие в азартных играх не гарантирует выигрыша и может привести к потере денег.

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
