# Lab 7: Fuzzing for Input Validation Bugs — Parking Fee

Student: Devansh Gupta · PES1UG24CS145 · Section C

Assigned repository: <https://github.com/SETAPESU26/L6_L7_19_parking_fee>

Source commit: `fef20d42191cdd992b14c5717db612b929c2cfd0` (`Lab 7/`).

This submission follows the Lab 7 fuzz-testing handout. The repository calls
its application `parking_fee.py` and its tests `test_parking_fee.py`; these
are the equivalents of the handout's generic `processor.py` filenames.

`baseline/parking_fee.py` is an unchanged copy of the assigned application.
`baseline/test_parking_fee.py.txt` preserves the incomplete test starter as
text so pytest does not try to collect its empty function bodies.

The three functions are `minutes_parked`, `hourly_rate`, and `format_plate`.
They will be fuzzed before being hardened, preserving both failures and
successful verification as evidence.
