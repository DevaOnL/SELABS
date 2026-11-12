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
    """Run the three demonstrations and explain invalid or interrupted input."""
    steps = (
        (
            "minutes_parked",
            "Enter entry and exit time (e.g. 09:30-11:45): ",
            minutes_parked,
            "Minutes Parked:",
            "Invalid time range. Use HH:MM-HH:MM in same-day order.",
        ),
        (
            "hourly_rate",
            "Enter vehicle type (bike/car/truck): ",
            hourly_rate,
            "Hourly Rate:",
            "Invalid vehicle type. Choose bike, car, or truck.",
        ),
        (
            "format_plate",
            "Enter a number plate (e.g. ka01ab1234): ",
            format_plate,
            "Formatted Plate:",
            "Invalid number plate. Use KA01AB1234 or KA 01 AB 1234 format.",
        ),
    )
    try:
        for index, (name, prompt, handler, label, error) in enumerate(steps):
            if index:
                print()
            print(f"==== Running {name} ====")
            result = handler(input(prompt))
            if result is None:
                print(error)
            else:
                print(label, result)
    except EOFError:
        print("\nInput ended. Exiting.")
    except KeyboardInterrupt:
        print("\nInput cancelled. Exiting.")


if __name__ == "__main__":
    main()
