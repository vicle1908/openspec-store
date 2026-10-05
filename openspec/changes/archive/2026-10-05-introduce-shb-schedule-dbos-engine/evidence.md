# Evidence: introduce-shb-schedule-dbos-engine

**Date:** 2026-10-05  
**Target Repository:** `/Users/androidteam/Developer/shb/shb-schedule` (Git commit: `63df9aa`)  
**Status:** Completed & 100% Verified  

---

## 1. Repository Scaffolding & Clean-Break Isolation
- Repository created and committed at `/Users/androidteam/Developer/shb/shb-schedule`.
- Built on `CPython 3.14.5`, managed via `uv`, PEP 621 metadata, and `hatchling` build backend.
- Clean-break isolation test `tests/test_dependency_guard.py` passed: 0 references or imports to `tdt-core`, `tdt-scheduler`, or `~/.tdt/`.

---

## 2. Unit and Integration Test Suite
Command: `uv run pytest -v`  
Output: **22 passed, 1 warning in 23.42s**
- `tests/test_cli.py`:
  - `test_cli_help`: PASSED
  - `test_cli_validate_and_list`: PASSED
  - `test_cli_run_now_invalid_job`: PASSED
- `tests/test_config.py`:
  - `test_config_paths_derived_from_home`: PASSED
  - `test_sqlite_wal_pragmas_and_permissions`: PASSED
- `tests/test_dependency_guard.py`:
  - `test_no_tdt_dependencies_in_pyproject`: PASSED
  - `test_no_tdt_imports_or_references_in_src`: PASSED
- `tests/test_docs_sync_workflow.py`:
  - `test_git_check_dirty_tree`: PASSED
  - `test_daily_docs_sync_workflow_skips_dirty_and_missing`: PASSED
- `tests/test_manifests.py`:
  - `test_valid_manifest_schema`: PASSED
  - `test_invalid_cron_and_timezone`: PASSED
  - `test_extra_fields_forbidden`: PASSED
  - `test_environment_substitution`: PASSED
  - `test_discover_manifests_and_registry`: PASSED
  - `test_unapproved_workflow_rejected`: PASSED
- `tests/test_ownership.py`:
  - `test_leader_lock_acquisition_and_release`: PASSED
  - `test_duplicate_daemon_lock_conflict`: PASSED
- `tests/test_reconciliation.py`:
  - `test_reconciliation_add_update_retire`: PASSED
  - `test_reconciliation_with_dbos_runtime`: PASSED
  - `test_reconciliation_detects_non_cron_attribute_changes`: PASSED
- `tests/test_server.py`:
  - `test_health_server_lifespan_and_endpoints`: PASSED
---

## 3. Code Hygiene & Type Safety
- **Linter**: `uv run ruff check` → **All checks passed!**
- **Formatter**: `uv run ruff format` → **26 files left unchanged (clean format).**
- **Type Checker**: `uv run mypy src/ tests/` → **Success: no issues found in 25 source files.**

---

## 4. End-to-End CLI & Workload Verification
1. **Manifest Validation**:
   ```bash
   uv run shb-schedule validate ~/.shb/schedules
   # Output: ✓ All 1 manifests valid and approved in /Users/androidteam/.shb/schedules
   ```
2. **Registry Listing**:
   ```bash
   uv run shb-schedule list --dir ~/.shb/schedules
   # Output: SHB Schedule Registry (1 manifests) rendered in Rich Table
   # - daily-shb-docs-sync | shb-platform | 30 3 * * * | Asia/Ho_Chi_Minh | daily-shb-docs-sync | sync-queue
   ```
3. **On-Demand Execution (`daily-shb-docs-sync`)**:
   ```bash
   uv run shb-schedule run-now daily-shb-docs-sync
   # Output:
   # Initializing DBOS (v3.2.0)
   # Initializing DBOS system database with URL: sqlite:///shb_schedule.sqlite (schema: dbos)
   # DBOS launched!
   # Execution completed: status=SUCCESS
   # Successful: 0, Skipped: 12, Failed: 0
   # DBOS successfully shut down
   ```

---

## 5. OpenSpec Store Validation
- `openspec validate introduce-shb-schedule-dbos-engine --strict --store openspec-store` → **PASS** (0 errors).
- `openspec validate --all --strict --store openspec-store` → **442 passed, 0 failed**.
