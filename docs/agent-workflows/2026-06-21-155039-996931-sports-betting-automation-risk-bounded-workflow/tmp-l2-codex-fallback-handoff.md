# L2 Codex fallback engineering review

Fallback reason: Antigravity CLI L2 unavailable through valid workflow output; user approved continuation with `продолжи`.

## Что было сделано

Проведена инженерная проверка вариантов автоматизации ставок и отбор допустимых решений:

- `allowed`: аналитический dashboard, pre-match forecast, live forecast, odds/EV scanner, paper-trading executor, alerting, audit журнал, bankroll/risk module.
- `conditional`: интеграция с легальными odds/data providers или партнерским API БК при договорном разрешении.
- `blocked`: скрытый real-money auto-betting, browser bot/autoclick, обход KYC/CAPTCHA/anti-bot/лимитов, мультиаккаунтинг, credential sharing.

## На чем основан вывод

- L1.0/L1.1 границы.
- 244-ФЗ, ЕРАИ, ФНС registry, ЦУПИС и responsible-game ограничения.
- Инженерная реальность live betting: latency, line movement, settlement ambiguity, market suspension, odds changes, void rules.
- Статистическая реальность: БК имеют маржу; "вероятное событие" обычно имеет низкий коэффициент, а "высокий коэффициент" требует доказанного mispricing, а не интуиции.

## Что получилось хорошо

Можно построить полезный и безопасный MVP:

1. Data ingestion:
   - fixtures/results;
   - team/player metrics;
   - odds snapshots from permitted sources;
   - injury/news/lineup/context features;
   - live event feed if licensed.
2. Probability engine:
   - market implied probability and margin removal;
   - model probability;
   - calibration layer;
   - uncertainty interval.
3. EV scanner:
   - `edge = p_model - p_market_no_vig`;
   - `expected_value = p_model * decimal_odds - 1`;
   - only alerts when EV, liquidity, latency and confidence gates pass.
4. Paper executor:
   - no real money;
   - records hypothetical stake, odds, timestamp, market, selection, model version.
5. Risk controls:
   - fractional Kelly cap;
   - per-day/per-event exposure;
   - stop-loss;
   - drawdown guard;
   - responsible-game/self-limit reminders.

## Что требует доработки

- Выбрать первый спорт и рынки. Для ЧМ-2026 рациональный MVP: футбол, pre-match 1X2/double chance/totals, затем live next-goal/totals только после качественного live feed.
- Найти легальный источник odds snapshots. Без разрешенного источника нельзя строить промышленный scanner на скрейпинге БК.
- Определить storage schema и model registry.
- Сделать small backtest на исторических матчах и odds snapshots до любого live использования.
- Добавить "human approval wall": система может дать сигнал, но не нажимает ставку.

## Какие есть риски

- Data leakage: использовать closing odds или постфактум lineup как будто они были доступны до ставки.
- Selection bias: тестировать только на матчах, где были красивые сигналы.
- Look-ahead bias в live данных.
- Несравнимые коэффициенты: разные БК имеют разные правила settlement/void.
- Неправильная цель: winrate вместо risk-adjusted EV.
- Ответственность: автоматизация может усиливать зависимое поведение, поэтому лимиты и self-exclusion должны быть частью продукта.

## Что нельзя потерять/исказить дальше

- MVP не размещает реальные ставки.
- Любой future real-money execution требует отдельного legal/compliance review, правил конкретной БК и ручного подтверждения пользователя.
- Backtest должен быть walk-forward/out-of-sample, с учетом времени доступности данных.
- Для live нужен latency budget и отказ от сигнала при stale data.

## Решение

escalate
