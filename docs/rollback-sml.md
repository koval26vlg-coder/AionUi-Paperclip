# Rollback-процедура Shared_Memory_Layer

Документ описывает, как откатить SML обратно на `aion-file-memory` на каждой из 4 фаз миграции. Источник истины — файлы в `docs/`, поэтому ни на одной фазе данные не теряются.

## Общий принцип

- **Данные в `docs/` не зависят от SML.** AGENTS.md, `docs/decisions.md`, `docs/tasks.md`, `docs/memory/layers/*`, `docs/agent-log/`, `docs/context-packs/context-pack-latest.md` — единственный источник истины. SML — индекс и MCP-фасад поверх них.
- **Индекс SML восстанавливается из файлов.** Если `var/sml/state.db` повреждён или сброшен, достаточно удалить `var/sml/` и запустить `SyncService.sync_all()` — все записи переиндексируются из `docs/` (маппинг в `tools/sml/file_watcher.py::FILE_TO_TYPE`).
- **`aion-file-memory` остаётся в конфигах клиентов** на фазах 1–3. Его удаление — только в Фазе 4.

## Условия rollback

Откатываемся, если в течение 24 часов после переключения одного из агентов наблюдается хотя бы одно из:

- `Operation_Log` содержит ≥ 0.5% записей с `result ∈ {io_error, timeout, conflict}` от общего числа операций;
- любая запись с `reason_category = "secret_rejected"` оказалась ложным срабатыванием (проверено вручную);
- `sml.ping` вернул HTTP/RPC-ошибку более 3 раз подряд;
- агент сообщил о потере контекста между сессиями (Memory_Record не найден после перезапуска).

При rollback наблюдение не останавливается — после отката продолжаем собирать метрики, чтобы понять причину.

## Фаза 1 → базовое состояние

**Что было сделано:** Оба сервера (`sml` и `aion-file-memory`) зарегистрированы в `~/.codex/config.toml`, `.cursor/mcp.json`, `.kiro/settings/mcp.json`.

**Rollback:**

1. В каждом конфиге удалить блок `sml` (секцию `[mcp_servers.sml]` в Codex, объект `"sml"` в Cursor/Kiro).
2. Перезапустить MCP-клиенты. Старый `aion-file-memory` продолжает работать без изменений.
3. Файлы в `var/sml/` и `logs/sml-*.ndjson` можно удалить или оставить — они не влияют на `aion-file-memory`.

**Время:** ≤ 10 минут.

## Фаза 2 → Фаза 1

**Что было сделано:** Один из трёх агентов (Codex, Cursor или Kiro) переключил дефолтный сервер памяти на `sml`.

**Rollback:**

1. В конфиге этого агента поменять порядок серверов: `aion-file-memory` снова первым.
2. Перезапустить только этого агента. Остальные продолжают на `sml`.
3. Если в `logs/sml-operation-log.ndjson` видны причины сбоя — зафиксировать их в `docs/agent-log/` как post-mortem.

**Время:** ≤ 5 минут на агента.

## Фаза 3 → Фаза 2

**Что было сделано:** Write-эндпоинты `aion-file-memory` отключены, всё пишет SML.

**Rollback:**

1. В клиентских обёртках отменить no-op на `add_memory`, `add_agent_log`, `build_context_pack` для `aion-file-memory`.
2. Проверить, что последние записи SML (`Memory_Record` типа `decision` и `agent_log` за период after Фаза 3) отражены в файлах `docs/` — SML уже пишет их синхронно, так что данные не потеряны.
3. Если SML за период Фазы 3 создал записи **только** в `var/sml/state.db` без file writer (например, `sml.write` с `source_file=None` через прямой MCP-вызов), экспортировать их в `docs/memory/layers/facts.md` руками через скрипт `tools/sml/bench/export_facts.py` (ещё не написан — однажды понадобится, пока опциональный шаг).

**Время:** ≤ 30 минут.

## Фаза 4 → Фаза 3

**Что было сделано:** `aion-file-memory` удалён из всех конфигов MCP-клиентов.

**Rollback:**

1. Вернуть блок `aion-file-memory` в `~/.codex/config.toml`, `.cursor/mcp.json`, `.kiro/settings/mcp.json`. Шаблон блока — в `docs/mcp-memory.md` или в истории git.
2. Перезапустить MCP-клиенты.
3. `aion-file-memory` автоматически пересоберётся по файлам `docs/` при первом `read_context_pack`.

**Время:** ≤ 15 минут.

## Катастрофический rollback (SML сломан, файлы целы)

Если ни одна из фазных процедур не работает, а `docs/` цел:

1. Остановить `sml` во всех MCP-клиентах (удалить блок в конфиге, перезапустить клиент).
2. Удалить каталог `var/sml/` целиком и лог-файлы `logs/sml-*.ndjson`.
3. Оставить `aion-file-memory` как основной сервер.
4. При желании восстановить SML: выполнить `python -m tools.sml.mcp_adapter --selfcheck` — он заново создаст `var/sml/state.db`. Затем:

   ```python
   from tools.sml.file_watcher import SyncService
   from tools.sml.temporal_store import open_store
   from tools.sml.operation_log import OperationLog
   from pathlib import Path
   root = Path("D:/AionUi-Paperclip")
   store = open_store(root / "var/sml/state.db")
   op_log = OperationLog(root / "logs")
   sync = SyncService(store=store, op_log=op_log, root=root)
   print(sync.sync_all())
   ```

   — переиндексирует все известные файлы из `docs/` и `AGENTS.md` в новую БД.

## Проверка целостности после rollback

На каждом уровне rollback после возврата:

1. Запустить `python -m tools.sml.mcp_adapter --selfcheck` (должен напечатать `sml-selfcheck-ok`).
2. Запустить `python -m pytest tools/sml/tests/ -q` — все тесты SML зелёные. Текущий ориентир: `141 passed`.
3. Проверить, что `docs/context-packs/context-pack-latest.md` первой строкой содержит `# Контекстный пакет` (и `tools/watch-memory.ps1`, и `sml.build_context_pack` могут его корректно пересобрать).
4. Зафиксировать факт rollback в `docs/agent-log/` через `sml.add_log` (если rollback не до Фазы 0) или вручную.

## Решения и последствия

Rollback не является редким или экстренным сценарием. Он встроен в архитектуру: SML с самого начала проектировался так, чтобы файлы оставались первичными. Любая процедура отката безопасна, если `docs/` не повреждены.

Если повреждены и `docs/`, и `var/sml/` одновременно — восстановление идёт из последнего `docs/context-packs/context-pack-<timestamp>.md` и git-истории `docs/`. Это выходит за рамки rollback SML и обсуждается в отдельной процедуре disaster recovery.
