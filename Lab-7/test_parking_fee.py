"""Hypothesis fuzz tests for all three parking input helpers."""

import pytest
from hypothesis import given, settings, strategies as st

from parking_fee import format_plate, hourly_rate, minutes_parked


@settings(max_examples=500, deadline=None, derandomize=True)
@given(st.text() | st.none())
def test_minutes_parked_no_crash(value):
    """Malformed text and missing values must be rejected without exceptions."""
    result = minutes_parked(value)
    assert result is None or (type(result) is int and 0 <= result <= 1439)


@settings(max_examples=500, deadline=None, derandomize=True)
@given(st.text() | st.none())
def test_hourly_rate_no_crash(value):
    """Only a supported numeric rate or the invalid-input sentinel is allowed."""
    result = hourly_rate(value)
    assert result is None or (type(result) is int and result in {10, 30, 60})


@settings(max_examples=500, deadline=None, derandomize=True)
@given(st.text() | st.none())
def test_format_plate_no_crash(value):
    """Formatting arbitrary Unicode must not index past a short string."""
    result = format_plate(value)
    assert result is None or (isinstance(result, str) and len(result) == 13)


@pytest.mark.parametrize(("value", "expected"), [
    ("09:30-11:45", 135),
    ("00:00-00:00", 0),
    ("23:59-23:59", 0),
    ("00:00-23:59", 1439),
    ("09:59-10:00", 1),
    (" 09:30-11:45 ", 135),
    ("25:00-26:00", None),
    ("09:60-10:00", None),
    ("00:00-24:00", None),
    ("11:00-10:00", None),
    ("23:30-00:30", None),
    ("9:30-11:45", None),
    ("09:30 - 11:45", None),
    ("09:30-11:45-extra", None),
    ("０９:３０-１１:４５", None),
])
def test_minutes_parked_regressions(value, expected):
    """Keep clock boundaries and silent baseline failures visible."""
    assert minutes_parked(value) == expected
