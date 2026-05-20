"""Pydantic-модель ``Memory_Record``.

Модель закрыта от лишних полей (``extra="forbid"``) и сохраняет
побайтовое содержимое без трогания пробелов (``str_strip_whitespace=False``,
Req 9.1).

Требования: Req 4.1, Req 4.2, Req 5.3, Req 6.1, Req 8.4, Req 9.1.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .ids import UUIDV7_RE
from .timefmt import parse_iso8601_ms
from .validation import (
    MEMORY_TYPE_VALUES,
    MemoryType,
    validate_source_lines,
    validate_tags,
)

__all__ = ["MemoryRecord"]


class MemoryRecord(BaseModel):
    """Единица хранения Shared_Memory_Layer.

    Поля:
    - ``id``              — UUIDv7 (36 символов).
    - ``type``            — один из 8 типов из ``MemoryType``.
    - ``content``         — 1–10000 символов UTF-8, без обрезки пробелов.
    - ``author_agent``    — 1–128 символов, имя агента (codex/cursor/kiro/…).
    - ``created_at``      — ISO 8601 UTC с миллисекундами.
    - ``updated_at``      — тот же формат.
    - ``is_current``      — bool, при создании ``True``.
    - ``supersedes_id``   — опциональный UUIDv7 суперседируемой записи.
    - ``superseded_by_id``— заполняется автоматически при суперседировании.
    - ``source_file``     — относительный путь от корня проекта.
    - ``source_lines``    — ``"start-end"``, 1≤start≤end.
    - ``tags``            — 0–20 тегов, каждый 1–64 символов.
    - ``embedding_vector``— 1024-мерный float32, хранится в LanceDB (в MCP не сериализуется).
    - ``relevance_score_last`` — транзиентное значение релевантности (только в ответах).
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)

    id: str
    type: MemoryType
    content: str = Field(min_length=1, max_length=10000)
    author_agent: str = Field(min_length=1, max_length=128)
    created_at: str
    updated_at: str
    is_current: bool = True
    supersedes_id: Optional[str] = None
    superseded_by_id: Optional[str] = None
    source_file: Optional[str] = None
    source_lines: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    embedding_vector: Optional[List[float]] = None
    relevance_score_last: Optional[float] = None

    # --- Валидаторы ---

    @field_validator("id")
    @classmethod
    def _check_id(cls, v: str) -> str:
        if not isinstance(v, str) or len(v) != 36 or UUIDV7_RE.fullmatch(v) is None:
            raise ValueError(
                "id должен быть канонической строкой UUIDv7 длиной 36 символов"
            )
        return v

    @field_validator("supersedes_id", "superseded_by_id")
    @classmethod
    def _check_optional_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) != 36 or UUIDV7_RE.fullmatch(v) is None:
            raise ValueError(
                "supersedes_id/superseded_by_id должны быть UUIDv7 длиной 36"
            )
        return v

    @field_validator("type", mode="before")
    @classmethod
    def _check_type(cls, v: object) -> object:
        # pydantic сам валидирует enum, но даём понятное сообщение заранее
        if isinstance(v, MemoryType):
            return v
        if isinstance(v, str) and v not in MEMORY_TYPE_VALUES:
            raise ValueError(
                f"Неизвестный тип Memory_Record: {v!r}. "
                f"Допустимо: {sorted(MEMORY_TYPE_VALUES)}"
            )
        return v

    @field_validator("content")
    @classmethod
    def _check_content_not_whitespace(cls, v: str) -> str:
        # Пробелы НЕ обрезаем (Req 9.1 — побайтовая сохранность),
        # но запрещаем значения, состоящие только из пробельных символов.
        if v.strip() == "":
            raise ValueError("content не должен состоять только из пробельных символов")
        return v

    @field_validator("created_at", "updated_at")
    @classmethod
    def _check_iso8601(cls, v: str) -> str:
        parse_iso8601_ms(v)
        return v

    @field_validator("source_lines")
    @classmethod
    def _check_source_lines(cls, v: Optional[str]) -> Optional[str]:
        try:
            return validate_source_lines(v)
        except Exception as exc:
            raise ValueError(str(exc)) from exc

    @field_validator("tags")
    @classmethod
    def _check_tags(cls, v: List[str]) -> List[str]:
        try:
            return validate_tags(v)
        except Exception as exc:
            raise ValueError(str(exc)) from exc

    @field_validator("embedding_vector")
    @classmethod
    def _check_vector(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        if v is None:
            return v
        if len(v) != 1024:
            raise ValueError(
                f"embedding_vector должен быть длиной 1024, получено {len(v)}"
            )
        return v

    @field_validator("relevance_score_last")
    @classmethod
    def _check_score(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if not 0.0 <= float(v) <= 1.0:
            raise ValueError(
                f"relevance_score_last должен быть в [0.0, 1.0], получено {v}"
            )
        return v

    # --- Утилиты ---

    def as_public_dict(self) -> dict:
        """Dict для MCP-ответа без ``embedding_vector`` (не уходит клиенту)."""
        data = self.model_dump()
        data.pop("embedding_vector", None)
        # relevance_score_last — заполняется только в результатах семантического
        # поиска, в обычном read его не возвращаем, если None.
        if data.get("relevance_score_last") is None:
            data.pop("relevance_score_last", None)
        return data
