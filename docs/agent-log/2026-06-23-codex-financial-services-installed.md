# 2026-06-23 20:02 +03:00 — Codex — Financial services agents installed

## Исходный запрос
Пользователь попросил установить все нужные финансовые agents/skills из материала `10 финансовых агентов Claude.pdf` с мерами предосторожности.

## Краткий план
- Проверить active-run gate и Aion SML bootstrap.
- Сделать backup текущих agent/Claude/Codex manifest/config.
- Добавить Claude marketplace `anthropics/financial-services`.
- Установить first-party Claude financial-services plugins и проверить `claude plugin list`.
- Создать локальный `finance-workflow-router` skill и разложить его в Codex/Claude/.agents/shared roots.
- Обновить manifests и context.

## Что сделано
- Active-run gate проверен: `trading_mvp` был `RUNNING`; trading-постпроцесс не запускался.
- Backup создан: `C:\Users\koval\Documents\Codex\2026-05-18\npx-skills-add-anthropics-claude-code\agent-skills\backups\financial-services-20260623-195616`.
- Claude marketplace добавлен:
  - `claude-for-financial-services`
  - source `anthropics/financial-services`
- Установлены и проверены как `√ enabled`:
  - core: `financial-analysis`
  - 10 named agents: `pitch-agent`, `meeting-prep-agent`, `market-researcher`, `earnings-reviewer`, `model-builder`, `valuation-reviewer`, `gl-reconciler`, `month-end-closer`, `statement-auditor`, `kyc-screener`
  - first-party vertical bundles: `investment-banking`, `equity-research`, `private-equity`, `wealth-management`, `fund-admin`, `operations`
- Не установлены намеренно:
  - partner-built LSEG/S&P plugins
  - Claude for Microsoft 365 admin tooling
  - paid/provider financial MCP credentials
- Создан и валидирован локальный skill `finance-workflow-router`.
- `agent-workflow-router` обновлен: finance/business/investment tasks теперь route через `finance-workflow-router`.

## Измененные файлы
- `C:\Users\koval\.codex\skills\finance-workflow-router\SKILL.md`
- `C:\Users\koval\.codex\skills\finance-workflow-router\references\financial-services-map.md`
- `C:\Users\koval\.claude\skills\finance-workflow-router\SKILL.md`
- `C:\Users\koval\.agents\skills\finance-workflow-router\SKILL.md`
- `C:\Users\koval\Documents\Codex\2026-05-18\npx-skills-add-anthropics-claude-code\agent-skills\finance-workflow-router\SKILL.md`
- `C:\Users\koval\.codex\skills\agent-workflow-router\SKILL.md`
- `C:\Users\koval\.claude\skills\agent-workflow-router\SKILL.md`
- `C:\Users\koval\.agents\skills\agent-workflow-router\SKILL.md`
- `C:\Users\koval\Documents\Codex\2026-05-18\npx-skills-add-anthropics-claude-code\agent-skills\agent-workflow-router\SKILL.md`
- `agent-skills\INSTALL_MANIFEST.md`
- `agent-skills\install-manifest.json`
- `agent-skills\FINANCIAL_SERVICES_INSTALL_MANIFEST.md`
- `agent-skills\financial-services-install-manifest.json`

## Проверки
- `claude plugin list` показал все 17 financial-services plugins как `√ enabled`.
- `quick_validate.py` прошел для `finance-workflow-router`.
- `quick_validate.py` прошел для обновленного `agent-workflow-router` после удаления старого невалидного frontmatter key `compatibility`.
- Все 4 skill roots содержат `finance-workflow-router/SKILL.md`.

## Риски и ограничения
- Provider financial MCP connectors не настроены: они требуют отдельные подписки/API-ключи и явное решение пользователя.
- Финансовые агенты используются только для draft analysis и decision support. Запрещены автотрейдинг, финальные investment recommendations, ledger posting, KYC approval и юридическая/финансовая финализация.
- После установки желательно перезапустить Claude Code и Codex, чтобы все новые skills/plugins точно подхватились в новых сессиях.

## Следующий агент
При финансовых задачах сначала использовать `finance-workflow-router`. Для Claude Code можно использовать установленные financial-services plugins; для Codex/Antigravity использовать локальный skill и source-grounded workflow.
