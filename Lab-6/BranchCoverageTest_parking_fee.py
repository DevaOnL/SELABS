"""Cover decision outcomes, boundaries, and interacting parking policies."""

import pytest

from parking_fee import find_slot, monthly_pass, parking_fee


@pytest.mark.parametrize(
    ("vehicle", "minutes", "expected"),
    [
        ("bike", 0, 0),
        ("bike", 1, 0),
        ("bike", 29, 0),
        ("bike", 30, 0),
        ("bike", 31, 10),
        ("bike", 59, 10),
        ("bike", 60, 10),
        ("bike", 61, 20),
        ("bike", 119, 20),
        ("bike", 120, 20),
        ("bike", 121, 30),
        ("car", 31, 30),
        ("car", 60, 30),
        ("car", 61, 60),
        ("truck", 31, 60),
        ("truck", 60, 60),
        ("truck", 61, 120),
        ("car", 1440, 720),
        ("truck", 1441, 1500),
    ],
)
def test_duration_boundaries_and_vehicle_rates(vehicle, minutes, expected):
    assert parking_fee(vehicle, minutes, False, False) == expected


@pytest.mark.parametrize(
    ("vehicle", "minutes", "expected"),
    [
        ("bike", 0, 0),
        ("bike", 30, 0),
        ("bike", 31, 5),
        ("bike", 60, 5),
        ("bike", 61, 10),
        ("car", 31, 15),
        ("car", 60, 15),
        ("car", 61, 30),
        ("truck", 31, 60),
        ("truck", 61, 120),
    ],
)
def test_ev_discount_and_truck_exclusion(vehicle, minutes, expected):
    assert parking_fee(vehicle, minutes, True, False) == expected


@pytest.mark.parametrize(
    ("vehicle", "minutes", "is_ev", "expected"),
    [
        ("bike", 0, False, 200),
        ("car", 30, False, 200),
        ("bike", 31, False, 210),
        ("car", 61, False, 260),
        ("truck", 60, False, 260),
        ("bike", 61, True, 210),
        ("car", 61, True, 230),
        ("truck", 61, True, 320),
    ],
)
def test_lost_ticket_penalty_is_added_after_discount(
    vehicle, minutes, is_ev, expected
):
    assert parking_fee(vehicle, minutes, is_ev, True) == expected


@pytest.mark.parametrize("vehicle", ["van", "", "CAR"])
def test_unknown_vehicle_is_rejected(vehicle):
    with pytest.raises(ValueError, match="^unknown vehicle$"):
        parking_fee(vehicle, 60, False, False)


@pytest.mark.parametrize("vehicle", ["bike", "car", "truck"])
def test_negative_duration_is_rejected(vehicle):
    with pytest.raises(ValueError, match="^invalid duration$"):
        parking_fee(vehicle, -1, False, False)


def test_vehicle_validation_precedes_duration_validation():
    with pytest.raises(ValueError, match="^unknown vehicle$"):
        parking_fee("van", -1, True, True)


@pytest.mark.parametrize(
    ("vehicle", "free_slots", "is_disabled", "expected"),
    [
        ("car", 0, False, "full"),
        ("car", -1, False, "full"),
        ("car", 0, True, "full"),
        ("truck", 0, True, "full"),
        ("truck", -1, True, "full"),
        ("bike", 1, True, "ground floor"),
        ("car", 1, True, "ground floor"),
        ("truck", 1, True, "ground floor"),
        ("truck", 1, False, "basement"),
        ("bike", 1, False, "any floor"),
        ("car", 1, False, "any floor"),
    ],
)
def test_slot_decisions_and_priority(vehicle, free_slots, is_disabled, expected):
    assert find_slot(vehicle, free_slots, is_disabled) == expected


@pytest.mark.parametrize(
    ("vehicle", "is_resident", "expected"),
    [
        ("bike", False, 500),
        ("bike", True, 400),
        ("car", False, 1500),
        ("car", True, 1200),
    ],
)
def test_monthly_pass_prices_with_and_without_residency(
    vehicle, is_resident, expected
):
    assert monthly_pass(vehicle, is_resident) == expected


@pytest.mark.parametrize("vehicle", ["truck", "van", ""])
@pytest.mark.parametrize("is_resident", [False, True])
def test_unsupported_monthly_pass_is_rejected(vehicle, is_resident):
    with pytest.raises(ValueError, match="^no pass for this vehicle$"):
        monthly_pass(vehicle, is_resident)
