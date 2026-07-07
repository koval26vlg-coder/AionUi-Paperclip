Задача: независимый Рой-checkpoint по текущей цели trading_mvp.

Контекст:
- Цель: найти/доказать или честно отбросить trading edge/high-winrate scheme в trading_mvp через data/backtest/OOS/walk-forward/stress/economics/paper-forward gates.
- Research-only: no live orders, no API keys, no leverage, no margin, no investment advice.
- Active gate проверен: READY_FOR_POSTPROCESS только формально; funding dataset funding_collect_7d_spotliq_visible_20260617_185732 заблокирован guard review из-за data_quality:min_min_rows_per_cycle, min_rows_per_cycle=9. Funding rank/backtest/paper-forward запрещены.
- trading_next_goal_step.ps1 сейчас ведет к guarded visible 6h WS collect plan: start_ws_collect_visible.ps1 -Hours 6 -PlanOnly. Actual collect НЕ запускать без отдельного явного подтверждения пользователя и -ConfirmedLongRun.
- Важно: недавно найден возможный stale/legacy mismatch в tools/trading_goal_status.ps1: поля visible_ws_collect_* указывают на правильный WS path, но legacy visible_collect_command может все еще указывать на старый 7d funding collect, несмотря на funding_blocked_by_swarm=true.

Что нужно от Роя:
1. Проверить, является ли stale legacy visible_collect_command реальным риском для цели и automation/handoff.
2. Подтвердить, что следующий безопасный шаг до long-run: выровнять status/preflight/next-step outputs так, чтобы при funding_blocked_by_swarm=true legacy visible_collect_command не вел к funding collect, а явно вел к guarded WS path или был помечен deprecated.
3. Проверить, что это не нарушает Active Run Gate Rule и Visible Run Rule.
4. Сформировать handoff: accept/reject, риски, какие файлы проверить/изменить, какие тесты запустить.

Запрещено:
- Не запускать collectors/backtests/replay/grid/long runs.
- Не запускать postprocess funding dataset.
- Не анализировать новые видео/канал/P2P/off-ramp/legal/custody.
- Не предлагать live trading.
