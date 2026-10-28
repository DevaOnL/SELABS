# Reflection — Lab 5: Static Code Analysis

Student: Devansh Gupta (PES1UG24CS145) · Repo: L5_19_music_catalog

## Q1. What does static code analysis do, and how is it different from running and testing the program?

Static analysis examines the source code *without executing it*. The program
worked when I ran it — it printed the playlist summary and the popularity
ratings — yet the tools found a SQL injection, an arbitrary-code-execution
hole, a shared-list bug and a pile of style violations. That is the key
difference from testing: a test only checks the paths and inputs I thought to
try, while static analysis reasons about the code itself and flags patterns
that are *always* dangerous, whatever inputs happen to be used in a demo run.
My run never fed a song title containing a quote into `addSong`, so the SQL
injection never fired — the vulnerability was still there. Static analysis
finds the bugs my tests never trigger.

## Q2. What did each tool focus on, and which findings were the most serious?

- **Pylint** was the strict code reviewer. It gave the original file 4.57/10
  and found 23 messages: missing docstrings, camelCase function names, the
  mutable default argument `playlist=[]` (W0102), a bare `except:` (W0702), an
  `else` after `return`, %-formatting, over-long lines and two statements
  crammed onto one line.
- **Flake8** was the grammar checker: 7 PEP 8 findings — four lines over 79
  characters (E501), the bare `except` again (E722), the ambiguous variable
  name `l` (E741) and an `if: print()` one-liner (E701).
- **Bandit** was the security guard: 4 findings — SQL injection through
  string-built SQL (B608, medium), `pickle.loads` insecure deserialization
  (B301, plus the `import pickle` B403), and `random.choice` (B311, low).

The most serious were Bandit's B608 and B301. B608 meant any song title was
parsed as SQL — one quoted character crashes the insert, a crafted one rewrites
the query. B301 was worse: `pickle.loads()` executes code hidden in the blob,
so a tampered "playlist file" would give an attacker full code execution. The
style findings are annoyances; these two are attack vectors.

## Q3. What are the limits of static analysis? What can it not catch?

Three things stood out. First, it knows nothing about *intent or logic*: no
tool noticed that the popularity threshold is a hardcoded 100, or that the
`except: return 0` silently converts every database failure into "zero plays".
Second, it cannot see runtime or data problems — a schema that loses data, a
wrong query result, performance, or concurrency issues are invisible to it.
Third, it produces false positives: Bandit flagged `random.choice` (B311)
because `random` is not cryptographically secure, but picking a demo song is
not a security decision. I handled that with a `# nosec B311` comment and a
justification rather than blindly "fixing" it — knowing when a finding is a
false positive is as important as fixing the real ones. Static analysis is a
cheap first line of defence, not a replacement for thinking, tests and review.

## Q4. How does static analysis contribute to code quality and maintainability, and how will you use it going forward?

It catches entire bug classes before the code ever runs — the mutable default
argument and the bare `except` in this file had been sitting there working
"just fine" until the tools named them. It also enforces one set of
conventions: after renaming to snake_case, adding docstrings and fixing line
lengths, the file reads like any other Python codebase instead of a personal
dialect, which is what maintainability means for the next reader (usually
future me). The reports also double as a review checklist — each finding came
with a code, a line and a documented fix. Going forward I will run
pylint/flake8/bandit from the first commit (a pre-commit hook or CI job), so
issues are caught while the code is still fresh instead of accumulating into
a 4.57/10 file that someone has to clean up later. Fixing was cheap; the value
came from running the tools early and often.
