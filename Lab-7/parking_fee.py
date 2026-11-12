"""Parking input helpers and an interactive demonstration."""

import re

_TIME_RANGE = re.compile(r"([0-9]{2}):([0-9]{2})-([0-9]{2}):([0-9]{2})")
_PLATE_COMPACT = re.compile(r"([A-Za-z]{2})([0-9]{2})([A-Za-z]{2})([0-9]{4})")
_PLATE_GROUPED = re.compile(r"([A-Za-z]{2}) ([0-9]{2}) ([A-Za-z]{2}) ([0-9]{4})")

RATES = {"bike": 10, "car": 30, "truck": 60}


def minutes_parked(times):
    """Return same-day elapsed minutes, or None for invalid HH:MM-HH:MM input."""
    if not isinstance(times, str):
        return None
    match = _TIME_RANGE.fullmatch(times.strip())
    if match is None:
        return None
    h1, m1, h2, m2 = map(int, match.groups())
    if h1 > 23 or h2 > 23 or m1 > 59 or m2 > 59:
        return None
    entry = h1 * 60 + m1
    departure = h2 * 60 + m2
    if departure < entry:
        return None
    return departure - entry


def hourly_rate(vehicle):
    """Return a supported vehicle's hourly rate, or None for invalid input."""
    if not isinstance(vehicle, str):
        return None
    return RATES.get(vehicle.strip().lower())


def format_plate(plate):
    """Normalize the lab's AA99AA9999 plate syntax, or return None."""
    if not isinstance(plate, str):
        return None
    text = plate.strip()
    match = _PLATE_COMPACT.fullmatch(text) or _PLATE_GROUPED.fullmatch(text)
    if match is None:
        return None
    return " ".join(match.groups()).upper()


def main():
    print("==== Running minutes_parked ====")
    user_input = input("Enter entry and exit time (e.g. 09:30-11:45): ")
    result = minutes_parked(user_input)
    print("Minutes Parked:", result)

    print("\n==== Running hourly_rate ====")
    user_input = input("Enter vehicle type (bike/car/truck): ")
    result = hourly_rate(user_input)
    print("Hourly Rate:", result)

    print("\n==== Running format_plate ====")
    user_input = input("Enter a number plate (e.g. ka01ab1234): ")
    result = format_plate(user_input)
    print("Formatted Plate:", result)

if __name__ == "__main__":
    main()
