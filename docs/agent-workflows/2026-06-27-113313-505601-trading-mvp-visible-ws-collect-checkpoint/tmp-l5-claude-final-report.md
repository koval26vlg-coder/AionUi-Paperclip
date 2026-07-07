# L5 Final Review — trading_mvp / «используй Рой»

## Что проверено
- **Запрос пользователя**: «используй Рой» → корректно развернут в иерархический workflow `2026-06-27-113313-505601-trading-mvp-visible-ws-collect-checkpoint` с прохождением L1→L4, все вернули `approve`.
- **Соответствие цели**: следующий шаг = видимый 6h dense WS collect по MEXC/Gate для spot maker liquidity sweep reversal, а **не** postprocess / live / paper-forward / acceptance стратегии. Совпадает с заявленной целью (свежий независимый dataset после rejection старых данных).
- **Active Run Gate**: `READY_FOR_POSTPROCESS`, `funding_collect_7d_spotliq_visible_20260617_185732`, live PIDs нет. Запуск нового collect гейт не нарушает.
- **Visible Run Rule**: фактический long collect не запускался; `would_start=false`, `requires_confirmed_long_run=true`, `next_goal_decision=SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT`.
- **PlanOnly ↔ next_goal_step** согласованы (L3 устранил неоднозначную reason-строку; `block` относится к funding-carry branch, не к WS checkpoint).

## Подтвержден ли следующий шаг
**Да, но только как research-only data-collection step.** `approve` всех уровней относится к запуску видимого 6h collect **после явного approval пользователя**, а не к принятию торговой стратегии и не к postprocess старого funding-датасета.

## Ограничения, которые нельзя нарушать
- Research-only: no live orders, no API keys (с торговыми правами), no leverage/margin, no investment advice.
- Только spot-пары MEXC и Gate; visible-run на весь процесс; никаких скрытых фоновых долгих процессов.
- Нет channel/P2P/off-ramp/custody/legal анализа в рамках цели.
- Funding-carry branch остается заблокированной (нет fee-tier evidence) — это отдельная ветка, не смешивать.
- Старый `READY_FOR_POSTPROCESS` датасет не «протаскивать» как замену свежему collect; partial ≠ final.

## Что сделать дальше
1. Запускать видимый 6h collect **только** после явного «да» пользователя командой с `-ConfirmedLongRun` (из PlanOnly).
2. До/в момент запуска убедиться, что monitor показывает: elapsed, ETA, rows, per-exchange/per-symbol counts, last write age, reconnect/errors.
3. После collect — обязательные data-quality gates (coverage, gaps, stale, density, malformed) до любого postprocess/OOS; недостаточный dataset → `inconclusive/rejected`, без подгонки параметров.
4. Если лимиты Роя недоступны на следующем checkpoint — фиксировать `swarm_limited` и продолжать Codex вручную.

## Решение
**approve** — следующий шаг (видимый 6h WS collect после явного approval пользователя) корректен и безопасен; принятие стратегии не одобрено и остается под строгими OOS/walk-forward/stress/net-PnL/sample-size gates.
