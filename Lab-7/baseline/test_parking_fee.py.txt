from hypothesis import given, strategies as st
from parking_fee import minutes_parked, hourly_rate, format_plate

@given(st.text() | st.none())
def test_minutes_parked_no_crash(s):

@given(st.text() | st.none())
def test_hourly_rate_no_crash(s):

@given(st.text() | st.none())
def test_format_plate_no_crash(s):
