"""Property-тесты генератора UUIDv7 (задача 2.8).

Покрывают:
- P3 (Monotonicity of id): в пределах одного процесса id монотонно растут
  лексикографически.
- Req 4.2: формат ``UUIDv7`` канонической длины 36, вариант RFC 4122.
"""

from __future__ import annotations

from hypothesis import given, settings, strategies as st

from tools.sml.ids import UUIDV7_RE, new_id, validate_id


@settings(max_examples=200)
@given(n=st.integers(min_value=2, max_value=200))
def test_new_id_is_monotonically_increasing(n: int) -> None:
    """n последовательных new_id() дают лексикографически возрастающую последовательность."""
    ids = [new_id() for _ in range(n)]
    # строгий порядок (без повторов)
    assert ids == sorted(ids)
    assert len(set(ids)) == n


@settings(max_examples=100)
@given(st.data())
def test_new_id_matches_uuidv7_format(data) -> None:
    ident = new_id()
    assert len(ident) == 36
    assert UUIDV7_RE.fullmatch(ident) is not None
    # validate_id не должен бросать исключение
    validate_id(ident)


def test_validate_id_rejects_garbage() -> None:
    import pytest

    bad = [
        "",
        "abc",
        "00000000-0000-0000-0000-000000000000",  # версия 0
        "00000000-0000-1000-8000-000000000000",  # версия 1
        "xxxxxxxx-xxxx-7xxx-8xxx-xxxxxxxxxxxx",  # не hex
        "00000000-0000-7000-c000-000000000000",  # неверный variant (c вместо 8-b)
    ]
    for value in bad:
        with pytest.raises(ValueError):
            validate_id(value)
