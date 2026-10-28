# Issues Found by Static Analysis — `music_catalog.py`

Student: Devansh Gupta (PES1UG24CS145) · Repo: L5_19_music_catalog

Tools used: Pylint 4.1.3, Bandit 1.9.4, Flake8 7.4.1 (Python 3.14). The original
reports are in `reports/before/`. Before the fixes the file scored **4.57/10 on
Pylint**, had **4 Bandit findings** (2 medium, 2 low) and **7 Flake8 findings**.

The table below lists every issue found, ordered by severity (high/medium
first), as required. All of them were fixed — well above the minimum of 4.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| SQL injection (Bandit B608) | Security — Medium | 10 | The INSERT statement is built with `%` string formatting, so titles and artists are interpolated directly into the SQL. A hostile value such as `x'); DROP TABLE songs;--` rewrites the query, and any ordinary title containing a single quote (e.g. *Don't Stop*) crashes the insert. | Use a parameterized query: `conn.execute("INSERT INTO songs (title, artist, plays) VALUES (?, ?, ?)", (title, artist, plays))` so values are bound, never parsed as SQL. |
| Insecure deserialization (Bandit B301 + B403) | Security — Medium | 1, 29, 33 | `pickle.loads()` executes arbitrary code hidden inside the blob it unpacks. A tampered playlist handed to `loadPlaylist()` means full remote code execution, so a "playlist file" is really an attack vector. | Drop `pickle` entirely and serialize playlists as JSON (`json.dumps` / `json.loads`). JSON is data-only and safe on untrusted input, and the save/load feature still works. |
| Mutable default argument (Pylint W0102) | Bug — High | 9 | `playlist=[]` is evaluated once, at function definition time, so the same list object is shared by every call that omits the argument. Songs silently pile up in a "new" playlist across calls. | Default to `playlist=None` and create a fresh list inside the function body. |
| Bare `except` (Pylint W0702, Flake8 E722) | Bug / Robustness — High | 39 | `except:` catches everything — including `KeyboardInterrupt` and `SystemExit` — and silently returns 0, hiding real database failures. | Catch the specific error: `except sqlite3.Error:`. |
| Pseudo-random generator (Bandit B311) | Security — Low | 17 | Bandit flags `random.choice` because the `random` module is not cryptographically secure. Here it only shuffles songs for a demo, so this is a false positive. | Keep `random.choice` and mark the line `# nosec B311` with a justification comment, the standard way to document an accepted finding. |
| Naming-convention violations (Pylint C0103, Flake8 E741) | Style — Low | 9, 15, 20, 28, 32, 36, 47 | `addSong`, `shufflePick`, `savePlaylist`, `loadPlaylist`, `totalPlays` are camelCase (PEP 8 wants snake_case), and the variable `l` is easily confused with `1` or `I`. | Rename functions to snake_case (`add_song`, `shuffle_pick`, `save_playlist`, `load_playlist`, `total_plays`) and `l` to `loaded`. |
| Missing docstrings (Pylint C0114, C0116) | Documentation — Low | 1, 9, 15, 20, 28, 32, 36, 43 | The module and all seven functions lack docstrings, so intent must be reverse-engineered from the code. | Add a one-line docstring to the module and to every function. |
| Lines too long (Pylint C0301, Flake8 E501) | Style — Low | 6, 10, 21, 49 | Four lines run 83–109 characters (Flake8 limit 79, Pylint limit 100), which hurts readability and diffs. | Wrap the SQL statements and the final `print` across multiple lines. |
| Multiple statements on one line (Pylint C0321, Flake8 E701) | Style — Low | 48 | `if len(l) > 1: print("multi-song playlist")` puts a compound statement on a single line. | Put the `print` on its own indented line under the `if`. |
| `else` after `return` (Pylint R1705) | Code quality — Low | 22–25 | The `else` branch following a `return` adds dead-looking nesting. | Remove the `else` and de-indent its body. |
| `%`-formatted string (Pylint C0209) | Style — Low | 10 | `%` formatting is legacy style — and in SQL context it is exactly the injection vector behind B608. | Eliminated by the parameterized-query fix (no string formatting of SQL remains). |

## Result after fixing

| Check | Before | After |
|-------|--------|-------|
| Pylint score | 4.57/10 | **10.00/10** |
| Bandit issues | 4 (2 medium, 2 low) | **0** |
| Flake8 issues | 7 | **0** |
| Program output | `multi-song playlist` / `popular niche <id> 290` | identical (see `reports/after/program_output.txt`) |

Final reports: `reports/after/`. The program still runs and does its job.
