"""Compare minimized fuzz examples and directed boundary cases with the baseline."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("minutes_parked", None, "Hypothesis"),
    ("minutes_parked", "", "Hypothesis"),
    ("hourly_rate", None, "Hypothesis"),
    ("hourly_rate", "", "Hypothesis"),
    ("format_plate", None, "Hypothesis"),
    ("format_plate", "", "Hypothesis"),
    ("format_plate", "00", "Hypothesis"),
    ("minutes_parked", "25:00-26:00", "directed boundary"),
    ("minutes_parked", "11:00-10:00", "directed boundary"),
    ("minutes_parked", "09:60-10:00", "directed boundary"),
    ("format_plate", "KA01AB123456", "directed boundary"),
]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def outcome(module, function, value):
    try:
        return repr(getattr(module, function)(value))
    except (AttributeError, ValueError, KeyError, IndexError, TypeError) as error:
        return f"{type(error).__name__}: {error}"


if __name__ == "__main__":
    baseline = load(ROOT / "baseline" / "parking_fee.py", "baseline_parking")
    fixed = load(ROOT / "parking_fee.py", "fixed_parking")
    for function, value, origin in CASES:
        print(f"{function}({value!r}) [{origin}]")
        print(f"  baseline: {outcome(baseline, function, value)}")
        print(f"  current:  {outcome(fixed, function, value)}")
