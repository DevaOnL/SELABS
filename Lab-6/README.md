# Lab 6: Code and Branch Coverage — Parking Fee

**Student:** Devansh Gupta · **SRN:** PES1UG24CS145

**Assigned repository:** <https://github.com/SETAPESU26/L6_L7_19_parking_fee>

**Source commit:** `af37455c32c127506e00acc63ccd5e3309c7ce0b`

The assigned `parking_fee.py` and `test_parking_fee.py` are copied unchanged
from the repository's `Lab 6/` directory. The application calculates parking
fees, chooses a parking floor, and prices monthly passes.

## Setup

Run these commands from `Lab-6/` with Python 3.10 or later:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` in place of
`python` in the commands below. Coverage measures only `parking_fee.py` via
`.coveragerc`; tests are outside the coverage denominator.

## Initial coverage

```powershell
python -m coverage run --data-file=.coverage.baseline-line -m pytest test_parking_fee.py -q
python -m coverage report --data-file=.coverage.baseline-line -m
python -m coverage run --branch --data-file=.coverage.baseline-branch -m pytest test_parking_fee.py -q
python -m coverage report --data-file=.coverage.baseline-branch -m
```

Both starter tests pass. They execute 15 of 34 statements (**44.12%**) and
8 of 24 branch outcomes (**33.33%**). No monthly-pass path is exercised;
paid parking, errors, EV discounts, ticket penalties, and the special slot
assignments are also untested.

The branch-mode `Cover` column is a combined statement-and-branch percentage:
`(15 + 8) / (34 + 24) = 39.66%`. It is different from branch coverage alone.
The raw output is in [reports/baseline.txt](reports/baseline.txt), and the
counts are in [reports/baseline.json](reports/baseline.json).

The handout requests screenshots only after reaching at least 90% coverage,
so the initial results are retained as text and JSON.
