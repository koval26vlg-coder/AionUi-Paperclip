"""Интеграционные тесты EmbeddingEngine с реальной Ollama (задачи 4.1–4.6).

Требуют запущенной Ollama на 127.0.0.1:11434 с моделью bge-m3.
Если Ollama недоступна — тесты скипаются.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import requests

from tools.sml.embedding_engine import (
    EMBEDDING_DIM,
    EmbeddingEngine,
    EmbeddingStore,
    OllamaEmbedder,
    build_default_engine,
)
from tools.sml.errors import IOErrorSML, ValidationError


def _ollama_running() -> bool:
    try:
        r = requests.get("http://127.0.0.1:11434/api/version", timeout=2)
        return r.status_code == 200
    except requests.RequestException:
        return False


pytestmark = pytest.mark.skipif(
    not _ollama_running(),
    reason="Ollama не запущена на 127.0.0.1:11434",
)


@pytest.fixture
def engine(tmp_path: Path) -> EmbeddingEngine:
    return build_default_engine(tmp_path / "lance")


# --- OllamaEmbedder ---


def test_ollama_embed_russian_text_returns_1024() -> None:
    emb = OllamaEmbedder()
    v = emb.embed_text("проверка русского языка")
    assert len(v) == EMBEDDING_DIM
    assert all(isinstance(x, float) for x in v)


def test_ollama_embed_determinism() -> None:
    emb = OllamaEmbedder()
    v1 = emb.embed_text("тест детерминизма")
    v2 = emb.embed_text("тест детерминизма")
    # bge-m3 детерминирован при одинаковом входе
    assert v1 == v2


def test_ollama_rejects_non_loopback_host() -> None:
    with pytest.raises(IOErrorSML):
        OllamaEmbedder(host="example.com")


def test_ollama_rejects_empty_text() -> None:
    emb = OllamaEmbedder()
    with pytest.raises(ValidationError):
        emb.embed_text("")


def test_ollama_rejects_too_long_text() -> None:
    emb = OllamaEmbedder()
    with pytest.raises(ValidationError):
        emb.embed_text("x" * 2000)


# --- EmbeddingStore ---


def test_store_upsert_and_count(tmp_path: Path) -> None:
    store = EmbeddingStore.open(tmp_path / "lance")
    vec = [0.0] * EMBEDDING_DIM
    vec[0] = 1.0
    store.upsert("id-1", vec)
    assert store.count() == 1
    # Повторный upsert не увеличивает количество (идемпотентно)
    store.upsert("id-1", vec)
    assert store.count() == 1


def test_store_rejects_wrong_dim(tmp_path: Path) -> None:
    store = EmbeddingStore.open(tmp_path / "lance")
    with pytest.raises(ValidationError):
        store.upsert("id-1", [0.0] * 10)


# --- EmbeddingEngine.search ---


def test_search_finds_exact_text(engine: EmbeddingEngine) -> None:
    engine.upsert("r1", "семантический поиск в базе памяти")
    engine.upsert("r2", "приготовление борща")
    engine.upsert("r3", "расписание электричек")
    hits = engine.search("поиск в памяти", limit=5)
    assert len(hits) >= 1
    assert hits[0].record_id == "r1"
    assert hits[0].relevance_score >= 0.5


def test_search_returns_empty_for_irrelevant(engine: EmbeddingEngine) -> None:
    engine.upsert("r1", "машинное обучение и нейросети")
    # Совсем нерелевантный запрос; если bge-m3 всё же найдёт сходство,
    # порог 0.9 гарантированно отсечёт.
    hits = engine.search("картофельные чипсы", limit=5, min_score=0.9)
    assert hits == []


def test_search_finds_by_synonym(engine: EmbeddingEngine) -> None:
    """Req 5.5: синоним/перефразирование попадают в первые 10 результатов."""
    engine.upsert("r1", "стартовый контекстный пакет для нового агента")
    engine.upsert("r2", "рецепт пиццы")
    engine.upsert("r3", "настройка SSL сертификатов")
    hits = engine.search("инициализация контекста agent", limit=10)
    ids = [h.record_id for h in hits]
    assert "r1" in ids


def test_search_validates_query(engine: EmbeddingEngine) -> None:
    with pytest.raises(ValidationError):
        engine.search("")
    with pytest.raises(ValidationError):
        engine.search("   ")
    with pytest.raises(ValidationError):
        engine.search("x" * 2000)
    with pytest.raises(ValidationError):
        engine.search("норма", limit=0)
    with pytest.raises(ValidationError):
        engine.search("норма", limit=100)


def test_search_determinism(engine: EmbeddingEngine) -> None:
    """P8: два последовательных поиска дают идентичные id и score."""
    engine.upsert("a", "первая запись про Python")
    engine.upsert("b", "вторая запись про ML")
    engine.upsert("c", "третья запись про памать агентов")

    hits1 = [(h.record_id, h.relevance_score) for h in engine.search("python", limit=10)]
    hits2 = [(h.record_id, h.relevance_score) for h in engine.search("python", limit=10)]
    assert hits1 == hits2


def test_score_in_bounds(engine: EmbeddingEngine) -> None:
    engine.upsert("r1", "тест границ метрики")
    hits = engine.search("границы метрики", limit=5)
    for h in hits:
        assert 0.0 <= h.relevance_score <= 1.0
        # Три знака после запятой после round()
        assert round(h.relevance_score, 3) == h.relevance_score
