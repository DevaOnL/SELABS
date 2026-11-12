"""Hypothesis fuzz tests for all three parking input helpers."""

from datetime import datetime
import string

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


@pytest.mark.parametrize(("value", "expected"), [
    ("bike", 10),
    ("car", 30),
    ("truck", 60),
    (" BIKE ", 10),
    ("CaR", 30),
    ("\tTruck\n", 60),
    ("", None),
    ("   ", None),
    ("hovercraft", None),
    ("car truck", None),
    ("cars", None),
    (None, None),
    (123, None),
])
def test_hourly_rate_regressions(value, expected):
    """Preserve prices and normalization while rejecting unknown vehicles."""
    assert hourly_rate(value) == expected


@pytest.mark.parametrize(("value", "expected"), [
    ("ka01ab1234", "KA 01 AB 1234"),
    ("KA01AB1234", "KA 01 AB 1234"),
    (" ka01ab1234 ", "KA 01 AB 1234"),
    ("ka 01 ab 1234", "KA 01 AB 1234"),
    ("KA 01 AB 1234", "KA 01 AB 1234"),
    ("", None),
    ("x", None),
    ("00", None),
    ("KA01AB123456", None),
    ("KA01AB123", None),
    ("KA-01-AB-1234", None),
    ("KA01 AB1234", None),
    ("KA  01 AB 1234", None),
    ("KA\t01 AB 1234", None),
    ("KA01AB１２３４", None),
    ("KA01AB1234", None),
    ("ß01AB1234", None),
])
def test_format_plate_regressions(value, expected):
    """Reject partial plates and Unicode lookalikes before normalization."""
    assert format_plate(value) == expected


def clock_text(total_minutes):
    """Build inputs from generated minute offsets, without parsing them."""
    hour, minute = divmod(total_minutes, 60)
    return f"{hour:02d}:{minute:02d}"


@settings(max_examples=500, deadline=None, derandomize=True)
@given(st.integers(0, 1439), st.integers(0, 1439))
def test_valid_time_ranges_match_datetime(first, second):
    start, finish = sorted((first, second))
    entry = datetime(2026, 1, 1, *divmod(start, 60))
    departure = datetime(2026, 1, 1, *divmod(finish, 60))
    expected = int((departure - entry).total_seconds() / 60)
    assert minutes_parked(f"{clock_text(start)}-{clock_text(finish)}") == expected


@settings(max_examples=500, deadline=None, derandomize=True)
@given(st.integers(1, 1439), st.data())
def test_generated_backward_time_ranges_are_rejected(start, data):
    finish = data.draw(st.integers(0, start - 1), label="earlier exit")
    assert minutes_parked(f"{clock_text(start)}-{clock_text(finish)}") is None


@settings(max_examples=500, deadline=None, derandomize=True)
@given(
    st.sampled_from([
        ("bike", 10), ("BIKE", 10), ("BiKe", 10),
        ("car", 30), ("CAR", 30), ("CaR", 30),
        ("truck", 60), ("TRUCK", 60), ("TrUcK", 60),
    ]),
    st.text(alphabet=" \t\r\n", max_size=5),
    st.text(alphabet=" \t\r\n", max_size=5),
)
def test_generated_known_rates_are_exact(vehicle_and_rate, before, after):
    vehicle, expected = vehicle_and_rate
    assert hourly_rate(before + vehicle + after) == expected


@settings(max_examples=500, deadline=None, derandomize=True)
@given(st.text())
def test_generated_unknown_vehicle_names_are_rejected(value):
    assert hourly_rate("unknown:" + value) is None


@settings(max_examples=500, deadline=None, derandomize=True)
@given(
    state=st.text(alphabet=string.ascii_letters, min_size=2, max_size=2),
    district=st.integers(0, 99),
    series=st.text(alphabet=string.ascii_letters, min_size=2, max_size=2),
    serial=st.integers(0, 9999),
    grouped=st.booleans(),
    padding=st.sampled_from(["", " ", "\t", "\n"]),
)
def test_generated_valid_plates_are_normalized_and_idempotent(
    state, district, series, serial, grouped, padding,
):
    parts = [state, f"{district:02d}", series, f"{serial:04d}"]
    value = (" " if grouped else "").join(parts)
    expected = f"{state.upper()} {district:02d} {series.upper()} {serial:04d}"
    result = format_plate(padding + value + padding)
    assert result == expected
    assert format_plate(result) == result


@settings(max_examples=500, deadline=None, derandomize=True)
@given(st.integers(0, 99), st.integers(0, 9999), st.text(min_size=1))
def test_generated_plate_suffix_is_never_silently_truncated(district, serial, extra):
    value = f"KA{district:02d}AB{serial:04d}"
    assert format_plate(value + "!" + extra) is None
