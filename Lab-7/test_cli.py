"""End-to-end checks for the original interactive parking demonstration."""

from pathlib import Path
import subprocess
import sys

import pytest

from parking_fee import main

ROOT = Path(__file__).resolve().parent


def run_cli(stdin):
    return subprocess.run(
        [sys.executable, str(ROOT / "parking_fee.py")],
        input=stdin, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, timeout=10, check=False,
    )


def test_cli_valid_inputs():
    result = run_cli("09:30-11:45\ncar\nka01ab1234\n")
    assert result.returncode == 0
    assert "Minutes Parked: 135" in result.stdout
    assert "Hourly Rate: 30" in result.stdout
    assert "Formatted Plate: KA 01 AB 1234" in result.stdout
    assert result.stderr == ""


def test_cli_invalid_inputs_continue_to_all_prompts():
    result = run_cli("\nhovercraft\nx\n")
    assert result.returncode == 0
    assert "Invalid time range" in result.stdout
    assert "Invalid vehicle type" in result.stdout
    assert "Invalid number plate" in result.stdout
    assert "Traceback" not in result.stdout
    assert result.stderr == ""


def test_cli_zero_duration_is_valid():
    result = run_cli("00:00-00:00\nBIKE\nKA 01 AB 1234\n")
    assert result.returncode == 0
    assert "Minutes Parked: 0" in result.stdout
    assert "Hourly Rate: 10" in result.stdout
    assert "Formatted Plate: KA 01 AB 1234" in result.stdout
    assert "Invalid" not in result.stdout
    assert result.stderr == ""


@pytest.mark.parametrize("stdin", ["", "09:30-11:45\n", "09:30-11:45\ncar\n"])
def test_cli_eof_at_each_prompt(stdin):
    result = run_cli(stdin)
    assert result.returncode == 0
    assert "Input ended" in result.stdout
    assert "Traceback" not in result.stdout
    assert result.stderr == ""


@pytest.mark.parametrize("accepted_inputs", [0, 1, 2])
def test_cli_ctrl_c_at_each_prompt(monkeypatch, capsys, accepted_inputs):
    inputs = iter(["09:30-11:45", "car", "ka01ab1234"][:accepted_inputs])

    def interrupt_when_exhausted(_prompt):
        try:
            return next(inputs)
        except StopIteration:
            raise KeyboardInterrupt from None

    monkeypatch.setattr("builtins.input", interrupt_when_exhausted)
    main()
    output = capsys.readouterr()
    assert "Input cancelled" in output.out
    assert "Traceback" not in output.out
    assert output.err == ""
