# Benchmark Fixtures

Source commit: `a02714a866b01454f71f7abaa1eca39509f489f2` in `/tmp/droid-benchmark`

## Files

| Path | Purpose | Expected pre-fix outcome |
|---|---|---|
| `buggy-module/calculator.py` | Two deterministic bugs: divide(a,b) computes b/a; accumulate() overwrites instead of summing | — |
| `buggy-module/test_calculator.py` | unittest: 4 tests — 2 fail before fix, 2 pass (normalize) | 2 failures, 2 passes |
| `edit-task/string_utils.py` | One bug: capitalize_words() returns text.upper() instead of per-word capitalization | — |
| `edit-task/test_string_utils.py` | unittest: 3 tests — 2 fail before edit, 1 passes (empty string) | 2 failures, 1 pass |
| `planning-project/app.py` | FastAPI app with /, /users/{id}, POST /users | Control fixture |
| `planning-project/requirements.txt` | fastapi>=0.100.0, uvicorn>=0.23.0 | Control fixture |
| `patch-review/auth.py` | Three deliberate security findings: hardcoded password, MD5, SQL injection | 3 rubric findings |
| `empty-dir/` | Intentionally empty directory for tool round-trip test (has .gitkeep) | — |

## Verification Commands

```bash
# S5: buggy-module — expect 2 failures, 2 passes
python3 -m unittest buggy-module.test_calculator -v

# S6: edit-task — expect 2 failures, 1 pass (before model edit)
python3 -m unittest edit-task.test_string_utils -v

# S7: patch-review — expect 3 findings (manual or harness scoring)
# 1. Hardcoded password (ADMIN_PASSWORD = "supersecret123")
# 2. Weak hash (hashlib.md5)
# 3. SQL injection (f-string in get_user_profile)
```

## Design Constraints

- No `BUG:` or `FINDING:` comments in source files — answer-leakage prevention.
- All tests use `unittest`, not pytest — no external dependencies.
- normalize() is intentionally correct as a control — models must not flag it as a bug.
- empty-dir uses `.gitkeep` to survive git operations.
