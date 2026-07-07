Ты Claude Code L5 в workflow Рой. Не запускай команды, не читай файлы, не пиши файлы. Ниже весь пакет. Верни финальный markdown-отчет для пользователя на русском.

Требования:
- короткий verdict: approve / revise / escalate / block;
- проверь, не исказили ли L1-L4 brief и risk boundaries;
- зафиксируй, что funding branch на текущем 7d dataset заблокирован data-quality gate, а не принят;
- укажи следующий допустимый шаг цели;
- не давай инвестиционный совет.

# Brief
Контекст: проект C:\Users\koval\Documents\ZolotyayLopata, цель trading_mvp: найти, доказать или честно отбросить high-winrate trading edge для non-Binance markets через данные, backtest, OOS/walk-forward/stress/economics/paper-forward gates.

Текущий gate: READY_FOR_POSTPROCESS по run_id funding_collect_7d_spotliq_visible_20260617_185732; manifest final=true, cycles=2016/2016, rows=50583, errors=657. Следующий gate-шаг из проекта: guarded funding-final-review на завершенном JSONL, сравнение с predeclared watchlist, затем обновление viability/economics. Live orders/API keys/leverage/margin запрещены. Не анализировать новый канал, P2P/off-ramp/custody/legal. Не запускать новые длительные collectors/backtests скрыто.

Задача Роя: независимо проверить, что следующий шаг цели корректен и безопасен: 1) какие входные файлы и gates должны быть проверены перед funding-final-review; 2) какие команды допустимы research-only; 3) какие критерии должны блокировать paper-forward/live; 4) какие результаты считать достаточными для продолжения funding carry branch или перехода к sweep/reversal dense WS branch; 5) какие риски переоптимизации, costs/slippage/liquidity/fill/funding-regime нужно явно отразить.

Ожидаемый результат: handoff/final-report с verdict approve/block/approve_with_conditions и точным next-step contract для Codex. Не выдавать инвестсовет.


# Contract
{
  "workflow_id": "2026-06-27-120058-958256-trading-mvp-funding-final-review-checkpoint",
  "title": "trading_mvp funding final-review checkpoint",
  "state": "ready_for_final",
  "created_at": "2026-06-27T12:00:58+03:00",
  "updated_at": "2026-06-27T12:06:53+03:00",
  "created_by": "Codex",
  "principal": "User",
  "current_level": "L4",
  "allowed_next_agents": [
    "Claude Code"
  ],
  "levels": {
    "L1": {
      "name": "Исследовательский отдел",
      "agent": "Antigravity CLI",
      "subagents": [
        {
          "id": "antigravity-source-verifier",
          "name": "Проверяющий фактов",
          "role": "Сверить brief, handoff, события и доступные источники перед передачей на инженерную проверку.",
          "model": {
            "provider": "Google Antigravity",
            "name": "Antigravity CLI AUTO",
            "effort": "High"
          }
        },
        {
          "id": "antigravity-context-expander",
          "name": "Расширитель контекста",
          "role": "Добавить недостающие альтернативы, ограничения, зависимости и edge cases.",
          "model": {
            "provider": "Google Antigravity",
            "name": "Antigravity CLI AUTO",
            "effort": "Low"
          }
        },
        {
          "id": "antigravity-noise-filter",
          "name": "Фильтр шума",
          "role": "Убрать неподтвержденные или лишние идеи, чтобы L1 не передал искажение выше.",
          "model": {
            "provider": "Google Antigravity",
            "name": "Antigravity CLI AUTO",
            "effort": "Low"
          }
        },
        {
          "id": "antigravity-handoff-editor",
          "name": "Редактор L1-handoff",
          "role": "Собрать проверенный handoff с явным решением approve/revise/escalate/block.",
          "model": {
            "provider": "Google Antigravity",
            "name": "Antigravity CLI AUTO",
            "effort": "Medium"
          }
        }
      ],
      "status": "approved",
      "handoff": "levels/L1/handoff.md",
      "approved_by": "Antigravity CLI",
      "submitted_at": "2026-06-27T12:02:40+03:00",
      "approved_at": "2026-06-27T12:02:41+03:00"
    },
    "L2": {
      "name": "Инженерная проверка",
      "agent": "Antigravity CLI",
      "subagents": [
        {
          "id": "antigravity-engineering-reviewer",
          "name": "Инженерный ревьюер",
          "role": "Проверить применимость L1-выводов к реальной реализации.",
          "model": {
            "provider": "Google Antigravity",
            "name": "Antigravity CLI AUTO",
            "effort": "High"
          }
        },
        {
          "id": "antigravity-constraint-checker",
          "name": "Проверяющий ограничений",
          "role": "Сверить решение с brief, контрактом, risk flags, allowed_next_agents и контекстными лимитами.",
          "model": {
            "provider": "Google Antigravity",
            "name": "Antigravity CLI AUTO",
            "effort": "High"
          }
        },
        {
          "id": "antigravity-edge-case-scout",
          "name": "Разведчик крайних случаев",
          "role": "Найти скрытые сценарии, неполные данные, конфликтующие требования и слабые места.",
          "model": {
            "provider": "Google Antigravity",
            "name": "Antigravity CLI AUTO",
            "effort": "High"
          }
        },
        {
          "id": "antigravity-revision-gate",
          "name": "Gate ревизии",
          "role": "Решить, можно ли передавать работу на Codex L3 или нужно вернуть на доработку.",
          "model": {
            "provider": "Google Antigravity",
            "name": "Antigravity CLI AUTO",
            "effort": "High"
          }
        }
      ],
      "status": "approved",
      "handoff": "levels/L2/handoff.md",
      "approved_by": "Codex",
      "submitted_at": "2026-06-27T12:03:40+03:00",
      "approved_at": "2026-06-27T12:04:07+03:00"
    },
    "L3": {
      "name": "Декомпозиция реализации, тесты и automation",
      "agent": "Codex",
      "subagents": [
        {
          "id": "codex-implementation-decomposer",
          "name": "Декомпозитор реализации",
          "role": "Разбить задачу на исполнимые шаги, файлы, интерфейсы и критерии готовности.",
          "model": {
            "provider": "OpenAI Codex",
            "name": "codex-5.3",
            "effort": "xhigh"
          }
        },
        {
          "id": "codex-test-planner",
          "name": "Планировщик тестов",
          "role": "Определить unit/smoke/integration проверки и негативные сценарии.",
          "model": {
            "provider": "OpenAI",
            "name": "gpt-5.5",
            "effort": "xhigh"
          }
        },
        {
          "id": "codex-automation-builder",
          "name": "Инженер automation",
          "role": "Предложить или реализовать CLI/скрипты/мониторы для повторяемого выполнения.",
          "model": {
            "provider": "OpenAI",
            "name": "gpt-5.4 mini",
            "effort": "xhigh"
          }
        },
        {
          "id": "codex-integration-checker",
          "name": "Проверяющий интеграции",
          "role": "Проверить совместимость с существующей структурой, SML, файлами памяти и политиками запуска.",
          "model": {
            "provider": "OpenAI",
            "name": "gpt-5.4",
            "effort": "xhigh"
          }
        }
      ],
      "status": "approved",
      "handoff": "levels/L3/handoff.md",
      "approved_by": "Codex",
      "submitted_at": "2026-06-27T12:06:25+03:00",
      "approved_at": "2026-06-27T12:06:25+03:00"
    },
    "L4": {
      "name": "Архитектурный синтез",
      "agent": "Codex",
      "subagents": [
        {
          "id": "codex-architecture-synthesizer",
          "name": "Архитектурный синтезатор",
          "role": "Собрать L1-L3 в целостное техническое решение без противоречий.",
          "model": {
            "provider": "OpenAI",
            "name": "gpt-5.5",
            "effort": "xhigh"
          }
        },
        {
          "id": "codex-contract-auditor",
          "name": "Аудитор контракта",
          "role": "Проверить, что contract, handoff, events и итоговые выводы согласованы.",
          "model": {
            "provider": "OpenAI",
            "name": "gpt-5.5",
            "effort": "xhigh"
          }
        },
        {
          "id": "codex-risk-gate",
          "name": "Risk gate",
          "role": "Отдельно оценить риски trading/long-running/secrets/external writes/destructive действий.",
          "model": {
            "provider": "OpenAI",
            "name": "gpt-5.5",
            "effort": "xhigh"
          }
        },
        {
          "id": "codex-maintainability-reviewer",
          "name": "Ревьюер сопровождения",
          "role": "Оценить простоту поддержки, расширения и передачи следующему агенту.",
          "model": {
            "provider": "OpenAI",
            "name": "gpt-5.5",
            "effort": "xhigh"
          }
        }
      ],
      "status": "submitted",
      "handoff": "levels/L4/handoff.md",
      "approved_by": null,
      "submitted_at": "2026-06-27T12:06:53+03:00",
      "approved_at": null
    },
    "L5": {
      "name": "Финальная инстанция для пользователя",
      "agent": "Claude Code",
      "subagents": [
        {
          "id": "claude-executive-summarizer",
          "name": "Executive summarizer",
          "role": "Сжато объяснить пользователю итог, решение и оставшиеся риски.",
          "model": {
            "provider": "Anthropic",
            "name": "Claude Opus 4.7 alias",
            "effort": "xhigh"
          }
        },
        {
          "id": "claude-technical-verifier",
          "name": "Финальный техпроверяющий",
          "role": "Независимо проверить техническую связность L1-L4 перед финальным отчетом.",
          "model": {
            "provider": "Anthropic",
            "name": "Claude Haiku 4.5 alias",
            "effort": "xhigh"
          }
        },
        {
          "id": "claude-anti-distortion-auditor",
          "name": "Аудитор против искажения",
          "role": "Сверить final-report с brief, handoff и events, чтобы не было испорченного телефона.",
          "model": {
            "provider": "Anthropic",
            "name": "Claude Sonnet 4.6 alias",
            "effort": "xhigh"
          }
        },
        {
          "id": "claude-final-decision-writer",
          "name": "Автор заключения",
          "role": "Сформировать final-report.md для пользователя с понятным решением approve/revise/escalate/block.",
          "model": {
            "provider": "Anthropic",
            "name": "Claude Opus 4.8 alias",
            "effort": "xhigh"
          }
        }
      ],
      "status": "pending",
      "handoff": null,
      "approved_by": null,
      "submitted_at": null,
      "approved_at": null
    }
  },
  "risk_flags": {
    "trading": true,
    "writes_external_system": false,
    "long_running": false,
    "uses_secrets": false,
    "destructive": false
  },
  "risk_gate": {
    "required": true,
    "status": "pending",
    "agent": "Claude Code",
    "summary": null,
    "approved_at": null,
    "approved_by": null
  },
  "blockers": [],
  "last_event": "level_submitted",
  "last_handoff": "levels/L4/handoff.md",
  "final_report": null
}


# L1
## Что было сделано
- Проведен независимый анализ корректности и безопасности перехода к следующему этапу `guarded funding-final-review` на основе предоставленного контракта и контекста сбора данных за 7 дней (`run_id: funding_collect_7d_spotliq_visible_20260617_185732`).
- Оценены параметры собранного датасета: 2016 из 2016 циклов, 50 583 строки, 657 циклов/запросов с ошибками (высокая доля ошибок ~32.5%, требующая особого внимания при анализе полноты данных).
- Определены границы дозволенного в рамках фазы исследований (research-only), исключающие выполнение живых транзакций и использование приватных ключей.

## На чем основан вывод
- Переход к `funding-final-review` является логичным и безопасным следующим шагом, так как данный этап носит аналитический характер (исследование завершенного JSONL, сравнение с watchlist) и не инициирует торговлю или активные транзакции во внешних системах (`writes_external_system: false`).
- Уровень ошибок (657 из 2016) является критическим фактором качества данных, но этот риск должен быть детально разобран именно на этапе `funding-final-review` перед принятием решения о переходе к walk-forward/paper-forward фазам.

## Что получилось хорошо
- Успешно завершен 7-дневный цикл сбора данных (`manifest final=true`), собран репрезентативный объем сырых данных (более 50 тыс. строк) для первичного анализа ставок финансирования на целевых non-Binance площадках.
- Четко определены границы безопасности (запрет на live-ордера, API keys, leverage/margin, P2P/custody).

## Что требует доработки
- **Анализ природы ошибок**: Необходимо классифицировать и разобрать 657 ошибок сбора (таймауты, ошибки API, пропущенные интервалы) для оценки полноты и пригодности собранного JSONL.
- **Интеграция с Watchlist**: Требуется реализовать автоматический маппинг собранных данных со списком отслеживаемых активов (predeclared watchlist) для выявления пробелов.

## Какие есть риски
- **Риск неполноты данных**: Из-за ~32.5% ошибок в циклах сбора расчеты средних ставок финансирования и доходности carry-стратегии могут быть смещены.
- **Риск переоптимизации**: 7-дневный период является очень коротким таймфреймом и может отражать аномальный режим рынка (funding regime), не репрезентативный для долгосрочной торговли.
- **Риски исполнения (Costs/Slippage/Liquidity/Fill)**: Высокая стоимость транзакций и проскальзывание на низколиквидных non-Binance рынках могут полностью нивелировать теоретическую доходность от ставок финансирования.

## Что нельзя потерять/исказить дальше
- **Целостность сырых логов сбора**: Исходный JSONL-файл сбора не должен подвергаться ручной фильтрации без логирования шагов очистки данных.
- **Watchlist-фильтрацию**: При сравнении с predeclared watchlist нельзя исключать активы с нулевым финансированием, так как они важны для оценки общего распределения ликвидности.

## Решение
approve


# L2
## Что было сделано
- Проведен инженерный и регуляторный аудит результатов этапа L1 по проекту `trading_mvp` в рамках гейта `READY_FOR_POSTPROCESS` (набор данных `funding_collect_7d_spotliq_visible_20260617_185732`).
- Оценена готовность к запуску этапа `guarded funding-final-review` со стороны Codex.
- Сформулированы детальные предпроверки (prechecks), правила обработки ошибок и качества данных (data-quality/error treatment), разрешенные команды (allowed commands), требования к артефактам (artifact expectations) и жесткие блокирующие факторы (hard blockers) для перехода к стадиям тестирования на исторических данных и симуляции (walk-forward/paper-forward).

## На чем основан вывод
- Переход к фазе `guarded funding-final-review` является логичным и безопасным, так как эта фаза носит исключительно аналитический характер (исследование завершенного JSONL, сравнение с watchlist) и не инициирует транзакционную активность во внешних системах (`writes_external_system: false`).
- Уровень ошибок сбора данных (657 из 2016 циклов, около 32.5%) является критическим фактором риска, однако этот риск должен быть количественно оценен и обработан именно в рамках `funding-final-review` перед принятием инвестиционных и операционных решений.

## Что получилось хорошо
- Успешно завершен сбор данных за 7 дней (`manifest final=true`) с фиксацией 50 583 строк сырых данных.
- Корректно определены границы безопасности (полный запрет на использование API-ключей с правами торговли, маржинальное плечо и операции с кастоди/легальными вопросами).

## Что требует доработки
Для безопасного проведения `guarded funding-final-review` исполнителю (Codex) необходимо руководствоваться следующими требованиями:
1. **Точные предпроверки (Prechecks):**
   - Проверка хэш-суммы (SHA-256) исходного JSONL-файла.
   - Валидация формата и типов полей каждой записи датасета.
   - Сверка фактического набора тикеров в датасете со списком отслеживания (predeclared watchlist).
2. **Протокол обработки ошибок (Error Treatment):**
   - Классификация 657 ошибок сбора по типам (таймаут, лимиты запросов, ошибки API).
   - Запрет на неявную фильтрацию пропущенных интервалов. Оценка доходности carry-стратегии должна производиться по двум сценариям: пессимистичному (ставка во время ошибки равна 0 или ведет к убытку из-за проскальзывания) и базовому.
3. **Разрешенные команды (Allowed Commands):**
   - Допускаются исключительно локальные команды чтения файлов и выполнения расчетно-аналитических скриптов (Pandas, Numpy) в изолированном окружении без исходящих сетевых запросов.
4. **Требования к артефактам (Artifact Expectations):**
   - Создание отчета по качеству данных `data_quality_report.md`.
   - Создание отчета по carry-анализу `funding_analysis.md` с явным учетом стоимости транзакций, проскальзывания (slippage) и доступной ликвидности.
   - Обновление файла `viability_assessment.json`.
5. **Жесткие блокирующие факторы (Hard Blockers) для paper-forward/live:**
   - Доля ошибок сбора данных за любой 24-часовой интервал превышает 15%.
   - Отсутствие учета проскальзывания (slippage) и комиссии в модели carry-стратегии.
   - Любая попытка импорта приватных ключей или инициализации live-ордеров.

## Какие есть риски
- **Риски переоптимизации:** Короткий период сбора данных (7 дней) может отражать локальный рыночный режим (funding regime), который не повторится в будущем.
- **Риски неполноты данных:** Высокий процент пропущенных циклов (~32.5%) может скрывать периоды резкого изменения ставок финансирования, приводя к переоценке прибыльности.
- **Операционные риски исполнения:** Ограниченная ликвидность на non-Binance площадках может сделать невозможным открытие и закрытие carry-позиций по расчетным ценам.

## Что нельзя потерять/исказить дальше
- Целостность исходных логов сбора данных без внесения ручных нелогируемых изменений.
- Полный состав predeclared watchlist (включая активы с нулевым или отрицательным финансированием для сохранения объективности картины).

## Решение
approve


# L3
## Что было сделано
- Приняты L1/L2 handoff Роя по checkpoint `trading_mvp funding final-review`.
- Active-run gate проверен: `READY_FOR_POSTPROCESS`, run `funding_collect_7d_spotliq_visible_20260617_185732`, `final=true`, `2016/2016` циклов, `50583` строк, `657` ошибок.
- Запущен guarded `tools/run_funding_final_review_visible.ps1 -NoPause` в research-only режиме.
- Final-review не допустил dataset к downstream rank/backtest/OOS/walk-forward/paper из-за data-quality gate: `min_rows_per_cycle=9`, строгий порог `20`, reason `min_min_rows_per_cycle`.
- Найден и исправлен баг wrapper-а: после guard-stop он пытался запускать `funding_watchlist_review.ps1` по несуществующему rank artifact и падал вторичной ошибкой.
- Повторная проверка с `-RunLabel guard_stop_verify_20260627 -NoPause` завершилась чисто: watchlist-review пропущен намеренно, причины guard-stop выведены явно.

## На чем основан вывод
- L1 Antigravity handoff: `levels/L1/handoff.md`, решение `approve`.
- L2 Antigravity handoff: `levels/L2/handoff.md`, решение `approve`.
- Guard output: `C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\funding\funding_final_review_guard_stop_verify_20260627.json`.
- Console log: `C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\run\funding_final_review_guard_stop_verify_20260627.console.log`.
- Исправленный файл: `C:\Users\koval\Documents\ZolotyayLopata\tools\run_funding_final_review_visible.ps1`.

## Что получилось хорошо
- Рой подключен до принятия решения по funding branch.
- Research-only границы соблюдены: no live orders, no API keys, no leverage/margin, no investment advice.
- Строгий data-quality gate не был ослаблен ради получения rank/backtest.
- Wrapper теперь различает корректный guard-stop и настоящую ошибку postprocess.

## Что требует доработки
- Funding branch нельзя продвигать в paper-forward на этом dataset.
- Нужно либо собрать более качественный funding dataset с меньшими провалами per-cycle coverage, либо временно отложить funding carry и перейти к уже одобренной Роем visible dense WS branch.
- Для следующего funding collect нужно явно мониторить per-cycle market coverage, чтобы не ждать 7 дней и не получить `min_rows_per_cycle < threshold` в конце.

## Какие есть риски
- Текущий 7d funding dataset имеет хороший общий объем, но худший цикл содержит только 9 строк, что ломает строгую полноту cross-market сравнения.
- Если ослабить порог без отдельного решения, можно получить переоптимизированный carry вывод на неполной панели рынков.
- Funding может быть структурно интересен, но на этом наборе данных нет допуска к economics/rank/paper-forward.

## Что нельзя потерять/исказить дальше
- Отказ funding final-review является data-quality rejection, а не доказательством отсутствия funding edge вообще.
- Нельзя утверждать winrate/PnL/rentability по funding, потому что rank/backtest/OOS/walk-forward не были созданы из-за guard-а.
- Следующий основной шаг цели должен быть либо исправление качества будущего funding collect, либо переход к visible dense WS collect/postprocess по sweep/reversal branch. Любой долгий прогон только видимо и после явного подтверждения пользователя.

## Решение
approve


# L4
## Что было сделано
- Выполнен L4 architecture/risk gate по результатам L1/L2 Роя и L3 Codex.
- Проверено, что funding final-review был запущен в research-only режиме и остановлен strict data-quality gate.
- Проверено, что исправление wrapper-а не ослабляет критерии стратегии: оно только корректно завершает guard-stop без запуска downstream watchlist-review при отсутствии rank artifact.
- Сформирован next-step contract для цели `trading_mvp`.

## На чем основан вывод
- Workflow handoffs L1-L3.
- Guard artifact `funding_final_review_guard_stop_verify_20260627.json`: `ok=false`, `status=not_ready_for_postprocess`, `data_quality_reasons=[min_min_rows_per_cycle]`, `min_rows_per_cycle=9`, threshold `20`.
- Повтор wrapper-а завершился с exit code 0 и сообщением `No rank artifact exists, so watchlist review is intentionally skipped`.
- Project rules: Visible Run Rule, Active Run Gate Rule, Trading Edge Scope Rule, Trading Swarm Rule.

## Что получилось хорошо
- Funding branch получил честную отбраковку на качестве данных до расчета PnL/rank.
- Нет ложного вывода о winrate, PnL или окупаемости на неполном dataset.
- Рой использован как независимый checkpoint, а не как замена строгим gates.
- Исправлен операционный баг, который мог путать guard-stop с поломкой postprocess.

## Что требует доработки
- Для funding branch нужен отдельный collector-quality improvement: ранний abort/alert при `min_rows_per_cycle` ниже порога, per-cycle coverage monitor, и, возможно, меньший universe или надежная ротация API при деградации бирж.
- Основной путь к цели после этого checkpoint: не funding paper-forward, а либо подготовка улучшенного funding collect, либо переход к ранее одобренной Роем visible dense WS branch для sweep/reversal event-quality/OOS.
- Если пользователь хочет не ждать новый 7d funding, следующий рациональный шаг: visible 6h WS collect только после явного подтверждения запуска.

## Какие есть риски
- Повторный funding collect без улучшения coverage может снова завершиться data-quality rejection.
- Переход к WS branch также не доказывает edge сам по себе; он только дает независимый плотный dataset для replay/OOS.
- Нельзя делать live или paper-forward из funding branch до прохождения data-quality, economics, OOS/walk-forward/stress и watchlist gates.

## Что нельзя потерять/исказить дальше
- Текущий вывод: funding carry branch `blocked_by_data_quality_on_current_7d_dataset`, а не `strategy accepted` и не `strategy impossible`.
- Не ослаблять `min_min_rows_per_cycle` ради результата без отдельного labeled relaxed experiment.
- Не запускать долгие процессы скрыто; любой collect/replay/grid/paper-forward только видимо и после явного подтверждения пользователя.

## Решение
approve

