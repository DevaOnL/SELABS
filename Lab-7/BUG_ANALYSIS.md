# Bugs found before fixing the application

The first three Hypothesis properties each generated Unicode strings and
`None`, with up to 500 examples per property. All three properties failed.
Hypothesis shrank the failures to the inputs below; the full tracebacks are
saved in `reports/before/pytest.txt`.

| Helper | Minimized input | Original behavior | Required behavior |
| --- | --- | --- | --- |
| `minutes_parked` | `None` | `AttributeError` on `.split()` | Return `None` |
| `minutes_parked` | `""` | `ValueError` while unpacking | Return `None` |
| `hourly_rate` | `None` | `AttributeError` on `.strip()` | Return `None` |
| `hourly_rate` | `""` | `KeyError` on dictionary lookup | Return `None` |
| `format_plate` | `None` | `AttributeError` on `.upper()` | Return `None` |
| `format_plate` | `""` | `IndexError` on character access | Return `None` |
| `format_plate` | `"00"` | Returns malformed `"00   "` | Return `None` |

These are seven distinct failing outcomes across three failing tests. They
are not seven separate pytest test cases. Shrinking finds small witnesses;
it does not mean that only those inputs are broken.

Directed checks of the input rules also expose these silent validation bugs:

| Input | Original result | Why it is invalid |
| --- | --- | --- |
| `25:00-26:00` | 60 | Hours exceed 23 |
| `09:60-10:00` | 0 | Minute field exceeds 59 |
| `11:00-10:00` | -60 | Exit precedes entry in the same day |
| `KA01AB123456` | `KA 01 AB 1234` | Extra characters are silently discarded |

The directed examples are kept separate from the cases discovered by
Hypothesis. `tools/replay_counterexamples.py` executes both groups against
the preserved baseline and the current application.

## Fix approach

Validate the type before invoking string methods. Match the complete input,
check clock ranges and time order, use a safe lookup for vehicle rates, and
validate the entire plate before formatting it. The helpers use `None` for
invalid input, while the command-line layer supplies messages for the user.
The input rules are recorded in `INPUT_CONTRACT.md` because the starter does
not define policies for overnight stays or alternate registration formats.
