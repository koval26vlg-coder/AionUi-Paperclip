# Запрос
Пользователь спросил "ну что приступим?" по проекту подработки с AI быстрыми задачами.

# Дата и агент
2026-06-30 17:23:12 +03:00, Codex

# Краткий план
Проверить gate/SML, взять текущий shortlist, не отправлять внешние сообщения без подтверждения, подготовить первую live-очередь откликов и точные тексты для ручной отправки.

# Что сделано
В C:\Users\koval\Documents\Подработка добавлены outreach/day1_send_queue.csv и outreach/day1_replies.md. В leads.csv добавлены live-лиды V001-V005 и старые сомнительные L010/L012/L017/L021/L027 помечены needs_reverify. Обновлен tools/score_leads.ps1, чтобы ready_to_apply поднимались выше, а needs_reverify исключались из топа. Добавлен docs/verification_notes.md.

# Проверки
Active run gate: READY_FOR_POSTPROCESS, задача не относится к trading_mvp. SML bootstrap выполнен. score_leads.ps1 -Top 10 выводит V003, V001, V002, V004 в топе и V005 в очереди. Import-Csv: 35 строк, 5 ready_to_apply, 5 needs_reverify, 5 shortlist.

# Риски и ограничения
Прямые URL старых shortlist строк частично вернули несовпадающие заголовки или 403, поэтому они не используются для отправки. Внешние отклики не отправлялись: пользователь должен вручную открыть карточку через свой аккаунт и подтвердить/отправить текст.

# Следующему агенту
Использовать outreach/day1_replies.md и outreach/day1_send_queue.csv. После ручной отправки менять send_status на sent/replied/test_task/won/lost. Не считать отклик отправленным заранее.
