# Отчёт агента

- Дата и время: 2026-06-18
- Агент: Claude Code

## Запрос пользователя

Проверить проект AionUi-Paperclip, дать оценку и рекомендации (через несколько моделей), затем реализовать правки P0/P2/P3 и P1 с поправкой: активные исполнители — Codex, Claude Code, Gemini; Cursor/Kiro/MiMo вывести из схемы.

## Краткий план

- P0: подключить экспорт дашборда к watcher; нормализовать `author_agent` в SML.
- P2: фиксы Aion Vision (цвета типов, guard графа, мёртвый endpoint).
- P3: бэкапы БД SML с ротацией; достроить CLI ядра.
- P1: удалить конфиги Cursor/Kiro/MiMo, обновить документацию, сохранить ценные спецификации.

## Что сделано

- **P0.1** В `tools/watch-memory.ps1` добавлены `Build-DashboardData` (экспорт `aion-data.json`) и `Backup-SmlDatabase` — теперь витрина и бэкап обновляются автоматически. Ранее `aion-data.json` отставал от БД на ~месяц.
- **P0.2** Добавлена `normalize_author` в `tools/sml/validation.py`, применена в `make_new_record`. Разовый прогон `tools/normalize-sml-authors.py` свёл 7 «авторов» к 4 реальным (codex→Codex: 17 зап., gemini/Gemini-CLI→Gemini CLI: 2 зап.).
- **P2.1** `RecordCard.tsx`: `getTypeColor` покрывает все 8 типов (было 3).
- **P2.2** `NexusGraph.tsx`: guard на пустой массив узлов (раньше давал NaN-координаты и пустой SVG).
- **P2.3** `dashboardData.ts`: убран мёртвый `/api/sml-dashboard` (лишний 404 на каждой загрузке).
- **P3.1** `tools/backup-sml.py`: консистентный бэкап через `VACUUM INTO` с ротацией в `var/sml/backups/`, флаг `--if-stale` для watcher.
- **P3.2** `tools/sml/core.py`: CLI `selfcheck | ping | stats` (раньше была WIP-заглушка).
- **P1** Удалены `.cursor/`, `.kiro/`, `.mimocode/` и запускатели `OPEN-KIRO-RU.cmd`, `OPEN-MIMO-SML.cmd`, `CHECK-MIMO-SML.cmd`. Спецификации из `.kiro/specs/` перенесены в `docs/specs/`. Обновлены `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/agents.md`, `docs/current-context.md`, `docs/tasks.md`, `docs/memory/layers/constraints.md`, `tools/open-agent-workspace.ps1`. Удалён `docs/mimo-code-integration.md`. Решение записано в `docs/decisions.md`.

## Изменённые файлы

- `tools/watch-memory.ps1`, `tools/sml/validation.py`, `tools/sml/temporal_store.py`, `tools/sml/core.py`, `tools/sml/__init__.py`
- `tools/normalize-sml-authors.py` (новый), `tools/backup-sml.py` (новый), `tools/open-agent-workspace.ps1`
- `apps/aion-vision/src/components/dashboard/RecordCard.tsx`, `.../NexusGraph.tsx`, `apps/aion-vision/src/lib/dashboardData.ts`
- `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/agents.md`, `docs/current-context.md`, `docs/tasks.md`, `docs/decisions.md`, `docs/memory/layers/constraints.md`
- Перенос: `.kiro/specs/*` → `docs/specs/*`. Удалено: `.cursor/`, `.kiro/`, `.mimocode/`, 3 `.cmd`, `docs/mimo-code-integration.md`

## Проверки

- `python -m tools.sml.core selfcheck` → `sml-selfcheck-ok`
- `python -m tools.sml.core stats` → 4 автора (Codex 204, Gemini CLI 15, kiro 2, Cursor Agent 2)
- `tools/backup-sml.py` → создан `var/sml/backups/state-2026-06-18.db`; `--if-stale` корректно пропускает повтор
- Экспорт дашборда → `status: live`, 223 записи

## Риски и ограничения

- Нормализация на входе применится к новым записям только после перезапуска MCP-сервера `sml` у активных клиентов: живой процесс держит старый код. До перезапуска новые записи `codex` нужно периодически прогонять через `normalize-sml-authors.py`.
- Историческая память Cursor/Kiro (по 2 записи) сохранена намеренно — это контекст, не удалялась.
- TypeScript-правки не проверены сборкой в этой сессии (нужен `npm run build`/`lint` в `apps/aion-vision`).

## Что проверить следующему агенту

- Перезапустить MCP `sml` и убедиться, что новые записи пишутся каноническими именами.
- Прогнать `npm run lint && npm run build` в `apps/aion-vision`.
- Убедиться, что watcher после изменения документов пересобрал `aion-data.json` и сделал бэкап.
