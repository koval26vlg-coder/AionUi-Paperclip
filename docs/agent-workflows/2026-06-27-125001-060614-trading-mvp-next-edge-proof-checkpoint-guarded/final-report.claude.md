## Итог

Цепочка L1→L4 непротиворечива и сходится к единому verdict `approve`. Все уровни корректно фиксируют исходное состояние цели `trading_mvp` (research-only edge на non-Binance markets):

- funding-датасет `funding_collect_7d_spotliq_visible_20260617_185732` **отвергнут** data-quality guard (`min_rows_per_cycle=9 < 20`, `ok=false`, `not_ready_for_postprocess`) — никакой rank/backtest/paper-forward по нему не предлагается;
- next branch правильно переключён на `SWEEP_REVERSAL_CURRENT_DATA_REJECTED_PLAN_VISIBLE_DENSE_COLLECT`, а не на funding postprocess;
- первичный шаг — только `start_ws_collect_visible.ps1 -Hours 6 -PlanOnly` (PlanOnly вернул `would_start=false`, `requires_confirmed_long_run=true`);
- post-collect цепочка выражена явно: active-run gate → guarded WS postprocess на exact manifest → replay-validation PlanOnly с `-ExpectedManifestPath` → `-ConfirmedResearchRun` только после прохождения data-quality gate и явного review;
- L3 подтверждён прогонами (preflight `READY_FOR_EDGE_PROOF_STEP`, acceptance gate `research_only_no_accepted_strategy`, tests `198 OK`), L4 закрыл архитектурный/risk gate.

Все критичные правила соблюдены: нет live orders, API keys, leverage/margin, инвестсоветов; long-run требует видимого терминала и явного подтверждения.

## Проверка искажения

Искажения цели или подмены verdict между уровнями **не обнаружено**. Контрольные факты сохранены сквозь все уровни без дрейфа:

- funding rejection не «потерян» и нигде не переинтерпретирован как годный датасет;
- старый gate-status `READY_FOR_POSTPROCESS` корректно помечен как относящийся к отвергнутому funding run и не используется как разрешение (L4 явно даёт приоритет next-goal logic + guard artifact над строкой `next_step_after_ready`);
- ни на одном уровне нет скрытого повышения шага до фактического collect/replay/grid/postprocess;
- предыдущий workflow без risk-флагов (`2026-06-27-124834-...`) корректно исключён как источник решения.

Замечания (не блокеры, влияют на качество, а не на корректность):
- **L1 и L2 идентичны почти дословно** — L2 не добавил независимой ценности, фактически дублирует L1. Это снижает реальную глубину независимой перекрёстной проверки, но не искажает вывод.
- L3 отметил ~20s overhead PlanOnly из-за `trading_next_goal_step.ps1` — честно зафиксировано как UX-, а не safety-вопрос.

## Допустимый следующий шаг

Единственный разрешённый следующий шаг для Codex — **PlanOnly-превью без запуска долгого прогона**:

```
pwsh -NoProfile -ExecutionPolicy Bypass -File tools\start_ws_collect_visible.ps1 -Hours 6 -PlanOnly
```

(предварительно — `tools\check_active_run_gate.ps1`).

Далее строго по цепочке и только при явном подтверждении пользователя:
1. фактический 6h WS collect — **только в видимом терминале и только после явного `-ConfirmedLongRun`/подтверждения пользователя**;
2. после завершения — `run_ws_postprocess_visible.ps1` (guarded) на exact completed manifest;
3. `run_ws_replay_validation_visible.ps1 -PlanOnly -PostprocessPath <...> -ExpectedManifestPath <тот же manifest>`;
4. фактический replay/grid — только при `replay_allowed=true` после data-quality acceptance и отдельном `-ConfirmedResearchRun` с human review.

## Блокировки

- Запрет на старт нового long collector/backtest/replay/grid/paper-forward без явного подтверждения пользователя и видимого терминала.
- Funding 7d dataset остаётся заблокирован; rank/backtest/paper-forward по нему запрещены.
- Перед каждым шагом обязателен `check_active_run_gate.ps1`; при статусе `RUNNING` — только status/ETA.
- После нового WS collect необходимо убедиться, что active-run gate перезаписан WS-метаданными и не ссылается на старый funding run.
- Winrate не оптимизировать в отрыве от expectancy / net PnL after costs / PF / drawdown / sample size / liquidity-fill risk / OOS.
- Нет live orders, API keys, leverage/margin, инвестсоветов, внешних media/channel/P2P/off-ramp/custody/legal входов.

## Решение

approve

