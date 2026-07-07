# trading_mvp: H2 cross-exchange funding pairs — paired-анализ выполнен (promising)

Дата: 2026-07-03 ~09:10 +03
Агент: Claude Code

## Исходный запрос

«Продолжаем» после H1/H3: paired-анализ cross-exchange funding carry (H2) по кандидатам из costgate v2.

## Что сделано

1. **Модуль**: `trading_mvp/src/funding_pairs.py` — выравнивание дневного funding по 113 общим символам MEXC∩Gate, спред Gate−MEXC, sign consistency, basis-риск (std/max дневного отношения close), наличие спота на MEXC из fee-evidence снапшота. Тесты `tests/test_funding_pairs.py` — 9 OK; суммарно 40 тестов новых модулей OK.
2. **Setup зарегистрирован**: `cross_exchange_funding_carry` в SETUP_REGISTRY; `setup_registry.json` перегенерирован.
3. **Прогон**: 105 пар, окно 90д. Артефакт `exports/trading-mvp/analysis/funding_pairs_20260703_090100.json`.
4. **Ledger**: H2 `exp_20260703_090252_380b1c185495` (promising), H3 reopened `exp_20260703_090252_8fef38415a4e` (promising, funding_basis_carry разблокирован fee-evidence).
5. **Документ**: `docs/analysis/2026-07-03-h2-funding-pairs-results.md`.

## Ключевые результаты

- **G-кандидаты** (perp-perp спред, cons≥0.75): RAVE 91.5%/год, BROCCOLIF3B 80.5%, EVAA 37%, M 28%, BEAT 25%, NOM 23% — при издержках −2 bps.
- **E-кандидаты** (short MEXC perp + long MEXC spot, издержки ~0): SKYAI +69.7%/год ($5.7M объём, basis std 18 bps), BEAT +56.4% ($17M, 17 bps), EVAA +50.6%, BAS +46.2% и ещё 6 с ≥40%.
- Концептуально зафиксировано: для двойне-положительных монет E-конструкция собирает весь уровень funding и доминирует G; высокоспредовые пары с cons<0.7 (GUA, TAIKO, H) отклонены.

## Вердикт

Promising, НЕ accepted: 90д назад ≠ персистентность; execution gate (maker fill, спот-глубина) не пройден; basis MtM и margin-модель не построены; venue/capacity риски тонких рынков.

## Изменённые файлы

- `trading_mvp/src/funding_pairs.py`, `trading_mvp/tests/test_funding_pairs.py` (новые)
- `trading_mvp/src/experiments.py` (setup H2)
- `exports/trading-mvp/experiments/experiment_ledger.jsonl` (+2), `setup_registry.json`
- `exports/trading-mvp/analysis/funding_pairs_20260703_090100.json`
- `docs/analysis/2026-07-03-h2-funding-pairs-results.md`

## Что дальше (для следующего агента / пользователя)

1. Еженедельный forward: `daily_collector.py` + пересчёт `funding_pairs.py` — деградация кандидатов.
2. Execution gate по BEAT/SKYAI/BAS/M/EVAA (maker fill, глубина спота).
3. Capacity-aware economics; после 3–4 недель стабильного forward — paper-forward план через штатные ворота.
4. Scorecard: funding-ветка → reopened_research/promising, momentum → promising (не сделано в этом заходе).

Live orders/API keys/leverage не затрагивались; research-only.
