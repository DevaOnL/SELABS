"""Hypothesis fuzz tests for all three parking input helpers."""

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
