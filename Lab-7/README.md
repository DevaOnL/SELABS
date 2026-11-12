# Lab 7: Fuzzing for Input Validation Bugs — Parking Fee

Student: Devansh Gupta · PES1UG24CS145 · Section C

Assigned repository: <https://github.com/SETAPESU26/L6_L7_19_parking_fee>

Source commit: `fef20d42191cdd992b14c5717db612b929c2cfd0` (`Lab 7/`).

This submission completes the Lab 7 fuzz-testing handout. The assigned files
are named `parking_fee.py` and `test_parking_fee.py`; they correspond to the
handout's generic `processor.py` and `test_processor.py` filenames.

## Submission files

- [PDF report with screenshots](PES1UG24CS145_SE_Lab7.pdf)
- [Fixed application](parking_fee.py)
- [Completed Hypothesis tests](test_parking_fee.py)
- [Command-line regression tests](test_cli.py)
- [Input rules and assumptions](INPUT_CONTRACT.md)
- [Bugs, minimized examples, and fixes](BUG_ANALYSIS.md)

## Install and run

Use Python 3.11 or later; this submission was run with Python 3.14.6. From
`Lab-7/`, create a virtual environment and install the pinned test dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python parking_fee.py
python -m pytest test_parking_fee.py
python -m pytest -q
```

On Windows, replace the activation command with
`.venv\Scripts\Activate.ps1`. If activation is blocked, use
`.venv\Scripts\python.exe` in place of `python`. The application itself uses
only the Python standard library.

The sample inputs `09:30-11:45`, `car`, and `ka01ab1234` produce 135 minutes,
a rate of 30, and `KA 01 AB 1234`. Invalid helper input returns `None`; the
CLI prints an explanation and continues. Equal entry and exit times return
zero. Backward times are rejected because the input does not include a date.

## Results

- Original three Hypothesis properties: **3 failed**.
- Fixed helpers: **79 passing test instances**, including 14 Hypothesis
  property instances and 65 explicit regression cases.
- Command-line checks: **9 passed**.
- Complete suite: **88 passed in 4.61 seconds** in the saved run.

A Hypothesis property executes multiple generated examples; the pytest test
count is not the generated-input count. Each property uses a maximum of 500
examples, and finite strategies can finish earlier.

## Before and after

`baseline/parking_fee.py` is unchanged upstream code. The supplied incomplete
test file is preserved as `baseline/test_parking_fee.py.txt`; a snapshot of
the first three completed properties is `baseline/fuzz_tests.py.txt`. These
snapshots use `.txt` so ordinary pytest discovery does not collect incomplete
or deliberately failing baseline tests. Original file hashes and the source
commit are recorded in `baseline/source.json`.

The first three properties fuzz `st.text() | st.none()` for each helper,
with up to 500 examples per property and deterministic generation. They
failed against the starter and pass against the fixed application. Hypothesis
found seven distinct failing outcomes across the three failing tests; the
full tracebacks include the minimized examples `None`, `""`, and `"00"`.
Directed boundary checks additionally expose invalid clock values, negative
durations, and silent truncation of long plates. See [BUG_ANALYSIS.md](BUG_ANALYSIS.md)
for the distinction between fuzz-discovered and directed examples.

The expanded suite verifies valid outputs with independent expected values,
not just crash resistance. It covers clock arithmetic, malformed time
fields, unknown vehicles, normalization, complete plate syntax, formatting
idempotence, unsupported Python types, and CLI error handling. A helper that
always returns `None` fails the generated valid-input properties.

## Evidence

| Handout step | Evidence |
| --- | --- |
| 2: Original application | [Valid run](screenshots/before_application_valid.png), [invalid run](screenshots/before_application_invalid.png) |
| 4: Failing fuzz tests | [Failure screenshot](screenshots/before_pytest_summary.png), [full tracebacks](reports/before/pytest.txt) |
| 5: Fixed application | [Valid run](screenshots/after_application_valid.png), [invalid run](screenshots/after_application_invalid.png) |
| 6: Passing tests | [Original three properties](screenshots/after_pytest_summary.png), [complete suite](screenshots/after_all_tests.png) |

The seven PNGs are direct Grim screenshots of commands running in a live,
fullscreen Foot terminal with the current user theme. The terminal shows the
working directory, commands, typed application inputs, results, and exit codes.

Matching terminal transcripts are under `reports/before/` and `reports/after/`.
The `terminal_*.ansi` files preserve the raw PTY output, including terminal
control sequences; the corresponding `.txt` files contain readable transcripts.
Detailed failure tracebacks remain in `reports/before/pytest.txt`.

[Baseline capture metadata](reports/before/screenshots.json) and
[fixed-application capture metadata](reports/after/screenshots.json) record the
capture time, fullscreen state, Foot process, Grim capture geometry, image
hashes, and matching transcript hashes. The command manifests also retain
source/test hashes and expected exit codes.

## Reproduce the evidence and report

Install the extra report tools only if rebuilding screenshots or the PDF.
Live capture requires a running Hyprland desktop with Foot, Grim, and Bash
installed. The capture script uses Hyprland 0.56's Lua dispatch interface,
loads the current Foot configuration, and enlarges the terminal font for
readability. It opens a temporary fullscreen workspace and restores the
previous workspace and focused window after capture.

```bash
python -m pip install -r requirements-report.txt
python tools/capture_evidence.py --phase before
python tools/capture_evidence.py --phase after
python tools/replay_counterexamples.py
python tools/capture_terminal_screenshots.py --phase before
python tools/capture_terminal_screenshots.py --phase after
python tools/build_report.py
python tools/verify_submission.py --write-report
```

The capture tool temporarily materializes the preserved three-property
snapshot as `baseline/fuzz_snapshot.py`, runs it from `baseline/` using
pytest's `--import-mode=importlib`, then removes the temporary file. This
selects the original application and preserves the exact initial tests. Baseline tests
and the invalid baseline application are expected to exit with code 1; the
capture tool treats that expected failure as successful evidence collection.
All fixed-application commands must exit with code 0. Rebuilding evidence
updates its timestamps and run timings.

These tests implement the documented lab input policy. They do not establish
validity against a real vehicle registry or prove correctness for every
possible input. Supporting files retain the failures as well as the fixes.
