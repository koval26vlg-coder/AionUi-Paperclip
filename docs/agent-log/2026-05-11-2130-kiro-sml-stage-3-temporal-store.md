# Отчет агента

## Дата и время

2026-05-11 21:30

## Агент

kiro (оркестратор, автономное исполнение Этапа 3)

## Исходный запрос

«Да погнали!» — продолжение работы по tasks.md. Этап 3: Temporal_Store на SQLite + WAL.

## Закрытые задачи (3.1–3.9)

- **3.1 Схема БД** — `tools/sml/temporal_store.py`, таблицы `records`, `records_history`, `sync_state`, `schema_migrations`. WAL-режим, synchronous=NORMAL, foreign_keys=ON. Каталог создаётся автоматически.
- **3.2 Индексы** — 6 индексов из design §8.1: `idx_records_id`, `idx_records_current`, `idx_records_type_updated`, `idx_records_supersedes`, `idx_records_source_file`, плюс `idx_history_id_from`. EXPLAIN QUERY PLAN подтверждает использование `idx_records_current`.
- **3.3 CRUD** — `insert`, `read_by_id`, `exists`, `update_fields`, `delete` (soft). Параметризованные запросы, дубликат id → `ConflictError`, missing id → `NotFoundError`. История пишется автоматически в `records_history`.
- **3.4 Supersede** — атомарно в `BEGIN IMMEDIATE...COMMIT`. Валидация `new_id` и всех `old_ids`, запрет self-supersede, запрет на уже суперседированные записи. При любой ошибке — полный откат.
- **3.5 Temporal_Query** — `query_at(at)` через `records_history`, фильтрация по типу и `is_current` на момент `at`, отклонение меток в будущем и до первой записи.
- **3.6 Durability** — WAL + `synchronous=NORMAL`, `wal_checkpoint(TRUNCATE)` при закрытии. Любая IO-ошибка → `IOErrorSML` без частичного состояния.
- **3.7 Миграции** — `schema_migrations(version, applied_at)`, применяются строго по возрастанию, idempotent при повторном запуске.
- **3.8 Тесты** — 20 тестов (см. ниже), все зелёные.
- **3.9 Бенчмарк** — **p99 = 0.058 мс** (целевой SLA 200 мс, превышен в 3400 раз). Вставка 10 000 записей за 2.41 с (4155 rec/s).

## Фиксы на ходу

- **Миграции**: `executescript()` SQLite сам открывает/закрывает транзакцию. Убрал ручные `BEGIN/COMMIT/ROLLBACK` — оставил только `executescript` + INSERT в autocommit.
- **Test query_at**: обратился к колонке `updated_at` в `records_history` (её там нет). Поправил на `valid_from`.

## Тесты (44 passed, 3.03 с)

### Unit (test_temporal_store.py) — 17 тестов

- CRUD: insert/read roundtrip, дубликат id, missing id, update + history, unknown id в update, soft delete.
- Supersede: happy path, unknown new_id, unknown old_id, atomicity при конфликте в середине списка (P5), self-supersede отклонён.
- Temporal query: возвращает состояние на метку, отклоняет будущее, отклоняет до первой записи.
- Инфраструктура: миграции idempotent, durability across reopen, WAL включён, индекс idx_records_current используется в EXPLAIN.

### Property-based (test_temporal_store_properties.py) — 2 свойства

- **P1 Durability** — hypothesis генерирует до 20 записей на тест, 50 прогонов, после close + open все записи читаются побайтово.
- **P3 Monotonicity** — hypothesis генерирует 1–15 записей, 30 прогонов, подтверждает что без явного supersede/delete `is_current=true` и `superseded_by_id=None`.

Итог: **44 passed in 3.03 s** (включая ранее написанные 24 теста Этапа 2).

## Бенчмарк sml.read на 10 000 записей

```
Inserted 10000 records in 2.41s (4155.3 rec/s)
read_by_id over 1000 samples: mean=0.023ms, p50=0.019ms, p95=0.044ms, p99=0.058ms
SLA p99 ≤ 200.0ms → OK
```

Запас по SLA огромный — primary key lookup на SQLite WAL с WAL checkpoint работает субмиллисекундно. Это даёт пространство для MCP-адаптера (задача 5.1) и JSON-сериализации, не нарушая Req 11.3.

## Изменённые файлы

- `tools/sml/temporal_store.py` — ядро слоя персистентности, 480 строк.
- `tools/sml/tests/test_temporal_store.py` — unit-тесты.
- `tools/sml/tests/test_temporal_store_properties.py` — property-тесты.
- `tools/sml/bench/bench_read.py` — бенчмарк sml.read.
- `logs/bench/bench-read-2026-05-11-2130.txt` — лог бенчмарка.
- `docs/agent-log/2026-05-11-2130-kiro-sml-stage-3-temporal-store.md` — настоящий отчёт.

## Решения на ходу

- `isolation_level=None` в `sqlite3.connect` — отключает авто-BEGIN у Python'овского sqlite3. Этим получаем полный контроль над транзакциями через `BEGIN IMMEDIATE ... COMMIT`. Это критично для `supersede` (Req 6.2) — гарантирует сериализацию со стороны SQLite.
- `records_history` хранит `snapshot` как JSON строку. Это дороже по памяти, чем нормализованные колонки, но сильно проще для `query_at` — snapshot возвращается напрямую без сложных UNION'ов. При Typical_Volume = 10 000 × средний размер 1 КБ даёт ~10 МБ истории на 1 поколение — приемлемо.
- `supersedes_id` у новой записи заполняется первым `old_id` через `COALESCE` (если пользователь уже поставил его при insert, не затираем). Это поведение разумно для большинства случаев; множественное суперседирование (N→1) при этом корректно работает через `superseded_by_id` у каждой старой записи.
- `delete` — soft-delete через `deleted_at`. Физического удаления нет нигде в коде (Req 4.6). `read_by_id` фильтрует `deleted_at IS NULL`, но записи в `records_history` остаются для аудита.
- Content hash (SHA-256) — готовится для будущей детекции конфликтов файл↔SML в Этапе 6. Не используется пока, но поле в схеме уже есть.

## Риски и ограничения

- `execute_pwsh` под нагрузкой иногда обрывает очень длинные команды. Бенчмарк отрабатывает быстро (< 3 с), но если увеличить до 100 000 записей, может понадобиться background process.
- `query_at` при большой истории (>1000 интервалов на одну запись) может замедлиться. Это сценарий «частое суперседирование одной и той же записи». При Typical_Volume не проблема, при 10× — надо будет добавить индекс на `records_history(valid_from, valid_to)`.
- Бенчмарк гоняется на SSD. На HDD `synchronous=NORMAL` может дать заметный провал на записи. Для одного пользователя на типичном Windows SSD это не актуально.

## Что следующему агенту

- Этап 4 (Embedding_Engine): использовать `Memory_Record.content` как вход для `bge-m3`, сохранять результат в LanceDB, связывать через `id`. Для benchmark запросов можно переиспользовать `bench_read.py`.
- В задаче 5.2 (`sml.write`) последовательность: (1) валидация, (2) проверка секретов, (3) `TemporalStore.insert`, (4) `EmbeddingEngine.embed_text` + `upsert`, (5) опционально `supersede`. Каждая ошибка должна откатывать всё, что уже успело записаться — для LanceDB это непросто, в design это Решение №2 раздел 4.3.
- P5 в property-тестах пока проверена через concrete scenario (mid-list conflict). После задачи 5.6 (`sml.supersede`) добавить полноценный PBT с Hypothesis-стратегией для N записей.
