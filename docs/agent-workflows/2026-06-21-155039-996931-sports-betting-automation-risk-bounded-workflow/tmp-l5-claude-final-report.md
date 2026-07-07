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
