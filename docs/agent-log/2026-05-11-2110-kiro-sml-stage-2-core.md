# Отчет агента

## Дата и время

2026-05-11 21:10

## Агент

kiro (оркестратор, автономное исполнение Этапа 2)

## Исходный запрос пользователя

«Сам, весь Этап 2 за один заход» — ядро SML_Core: каркас пакета, pydantic-модели, валидация, UUIDv7, ошибки, unified response, метки времени, property-тесты.

## Закрытые задачи (2.1–2.7)

- **2.1 Каркас пакета** — `tools/sml/__init__.py` (`__version__ = "0.1.0"`), `core.py` с рабочим CLI `--selfcheck`, подкаталоги `writers/`, `tests/`, `bench/`. `start-sml.ps1 -SelfCheck` печатает `sml-selfcheck-ok` через реальный модуль.
- **2.2 MemoryRecord** — pydantic v2, `extra="forbid"`, `str_strip_whitespace=False` (Req 9.1). 14 полей из `design.md §5.1`, границы по `content` (1–10000), `author_agent` (1–128), `tags` (0–20 по 1–64), `embedding_vector` (строго 1024). Метод `as_public_dict()` вычищает `embedding_vector` из MCP-ответа.
- **2.3 Валидация** — `MemoryType` (StrEnum из 8 значений), `validate_type/source_lines/tags`. Бросают `SMLError`, а pydantic-валидаторы перепаковывают в `ValueError`.
- **2.4 UUIDv7** — `tools/sml/ids.py`: честные 48 бит timestamp_ms, версия 7, вариант RFC 4122, монотонность через потокобезопасный `_last_int`. `validate_id` через strict regex.
- **2.5 Ошибки** — 7 категорий (`validation`, `not_found`, `conflict`, `secret_rejected`, `io_error`, `timeout`, `unsupported`). Базовый `SMLError`, фабрики `for_field`/`for_id`/`for_reason`. Сообщения на русском.
- **2.6 Response** — `ok_response`, `error_response(err, operation_id)`, `format_score` (округление до 3 знаков, клампинг в [0,1]).
- **2.7 Timefmt** — `now_utc_ms`, `format_iso8601_ms`, `parse_iso8601_ms`. Принимается только `YYYY-MM-DDTHH:MM:SS.sssZ`. Отклоняет offset-формы, отсутствие миллисекунд и микросекундную точность.

## Тесты (24 passed за 1.02 с)

- `test_core_smoke.py` — __version__, `--selfcheck`, типы, русскоязычные сообщения.
- `test_ids_properties.py` — property P3 (монотонность UUIDv7, ≥200 примеров), регекс версии 7, отрицательные тесты.
- `test_timefmt_properties.py` — round-trip ISO 8601 UTC ms (≥200 примеров), явные отказы по формату.
- `test_models_properties.py` — property P9 (UTF-8 fidelity для кириллицы/эмодзи/знаков ≥200 примеров), отрицательные тесты на границы полей, `extra="forbid"`, дубликаты тегов, `embedding_vector` длиной 1024.

## Изменённые файлы

- `tools/__init__.py` — новый (пустой, чтобы пакет импортировался).
- `tools/sml/__init__.py` — `__version__ = "0.1.0"` и docstring.
- `tools/sml/core.py` — CLI с `--selfcheck`.
- `tools/sml/models.py` — pydantic MemoryRecord.
- `tools/sml/validation.py` — MemoryType и валидаторы.
- `tools/sml/ids.py` — UUIDv7.
- `tools/sml/errors.py` — иерархия SMLError.
- `tools/sml/response.py` — унифицированный формат ответов.
- `tools/sml/timefmt.py` — ISO 8601 UTC ms.
- `tools/sml/writers/__init__.py`, `tools/sml/tests/__init__.py` — пустые.
- `tools/sml/tests/conftest.py` — добавляет корень проекта в sys.path.
- `tools/sml/tests/test_core_smoke.py`, `test_ids_properties.py`, `test_timefmt_properties.py`, `test_models_properties.py` — тесты.
- `tools/sml/start-sml.ps1` — `-SelfCheck` теперь вызывает `python -m tools.sml.core --selfcheck`, а не заглушку.
- `docs/agent-log/2026-05-11-2110-kiro-sml-stage-2-core.md` — настоящий отчёт.

## Проверки приёмки Этапа 2

- `pytest tools/sml/tests/ -q` → 24 passed.
- `pwsh -NoProfile -File tools/sml/start-sml.ps1 -SelfCheck` → `sml-selfcheck-ok`, exit 0.
- Property-based тесты P3 (монотонность UUIDv7) и P9 (UTF-8 fidelity) проходят на ≥200 примерах Hypothesis.

## Решения на ходу

- Pydantic-валидаторы перехватывают `SMLError` и выбрасывают `ValueError`, чтобы pydantic правильно заворачивал ошибки в `pydantic.ValidationError`. Такой приём позволяет тестам использовать стандартный `pytest.raises(ValueError)`, а MCP-адаптер позже достанет оригинальный `SMLError` из `__cause__` и передаст его категорию клиенту.
- `content` не обрезается от пробелов (`str_strip_whitespace=False`), но отклоняется, если состоит только из пробелов. Это сохраняет побайтовое равенство для кириллицы/эмодзи и одновременно не пропускает «пустые» записи.
- `relevance_score_last` помечен как транзиентное поле: `as_public_dict()` удаляет его, если `None`, чтобы обычный `sml.read` не содержал лишнего поля.

## Риски и ограничения

- В pydantic v2 встроенная `ValidationError` перехватывает наш `ValueError` и заворачивает в `ExceptionGroup`. Внутри сообщения теряется русский текст SMLError (остаётся хвост от pydantic). Для MCP-адаптера в задаче 5.1 потребуется явный мост: парсить `ValidationError.errors()` и отдавать клиенту категорию `validation` с первой причиной.
- Python 3.13 на Windows: `hypothesis` по умолчанию устанавливает `deadline` на тесты. В `test_utf8_fidelity_byte_identical` явно отключён `deadline=None`, чтобы избежать ложных таймаутов на больших примерах.
- Чистота `as_public_dict()` пока проверена только для случая `embedding_vector=None/len=1024`. При переходе на сериализацию через MCP в задаче 5.1 нужно добавить integration-тест, что вектор никогда не уходит клиенту.

## Что следующему агенту

- Этап 3 (Temporal_Store): SQLite WAL, схема `records`/`records_history`/`sync_state`, индексы из design §8.1, атомарный `supersede`. Использовать `MemoryRecord.as_public_dict()` / `.model_dump()` для сериализации в SQLite JSON-полей.
- Этап 4 (Embedding_Engine): использовать `Embedding_Engine.embed_text` с моделью `bge-m3` на `http://127.0.0.1:11434`, вектор 1024. Лимит `content` для запроса — 10 000 символов (уже проверяется моделью).
- Ollama не всегда автозапускается между Windows-сессиями — технический долг, разрешается в Этапе 8 через Task Scheduler либо внутри `start-sml.ps1`.
