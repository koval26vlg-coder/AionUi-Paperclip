# L3 Codex implementation decomposition

## Что было сделано

Сформирована декомпозиция реализации risk-bounded decision-support MVP для спортивных прогнозов и paper betting.

## На чем основан вывод

- L1/L2 handoff-и.
- Текущие правовые/compliance источники.
- Требование пользователя автоматизировать прогнозирование и live-предугадывание, но без небезопасного real-money auto-execution.

## Что получилось хорошо

Предложен MVP в 8 модулях:

1. `data_ingestion`
   - fixtures/results;
   - odds snapshots from allowed provider/API/manual export;
   - team/player stats;
   - lineups/injuries/news;
   - live events only through licensed feed.
2. `normalization`
   - unified event/team ids;
   - decimal odds;
   - market taxonomy: 1X2, totals, handicaps, next goal, cards/corners only later;
   - timestamp normalization.
3. `feature_store`
   - pre-match features: Elo/Glicko, xG/xGA, rest/travel, form, squad strength, injuries, motivation, weather.
   - live features: score, minute, red cards, substitutions, shots/xG, pressure, possession zones, market movement.
4. `modeling`
   - baseline: market-implied no-vig probability.
   - football pre-match: Poisson/Dixon-Coles, Elo + gradient boosting, Bayesian update, ensemble.
   - live: hazard/survival model for next goal and total goals, updated by game state.
   - calibration: Platt/isotonic/beta calibration.
5. `ev_engine`
   - no-vig market probability;
   - model probability and confidence interval;
   - EV, edge, stake suggestion;
   - reject stale odds and weak confidence.
6. `paper_executor`
   - hypothetical ticket only;
   - no bookmaker login, no click, no write to external БК;
   - full audit trail.
7. `risk_manager`
   - fractional Kelly with hard cap, e.g. 0.25 Kelly and max 0.5-1.0% bankroll per signal;
   - daily/event/market exposure;
   - stop-loss and cooldown;
   - responsible-game check.
8. `alerting_dashboard`
   - signal queue;
   - why-this-signal explanation;
   - model version and data freshness;
   - manual approval only if later legally allowed.

## Что требует доработки

Минимальный порядок реализации:

1. `spec/data-contract.md`: schema for fixtures, odds, events, predictions, paper bets.
2. `spec/compliance-gates.md`: blocked actions and allowed sources.
3. `scripts/import_odds_snapshot.py`: import from legal CSV/API export, not scraping.
4. `scripts/train_baseline.py`: market baseline + Elo/Poisson baseline.
5. `scripts/backtest_walk_forward.py`: visible-run only, with manifest.
6. `scripts/paper_forward.py`: visible monitor, no external writes except local artifacts.
7. `dashboard`: read-only signals and audit.

## Какие есть риски

- Долгие backtest/collector/paper-forward подпадают под Visible Run Rule: запускать только в видимом терминале или monitor script.
- Любой secrets/API provider key нельзя сохранять в docs/SML.
- Без разрешенного odds source MVP должен принимать только ручной CSV/import или demo dataset.
- В live режиме stale odds делают сигнал недействительным.

## Что нельзя потерять/исказить дальше

- Не строить букмекерский bot.
- Не строить обход антибота.
- Не давать betting advice как гарантию.
- Все результаты маркировать как analytics/paper-trading, not financial/legal advice.

## Решение

escalate
