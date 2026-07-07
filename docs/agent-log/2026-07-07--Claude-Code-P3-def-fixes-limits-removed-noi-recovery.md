# 2026-07-07 — Claude Code — P3: DEF-02/03, удаление лимитов, восстановление NOI

## Запрос пользователя

Решения по P3: DEF-02/DEF-03 — делать; HH Booster — отложить; NOI VPS — восстанавливать;
лимиты агентов — убрать опцию (пользователь ожидал другого поведения).

## Что сделано

### DEF-02 / DEF-03 (сделаны + тесты)

- **DEF-02**: в `tools/agent_workflow.py submit-work` добавлены `--expect-level` и
  `--expect-assignment`; guard падает до записи handoff, если текущий assignment не совпал.
- **DEF-03**: `cmd_status` и `tools/watch-agent-workflows.ps1` теперь отделяют active blockers
  (показываются полностью) от `resolved=true` (показываются счётчиком).
- Тесты: `test_submit_work_expect_level_guard_rejects_wrong_level`,
  `test_status_separates_active_and_resolved_blockers`. `pytest test_agent_workflow.py` → 17 passed
  (было 15).

### Лимиты агентов (опция убрана)

Пользователь ожидал авто-отслеживания остатка/reset, но провайдеры не отдают эти значения
локально. Убрана именно опция ручного отслеживания, наблюдаемый расход сохранён:
- удалён `docs/agent-limits/limits-config.json`;
- `agent_limit_monitor.py build_report`: убраны колонки Limit/Remaining/Reset и секция
  «Reset And Remaining»; отчёт теперь `Agent | Status | Observed tokens | Cost`;
- `docs/agent-limits/README.md` обновлён (таблица без остатка, файл убран из списка).
- Drift-дашборд и тесты не тронуты — оба консумера limits-config уже терпят его отсутствие.
- Проверки: `test_agent_limit_monitor.py` + `test_export_drift_workflow.py` → 6 passed;
  живой smoke монитора выдаёт чистый 4-колоночный отчёт.

### NOI VPS (восстановление — почти завершено)

Диагностика `check-antigravity-noi.ps1` показала, что **SSH уже восстановился**:
`TCP: connected`, `SSH banner: SSH-2.0-OpenSSH_8.9p1`, `SSH_OK`, `agy 1.0.13` на сервере.
Console/rescue больше не нужен. `-Smoke` доходит до Google OAuth URL и падает по таймауту —
остался единственный шаг: пользователь завершает Google OAuth (`start-antigravity-noi-auth.ps1`),
затем smoke. Написан `docs/history/noi-vps-recovery-runbook.md`; задача в tasks.md переведена
в «В работе» с актуальным состоянием.

### HH Booster — отложен

Перенесён из «Ждут решения» в «Отложенные» tasks.md с пометкой: запуск требует 14 дней ручного
outreach, стартовать только при явной готовности; rehearsal протух, нужен свежий day-0.

## Проверки

- pytest: 17 (workflow) + 6 (limits/drift) passed; py_compile OK; SML selfcheck OK.

## Следующему агенту / пользователю

- NOI: завершить Google OAuth и smoke (шаг пользователя).
- P3 закрыт со стороны инфраструктуры; открытых дефектов workflow больше нет (кроме
  Antigravity L1/L2 runner hardening, вынесенного отдельно).
