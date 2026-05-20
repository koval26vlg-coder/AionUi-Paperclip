"""Property-тесты модели Memory_Record (задача 2.8).

Свойства:
- P9 UTF-8 Fidelity: произвольная UTF-8 строка сохраняется побайтово.
- P3 (часть): при создании ``is_current = True`` сохраняется.
- Req 4.3: недопустимые значения отклоняются.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from tools.sml.ids import new_id
from tools.sml.models import MemoryRecord
from tools.sml.timefmt import now_utc_ms


def _base_record(**overrides) -> dict:
    now = now_utc_ms()
    data = dict(
        id=new_id(),
        type="fact",
        content="пример факта",
        author_agent="kiro",
        created_at=now,
        updated_at=now,
        is_current=True,
        supersedes_id=None,
        superseded_by_id=None,
        source_file=None,
        source_lines=None,
        tags=[],
    )
    data.update(overrides)
    return data


def test_valid_record_creates() -> None:
    rec = MemoryRecord.model_validate(_base_record())
    assert rec.is_current is True
    assert rec.type.value == "fact"
    assert rec.content == "пример факта"


def test_extra_fields_are_forbidden() -> None:
    data = _base_record()
    data["malicious"] = "hack"
    with pytest.raises(ValueError):
        MemoryRecord.model_validate(data)


def test_content_whitespace_only_rejected() -> None:
    with pytest.raises(ValueError):
        MemoryRecord.model_validate(_base_record(content="   \t\n"))


def test_content_empty_rejected() -> None:
    with pytest.raises(ValueError):
        MemoryRecord.model_validate(_base_record(content=""))


def test_content_too_long_rejected() -> None:
    with pytest.raises(ValueError):
        MemoryRecord.model_validate(_base_record(content="а" * 10001))


def test_unknown_type_rejected() -> None:
    with pytest.raises(ValueError):
        MemoryRecord.model_validate(_base_record(type="unknown_type"))


def test_source_lines_invalid_format_rejected() -> None:
    with pytest.raises(ValueError):
        MemoryRecord.model_validate(_base_record(source_lines="abc"))


def test_source_lines_reversed_rejected() -> None:
    with pytest.raises(ValueError):
        MemoryRecord.model_validate(_base_record(source_lines="10-5"))


def test_tags_duplicates_rejected() -> None:
    with pytest.raises(ValueError):
        MemoryRecord.model_validate(_base_record(tags=["a", "a"]))


def test_as_public_dict_strips_embedding() -> None:
    rec = MemoryRecord.model_validate(
        _base_record(embedding_vector=[0.0] * 1024)
    )
    data = rec.as_public_dict()
    assert "embedding_vector" not in data
    assert data["content"] == "пример факта"


# --- Property-based ---


# Произвольный непробельный текст 1..10000 UTF-8: кириллица, эмодзи, знаки.
_content_strategy = st.text(
    alphabet=st.characters(
        min_codepoint=0x20, max_codepoint=0xFFFF,
        blacklist_categories=("Cs",),  # surrogates — не в UTF-8 payload
    ),
    min_size=1,
    max_size=2000,
).filter(lambda s: s.strip() != "")


@settings(max_examples=200, deadline=None)
@given(content=_content_strategy)
def test_utf8_fidelity_byte_identical(content: str) -> None:
    """P9: Memory_Record сохраняет content без экранирования/транслитерации."""
    rec = MemoryRecord.model_validate(_base_record(content=content))
    assert rec.content == content
    # И через round-trip через dict:
    again = MemoryRecord.model_validate(rec.model_dump())
    assert again.content == content
