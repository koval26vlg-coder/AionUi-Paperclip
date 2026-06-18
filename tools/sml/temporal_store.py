"""Temporal_Store — слой персистентности SML на SQLite + WAL.

Компонент отвечает за хранение ``Memory_Record`` (кроме ``embedding_vector`` —
он живёт в LanceDB), историю изменений (records_history) и состояние
синхронизации с файлами (sync_state).

Ключевые инварианты:

- **Req 3.1, Req 3.4, Req 3.5** — durability: ``insert`` / ``update`` /
  ``supersede`` возвращают успех только после завершения SQLite COMMIT.
- **Req 6.1** — метки времени в ISO 8601 UTC с миллисекундами.
- **Req 6.2** — суперседирование выполняется в одной транзакции
  ``BEGIN IMMEDIATE ... COMMIT``; любая ошибка → полный ROLLBACK.
- **Req 6.3** — неизвестный ``supersedes_id`` / ``old_id`` → ``NotFoundError``,
  состояние не меняется.
- **Req 6.4, Req 6.5** — ``records_history`` позволяет реконструировать
  состояние на произвольную метку времени; ``at`` вне диапазона → ошибка.
- **Req 4.6** — монотонность: ничего не удаляется автоматически. ``delete``
  выполняется только явно (мягкое удаление через ``deleted_at``).
- **Req 8.3** — приоритет файла при конфликте (записывается в ``sync_state``).

Схема задаётся миграциями в ``schema_migrations`` (см. ``MIGRATIONS``).
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
from typing import Any, Iterator, List, Optional

from .errors import ConflictError, IOErrorSML, NotFoundError
from .ids import new_id
from .models import MemoryRecord
from .timefmt import format_iso8601_ms, now_utc_ms, parse_iso8601_ms
from .validation import MemoryType, normalize_author

__all__ = ["TemporalStore", "open_store", "SchemaVersion", "MIGRATIONS"]


# ---------------------------------------------------------------------------
# Миграции схемы
# ---------------------------------------------------------------------------


class SchemaVersion:
    CURRENT = 2


# Каждая миграция — кортеж (version, sql_script). Применяются в одной
# транзакции, строго по возрастанию номера. Повторный запуск idempotent.
MIGRATIONS: list[tuple[int, str]] = [
    (
        1,
        """
        CREATE TABLE IF NOT EXISTS records (
            id               TEXT PRIMARY KEY,
            type             TEXT NOT NULL,
            content          TEXT NOT NULL,
            author_agent     TEXT NOT NULL,
            created_at       TEXT NOT NULL,
            updated_at       TEXT NOT NULL,
            is_current       INTEGER NOT NULL,
            supersedes_id    TEXT,
            superseded_by_id TEXT,
            source_file      TEXT,
            source_lines     TEXT,
            tags_json        TEXT NOT NULL DEFAULT '[]',
            content_hash     TEXT NOT NULL,
            deleted_at       TEXT
        );

        CREATE TABLE IF NOT EXISTS records_history (
            id           TEXT NOT NULL,
            valid_from   TEXT NOT NULL,
            valid_to     TEXT,
            is_current   INTEGER NOT NULL,
            snapshot     TEXT NOT NULL,
            PRIMARY KEY (id, valid_from)
        );

        CREATE TABLE IF NOT EXISTS sync_state (
            source_file      TEXT PRIMARY KEY,
            last_hash        TEXT NOT NULL,
            last_indexed_at  TEXT NOT NULL,
            last_conflict_at TEXT
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_records_id ON records(id);
        CREATE INDEX IF NOT EXISTS idx_records_current
            ON records(is_current, updated_at DESC);
        CREATE INDEX IF NOT EXISTS idx_records_type_updated
            ON records(type, updated_at DESC);
        CREATE INDEX IF NOT EXISTS idx_records_supersedes
            ON records(supersedes_id);
        CREATE INDEX IF NOT EXISTS idx_records_source_file
            ON records(source_file);
        CREATE INDEX IF NOT EXISTS idx_history_id_from
            ON records_history(id, valid_from);
        """,
    ),
    (
        2,
        # Полнотекстовый индекс FTS5 — фоллбэк семантического поиска, когда
        # Ollama/LanceDB недоступны. ``records_fts`` синхронизируется с
        # ``records`` триггерами по rowid; колонка ``id`` хранится, но не
        # индексируется (UNINDEXED) — нужна только чтобы достать UUID без JOIN.
        # tokenize unicode61 + remove_diacritics корректно работает с русским.
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS records_fts USING fts5(
            content,
            id UNINDEXED,
            tokenize='unicode61 remove_diacritics 2'
        );

        INSERT INTO records_fts (rowid, content, id)
            SELECT rowid, content, id FROM records WHERE deleted_at IS NULL;

        CREATE TRIGGER IF NOT EXISTS records_fts_ai AFTER INSERT ON records BEGIN
            INSERT INTO records_fts (rowid, content, id)
                VALUES (new.rowid, new.content, new.id);
        END;

        CREATE TRIGGER IF NOT EXISTS records_fts_ad AFTER DELETE ON records BEGIN
            DELETE FROM records_fts WHERE rowid = old.rowid;
        END;

        CREATE TRIGGER IF NOT EXISTS records_fts_au AFTER UPDATE ON records BEGIN
            DELETE FROM records_fts WHERE rowid = old.rowid;
            INSERT INTO records_fts (rowid, content, id)
                VALUES (new.rowid, new.content, new.id);
        END;
        """,
    ),
]


# ---------------------------------------------------------------------------
# TemporalStore
# ---------------------------------------------------------------------------


class TemporalStore:
    """Persistency для Memory_Record в SQLite WAL.

    Создаётся через ``open_store(path)``. Закрывается через ``close()`` или
    контекстным менеджером.
    """

    def __init__(self, conn: sqlite3.Connection, path: Path) -> None:
        self._conn = conn
        self._path = path
        self._last_checkpoint_at: Optional[str] = None

    # --- Управление соединением ---

    @property
    def path(self) -> Path:
        return self._path

    def close(self) -> None:
        try:
            # При закрытии слиём WAL обратно в основной файл (Req 3.4).
            self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        except sqlite3.Error:
            pass
        self._conn.close()

    def __enter__(self) -> "TemporalStore":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()

    # --- Транзакции ---

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        """Открывает BEGIN IMMEDIATE (Req 6.2).

        Использование ``isolation_level=None`` (автокоммит выключен) + явный
        ``BEGIN IMMEDIATE`` гарантирует, что другие писатели немедленно
        увидят блокировку и не будут мешать.
        """
        try:
            self._conn.execute("BEGIN IMMEDIATE;")
        except sqlite3.Error as exc:  # pragma: no cover - защитный код
            raise IOErrorSML(f"Не удалось начать транзакцию SQLite: {exc}") from exc
        try:
            yield self._conn
        except Exception:
            try:
                self._conn.execute("ROLLBACK;")
            except sqlite3.Error:
                pass
            raise
        try:
            self._conn.execute("COMMIT;")
        except sqlite3.Error as exc:  # pragma: no cover
            raise IOErrorSML(f"Сбой COMMIT SQLite: {exc}") from exc

    # --- CRUD ---

    def insert(self, record: MemoryRecord) -> None:
        """Вставляет новую запись в ``records`` + снапшот в ``records_history``.

        - Дубликат ``id`` → ``ConflictError`` (Req 3.1, Req 3.5).
        - После успешного COMMIT запись гарантированно на диске.
        """
        payload = _record_to_row(record)
        history = _record_to_history_snapshot(record)
        try:
            with self._transaction() as conn:
                conn.execute(
                    """
                    INSERT INTO records (
                        id, type, content, author_agent,
                        created_at, updated_at, is_current,
                        supersedes_id, superseded_by_id,
                        source_file, source_lines, tags_json,
                        content_hash, deleted_at
                    ) VALUES (
                        :id, :type, :content, :author_agent,
                        :created_at, :updated_at, :is_current,
                        :supersedes_id, :superseded_by_id,
                        :source_file, :source_lines, :tags_json,
                        :content_hash, :deleted_at
                    )
                    """,
                    payload,
                )
                conn.execute(
                    """
                    INSERT INTO records_history (
                        id, valid_from, valid_to, is_current, snapshot
                    ) VALUES (
                        :id, :valid_from, NULL, :is_current, :snapshot
                    )
                    """,
                    {
                        "id": record.id,
                        "valid_from": record.updated_at,
                        "is_current": int(record.is_current),
                        "snapshot": json.dumps(history, ensure_ascii=False),
                    },
                )
        except sqlite3.IntegrityError as exc:
            raise ConflictError(
                f"Запись с id={record.id!r} уже существует"
            ) from exc
        except sqlite3.Error as exc:
            raise IOErrorSML(f"Сбой SQLite при insert: {exc}") from exc

    def read_by_id(self, record_id: str) -> Optional[MemoryRecord]:
        """Возвращает ``MemoryRecord`` по id или ``None``, если его нет.

        Удалённые записи (``deleted_at`` NOT NULL) трактуются как
        отсутствующие для публичного API.
        """
        row = self._conn.execute(
            """
            SELECT id, type, content, author_agent, created_at, updated_at,
                   is_current, supersedes_id, superseded_by_id,
                   source_file, source_lines, tags_json
              FROM records
             WHERE id = :id AND deleted_at IS NULL
            """,
            {"id": record_id},
        ).fetchone()
        if row is None:
            return None
        return _row_to_record(row)

    def exists(self, record_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM records WHERE id = :id AND deleted_at IS NULL",
            {"id": record_id},
        ).fetchone()
        return row is not None

    def text_search(
        self,
        query: str,
        *,
        limit: int = 20,
        include_superseded: bool = False,
    ) -> List[tuple[MemoryRecord, float]]:
        """Полнотекстовый поиск по FTS5 — фоллбэк семантики без Ollama.

        Возвращает список ``(MemoryRecord, relevance)``, отсортированный по
        релевантности BM25 (лучшие первыми). ``relevance`` — синтетическая
        оценка в (0, 1], убывающая по позиции (у текстового поиска нет
        косинусной близости, но поле сохраняем для совместимости с API).

        Пустой запрос или запрос без значимых токенов → пустой список.
        Удалённые записи исключаются; устаревшие — по ``include_superseded``.
        """
        match = _build_fts_match(query)
        if match is None:
            return []
        try:
            rows = self._conn.execute(
                """
                SELECT r.id, r.type, r.content, r.author_agent,
                       r.created_at, r.updated_at, r.is_current,
                       r.supersedes_id, r.superseded_by_id,
                       r.source_file, r.source_lines, r.tags_json
                  FROM records_fts f
                  JOIN records r ON r.id = f.id
                 WHERE records_fts MATCH :match
                   AND r.deleted_at IS NULL
                 ORDER BY rank
                 LIMIT :limit
                """,
                {"match": match, "limit": max(1, int(limit)) * 2},
            ).fetchall()
        except sqlite3.Error as exc:
            raise IOErrorSML(f"Сбой FTS5-поиска: {exc}") from exc

        out: list[MemoryRecord] = []
        for row in rows:
            record = _row_to_record(row)
            if not include_superseded and not record.is_current:
                continue
            out.append(record)
            if len(out) >= limit:
                break
        # Синтетическая релевантность: 0.99 у первого, плавно вниз, но > 0.
        scored: list[tuple[MemoryRecord, float]] = []
        n = len(out)
        for idx, rec in enumerate(out):
            score = round(0.99 - (idx / max(n, 1)) * 0.49, 3)
            scored.append((rec, score))
        return scored

    def update_fields(self, record_id: str, **fields: Any) -> MemoryRecord:
        """Частичное обновление записи + запись истории.

        ``updated_at`` всегда обновляется автоматически. Если ``record_id``
        не найден — ``NotFoundError``.
        """
        now = now_utc_ms()
        # Оставляем только поля, которые разрешено менять.
        allowed = {
            "content",
            "author_agent",
            "is_current",
            "supersedes_id",
            "superseded_by_id",
            "source_file",
            "source_lines",
            "tags_json",
            "updated_at",
        }
        bad = set(fields.keys()) - allowed
        if bad:
            raise ValueError(f"Недопустимые поля для update_fields: {sorted(bad)}")
        try:
            with self._transaction() as conn:
                current = conn.execute(
                    """
                    SELECT id, type, content, author_agent, created_at, updated_at,
                           is_current, supersedes_id, superseded_by_id,
                           source_file, source_lines, tags_json, content_hash
                      FROM records
                     WHERE id = :id AND deleted_at IS NULL
                    """,
                    {"id": record_id},
                ).fetchone()
                if current is None:
                    raise NotFoundError.for_id(record_id)

                history_from = _unique_history_valid_from(conn, record_id, now)
                fields["updated_at"] = history_from
                assignments = ", ".join(f"{k} = :{k}" for k in fields)
                params = {**fields, "id": record_id}
                conn.execute(
                    f"UPDATE records SET {assignments} WHERE id = :id",
                    params,
                )

                updated_row = conn.execute(
                    """
                    SELECT id, type, content, author_agent, created_at, updated_at,
                           is_current, supersedes_id, superseded_by_id,
                           source_file, source_lines, tags_json
                      FROM records
                     WHERE id = :id
                    """,
                    {"id": record_id},
                ).fetchone()
                updated = _row_to_record(updated_row)
                snapshot = _record_to_history_snapshot(updated)

                # Закрываем предыдущий исторический интервал
                conn.execute(
                    """
                    UPDATE records_history
                       SET valid_to = :valid_to
                     WHERE id = :id AND valid_to IS NULL
                    """,
                    {"valid_to": history_from, "id": record_id},
                )
                # Открываем новый
                conn.execute(
                    """
                    INSERT INTO records_history (
                        id, valid_from, valid_to, is_current, snapshot
                    ) VALUES (
                        :id, :valid_from, NULL, :is_current, :snapshot
                    )
                    """,
                    {
                        "id": record_id,
                        "valid_from": history_from,
                        "is_current": int(updated.is_current),
                        "snapshot": json.dumps(snapshot, ensure_ascii=False),
                    },
                )
                return updated
        except sqlite3.Error as exc:
            raise IOErrorSML(f"Сбой SQLite при update: {exc}") from exc

    def delete(self, record_id: str) -> None:
        """Мягкое удаление: ставит ``deleted_at``; записи в истории остаются.

        Без явного вызова `delete` ничего не удаляется (Req 4.6).
        """
        now = now_utc_ms()
        try:
            with self._transaction() as conn:
                cur = conn.execute(
                    "UPDATE records SET deleted_at = :at WHERE id = :id AND deleted_at IS NULL",
                    {"at": now, "id": record_id},
                )
                if cur.rowcount == 0:
                    raise NotFoundError.for_id(record_id)
                conn.execute(
                    """
                    UPDATE records_history
                       SET valid_to = :at
                     WHERE id = :id AND valid_to IS NULL
                    """,
                    {"at": now, "id": record_id},
                )
        except sqlite3.Error as exc:
            raise IOErrorSML(f"Сбой SQLite при delete: {exc}") from exc

    # --- Supersede ---

    def supersede(self, new_id: str, old_ids: List[str]) -> List[str]:
        """Атомарно помечает ``old_ids`` как неактуальные, связывает с ``new_id``.

        Инвариант (Req 6.2, Req 6.3):
        - если любой из ``old_ids`` отсутствует или уже суперседирован,
          транзакция откатывается целиком и ни одно поле не меняется;
        - в случае успеха у ``new_id`` остаётся ``is_current=1``, а у каждого
          ``old_id`` ``is_current=0``, ``superseded_by_id=new_id``;
        - в ``records_history`` добавляется по одной строке на каждую
          изменённую запись.
        """
        if not old_ids:
            raise ValueError("supersede: old_ids должен содержать хотя бы один id")
        if new_id in old_ids:
            raise ConflictError("supersede: new_id не может совпадать с old_id")
        now = now_utc_ms()
        try:
            with self._transaction() as conn:
                # new_id должен существовать
                if conn.execute(
                    "SELECT 1 FROM records WHERE id = :id AND deleted_at IS NULL",
                    {"id": new_id},
                ).fetchone() is None:
                    raise NotFoundError.for_id(new_id)

                updated_ids: list[str] = []
                for oid in old_ids:
                    row = conn.execute(
                        """
                        SELECT is_current, superseded_by_id
                          FROM records
                         WHERE id = :id AND deleted_at IS NULL
                        """,
                        {"id": oid},
                    ).fetchone()
                    if row is None:
                        raise NotFoundError.for_id(oid)
                    is_current, superseded_by_id = row
                    if superseded_by_id is not None:
                        raise ConflictError(
                            f"Запись {oid!r} уже суперседирована записью "
                            f"{superseded_by_id!r}"
                        )
                    history_from = _unique_history_valid_from(conn, oid, now)

                    # Обновляем запись
                    conn.execute(
                        """
                        UPDATE records
                           SET is_current       = 0,
                               superseded_by_id = :new_id,
                               updated_at       = :history_from
                         WHERE id = :id
                        """,
                        {"new_id": new_id, "history_from": history_from, "id": oid},
                    )
                    # Историю закрываем и открываем новый интервал
                    conn.execute(
                        """
                        UPDATE records_history
                           SET valid_to = :now
                         WHERE id = :id AND valid_to IS NULL
                        """,
                        {"now": history_from, "id": oid},
                    )
                    snapshot_row = conn.execute(
                        """
                        SELECT id, type, content, author_agent, created_at, updated_at,
                               is_current, supersedes_id, superseded_by_id,
                               source_file, source_lines, tags_json
                          FROM records
                         WHERE id = :id
                        """,
                        {"id": oid},
                    ).fetchone()
                    snapshot_rec = _row_to_record(snapshot_row)
                    conn.execute(
                        """
                        INSERT INTO records_history (
                            id, valid_from, valid_to, is_current, snapshot
                        ) VALUES (
                            :id, :history_from, NULL, :is_current, :snapshot
                        )
                        """,
                        {
                            "id": oid,
                            "history_from": history_from,
                            "is_current": 0,
                            "snapshot": json.dumps(
                                _record_to_history_snapshot(snapshot_rec),
                                ensure_ascii=False,
                            ),
                        },
                    )
                    updated_ids.append(oid)

                # Зафиксируем на суперседирующей записи обратную ссылку
                # (supersedes_id хранит первый идентификатор старой записи;
                # если их несколько — остальные находятся через
                # superseded_by_id в old-записях).
                conn.execute(
                    """
                    UPDATE records
                       SET supersedes_id = COALESCE(supersedes_id, :first_old),
                           updated_at    = :now
                     WHERE id = :new_id
                    """,
                    {"first_old": old_ids[0], "now": now, "new_id": new_id},
                )

                return updated_ids
        except sqlite3.Error as exc:
            raise IOErrorSML(f"Сбой SQLite при supersede: {exc}") from exc

    # --- Temporal_Query ---

    def query_at(
        self,
        at: str,
        type_filter: Optional[str] = None,
        only_current_at: bool = True,
        limit: int = 100,
    ) -> List[MemoryRecord]:
        """Возвращает состояние на метку времени ``at`` (Req 6.4, Req 6.5)."""
        parse_iso8601_ms(at)  # строгая валидация формата
        if not 1 <= limit <= 500:
            raise ValueError("limit должен быть в диапазоне 1..500")

        # Проверка диапазона (Req 6.5): at в будущем или до первой записи
        now = now_utc_ms()
        if at > now:
            raise ValueError(f"at={at!r} в будущем относительно {now!r}")

        first_row = self._conn.execute(
            "SELECT MIN(created_at) FROM records"
        ).fetchone()
        first_created = first_row[0] if first_row else None
        if first_created is not None and at < first_created:
            raise ValueError(
                f"at={at!r} раньше первой записи {first_created!r}"
            )

        # Выбираем срез истории: интервал, покрывающий at.
        rows = self._conn.execute(
            """
            SELECT snapshot, is_current
              FROM records_history
             WHERE valid_from <= :at AND (valid_to IS NULL OR valid_to > :at)
             ORDER BY valid_from DESC
             LIMIT :limit
            """,
            {"at": at, "limit": limit * 2},  # extra запас для фильтрации
        ).fetchall()

        out: list[MemoryRecord] = []
        for snapshot_json, is_current in rows:
            data = json.loads(snapshot_json)
            data["is_current"] = bool(is_current)
            if type_filter is not None and data.get("type") != type_filter:
                continue
            if only_current_at and not data["is_current"]:
                continue
            out.append(MemoryRecord.model_validate(data))
            if len(out) >= limit:
                break
        return out

    # --- Утилиты ---

    def count(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) FROM records WHERE deleted_at IS NULL"
        ).fetchone()
        return int(row[0]) if row else 0


# ---------------------------------------------------------------------------
# Открытие и миграции
# ---------------------------------------------------------------------------


def open_store(path: Path | str) -> TemporalStore:
    """Открывает БД SQLite в WAL-режиме, применяет миграции.

    Путь создаётся при отсутствии (вместе с родительскими каталогами).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(
            str(path),
            isolation_level=None,  # автокоммит выключаем, управляем вручную
            detect_types=0,
            check_same_thread=False,
        )
    except sqlite3.Error as exc:
        raise IOErrorSML(f"Не удалось открыть SQLite {path!s}: {exc}") from exc

    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")

    _apply_migrations(conn)

    return TemporalStore(conn, path)


def _apply_migrations(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version    INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    current_row = conn.execute(
        "SELECT COALESCE(MAX(version), 0) FROM schema_migrations"
    ).fetchone()
    current = int(current_row[0]) if current_row else 0

    for version, script in MIGRATIONS:
        if version <= current:
            continue
        # executescript() сам делает BEGIN/COMMIT, поэтому не оборачиваем
        # в свою транзакцию. INSERT в schema_migrations тоже в autocommit.
        try:
            conn.executescript(script)
            conn.execute(
                "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                (version, now_utc_ms()),
            )
        except sqlite3.Error as exc:
            raise IOErrorSML(
                f"Сбой миграции v{version}: {exc}"
            ) from exc


# ---------------------------------------------------------------------------
# FTS5 helper
# ---------------------------------------------------------------------------


import re as _re

_FTS_TOKEN_RE = _re.compile(r"\w+", _re.UNICODE)


def _build_fts_match(query: str) -> Optional[str]:
    """Превращает естественный запрос в безопасный FTS5 MATCH-выражение.

    Слова длиной ≥ 2 берутся как префиксные термы в OR: ``"конверс"* OR
    "отчет"*``. Каждый терм обёрнут в двойные кавычки (внутренние кавычки
    удвоены) — это исключает интерпретацию спецсимволов FTS5 и инъекции в
    синтаксис запроса. Если значимых токенов нет — возвращает ``None``.
    """
    if not isinstance(query, str):
        return None
    terms: list[str] = []
    for tok in _FTS_TOKEN_RE.findall(query):
        if len(tok) < 2:
            continue
        safe = tok.replace('"', '""')
        terms.append(f'"{safe}"*')
    if not terms:
        return None
    return " OR ".join(terms)


# ---------------------------------------------------------------------------
# Сериализация MemoryRecord <-> SQLite row
# ---------------------------------------------------------------------------


def _record_to_row(record: MemoryRecord) -> dict[str, Any]:
    import hashlib

    content_hash = hashlib.sha256(record.content.encode("utf-8")).hexdigest()
    return {
        "id": record.id,
        "type": record.type.value if isinstance(record.type, MemoryType) else str(record.type),
        "content": record.content,
        "author_agent": record.author_agent,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "is_current": int(record.is_current),
        "supersedes_id": record.supersedes_id,
        "superseded_by_id": record.superseded_by_id,
        "source_file": record.source_file,
        "source_lines": record.source_lines,
        "tags_json": json.dumps(record.tags, ensure_ascii=False),
        "content_hash": content_hash,
        "deleted_at": None,
    }


def _row_to_record(row: sqlite3.Row) -> MemoryRecord:
    data = {
        "id": row["id"],
        "type": row["type"],
        "content": row["content"],
        "author_agent": row["author_agent"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "is_current": bool(row["is_current"]),
        "supersedes_id": row["supersedes_id"],
        "superseded_by_id": row["superseded_by_id"],
        "source_file": row["source_file"],
        "source_lines": row["source_lines"],
        "tags": json.loads(row["tags_json"] or "[]"),
    }
    return MemoryRecord.model_validate(data)


def _record_to_history_snapshot(record: MemoryRecord) -> dict[str, Any]:
    """Сериализуется в JSON для records_history.snapshot."""
    d = record.model_dump()
    d.pop("embedding_vector", None)
    d.pop("relevance_score_last", None)
    # Тип сохраняем в стабильном виде (строка) для последующей валидации.
    t = d.get("type")
    if isinstance(t, MemoryType):
        d["type"] = t.value
    return d


def _unique_history_valid_from(
    conn: sqlite3.Connection,
    record_id: str,
    preferred: str,
) -> str:
    """Возвращает свободную millisecond-метку для ``records_history``.

    SQLite-ключ истории — ``(id, valid_from)``. При быстрых операциях запись
    может измениться в ту же миллисекунду, в которую была создана. Тогда
    новая строка истории должна получить следующий свободный миллисекундный
    timestamp, иначе атомарные операции вроде ``supersede`` упадут на
    UNIQUE constraint.
    """
    candidate_dt = parse_iso8601_ms(preferred)
    while True:
        candidate = format_iso8601_ms(candidate_dt)
        exists = conn.execute(
            """
            SELECT 1
              FROM records_history
             WHERE id = :id AND valid_from = :valid_from
            """,
            {"id": record_id, "valid_from": candidate},
        ).fetchone()
        if exists is None:
            return candidate
        candidate_dt = candidate_dt + timedelta(milliseconds=1)


# Удобный alias — используется в tests.
def make_new_record(
    *,
    type: str,
    content: str,
    author_agent: str,
    tags: Optional[list[str]] = None,
    source_file: Optional[str] = None,
    source_lines: Optional[str] = None,
) -> MemoryRecord:
    """Вспомогательный конструктор нового Memory_Record с правильными id/временами."""
    now = now_utc_ms()
    return MemoryRecord.model_validate(
        {
            "id": new_id(),
            "type": type,
            "content": content,
            "author_agent": normalize_author(author_agent),
            "created_at": now,
            "updated_at": now,
            "is_current": True,
            "supersedes_id": None,
            "superseded_by_id": None,
            "source_file": source_file,
            "source_lines": source_lines,
            "tags": tags or [],
        }
    )
