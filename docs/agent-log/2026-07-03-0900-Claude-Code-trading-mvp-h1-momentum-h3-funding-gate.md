# trading_mvp: H1 momentum backtest (promising) + H3 funding cost gate v2 (carry разблокирован)

Дата: 2026-07-03 ~09:00 +03
Агент: Claude Code

## Исходный запрос

«Делаем следующий шаг» после E0 и сбора данных: активация H1 в experiment ledger, momentum-бэктест через ворота, повторный cost gate funding-ветки (H3).

## Что сделано

1. **Setup зарегистрирован**: `cross_sectional_momentum_daily` добавлен в `SETUP_REGISTRY` (`trading_mvp/src/experiments.py`), `setup_registry.json` перегенерирован.
2. **Модуль бэктеста**: `trading_mvp/src/momentum_backtest.py` — weekly L/S по трейлинг-доходности, dollar-neutral, funding-учёт с корректным знаком (long платит положительный funding), ликвидность-фильтр по rolling 30d quote volume, dedupe одинаковых монет между биржами по большему обороту. Честный протокол: lookback выбирается только на train (70%), OOS — только для выбранного. Fee-сценарии A/B/D/stress-39bps + slippage 10 bps.
3. **Тесты**: `tests/test_momentum_backtest.py`, 11 OK (знак funding, dedupe, liquidity filter, метрики, границы окон).
4. **Прогон H1** на `daily_collect_20260702_top200`:
   - extended (287 рынков): OOS 28 недель, lookback=30: +179 bps/нед (сценарий B), t=1.48, PF 2.16, hit 0.68, maxDD 19%; положителен во ВСЕХ сценариях включая stress 39 bps; WF-половины +125/+234 bps.
   - baseline (68 рынков): +602 bps/нед, t=2.06 — помечено как раздутое survivorship/илликвидностью, не доверять.
   - **Вердикт: promising, НЕ accepted** — survivorship/look-ahead bias universe (текущие top-200), t<2, нет concentration-check. Ledger: `exp_20260703_084900_27d97535f1dc`.
5. **H3 cost gate v2**: `exports/trading-mvp/analysis/funding_costgate_v2_20260703.json` — 373 символа, окно 90д: медиана annualized funding 2.3%, **77 символов ≥10%/год при positive_share ≥0.7, 63 ≥20%**. Топ 60–155% годовых (мем-коины/токенизированные акции — venue-риск). SKYAI и BROCCOLIF3B устойчиво положительны на обеих биржах — кандидаты H2 paired-анализа. При сценариях E (0 bps) / G (−2 bps) cost gate проходит по построению.
6. **Документ**: `docs/analysis/2026-07-03-h1-h3-first-results.md` — результаты, ограничения, условия промоушена H1, следующие шаги.

## Изменённые файлы

- `trading_mvp/src/experiments.py` (новый setup в реестре)
- `trading_mvp/src/momentum_backtest.py` (новый)
- `trading_mvp/tests/test_momentum_backtest.py` (новый)
- `exports/trading-mvp/experiments/experiment_ledger.jsonl` (+1 запись), `setup_registry.json` (перегенерирован)
- `exports/trading-mvp/backtests/momentum_daily_20260703_084744.json` (новый артефакт)
- `exports/trading-mvp/analysis/funding_costgate_v2_20260703.json` (новый артефакт)
- `docs/analysis/2026-07-03-h1-h3-first-results.md` (новый)

## Проверки

- 11 тестов momentum-модуля OK; тест знака funding подтверждает симметрию long/short.
- Selection только на train подтверждено кодом (OOS не участвует в выборе lookback).
- Kill rules goal v2 не ослаблены; live orders/API keys не затрагивались.

## Риски и ограничения

- Survivorship bias — главный дефект H1-результата, задокументирован в ledger/доке; без исторических составов universe продвижение запрещено.
- Funding-carry топ — тонкие рынки: ёмкость, venue-риск, разворот funding.
- Gate funding история ограничена 179 днями (API).

## Что проверить следующему агенту

1. H2 paired-анализ (SKYAI, BROCCOLIF3B: спред funding, basis, spot-наличие на MEXC).
2. Survivorship-чистый universe для H1 (даты листинга контрактов, архивные снапшоты объёма).
3. Обновление strategy scorecard (funding → reopened_research, momentum → promising).
4. Еженедельный forward-запуск `daily_collector.py` для накопления funding-истории.
