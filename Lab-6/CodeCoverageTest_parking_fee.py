"""Exercise every statement in the assigned parking-fee application."""

import pytest

from parking_fee import find_slot, monthly_pass, parking_fee


@pytest.mark.parametrize(
    ("minutes", "expected"),
    [(30, 200), (61, 230)],
    ids=["free-stay-with-lost-ticket", "rounded-hours-with-ev-and-lost-ticket"],
)
def test_fee_statements(minutes, expected):
    assert parking_fee("car", minutes, True, True) == expected


@pytest.mark.parametrize(
    ("vehicle", "minutes", "message"),
    [("van", 60, "unknown vehicle"), ("car", -1, "invalid duration")],
)
def test_fee_validation(vehicle, minutes, message):
    with pytest.raises(ValueError, match=f"^{message}$"):
        parking_fee(vehicle, minutes, False, False)


@pytest.mark.parametrize(
    ("vehicle", "free_slots", "is_disabled", "expected"),
    [
        ("car", 0, False, "full"),
        ("car", 5, True, "ground floor"),
        ("truck", 5, False, "basement"),
        ("car", 5, False, "any floor"),
    ],
)
def test_slot_return_statements(vehicle, free_slots, is_disabled, expected):
    assert find_slot(vehicle, free_slots, is_disabled) == expected


@pytest.mark.parametrize(("vehicle", "expected"), [("bike", 400), ("car", 1200)])
def test_resident_pass_statements(vehicle, expected):
    assert monthly_pass(vehicle, True) == expected


def test_pass_rejects_truck():
    with pytest.raises(ValueError, match="^no pass for this vehicle$"):
        monthly_pass("truck", True)
