"""Тесты формата меток времени (задача 2.7)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from hypothesis import given, settings, strategies as st

from tools.sml.timefmt import format_iso8601_ms, now_utc_ms, parse_iso8601_ms


def test_round_trip_exact_millisecond() -> None:
    s = "2026-05-11T11:09:12.345Z"
    dt = parse_iso8601_ms(s)
    assert format_iso8601_ms(dt) == s


def test_parse_rejects_missing_ms() -> None:
    with pytest.raises(ValueError):
        parse_iso8601_ms("2026-05-11T11:09:12Z")


def test_parse_rejects_offset_form() -> None:
    with pytest.raises(ValueError):
        parse_iso8601_ms("2026-05-11T11:09:12.345+00:00")


def test_parse_rejects_microseconds_longer_than_three() -> None:
    with pytest.raises(ValueError):
        parse_iso8601_ms("2026-05-11T11:09:12.345678Z")


def test_now_utc_ms_matches_format() -> None:
    s = now_utc_ms()
    # Формат должен парситься обратно.
    parse_iso8601_ms(s)
    assert s.endswith("Z")
    assert len(s) == len("2026-05-11T11:09:12.345Z")


@settings(max_examples=200)
@given(
    dt=st.datetimes(
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2099, 12, 31, 23, 59, 59),
        timezones=st.just(timezone.utc),
    )
)
def test_format_parse_round_trip(dt) -> None:
    s = format_iso8601_ms(dt)
    again = parse_iso8601_ms(s)
    # Парсер/форматтер работают на миллисекундной точности,
    # поэтому сравниваем только до миллисекунд.
    assert again.year == dt.year
    assert again.month == dt.month
    assert again.day == dt.day
    assert again.hour == dt.hour
    assert again.minute == dt.minute
    assert again.second == dt.second
    assert again.microsecond == (dt.microsecond // 1000) * 1000
