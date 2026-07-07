# trading_mvp: аудит слабых мест и дорожная карта

Дата: 2026-07-02 ~12:00 +03
Агент: Claude Code

## Исходный запрос

Пользователь попросил найти слабые места, предложить улучшения и развитие проекта; цель — максимальная прибыль от работы на биржах.

## План

1. Aion SML bootstrap по теме.
2. Чтение свежего состояния: goal v2, scorecard 2026-06-28, записка 2026-07-01, active-run-gate.json, completion audit.
3. Чтение кода: `trading_mvp/src/ws_collector.py`, структура src/tests, размеры монолитов.
4. Аналитическая записка со слабыми местами и приоритезированной дорожной картой.

## Что сделано

- Выполнен bootstrap памяти; подтверждено: активный проект — `C:\Users\koval\Documents\ZolotyayLopata` (trading_mvp), состояние STOPPED_INCOMPLETE после падения 72ч WS-сбора на 7.3ч.
- Проведён аудит: операционные слабости (all-or-nothing коллектор без supervisor/resume, сбор на машине с VPN-переключениями, JSONL+base64 без ротации/компрессии — 20.5 ГБ raw), кодовые (cli.py 5510 строк, basis.py 5194, run_mvp.ps1 1914, VPN не отделён), методологические (нет power-анализа перед сбором, нет multiple-testing поправки в grid-search, funding-ветка заблокирована на дёшево разблокируемом fee-tier evidence, нет capacity-модели), процессные (Рой без независимого L1/L2).
- Записана аналитика: `C:\Users\koval\Documents\ZolotyayLopata\docs\analysis\2026-07-02-trading-mvp-weak-points-and-roadmap.md`.

## Ключевые рекомендации (P0)

1. Collector v2: сегментированный сбор + stitching/gap accounting + supervisor/auto-restart + алертинг + ротация/zstd.
2. Вынести сбор данных с домашней машины на VPS/отдельную машину без VPN-переключений.
3. Зафиксировать публичные fee-tier (MEXC/Gate/OKX/Bybit) → разблокировать funding/basis и запустить multiweek сбор параллельно WS-ветке.
4. Power-анализ размера выборки до следующего длинного сбора.

## Изменённые файлы

- `C:\Users\koval\Documents\ZolotyayLopata\docs\analysis\2026-07-02-trading-mvp-weak-points-and-roadmap.md` (новый)
- `D:\AionUi-Paperclip\docs\agent-log\2026-07-02-1200-Claude-Code-trading-mvp-weak-points-audit.md` (этот файл)

## Проверки

- active-run-gate.json прочитан: STOPPED_INCOMPLETE, replay_allowed=false — согласуется с goal v2.
- Код ws_collector.py сверен с манифестом фейла: reconnect-цикл есть, но stop_reason указывает на выход процесса целиком — подтверждает отсутствие supervisor.
- Никакой код проекта не менялся; live trading/API keys не запускались.

## Риски и ограничения

- Аналитика research-only; не инвестсовет.
- Независимое L1/L2 ревю Роя недоступно (Antigravity geo-block) — выводы без независимой проверки.

## Что проверить следующему агенту

- Согласовать с пользователем порядок P0: collector v2 vs VPS vs fee-tier evidence (можно параллельно).
- При реализации collector v2 — обновить data-quality gate под сегментированные manifest'ы.
