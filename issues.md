# Lab 5 – Issue Table (`online_exam.py`)

Tools: Pylint 4.1.3, Bandit 1.9.4, Flake8 7.4.1 (Python 3.12).
Line numbers refer to the **original** file. Severity: Bandit's own rating for security findings; for the rest, High = real bug or security hole, Medium = maintainability, Low = style.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| **B605** shell command built from input (Bandit, **High**) | Security | 56 | `os.system("ssh " + labPc + " lock-screen")` passes a concatenated string to a shell. A host such as `pc1; rm -rf /` runs arbitrary commands (CWE-78). | `subprocess.run([ssh, "--", lab_pc, "lock-screen"], check=True)`: argument list, no shell, `shutil.which` for the binary, `--` so the host can't be read as an option, and a regex allow-list that rejects anything that isn't a plain host name. |
| **B324** weak MD5 hash (Bandit, **High**) | Security | 16 | `hashlib.md5` is broken (collisions) and unsuitable for any security use (CWE-327). | Switched to `hashlib.sha256`. |
| **W0102** mutable default argument (Pylint) | Bug | 23 | `penalties={}` is created once at definition time and shared by every call that omits it, so state leaks between calls (reproduced: two independent calls left `{'Anil': 8}` in the default). | Default changed to `None`; a fresh dict is created inside the function. |
| **B105** hard-coded password (Bandit, Low) | Security | 11 | `PROCTOR_PASSWORD = "proctor-demo"` is a secret committed to source control (CWE-259). | Read from the environment: `os.environ.get("PROCTOR_PASSWORD")`. |
| **B311** non-cryptographic RNG (Bandit, Low) | Security | 20 | `random.choice` is predictable; the bonus question should not be guessable. | `secrets.choice`. |
| **B404 / B603** subprocess notices (Bandit, Low) | Security | new (after B605 fix) | Switching to `subprocess` raises informational notes. Input is validated and no shell is used. | Targeted `# nosec B404` / `# nosec B603` with the justification beside them (not blanket suppression). |
| `topper()` crashes on empty results (found by manual review, no tool reports it) | Bug | 51-52 | `max()` of an empty dict raises `ValueError` when nobody has been graded, while `classAverage()` already handles that case. | Return `None` when `results` is empty. |
| `main()` runs on import (manual review) | Bug | 73 | Importing the module runs the demo and prints output, which also makes the code untestable. | `if __name__ == "__main__": main()`. |
| **C0103** invalid names (Pylint) | Convention | 15, 19, 23, 35, 45, 54 | `hashAnswer`, `pickBonusQuestion`, `gradeStudent`, `studentName`, `getGrade`, `classAverage`, `lockScreen`, `labPc` are camelCase. | Renamed to snake_case per PEP 8, and all call sites updated. |
| **C0114 / C0116** missing docstrings (Pylint) | Convention | 1, 15, 19, 23, 35, 45, 51, 54, 59 | Module and all functions undocumented. | Added concise docstrings. |
| **C0200** `range(len())` loop (Pylint) | Refactor | 25 | Indexing via `range(len(QUESTIONS))` is un-Pythonic. | `for i, question in enumerate(QUESTIONS)`. |
| **R1705** no-else-return (Pylint) | Refactor | 37-42 | `elif`/`else` after `return` in `getGrade`. | Flattened to sequential `if` + final `return`. |
| **E302** blank lines (Flake8) | Style | 54 | One blank line before `lockScreen`, PEP 8 wants two. | Added the second blank line. |
| **E225** operator spacing (Flake8) | Style | 67 | `average=classAverage()` | `average = class_average()` |
| **E261** inline comment spacing (Flake8) | Style | 69 | One space before `# highest score`. | Two spaces. |
| **E501** line too long (Flake8) | Style | 70 | 93 characters (limit 79). | Wrapped the `print(...)` over several lines. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.65/10 (20 messages) | **10.00/10** (0 messages) |
| Bandit | 4 issues (2 High, 2 Low) | **0 issues** (2 informational notes suppressed with justification) |
| Flake8 | 4 issues | **0 issues** |

Program output is identical before and after (apart from the intentionally random bonus question). Reports: `reports/before/` and `reports/after/`.

## Notes

- Flake8 had 8 findings by the time I reached it, not 4: my Pylint renames made `grade_student(` one character longer (E128 on the continuation line), and new docstrings pushed lines past 79 characters (E501). Fixed in the Flake8 commit.
- `hash_answer` hashes both the student's answer and the key before comparing. That is equivalent to comparing the normalised strings, so hashing adds no real protection here. I kept the design and only replaced the weak algorithm.
- The unused `penalties` bookkeeping is preserved (the signature is unchanged) but nothing ever reads it. It would be a candidate for removal in a later refactor.
