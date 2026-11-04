import pytest
from parking_fee import parking_fee, find_slot, monthly_pass

#Example test cases:
def test_free_short_stay():
    assert parking_fee("car", 20, False, False) == 0

def test_any_floor():
    assert find_slot("car", 5, False) == "any floor"

#Write the rest of the test cases so that the code is 90- 100% covered.
