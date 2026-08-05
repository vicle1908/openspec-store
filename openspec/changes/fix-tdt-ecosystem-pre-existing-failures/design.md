# Design: Fix TDT Ecosystem Pre-existing Failures

## 1. webhook-receiver: Remove module-level `app = create_app()`

**File:** `src/webhook_receiver/api/app.py` line 1110

**Problem:** `app = create_app()` executes at import time. This triggers:
- DBOS scheduler initialization (connects to PostgreSQL)
- `from webhook_receiver.jira_guard.routes import mount_jira_guard` (module doesn't exist)
- Any `from webhook_receiver.api.app import ...` fails with `ModuleNotFoundError`

**Fix:** Delete line 1110 (`app = create_app()`). The app is created by the
ASGI entrypoint or CLI, not at import time. Test files that import
`create_app` directly should call it explicitly in their fixtures.

## 2. jira-daily-reports: Update formatting tests

**File:** `tests/test_sprint_report_sheet.py`

**Problem:** Implementation at line 263 outputs:
```
2026-06-05: 3h | AM-1 (2h), AM-2 (1h)
```
Tests expect:
```
2026-06-05: AM-1 (2h), AM-2 (1h)
```

**Fix:** Update 5 test assertions to include the daily total prefix.
The implementation format is correct (daily total is useful operator information).

## 3. jira-skill: Fix hardcoded paths

**Files:**
- `tests/analysis/test_rca.py:903` — hardcoded `/Users/lekhanhvinh/Developer/tdt/jira-skill/...`
- `tests/test_cli_imports.py:48` — hardcoded `cwd="/Users/lekhanhvinh/Developer/tdt/jira-skill"`
- `tests/status/test_taxonomy.py:237` — depends on `~/Developer/tdt/tdt-meta/canonical_statuses.yaml`

**Fix:**
- `test_rca.py`: Replace hardcoded path with `Path(__file__).resolve().parents[2] / "src" / ...`
- `test_cli_imports.py`: Replace hardcoded `cwd` with `Path(__file__).resolve().parents[1]`
- `test_taxonomy.py`: Add `pytest.mark.skipif` when taxonomy file doesn't exist
