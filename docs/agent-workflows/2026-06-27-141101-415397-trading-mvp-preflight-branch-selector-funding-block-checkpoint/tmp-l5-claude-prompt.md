Ты Claude Code L5 в workflow Рой. Режим: финальное независимое review-only заключение. Не запускай команды, не проси API/live orders, не предлагай investment advice.

Задача: проверить checkpoint trading_mvp: funding dataset заблокирован по data_quality:min_min_rows_per_cycle; Codex усилил preflight/branch selector guard; L1/L2 Antigravity approve; L3/L4 Codex approve. Нужно вынести решение approve/revise/escalate/block.

Contract:
{
  "workflow_id": "2026-06-27-141101-415397-trading-mvp-preflight-branch-selector-funding-block-checkpoint",
  "title": "trading_mvp preflight branch-selector funding-block checkpoint",
  "state": "ready_for_final",
  "created_at": "2026-06-27T14:11:01+03:00",
  "updated_at": "2026-06-27T14:15:10+03:00",
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
      "submitted_at": "2026-06-27T14:12:37+03:00",
      "approved_at": "2026-06-27T14:12:37+03:00"
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
      "submitted_at": "2026-06-27T14:13:50+03:00",
      "approved_at": "2026-06-27T14:14:14+03:00"
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
      "submitted_at": "2026-06-27T14:14:42+03:00",
      "approved_at": "2026-06-27T14:14:43+03:00"
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
      "submitted_at": "2026-06-27T14:15:10+03:00",
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
    "long_running": true,
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


Brief:
Проверить текущий checkpoint trading_mvp после блокировки 7d funding dataset по data_quality:min_min_rows_per_cycle. Контекст: active gate READY_FOR_POSTPROCESS только формально; funding postprocess/rank/backtest/paper-forward запрещены на текущем dataset; Codex усилил trading_edge_preflight.ps1 source-level guard, чтобы branch selector сохранял original_scorecard_next_action, но текущий funding next_action был overridden на blocked_by_swarm_do_not_run_7d_funding_collect_or_final_review; тесты trading_mvp 205 OK; start_ws_collect_visible.ps1 -PlanOnly не запускает долгий прогон без подтверждения. Задача Роя: независимо проверить, достаточно ли guard/readback/test покрытия, нет ли stale funding command leakage, и подтвердить следующий research-only шаг: явное пользовательское подтверждение видимого 6h WS collect, либо указать, что надо исправить до запуска. Запрещено запускать collectors/backtests/grid/search/postprocess/live orders/API keys/leverage/margin; только review/checkpoint по файлам и коротким read-only проверкам.


Latest handoff:
## Что было сделано
Codex L4 выполнил architecture/risk gate текущего `trading_mvp` checkpoint после L1/L2/L3. Проверен контракт цели: funding dataset заблокирован, WS branch является следующим допустимым proof step, long-run запуск требует явного пользовательского подтверждения и видимого monitor/terminal.

## На чем основан вывод
- Gate output фиксирует: `READY_FOR_POSTPROCESS` только формально; `postprocess_block.ok=false`; причина `data_quality:min_min_rows_per_cycle`, `min_rows_per_cycle=9`.
- Unit suite: `205 tests OK`.
- Preflight: `ok=true`, `READY_FOR_EDGE_PROOF_STEP`, `branch_selector_funding_block_override=pass`.
- `start_ws_collect_visible.ps1` имеет hard stop: если нет `-ConfirmedLongRun` и нет `-PlanOnly`, команда падает с явной ошибкой. Это нужная защита для visible long run.
- `-PlanOnly` возвращает `would_start=false`, `requires_confirmed_long_run=true`.

## Что получилось хорошо
- Guard разделяет две ветки корректно: funding blocked; WS collect allowed only as next research data-collection step.
- Риск случайного запуска long collector снижен через явный флаг `-ConfirmedLongRun` и Active Run Gate.
- Старая funding scorecard-команда не уничтожается, а архивируется в `original_scorecard_next_action`, что сохраняет трассируемость.

## Что требует доработки
- Перед реальным 6h WS collect желательно показать пользователю точную confirmed command, чтобы подтверждение было предметным, а не абстрактным.
- Позже можно усилить funding wrappers отдельным guard: если dataset заблокирован, wrapper final-review/rank/backtest должен сам отказываться. Это отдельная защита, но не blocker для WS collect.

## Какие есть риски
- Если пользователь вручную запустит funding wrapper напрямую, минуя next-step scripts, возможен расход времени на уже заблокированную ветку. Этот риск управляем отдельной будущей hardening-задачей.
- Новый WS collect может снова дать недостаточную плотность или качество данных; это не failure стратегии, а фильтр proof pipeline.
- Нельзя переходить к paper/live только по результату collect; нужен guarded postprocess, replay validation, OOS/walk-forward/stress/economics.

## Что нельзя потерять/исказить дальше
- Текущий funding dataset не использовать для rank/backtest/paper-forward.
- Следующий основной шаг только после явного подтверждения: видимый 6h WS collect по `start_ws_collect_visible.ps1 ... -ConfirmedLongRun`.
- Research-only: no live orders, no API keys, no leverage/margin, no investment advice.

## Решение
approve


Events:
{"time": "2026-06-27T14:11:01+03:00", "event": "workflow_created", "agent": "Codex"}
{"time": "2026-06-27T14:12:36+03:00", "event": "level_claimed", "agent": "Antigravity CLI", "executor": "Codex", "level": "L1", "assignment": "L1"}
{"time": "2026-06-27T14:12:37+03:00", "event": "level_submitted", "agent": "Antigravity CLI", "executor": "Codex", "level": "L1", "assignment": "L1"}
{"time": "2026-06-27T14:12:37+03:00", "event": "level_approved", "agent": "Antigravity CLI", "executor": "Codex", "level": "L1", "assignment": "L1", "next_level": "L2", "next_assignment": "L2"}
{"time": "2026-06-27T14:13:49+03:00", "event": "level_claimed", "agent": "Antigravity CLI", "executor": "Codex", "level": "L2", "assignment": "L2"}
{"time": "2026-06-27T14:13:50+03:00", "event": "level_submitted", "agent": "Antigravity CLI", "executor": "Codex", "level": "L2", "assignment": "L2"}
{"time": "2026-06-27T14:14:14+03:00", "event": "level_approved", "agent": "Codex", "executor": "Codex", "level": "L2", "assignment": "L2", "next_level": "L3", "next_assignment": "L3"}
{"time": "2026-06-27T14:14:42+03:00", "event": "level_claimed", "agent": "Codex", "executor": "Codex", "level": "L3", "assignment": "L3"}
{"time": "2026-06-27T14:14:42+03:00", "event": "level_submitted", "agent": "Codex", "executor": "Codex", "level": "L3", "assignment": "L3"}
{"time": "2026-06-27T14:14:43+03:00", "event": "level_approved", "agent": "Codex", "executor": "Codex", "level": "L3", "assignment": "L3", "next_level": "L4", "next_assignment": "L4"}
{"time": "2026-06-27T14:15:10+03:00", "event": "level_claimed", "agent": "Codex", "executor": "Codex", "level": "L4", "assignment": "L4"}
{"time": "2026-06-27T14:15:10+03:00", "event": "level_submitted", "agent": "Codex", "executor": "Codex", "level": "L4", "assignment": "L4"}


Верни markdown с разделами:
## Verdict
## Evidence Reviewed
## Findings
## Required Before Next Run
## Decision

В Decision укажи одно слово: approve / revise / escalate / block.
