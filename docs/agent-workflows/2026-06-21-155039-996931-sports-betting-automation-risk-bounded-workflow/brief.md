# Цель пользователя

Использовать команду WorkFlow для анализа всех возможных решений по автоматизации ставок на спорт с повышением вероятности winrate, особенно во время чемпионата. Нужны варианты прогнозирования исходов и live-событий с высокой уверенностью, оценка возможности ставок на российских букмекерских конторах, автоматизация процесса и анализ рисков.

# Обязательные границы безопасности и законности

1. Не проектировать обход правил букмекерских контор, антибот-защит, лимитов, KYC, CAPTCHA, гео-ограничений или блокировок аккаунтов.
2. Не автоматизировать фактическое размещение денежных ставок без отдельного юридического/compliance допуска, проверки правил конкретной БК и явного ручного подтверждения пользователя на каждую ставку.
3. Разрешенный базовый результат: decision-support система, paper-trading/backtest, alerting, расчет вероятностей, сравнение с линией, журналирование и risk controls.
4. Любая интеграция с реальными БК должна быть только через легальные API/партнерские каналы или ручной approval step; web-скрейпинг/автоклик/credential stuffing запрещены.
5. Не давать гарантий выигрыша: букмекеры закладывают маржу, live-коэффициенты быстро меняются, edge должен доказываться backtest/out-of-sample и CLV/closing line value.

# Что должен сделать workflow

- L1: собрать гипотезы, источники данных, рынки ставок, риски и быстрые варианты.
- L2: проверить применимость, ограничения, compliance, edge cases и ложные допущения.
- L3: разложить реализацию на компоненты: ingestion, odds normalization, feature store, models, calibration, EV engine, bankroll/risk, paper execution, alerting, audit.
- L4: собрать архитектуру и risk gate.
- L5: дать итоговый отчет пользователю: что реально можно автоматизировать, что нельзя, как повысить вероятность прогноза, какие метрики доказывают edge, какой минимальный MVP делать первым.

# Критерии готовности

- Есть workflow artifact с contract/events/handoff/final-report.
- Указаны легальные/этичные границы: никакого скрытого автоклика ставок и обхода правил БК.
- Есть техническая архитектура decision-support/paper-trading MVP.
- Есть список моделей/подходов: pre-match, live, ensemble, calibration, market-implied probabilities, injury/news/xG/lineup/context features.
- Есть risk management: bankroll, Kelly cap, stop-loss, exposure limits, model drift, data latency, bookmaker margin, account/legal risks.
- Есть проверочный план: backtest, walk-forward, out-of-sample, CLV, hit rate vs EV, Brier/log loss, calibration curves.
