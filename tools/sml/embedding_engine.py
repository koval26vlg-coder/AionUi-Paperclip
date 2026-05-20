"""Embedding_Engine — расчёт эмбеддингов и ANN-поиск для SML.

Состоит из двух подсистем:

- ``OllamaEmbedder`` — клиент к локальной службе Ollama (``127.0.0.1:11434``),
  модель ``bge-m3``, возвращает 1024-мерные float-векторы.
- ``EmbeddingStore`` — встроенный LanceDB, таблица ``embeddings``.
- ``EmbeddingEngine`` — фасад: ``embed_text``, ``upsert``, ``delete``,
  ``search(query, limit, min_score)``.

Требования:
- Req 5.3, Req 5.5 — ``bge-m3``, 1024-мерные векторы, мультиязычная модель.
- Req 5.4 — метрика в диапазоне ``[0.0, 1.0]`` с точностью ≥ 3 знаков.
- Req 5.6 — пороговая фильтрация ниже 0.5.
- Req 9.4 — обработка русского без перевода.
- Req 10.4 — loopback-only, проверяется при инициализации.
- Req 11.1 — ``semantic_query`` ≤ 500 мс при Typical_Volume.
"""

from __future__ import annotations

import math
import os
import urllib.parse
from pathlib import Path
from typing import Any, Iterable, List, Optional

import requests

from .errors import IOErrorSML, ValidationError
from .response import format_score

__all__ = [
    "OllamaEmbedder",
    "EmbeddingStore",
    "EmbeddingEngine",
    "EMBEDDING_DIM",
    "RELEVANCE_THRESHOLD",
    "MAX_QUERY_LEN",
    "MAX_LIMIT",
]

EMBEDDING_DIM = 1024
RELEVANCE_THRESHOLD = 0.5
MAX_QUERY_LEN = 1000
MAX_LIMIT = 50
DEFAULT_LIMIT = 20


# ---------------------------------------------------------------------------
# OllamaEmbedder
# ---------------------------------------------------------------------------


def _is_loopback_host(host: str) -> bool:
    # Разрешаем 127.0.0.1, localhost, ::1. Всё остальное запрещено (Req 10.4).
    h = host.strip().lower()
    return h in {"127.0.0.1", "localhost", "::1", "[::1]"}


class OllamaEmbedder:
    """Клиент к локальной службе Ollama.

    - Отправляет запрос только на loopback-адрес, иначе падает на старте.
    - Таймаут одного запроса — 5 с.
    - Проверяет длину ответа (должна быть ``EMBEDDING_DIM = 1024``).
    """

    def __init__(
        self,
        *,
        host: Optional[str] = None,
        port: int = 11434,
        model: str = "bge-m3",
        timeout: float = 5.0,
    ) -> None:
        host = host or os.environ.get("OLLAMA_HOST", "127.0.0.1")
        # OLLAMA_HOST может быть задан как "127.0.0.1" или "127.0.0.1:11434".
        if ":" in host and not host.startswith("["):
            parsed = urllib.parse.urlsplit(f"//{host}")
            hostname = parsed.hostname or host
            port_override = parsed.port
            if port_override:
                port = port_override
            host = hostname
        if not _is_loopback_host(host):
            raise IOErrorSML(
                f"OLLAMA_HOST={host!r} не является loopback-адресом; "
                "разрешены только 127.0.0.1, localhost, ::1 (Req 10.4)"
            )
        self._base = f"http://{host}:{port}"
        self._model = model
        self._timeout = timeout

    @property
    def base_url(self) -> str:
        return self._base

    @property
    def model(self) -> str:
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """Возвращает 1024-мерный вектор для ``text``.

        Ошибки:
        - ``ValidationError`` — пустая строка / >MAX_QUERY_LEN символов;
        - ``IOErrorSML`` — недоступен сервис, неожиданный формат ответа,
          длина вектора ≠ EMBEDDING_DIM.
        """
        if not isinstance(text, str) or len(text) == 0:
            raise ValidationError.for_field("text", "должен быть непустой строкой")
        if len(text) > MAX_QUERY_LEN:
            raise ValidationError.for_field(
                "text",
                f"длина {len(text)} превышает лимит {MAX_QUERY_LEN}",
            )
        url = f"{self._base}/api/embeddings"
        try:
            resp = requests.post(
                url,
                json={"model": self._model, "prompt": text},
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise IOErrorSML(f"Ошибка обращения к Ollama по {url}: {exc}") from exc
        if resp.status_code != 200:
            raise IOErrorSML(
                f"Ollama вернула HTTP {resp.status_code}: {resp.text[:200]}"
            )
        try:
            body = resp.json()
        except ValueError as exc:
            raise IOErrorSML(f"Некорректный JSON от Ollama: {exc}") from exc
        vector = body.get("embedding") if isinstance(body, dict) else None
        if not isinstance(vector, list):
            raise IOErrorSML(f"В ответе Ollama нет поля embedding: {body!r}")
        if len(vector) != EMBEDDING_DIM:
            raise IOErrorSML(
                f"Размерность вектора {len(vector)} ≠ ожидаемой {EMBEDDING_DIM}"
            )
        return [float(x) for x in vector]


# ---------------------------------------------------------------------------
# EmbeddingStore (LanceDB)
# ---------------------------------------------------------------------------


class EmbeddingStore:
    """Обёртка над LanceDB-таблицей ``embeddings``.

    Таблица состоит из двух полей: ``id`` (UUIDv7) и ``vector`` (float32[1024]).
    Хранилище встраиваемое, находится в ``var/sml/lance/``.
    """

    TABLE_NAME = "embeddings"

    def __init__(self, db, table) -> None:
        self._db = db
        self._table = table

    @property
    def table(self):  # pragma: no cover - тривиально
        return self._table

    @classmethod
    def open(cls, path: Path | str) -> "EmbeddingStore":
        try:
            import lancedb
            import pyarrow as pa
        except ImportError as exc:  # pragma: no cover
            raise IOErrorSML(f"LanceDB/pyarrow недоступны: {exc}") from exc
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        db = lancedb.connect(str(path))
        # В разных версиях lancedb list_tables() возвращает либо list[str],
        # либо объект ListTablesResponse с полем tables.
        raw_tables = db.list_tables()
        if hasattr(raw_tables, "tables"):
            existing_tables = set(raw_tables.tables)
        else:
            try:
                existing_tables = set(raw_tables)
            except TypeError:  # pragma: no cover
                existing_tables = set()
        if cls.TABLE_NAME in existing_tables:
            table = db.open_table(cls.TABLE_NAME)
        else:
            schema = pa.schema(
                [
                    pa.field("id", pa.string()),
                    pa.field(
                        "vector",
                        pa.list_(pa.float32(), list_size=EMBEDDING_DIM),
                    ),
                ]
            )
            table = db.create_table(cls.TABLE_NAME, schema=schema)
        return cls(db, table)

    def upsert(self, record_id: str, vector: List[float]) -> None:
        if len(vector) != EMBEDDING_DIM:
            raise ValidationError.for_field(
                "vector",
                f"размерность {len(vector)} ≠ {EMBEDDING_DIM}",
            )
        try:
            # Идемпотентное обновление: удаляем предыдущую строку с этим id,
            # затем добавляем новую.
            self._table.delete(f"id = '{record_id}'")
            self._table.add([{"id": record_id, "vector": vector}])
        except Exception as exc:
            raise IOErrorSML(f"LanceDB upsert failed: {exc}") from exc

    def delete(self, record_id: str) -> None:
        try:
            self._table.delete(f"id = '{record_id}'")
        except Exception as exc:
            raise IOErrorSML(f"LanceDB delete failed: {exc}") from exc

    def count(self) -> int:
        try:
            return int(self._table.count_rows())
        except Exception as exc:  # pragma: no cover
            raise IOErrorSML(f"LanceDB count failed: {exc}") from exc

    def search(
        self,
        vector: List[float],
        limit: int,
    ) -> List[tuple[str, float]]:
        """Возвращает список ``(id, cos_distance)`` из LanceDB.

        LanceDB по умолчанию использует метрику L2; здесь переключаем на
        ``cosine``. Расстояние — это ``1 - cos_sim`` (диапазон [0, 2]).
        Дальнейшую нормировку выполняет ``EmbeddingEngine``.
        """
        if len(vector) != EMBEDDING_DIM:
            raise ValidationError.for_field(
                "vector",
                f"размерность {len(vector)} ≠ {EMBEDDING_DIM}",
            )
        try:
            query = self._table.search(vector).metric("cosine").limit(limit)
            rows = query.to_list()
        except Exception as exc:
            raise IOErrorSML(f"LanceDB search failed: {exc}") from exc
        out: list[tuple[str, float]] = []
        for row in rows:
            rid = row.get("id")
            # _distance всегда есть после .search(); в новых версиях может
            # называться иначе — страхуемся.
            dist = row.get("_distance", row.get("distance", 0.0))
            if rid is None:
                continue
            out.append((str(rid), float(dist)))
        return out


# ---------------------------------------------------------------------------
# EmbeddingEngine
# ---------------------------------------------------------------------------


class SearchHit:
    __slots__ = ("record_id", "relevance_score", "cos_similarity")

    def __init__(
        self,
        record_id: str,
        relevance_score: float,
        cos_similarity: float,
    ) -> None:
        self.record_id = record_id
        self.relevance_score = relevance_score
        self.cos_similarity = cos_similarity

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SearchHit(id={self.record_id!r}, score={self.relevance_score:.3f}, "
            f"cos={self.cos_similarity:.3f})"
        )


class EmbeddingEngine:
    """Фасад: эмбеддинг текста + ANN-поиск + нормировка + порог.

    Преобразование LanceDB distance → релевантность:

        cos_distance = 1 - cos_sim, где cos_sim ∈ [-1, 1]
        cos_sim      = 1 - cos_distance
        relevance    = (1 + cos_sim) / 2 ∈ [0, 1]

    Порог ``RELEVANCE_THRESHOLD = 0.5`` отсекает нерелевантные записи.
    """

    def __init__(
        self,
        embedder: OllamaEmbedder,
        store: EmbeddingStore,
    ) -> None:
        self._embedder = embedder
        self._store = store

    # --- Эмбеддинг и запись ---

    def embed_text(self, text: str) -> List[float]:
        return self._embedder.embed_text(text)

    def upsert(self, record_id: str, text_or_vector: str | List[float]) -> None:
        if isinstance(text_or_vector, str):
            vector = self.embed_text(text_or_vector)
        else:
            vector = list(text_or_vector)
        self._store.upsert(record_id, vector)

    def delete(self, record_id: str) -> None:
        self._store.delete(record_id)

    # --- Поиск ---

    def search(
        self,
        query: str,
        *,
        limit: int = DEFAULT_LIMIT,
        min_score: float = RELEVANCE_THRESHOLD,
    ) -> List[SearchHit]:
        """Возвращает отсортированный список ``SearchHit`` с релевантностью ≥ ``min_score``.

        Валидация:
        - ``query`` должен быть строкой длиной 1..MAX_QUERY_LEN;
        - пустая / только пробельная строка → ``ValidationError``;
        - ``limit`` — в диапазоне 1..MAX_LIMIT.
        """
        if not isinstance(query, str):
            raise ValidationError.for_field(
                "query", f"ожидалась строка, получено {type(query).__name__}"
            )
        if query.strip() == "":
            raise ValidationError.for_field(
                "query", "не должен быть пустым или состоять только из пробелов"
            )
        if len(query) > MAX_QUERY_LEN:
            raise ValidationError.for_field(
                "query",
                f"длина {len(query)} превышает лимит {MAX_QUERY_LEN}",
            )
        if not 1 <= limit <= MAX_LIMIT:
            raise ValidationError.for_field(
                "limit", f"должен быть в диапазоне 1..{MAX_LIMIT}"
            )
        if not 0.0 <= min_score <= 1.0:
            raise ValidationError.for_field(
                "min_score", "должен быть в диапазоне 0.0..1.0"
            )

        vector = self.embed_text(query)
        # Берём запас кандидатов, чтобы после фильтра по min_score
        # вернуть до ``limit`` релевантных.
        fetch = min(max(limit * 2, MAX_LIMIT), MAX_LIMIT)
        raw = self._store.search(vector, fetch)
        hits: list[SearchHit] = []
        for record_id, distance in raw:
            cos_sim = 1.0 - float(distance)
            # Клампим на случай числовой погрешности
            if cos_sim > 1.0:
                cos_sim = 1.0
            elif cos_sim < -1.0:
                cos_sim = -1.0
            relevance = format_score((1.0 + cos_sim) / 2.0)
            if relevance < min_score:
                continue
            hits.append(SearchHit(record_id, relevance, cos_sim))
        hits.sort(key=lambda h: h.relevance_score, reverse=True)
        return hits[:limit]

    # --- Утилиты ---

    def count(self) -> int:
        return self._store.count()


def build_default_engine(lance_path: Path | str) -> EmbeddingEngine:
    """Собирает EmbeddingEngine с OllamaEmbedder и EmbeddingStore по умолчанию."""
    embedder = OllamaEmbedder()
    store = EmbeddingStore.open(lance_path)
    return EmbeddingEngine(embedder, store)
