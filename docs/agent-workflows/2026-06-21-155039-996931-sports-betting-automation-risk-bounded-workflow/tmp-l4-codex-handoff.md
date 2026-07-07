# L4 Codex architecture synthesis

## Что было сделано

Собрана итоговая архитектура безопасной автоматизации: система не ставит деньги сама, а прогнозирует вероятности, сравнивает их с линией, ведет paper-trading, контролирует риск и дает объяснимые alerts.

## На чем основан вывод

- L1.0 MiMo block.
- L1.1/L2 Codex fallback review с источниками.
- L3 implementation decomposition.
- Risk flags: `trading`, `writes_external_system`, `long_running`, `uses_secrets`.

## Что получилось хорошо

Целевая архитектура:

```text
Allowed data sources
  -> ingestion/normalization
  -> feature store
  -> pre-match model
  -> live model
  -> calibration
  -> EV scanner
  -> risk manager
  -> paper executor
  -> read-only dashboard + alerts
  -> audit/metrics/backtest reports
```

Главный принцип:

```text
signal != bet
```

Сигнал может сказать: "модель считает вероятность выше no-vig рынка на X, данные свежие, риск в лимитах". Но реальная ставка не размещается автоматически.

## Что требует доработки

Перед любым кодом нужно создать рабочий пакет:

- `docs/specs/sports-betting-decision-support/requirements.md`
- `docs/specs/sports-betting-decision-support/data-contract.md`
- `docs/specs/sports-betting-decision-support/compliance-gates.md`
- `docs/specs/sports-betting-decision-support/backtest-plan.md`
- `docs/specs/sports-betting-decision-support/mvp-roadmap.md`

Практический MVP:

1. Start: ЧМ-2026 football pre-match.
2. Markets: 1X2, double chance, totals 2.5, both teams to score. Live markets только после легального live feed.
3. Data: FIFA fixtures/results, historical team stats, allowed odds snapshots.
4. Models: no-vig market baseline, Elo/Poisson, gradient boosted ensemble, calibration.
5. Validation: walk-forward backtest, CLV, Brier/log loss, calibration plot, ROI paper, max drawdown.
6. Interface: read-only dashboard with alerts and explanation.

## Какие есть риски

- Compliance risk remains high if any real bookmaker automation is added.
- Risk gate cannot pass for hidden auto-execution.
- Live high-odds signals are especially dangerous: they often reflect information/latency advantage already captured by the bookmaker or market suspension risk.
- "Максимальная уверенность" and "большой коэффициент" are usually opposing goals; the system should search for positive EV, not just rare outcomes.

## Что нельзя потерять/исказить дальше

- The MVP is analytics-first.
- Real-money execution is out of scope.
- A future real-money module would require:
  - written permission/API route from a bookmaker or licensed partner;
  - legal review;
  - explicit user confirmation for each bet;
  - kill switch, stake caps, audit logs, responsible-game limits.

## Решение

approve
