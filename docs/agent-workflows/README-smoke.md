# Smoke Workflow

Этот файл фиксирует цель smoke-проверки иерархического workflow.

Проверяем цепочку:

1. Antigravity CLI выполняет `L1` research lead и готовит проверенный L1-handoff.
2. Antigravity CLI принимает `L1` и выполняет `L2` инженерную проверку.
3. Codex принимает `L2` и выполняет `L3` декомпозицию реализации, тесты и automation.
4. Codex принимает `L3` и выполняет `L4` архитектурный синтез.
5. Claude Code выполняет `finalize` и готовит отчет для пользователя.

Smoke workflow не запускает внешние интеграции, не пишет в Bitrix/Google и не относится к `trading_mvp`.

