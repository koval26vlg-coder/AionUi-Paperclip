# Решения по backlog: universe разрешён, H9 подготовлен как отдельный проект

Дата: 2026-07-02 ~13:00 +03
Агент: Claude Code

## Исходный запрос

Пользователь дал решения по двум открытым вопросам edge hypothesis backlog:

1. Universe-constraint — «все разрешаю, но если что имеем в виду, что была и такая задумка» → расширенный universe разрешён, исходная non-Binance идея сохраняется как базовый вариант.
2. H9 (airdrops/фарминг) — «активировать как отдельный проект вне trading_mvp, создам отдельный проект в Codex, пока все подготовь» → подготовить пакет для бутстрапа.

## Что сделано

1. **Обновлён backlog** `C:\Users\koval\Documents\ZolotyayLopata\docs\analysis\2026-07-02-edge-hypothesis-backlog.md`:
   - H1/H4: решение зафиксировано — прогоны в двух конфигурациях (`non_binance_baseline` и `extended`), у H1 блокеров больше нет;
   - H9: статус «активирован отдельным проектом (Codex)», ссылки на spec и handoff;
   - сводная таблица обновлена.
2. **Подготовлен пакет проекта airdrop-farming-ops** (по конвенции docs/specs — requirements/design/tasks):
   - `docs/specs/airdrop-farming-ops/requirements.md` — цель (максимизация EV/час), scope, out-of-scope (P2P/off-ramp, промышленный сибил, торговля), обязательная безопасность S1–S7 (секреты никогда в docs/SML/git; агенты не исполняют транзакции; лимиты капитала задаёт пользователь), критерии успеха 4 недель;
   - `docs/specs/airdrop-farming-ops/design.md` — структура папки проекта, JSON-схема opportunity ledger, цикл scouting→vetting→activation→tracking→harvest, разделение ролей, метрики;
   - `docs/specs/airdrop-farming-ops/tasks.md` — чеклист бутстрапа фазами 0–2 с явными запретами.
3. **Создан handoff для Codex**: `docs/handoffs/2026-07-02-claude-code-to-codex-airdrop-farming-project.md`.

## Изменённые файлы

- `C:\Users\koval\Documents\ZolotyayLopata\docs\analysis\2026-07-02-edge-hypothesis-backlog.md` (обновлён)
- `D:\AionUi-Paperclip\docs\specs\airdrop-farming-ops\requirements.md` (новый)
- `D:\AionUi-Paperclip\docs\specs\airdrop-farming-ops\design.md` (новый)
- `D:\AionUi-Paperclip\docs\specs\airdrop-farming-ops\tasks.md` (новый)
- `D:\AionUi-Paperclip\docs\handoffs\2026-07-02-claude-code-to-codex-airdrop-farming-project.md` (новый)
- этот файл журнала

## Проверки

- Формат spec соответствует существующей конвенции docs/specs (requirements/design/tasks, как в bitrix24-automation-hygiene).
- Handoff — по шаблону docs/templates/handoff.md.
- Границы безопасности trading_mvp не ослаблены; H9 полностью отделён (капитал/ключи/ledger).

## Риски и ограничения

- Spec H9 — research/process документ; юридические/налоговые вопросы RU-контекста остаются на пользователе.
- До задачи 7 tasks.md (лимиты капитала, порог EV/час, допустимый KYC) активация программ невозможна.

## Что проверить следующему агенту (Codex)

- Взять handoff `2026-07-02-claude-code-to-codex-airdrop-farming-project.md` и пройти tasks.md фазу 0.
- Не забыть задачу 7 (лимиты от пользователя) до первого scouting.
- В trading_mvp следующие шаги без изменений: E0 (fee evidence) + REST-сбор daily klines/funding для H1/H2.
