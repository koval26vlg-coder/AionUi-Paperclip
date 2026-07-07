# airdrop-farming-ops: дизайн

Дата: 2026-07-02
Автор: Claude Code
Статус: проект дизайна для бутстрапа Codex. Уточняется при реализации.

## Структура проекта (предложение)

```text
<project-root>/                  # например C:\Users\koval\Documents\AirdropFarmOps
  AGENTS.md                      # правила агентов: роли, границы, безопасность S1-S7
  README.md                      # что это, как пользоваться
  docs/
    security-rules.md            # S1-S7 развёрнуто + анти-фишинг протокол + официальные домены
    weekly-reviews/              # еженедельные отчёты
    agent-log/                   # журнал работ агентов по проекту
  ledger/
    opportunities.json           # машиночитаемый реестр (схема ниже)
    opportunities.md             # генерируемая человекочитаемая витрина
    harvested.json               # закрытые программы с фактическим результатом
  tools/
    ledger.py                    # CRUD + валидация схемы + генерация витрины
    scoring.py                   # расчёт EV/час, приоритезация
    deadlines.py                 # ближайшие снапшоты/клеймы/окончания
    weekly_review.py             # сборка weekly-отчёта
  WEEKLY_REVIEW.cmd              # запускатель отчёта
  CHECK_DEADLINES.cmd            # запускатель дедлайн-трекера
```

## Схема записи ledger (opportunities.json)

```json
{
  "id": "opp-2026-07-02-001",
  "name": "...",
  "category": "points|launchpool|quest|testnet|referral|competition|grant",
  "source_url": "...",
  "official_domains": ["..."],
  "discovered_at": "2026-07-02",
  "deadline": "2026-08-01|null",
  "snapshot_rumor": "текст|null",
  "requirements": {
    "capital_usd": 0,
    "lockup_days": 0,
    "time_hours_est": 0,
    "kyc": "none|light|full",
    "geo_restrictions": "...",
    "chain": "...",
    "wallet_tier": "operational|disposable"
  },
  "ev": {
    "reward_pessimistic_usd": 0,
    "reward_base_usd": 0,
    "reward_optimistic_usd": 0,
    "probability": 0.0,
    "costs_usd": 0,
    "ev_per_hour_base": 0
  },
  "risk_flags": ["unaudited_contract", "sybil_sensitive", "kyc_required", "geo_blocked_ru", "..."],
  "status": "scouted|vetted|active|harvested|dropped",
  "status_reason": "...",
  "actual_result": {"reward_usd": null, "hours_spent": null, "closed_at": null},
  "notes": "..."
}
```

## Рабочий цикл

1. **Scouting** (агент): источники — агрегаторы аирдропов, анонсы бирж (MEXC/Gate launchpad), соцканалы протоколов, экосистемные календари. Каждая находка → запись `scouted` с черновой EV-оценкой.
2. **Vetting** (агент + пользователь): проверка официальных доменов, аудитов, правил программы, сибил-политики, гео-ограничений. Итог: `vetted` c финальным скорингом или `dropped` с причиной.
3. **Activation** (только пользователь): решение об участии, выделение капитала в пределах лимитов, выполнение on-chain/аккаунт-действий. Агент готовит пошаговый чеклист, но не исполняет.
4. **Tracking** (агент): дедлайны, снапшоты, изменения правил, напоминания.
5. **Harvest/Close** (пользователь исполняет, агент фиксирует): факт → `harvested.json`, калибровка прогнозов.
6. **Weekly review** (агент): витрина, топ-приоритеты, что дропнуть, факт vs прогноз.

## Разделение ролей

- **Агенты (Codex/Claude Code)**: разведка, оценка, ledger, отчёты, напоминания, скрипты. Никогда: транзакции, логины, хранение секретов, изменение лимитов капитала.
- **Пользователь**: активация программ, все on-chain/аккаунт-действия, KYC-решения, лимиты капитала.

## Безопасность (архитектура)

- Ярусы кошельков (S2): адреса ярусов можно хранить в ledger (публичная информация), ключи — никогда.
- `security-rules.md` включает: процедуру проверки домена перед любым interaction-чеклистом, правило «агент даёт ссылку только из official_domains», регулярный график revoke.
- В `AGENTS.md` проекта прописать: любые упоминания seed/ключей в задачах — немедленный отказ и пометка риска.

## Метрики проекта

- EV/час по портфелю активных программ (base-сценарий).
- Фактический ROI/час по harvested (скользящее окно 3 месяца).
- Калибровка: отношение факт/прогноз по закрытым программам.
- Счётчик инцидентов безопасности (цель: 0).

## Интеграция с общей памятью

- Bootstrap: стандартный `agent-memory-bootstrap.ps1` при работе из папки проекта.
- Итоги недель и решения — в `docs/agent-log/` проекта + важное в SML.
- Проект не смешивается с trading_mvp: ни общего капитала, ни общих ключей, ни общих ledger.
