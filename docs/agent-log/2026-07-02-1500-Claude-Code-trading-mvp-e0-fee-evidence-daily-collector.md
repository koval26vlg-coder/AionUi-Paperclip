# trading_mvp: E0 fee evidence закрыт + daily/funding коллектор собрал данные для H1/H2

Дата: 2026-07-02 ~15:00 +03
Агент: Claude Code

## Исходный запрос

Пользователь одобрил запуск P0 из backlog: E0 (фиксация fee-tier + условий MM-программ MEXC/Gate) и REST-сбор daily klines + funding history для H1/H2.

## Что сделано

### E0 — fee-tier evidence (блокер funding-ветки закрыт)

- Сняты машиночитаемые снимки публичных API без ключей: `exports/trading-mvp/analysis/fee_evidence_20260702/` (MEXC contract detail 951 перп, Gate USDT contracts 823, Gate spot pairs 2192, MEXC spot exchangeInfo 2218).
- Ключевые факты: MEXC futures maker 0 bps на 877/951 контрактов (taker 0 на 401 — вероятно промо); Gate futures maker −1 bps (рибейт) / taker 7.5 bps на всех; MEXC spot maker 0 bps; Gate spot базово 20 bps (дорого — spot-ногу планировать на MEXC).
- Программы: Gate MM (spot до −0.012%) требует ~$20M/30д — вне досягаемости, но базовые ставки и так рабочие; у MEXC формальной MM-программы нет, MX даёт −20% к futures fees.
- Документ: `docs/analysis/2026-07-02-fee-tier-evidence.md` — сценарии A–G для cost model. Старое допущение 39 bps round-trip переведено в stress-кейс; биндящим становится execution gate (spread/fill/adverse selection), не fees.

### Daily/funding коллектор (новый модуль)

- `trading_mvp/src/daily_collector.py` — переиспользует клиенты `funding.py`; MEXC: klines Day1 + пагинированная funding history (page_size=1000); Gate: klines 1d + funding через from/to окна.
- Найденные ограничения API (закодированы и задокументированы): Gate funding_rate без from/to отдаёт только 30 дней; глубина максимум 180 дней; limit=1000 обрезает 4h-контракты — решено рекурсивной разбивкой окна пополам. MEXC хранит ~540 дней funding.
- Фиксы по ходу: UnicodeEncodeError на не-ASCII символе контракта в cp1251-консоли → принудительный UTF-8 stdio.
- Тесты: `tests/test_daily_collector.py`, 16 тестов OK (без сети, fake-клиенты).
- Resume-механика: повторный запуск с тем же `--run-id` пропускает готовые файлы.

### Собранный датасет

- `exports/trading-mvp/daily/daily_collect_20260702_top200/` (47 MB, manifest.json):
  - 400 символов (top-200 по 24h обороту на MEXC и Gate);
  - 170,216 дневных свечей (140 символов ≥700 дней, 160 — 180-700 дней);
  - 488,862 funding-записей; ошибок 0;
  - universe-теги: non_binance_baseline = 41 (MEXC) + 61 (Gate) — оба конфига H1 (baseline/extended) покрыты одним датасетом.

## Проверки

- Тесты модуля: 16 OK. Smoke: 3 символа/биржа, интервалы funding проверены (8h mode, span соответствует).
- Полный тестовый набор проекта: 242 теста, 3 падения в `test_visible_ws_collect_wrapper.py` — pre-existing проблема кодировки кириллицы («Рой» → mojibake) в PowerShell-обёртке, НЕ связана с новым модулем (он аддитивен). Заведена отдельная задача на починку.
- Visible Run Rule: сбор шёл в foreground с видимым прогрессом; манифест сохранён.

## Ограничения

- Gate funding history — максимум 179 дней (ограничение API), MEXC ~540 дней. Для длинной истории funding нужен forward-сбор (уже стартовал накапливаться этим датасетом + существующий funding-контур).
- Live orders/API keys/leverage не затрагивались; research-only.

## Следующий шаг

1. H1: momentum-бэктест на собранных daily klines (обе universe-конфигурации, полная gate matrix goal v2, издержки по сценариям A–D из fee evidence).
2. H2/H3: повторный cost gate funding-ветки со сценариями fee evidence вместо 39 bps.
3. Запись новой гипотезной активации в experiment ledger перед бэктестом (правило backlog).
