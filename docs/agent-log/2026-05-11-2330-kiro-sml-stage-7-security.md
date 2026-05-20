# Отчет агента

## Дата и время

2026-05-11 23:30

## Агент

kiro (оркестратор, автономное исполнение Этапа 7)

## Исходный запрос

Этап 7 спека `agents-shared-memory-layer`: безопасность и Operation_Log.
Выполнен до Этапа 5 (MCP_Adapter), потому что MCP-инструменты в 5.2/5.7/5.8
должны использовать `guard_secret` и писать в Operation_Log с первого
вызова.

## Закрытые задачи (7.1–7.7)

- **7.1 Pattern detector** — 15 regex-паттернов известных секретов:
  OpenAI `sk-`, Anthropic `sk-ant-`, GitHub `ghp_/gho_/ghs_`, Slack
  `xox[baprs]-`, AWS `AKIA`/`aws_secret_access_key=`, Google `AIza/ya29.`,
  JWT (три base64-секции через точки), PEM-ключи, пары `api_key=` и
  `password=`, GitLab `glpat-`.
- **7.2 Энтропия Шеннона** — скользящее окно по подстрокам
  ``[A-Za-z0-9+/=_-]{20,200}``, порог 4.5 бит/символ. Фильтр ложных
  срабатываний через минимальный словарь из ~50 слов (EN+RU длиной ≥ 4):
  подстрока со ≥ 3 словарными словами не считается секретом. Это убирает
  ложные срабатывания на `context_memory_record_…`.
- **7.3 Интеграция** — `tools/sml/write_guard.py::guard_secret(agent, op,
  text, op_log, record_id, operation_id)`. Единая точка для
  `sml.write`/`sml.add_decision`/`sml.add_log`: при срабатывании — пишет
  `rejected` в Operation_Log с `reason_category` и бросает
  `SecretRejectedError`. Значение секрета нигде не логируется.
- **7.4 Operation_Log JSONL** — `tools/sml/operation_log.py::OperationLog`,
  append-binary режим, `flush + os.fsync` после каждой записи. Закрытый
  перечень допустимых `op` и `result`. Обязательный `reason_category`
  для `result != success`.
- **7.5 Ротация и TTL** — календарные UTC-сутки. Активный файл
  `sml-operation-log.ndjson`, ротированные — `sml-operation-log-YYYY-MM-DD.ndjson`.
  При первой записи нового UTC-дня активный файл копируется в ротированный
  через raw bytes (надёжнее `rename()` на Windows с антивирусом/индексером).
  После ротации cleanup удаляет ротированные файлы старше 30 дней.
- **7.6 Loopback-only guard** — `OllamaEmbedder.__init__` уже бросает
  `IOErrorSML`, если `OLLAMA_HOST` не loopback (127.0.0.1, localhost, ::1).
  Покрыто тестом `test_ollama_rejects_non_loopback_host`.
- **7.7 Доступность лога** — тест `test_readable_without_close` читает
  файл пока SML работает: `flush + fsync` на каждой записи гарантируют,
  что `Get-Content -Tail -Wait` видит строки сразу.

## Тесты (92 passed за ~11 с)

### test_security.py — 24 теста

- 15 параметризованных: по одному на каждую категорию регекса.
- Уровень 2: отлов случайной base64, пропуск русского предложения,
  пропуск короткой строки, фильтр словарных слов.
- `check_secret`: приоритет паттерна над энтропией, fallback на энтропию,
  пропуск чистого текста, пропуск пустой строки.
- Property-test P6: 100 случайных высокоэнтропийных строк разной длины →
  все флагаются.

### test_operation_log.py — 7 тестов

- Одна запись, требование `reason_category`, append-only, читаемость без
  `close`, отклонение неизвестного `op`, ротация по UTC-дню,
  retention-удаление старых файлов.

### test_write_guard.py — 3 теста

- Safe text проходит без записи в Operation_Log.
- OpenAI-подобный ключ отклоняется, в лог пишется `rejected` + `openai_api_key`,
  значение секрета нигде не проксируется.
- `guard_secret(op_log=None)` корректно работает без лога.

Итого: 92 passed за 11 с (24 stage2 + 20 stage3 + 13 stage4 + 24 security +
7 operation_log + 3 guard + 1 core_smoke).

## Фиксы на ходу

1. **Windows rename ненадёжен на `.ab`-файлах**: antivirus/indexer держит
   handle после `close()`. Заменил `path.rename(dest)` на
   `open(src, "rb") → data; open(dest, "ab/wb") → data; unlink(src)`.
2. **Тест ротации с `next_day="2030-01-01"`** падал по скрытой причине:
   `cleanup_old_files(2030-01-01)` удалял ротированный файл с датой
   `2026-05-12` как «старше 30 дней». Зафиксировал `next_day = today + 1`
   через `datetime.timedelta`.

## Изменённые файлы

- `tools/sml/security.py` — детектор (pattern + энтропия + словарь).
- `tools/sml/operation_log.py` — JSONL append-only + ротация.
- `tools/sml/write_guard.py` — `guard_secret` для всех write-путей.
- `tools/sml/tests/test_security.py`, `test_operation_log.py`,
  `test_write_guard.py` — 34 новых теста.
- `docs/agent-log/2026-05-11-2330-kiro-sml-stage-7-security.md` —
  настоящий отчёт.

## Риски и ограничения

- **Словарь ложных срабатываний маленький** (~50 слов). Если пользователь
  положит в `content` длинный техтекст без словарных слов, может
  сработать `high_entropy`. Решение — расширить словарь или ввести белые
  списки по тегам. Отложено до появления реальных кейсов.
- **Fsync на всех ФС поддерживается** в стандартной Windows NTFS, но на
  сетевых SMB/tmpfs может не работать. Добавил try/except — `flush`
  гарантирован.
- **Загрузка больших write-пайплайнов** (сотни записей в секунду) сейчас
  всегда делает fsync — это дорого. Для `sml.write` это приемлемо (SLA
  2 секунды). Если в будущем появится batch API, стоит дать ему
  `fsync_at_batch_end`.

## Что следующему агенту

- Этап 5 (MCP_Adapter): использовать `guard_secret()` в `sml.write`,
  `sml.add_decision`, `sml.add_log`. Для `Operation_Log` создать
  singleton-инстанс на запуск процесса.
- В `sml.write` порядок: валидация модели → `guard_secret` →
  `TemporalStore.insert` → `EmbeddingEngine.upsert`. Если embed падает,
  запись в SQLite остаётся (этим займётся reindex из Этапа 6).

## Прогресс

**После Этапа 7: 41/97 задач.** Готово: Этап 1 (7), Этап 2 (8), Этап 3 (9),
Этап 4 (8), Этап 7 (8) + пустой рут-пакет. Впереди: Этап 5 (MCP-адаптер
и 10 инструментов), Этап 6 (File_Watcher + writers), Этап 8 (миграция),
Этап 9 (E2E).
