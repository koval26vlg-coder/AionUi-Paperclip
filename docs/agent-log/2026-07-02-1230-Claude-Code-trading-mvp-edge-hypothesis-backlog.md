# trading_mvp: создан edge hypothesis backlog

Дата: 2026-07-02 ~12:30 +03
Агент: Claude Code

## Исходный запрос

Продолжение аудита слабых мест: пользователь спросил, как достичь положительного edge (любые альтернативы), согласился оформить предложенные идеи как hypothesis backlog («давай сделаем»).

## Что сделано

Создан приоритезированный backlog гипотез edge:
`C:\Users\koval\Documents\ZolotyayLopata\docs\analysis\2026-07-02-edge-hypothesis-backlog.md`

Состав:

- **E0 (P0, рычаг):** fee-tier evidence с публичных страниц + условия MM/rebate программ MEXC/Gate — разблокирует funding-ветку и меняет знак cost gate.
- **H1 (P0):** кросс-секционный momentum long/short на дневных klines — самая дешёвая по данным гипотеза, не требует WS-коллектора, можно начинать немедленно.
- **H2 (P0):** cross-exchange funding carry (перекос ставок между биржами), расширение существующей funding-ветки; после E0.
- **H3 (P0):** одно-биржевой funding/basis carry — существующая заблокированная ветка, повторный cost gate после E0.
- **H4 (P1):** шорты под token unlocks (event study по календарю разлоков).
- **H5 (P1):** listing-эффекты второго порядка (анонс Binance/Coinbase → репрайс на MEXC/Gate).
- **H6 (P2):** депеги/миграции — watch-only.
- **H7 (P2):** volatility risk premium (Deribit) — только paper-research, за safety boundaries до отдельного решения.
- **H8 (P2):** on-chain/sentiment — фича поверх H4/H5, не самостоятельная ветка.
- **H9:** airdrops/конкурсы — вне торгового контура, отдельное решение пользователя.

Правила: все гипотезы наследуют gate matrix и kill rules goal v2 без изменений; активация только через experiment ledger; максимум две активные гипотезы одновременно; вердикт или inconclusive не позже 4 недель.

Открытые решения для пользователя (зафиксированы в документе):

1. Universe-constraint «не на Binance» для H1/H4 — режет выборку; предложено два прогона с явной пометкой.
2. H9 (airdrops) — активировать ли как отдельный проект вне trading_mvp.

## Изменённые файлы

- `C:\Users\koval\Documents\ZolotyayLopata\docs\analysis\2026-07-02-edge-hypothesis-backlog.md` (новый)
- этот файл журнала

## Проверки

- Backlog согласован с goal v2 (kill rules не ослаблены), scorecard 2026-06-28 (отклонённые семейства не реанимируются) и roadmap-документом 2026-07-02 (collector v2 остаётся P0 для WS-веток, но H1–H3 его не ждут).
- Код проекта не менялся; live trading/API keys не затрагивались.

## Риски и ограничения

- Research-only, не инвестсовет; prior-оценки гипотез — экспертные, не подтверждённые данными проекта.
- Независимое L1/L2 ревью Роя по-прежнему недоступно (Antigravity geo-block).

## Что проверить следующему агенту

- Получить от пользователя решения по universe-constraint (H1/H4) и H9.
- Первые исполняемые шаги: E0 (фиксация fee evidence) и REST-сбор daily klines + funding history для H1/H2.
