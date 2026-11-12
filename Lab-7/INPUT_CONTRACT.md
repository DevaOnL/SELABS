# Input validation contract

All three public helpers accept strings. Unsupported Python types, missing
values, empty strings, and malformed values return `None`; they do not raise
an exception. A valid zero-minute stay returns integer `0`, so callers must
check `is None` rather than truthiness.

## Entry and exit time

- Format: `HH:MM-HH:MM` with exactly two ASCII digits per field.
- Leading and trailing whitespace is ignored; internal whitespace is invalid.
- Hours are 00–23 and minutes are 00–59.
- Exit must be at or after entry on the same day.
- Valid results are integer minutes in the inclusive range 0–1439.

There is no date in this input. A backward time is rejected rather than
silently assuming an overnight stay. Equal times mean zero minutes.

## Hourly rate

Leading and trailing whitespace and letter case are ignored. The supported
values are `bike` (10), `car` (30), and `truck` (60). Unknown vehicle names
return `None`; no default rate is charged.

## Number plate

This exercise uses the starter's example format, `KA01AB1234`:

- Two ASCII letters, two ASCII digits, two ASCII letters, four ASCII digits.
- Accept compact input or four groups separated by single ASCII spaces,
  such as `ka01ab1234` or `ka 01 ab 1234`.
- Ignore surrounding whitespace; normalize letters to uppercase.
- Return the canonical representation `KA 01 AB 1234`.
- Reject short/long values, wrong group lengths, extra characters, punctuation,
  internal tabs/newlines, and Unicode lookalikes rather than truncating them.

This is syntax validation for the lab example, not a check against a national
vehicle registry or a validator for every real registration scheme.

## Command-line interaction

The CLI keeps the three original prompts and result headings. It explains
invalid input and continues to the next helper. End of input or Ctrl+C exits
cleanly with an explanatory message. None of these input errors prints a
traceback.
