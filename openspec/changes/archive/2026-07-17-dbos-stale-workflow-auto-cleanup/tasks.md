## 1. Register `_stale_workflow_cleaner` in `tdt-scheduler` Docker container

- [x] 1.1 In `agent-core/scheduler_setup.py`, add a `@scheduled_workflow(cron="*/30 * * * *", cron_timezone="UTC")` decorated function `stale_workflow_cleaner` that calls `_cancel_stale_error_workflows` and `_cancel_stale_enqueued_workflows`. Registered alongside other scheduled workflows in the same module.

- [x] 1.2 Add `structlog` entries for the cleanup run: log `cancelled_error=N`, `cancelled_enqueued=M` at INFO level.

- [x] 1.3 Verify the workflow is registered: after starting the container, `SELECT schedule_name, schedule FROM dbos.workflow_schedules WHERE schedule_name='stale-workflow-cleaner';` returns `stale-workflow-cleaner | */30 * * * *`.

## 2. Unit tests

- [x] 2.1 Add a test that verifies `stale_workflow_cleaner` calls both internal functions with correct parameters.
- [x] 2.2 Add a test that verifies the cron schedule is `*/30 * * * *`.

## 3. Smoke test

- [x] 3.1 Start the Docker `tdt-scheduler` container, wait for a cron tick (or trigger manually), and verify in logs that the cleaner ran. Verified: at 11:30:03 UTC the cleaner ran and cancelled 1 stale ERROR row; `stale-workflow-cleaner | SUCCESS` confirmed in DB.

- [x] 3.2 Simulate stale ERROR rows by manually inserting a test row, then trigger the cleaner and verify it is cancelled. Verified: inserted a fake `_dbos_debouncer_workflow` ERROR row with old `application_version`; cleaner cancelled it and it appeared as `CANCELLED` in DB.

## 4. Documentation

- [x] 4.1 Updated `tdt-meta/docs/workflows/troubleshooting.md` — the `__psynch_cvwait` entry now leads with the automatic `stale-workflow-cleaner` running every 30 minutes, and keeps the manual `tdt-scheduler cancel-stale-errors` as a fallback.
- [x] 4.2 Added "Auto-cleanup (stale-workflow-cleaner)" section to `tdt-core/src/tdt_core/scheduler/README.md` documenting the schedule, what it cleans up, manual fallback, and SQL verification query.

## 5. Bonus: PENDING cleanup (discovered during runtime verification)

- [x] 5.1 Added `_cancel_stale_pending_workflows` to `tdt_core.scheduler.cli` — cancels PENDING rows from old application_versions for the same workflow names as ERROR cleanup (`_dbos_debouncer_workflow`, `_dispatch_review_workflow`, `_dispatch_mr_workflow`). Unlike ENQUEUED cleanup, no age threshold is used because a PENDING row from the current version is legitimately in-flight.
- [x] 5.2 Updated `_run_stale_workflow_cleanup` in `scheduler_setup.py` to call `_cancel_stale_pending_workflows` in addition to the ERROR and ENQUEUED cleanups. Structlog output now includes `cancelled_pending=N`.

## 6. Runtime bugs discovered 2026-06-20

### 6.1 Silent logging in stale-workflow-cleaner

**Problem:** `stale-workflow-cleaner` was registered, firing on schedule, and cancelling rows correctly (confirmed by DB records), but its `logger.warning()` / `logger.info()` calls produced zero visible output in `docker logs`. A stale ERROR row from `application_version=971c...` was created at 12:45 UTC but the 13:10 and 13:40 cleaner runs produced no log output — the cleaner's `logging.getLogger()` calls were silent because no handler was attached to those named loggers. The issue was masked because the workflow function returned normally (exit status: completed, error: None).

**Fix:** Replaced all `logging.getLogger()` calls inside `_run_stale_workflow_cleanup` and `_cancel_stale_pending_workflows` in `scheduler_setup.py` with `print()` to `sys.stderr`, guaranteeing visibility in `docker logs` regardless of logging pipeline configuration. Also added structlog + stdlib bridge setup at module load time as a defensive measure.

**Files changed:** `agent-core/scheduler_setup.py`

### 6.2 Scheduler rebuilds on every `docker compose up`

**Problem:** Every `docker compose up -d scheduler` (or `restart`) triggered a full rebuild: `Building tdt-core`, `Building agent-core`, downloading and reinstalling 199 packages (~5 minutes). Root causes:
1. `uv.lock` files in the Docker build context were generated on macOS ARM64 but the container runs Linux x86_64 — `uv sync --frozen` reinstalls when the platform mismatch is detected.
2. The compose command used `uv run tdt-scheduler serve` which, due to editable installs (`agent-core`, `tdt-core`) in `pyproject.toml` + volume mounts of the source, caused uv to detect stale packages on every startup and rebuild.

**Fix:**
- Removed `uv.lock` files from the Docker build context (no longer COPY'd into the container).
- Changed `uv sync --frozen` → `uv sync` (generates Linux-native lock file inside the container).
- Removed the editable install `uv pip install --python ... -e /workspace/tdt-sheets` — `tdt-sheets` is now importable via `PYTHONPATH`.
- Changed compose command from `["uv", "run", "tdt-scheduler", "serve"]` → `["/opt/scheduler/.venv/bin/tdt-scheduler", "serve"]` — direct invocation avoids `uv run`'s editable-package staleness check.
- Removed `~/.tdt/.env` from `env_file` in compose.yaml — the file is already mounted as a volume.

**Files changed:** `deployments/scheduler/Dockerfile`, `agent-core/compose.yaml`, `agent-core/scheduler_setup.py`

### 6.3 Stale ERROR row remaining (symptom of 6.1)

**Problem:** A `_dbos_debouncer_workflow` ERROR row from `application_version=971c48bb53fcf8be53ea4112ef0c6ef1` remained in the DB. Manual `tdt-scheduler cancel-stale-errors` successfully cancelled it, confirming the cleaner logic was correct but its log output was invisible.

**Resolution:** Fixed by 6.1. The row was manually cancelled as a one-time cleanup. The fix ensures future stale rows are cancelled AND logged visibly.

## 7. Runtime bugs discovered 2026-06-21

### 7.1 `jira-catalog-refresh` fails with Google Sheets API "Invalid value" error

**Problem:** `jira-catalog-refresh` workflow (scheduled at 03:00 UTC) was failing with exit code 1. Investigation revealed the Google Sheets API v4 `updateCells` batch update was being sent plain string arrays (`["Priority", "", "Active", ...]`) instead of the required `CellData` protobuf format. The API rejected these with `"Invalid value at 'requests[0].update_cells.rows[0].values[N]'"` for all values (empty or non-empty).

**Fix:**
- Eliminated the `batch_update` + `updateCells` approach for row updates entirely.
- Rewrote `write_delta()` in `jira-daily-reports/catalog/writer.py` to use `client.write()` (A1 notation, plain string arrays) for both updated and removed rows. This is simpler, more reliable, and the Sheets API accepts empty strings in this path.
- Removed the now-unused `_MACHINE_COL_INDICES` constant and `parse_a1_to_grid_range` import.

**Files changed:** `jira-daily-reports/src/jira_daily_reports/catalog/writer.py`

### 7.2 `daily-android-scan` / `daily-ios-scan` incorrectly fail with exit code 1

**Problem:** The `_run_platform_scan()` function in `scheduler_setup.py` tolerated `status=degraded` (exit 2) but not exit code 1. The `code-daily-scan` tool emits pretty-printed JSON to stdout (multi-line, `{` to `}` spanning ~18 lines) plus non-JSON noise lines (e.g. `python-dotenv` warnings to stdout). The JSON parser looked for the last line starting with `{`, found only the opening brace `{`, and failed to parse it — raising `CalledProcessError(exit 1)` instead of treating it as a successful degraded run.

**Fix:**
- Rewrote the JSON parsing in `_run_platform_scan()` to reconstruct the full JSON object by finding the first `{` line and last `}` line, then joining everything in between.
- This handles both pretty-printed JSON (multi-line) and noise lines anywhere in stdout.

**Files changed:** `agent-core/scheduler_setup.py`

### 7.3 `poems-mobile3-ios` not volume-mounted in scheduler container

**Problem:** `daily-ios-scan` scheduled workflow would hang indefinitely because the iOS git repository was not mounted in the container at the expected path (`/workspace/poems-mobile3-ios`). The `code-daily-scan` tool waited for the non-existent path and never returned.

**Fix:**
- Added `../poems-mobile3-ios:/workspace/poems-mobile3-ios:ro` to the scheduler service volumes in `agent-core/compose.yaml`.
- Added iOS section to `~/.tdt/code-daily-scan.yaml` with `repo_path: /workspace/poems-mobile3-ios` (container path, not host path) and the iOS spreadsheet ID.

**Files changed:** `agent-core/compose.yaml`, `~/.tdt/code-daily-scan.yaml`
