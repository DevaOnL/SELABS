"""Run real lab commands and preserve their unedited merged output."""

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASIC_TESTS = [
    "test_minutes_parked_no_crash",
    "test_hourly_rate_no_crash",
    "test_format_plate_no_crash",
]


def _capture(phase):
    """Replay the original or final application and record command metadata."""
    output_dir = ROOT / "reports" / phase
    output_dir.mkdir(parents=True, exist_ok=True)
    cwd = ROOT / "baseline" if phase == "before" else ROOT
    test_file = "fuzz_snapshot.py" if phase == "before" else "test_parking_fee.py"
    tests = [f"{test_file}::{name}" for name in BASIC_TESTS]
    cases = [
        ("application_valid", ["-u", "parking_fee.py"],
         "09:30-11:45\ncar\nka01ab1234\n", 0),
        ("application_invalid", ["-u", "parking_fee.py"],
         "\nhovercraft\nx\n", 1 if phase == "before" else 0),
        ("pytest", ["-m", "pytest", "--import-mode=importlib", *tests,
                    "-q", "--tb=short", "--color=no"], None,
         1 if phase == "before" else 0),
        ("pytest_summary", ["-m", "pytest", "--import-mode=importlib", *tests,
                            "-q", "--tb=no", "--color=no"], None,
         1 if phase == "before" else 0),
    ]
    if phase == "after":
        cases.extend([
            ("all_tests", ["-m", "pytest", "-q", "--color=no"], None, 0),
            ("counterexamples", ["tools/replay_counterexamples.py"], None, 0),
        ])
    records = []
    for name, args, stdin, expected_exit in cases:
        started = datetime.now(timezone.utc).isoformat()
        completed = subprocess.run(
            [sys.executable, *args], cwd=cwd, input=stdin or "",
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=180, check=False,
        )
        output = completed.stdout
        (output_dir / f"{name}.txt").write_text(output, encoding="utf-8", newline="")
        records.append({
            "name": name,
            "started_utc": started,
            "command": shlex.join(["python", *args]),
            "cwd_relative_to_lab": str(cwd.relative_to(ROOT)) or ".",
            "stdin": stdin,
            "exit_code": completed.returncode,
            "expected_exit_code": expected_exit,
            "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
        })
        print(f"{phase}/{name}: exit {completed.returncode} (expected {expected_exit})")
        if completed.returncode != expected_exit:
            raise SystemExit(f"Unexpected outcome for {name}; inspect saved output")
    metadata = {
        "python": sys.version,
        "dependencies": {name: version(name) for name in ["hypothesis", "pytest"]},
        "phase": phase,
        "application_sha256": hashlib.sha256(
            (cwd / "parking_fee.py").read_bytes()
        ).hexdigest(),
        "tests_sha256": hashlib.sha256(
            (cwd / test_file).read_bytes()
        ).hexdigest(),
        "commands": records,
    }
    if phase == "after":
        metadata["cli_tests_sha256"] = hashlib.sha256(
            (ROOT / "test_cli.py").read_bytes()
        ).hexdigest()
    (output_dir / "manifest.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8",
    )


def capture(phase):
    """Replay the exact preserved starter properties when collecting failures."""
    if phase == "after":
        return _capture(phase)
    snapshot = ROOT / "baseline/fuzz_snapshot.py"
    if snapshot.exists():
        raise SystemExit(f"Refusing to overwrite an existing file: {snapshot}")
    try:
        snapshot.write_bytes((ROOT / "baseline/fuzz_tests.py.txt").read_bytes())
        return _capture(phase)
    finally:
        snapshot.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True, choices=["before", "after"])
    capture(parser.parse_args().phase)
