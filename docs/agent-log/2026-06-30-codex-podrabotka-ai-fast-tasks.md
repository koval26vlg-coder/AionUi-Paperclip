# Запрос
Реализовать план подработки с AI через быстрые задачи: рабочая таблица лидов, офферы, источники, правила отбора, портфолио-примеры и проверяемый ежедневный процесс.

# Дата и агент
2026-06-30 15:35:29 +03:00, Codex

# Краткий план
Создать практический комплект в C:\Users\koval\Documents\Подработка: leads.csv, source watchlist, shortlist, офферы/отклики, правила, portfolio samples и скрипт сортировки лидов.

# Что сделано
Созданы файлы README.md, leads.csv, docs/day1_shortlist.md, docs/offers_and_replies.md, docs/source_watchlist.md, docs/daily_workflow.md, docs/rules.md, samples/portfolio_marketplace_card.md, samples/portfolio_research_table.csv, samples/portfolio_voice_agent_prompt.md, tools/score_leads.ps1.

# Измененные файлы
C:\Users\koval\Documents\Подработка\README.md
C:\Users\koval\Documents\Подработка\leads.csv
C:\Users\koval\Documents\Подработка\docs\*.md
C:\Users\koval\Documents\Подработка\samples\*
C:\Users\koval\Documents\Подработка\tools\score_leads.ps1

# Проверки
Запущен tools/score_leads.ps1: сортировка работает. Import-Csv подтвердил 30 строк, 10 shortlist, 2 skip, 9 watch. Active run gate проверен: READY_FOR_POSTPROCESS; к trading_mvp задача не относится.

# Риски и ограничения
Большая часть конкретных стартовых лидов собрана из открытого FL.ru AI-раздела, потому что Kwork/Workzilla/HH часто требуют входа для деталей конкретных задач. Эти каналы добавлены в ежедневный watchlist. Отклики и публикации не отправлялись, аккаунты и оплата остаются на пользователе.

# Следующему агенту
Ежедневно запускать C:\Users\koval\Documents\Подработка\tools\score_leads.ps1, добавлять свежие строки в leads.csv, отправлять 5 ручных откликов, обновлять статусы applied/replied/test_task/won/lost и считать конверсию через 3 дня.
