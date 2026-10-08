# OpenSpec Verification Evidence: containerize-shb-scheduler-postgres18

## 1. Environment & Target Roots

- **Scheduler Root**: `/Users/androidteam/Developer/shb/shb-schedule` (git commit: `c5f3d8c80214902bf7ab3116171f11547930ba29`)
- **Skills Root**: `/Users/androidteam/Developer/shb/shb-agent-skills` (git commit: `ac6d9ac074e5089cfae8bca1c10155b94faed9e1`)
- **OpenSpec Store**: `/Users/androidteam/Developer/platform/openspec-store`
- **Docker Engine**: Docker Desktop on macOS (daemon v29.8.2, arm64)

---

## 2. Container Image Build Verification

- **Built Image ID**: `sha256:bf69b8be6069381acd2abcd4634b578fca4bbc61afa44a1dc49ffc9717647f71` (CPython 3.14.8 runner)
- **Base Images**:
  - `ghcr.io/astral-sh/uv:0.12.23` (pinned uv binary)
  - `python:3.14-slim` (CPython 3.14.8)
  - `postgres:18.6-alpine` (PostgreSQL 18.6 Alpine)
- **Virtual Environment & Shebang Integrity**:
  - Builder sets `ENV UV_PYTHON=/usr/local/bin/python UV_PYTHON_PREFERENCE=only-system UV_PYTHON_DOWNLOADS=never` to link `/app/shb-schedule/.venv/bin/python` to the runner's system Python `/usr/local/bin/python3`, resolving missing-shebang startup failures.
  - Sibling sources `shb-core` and `shb-tools` installed via `uv sync --frozen --no-dev --no-editable` as pre-compiled wheels, eliminating host-dependent `.pth` links.
- **Context Transfer Minimization**:
  - `shb-schedule/Dockerfile.dockerignore` positioned at build context root (`context: ..`) successfully excluded `.venv/`, `.gitnexus/`, `graphify-out/`, `__pycache__/`, `.git/`, and secret patterns from the build context.

---

## 3. Base Production Manifest-Only Smoke (Fail-Closed Contract)

Executed using isolated Compose project `shb-verification-qr6zlch6`:

- **Container User**: Non-root UID `10001` (`shb:shb`).
- **Services Health**:
  - `db`: `postgres:18.6-alpine` passed `pg_isready -U shb_scheduler -d shb_scheduler` healthcheck.
  - `scheduler`: Passed HTTP health probe `http://127.0.0.1:9110/scheduler/health` returning `status=healthy`, `is_leader=true`, `backend=postgres`.
- **Manifest Loading**:
  - `shb-schedule validate /etc/shb/schedules`: All 3 manifests (`daily-shb-docs-sync`, `eod-settlement-recon`, `nightly-compliance-scan`) validated against `shb-schedule/v1`.
- **Fail-Closed Verification on Absent Input**:
  - `shb-schedule run-now eod-settlement-recon`: Reported `ACTION_REQUIRED` (0 transactions, fail-closed, no synthetic `BALANCED` fallback).
  - `shb-schedule run-now daily-shb-docs-sync`: Reported `PARTIAL` (0 successful, 12 skipped, unmounted workspaces).
  - `shb-schedule run-now nightly-compliance-scan`: Reported `PARTIAL` (0 successful, 12 skipped, unmounted workspaces).
- **Read-Only Manifest Reload**:
  - `shb-schedule reload`: Dispatched `POST /scheduler/reload` loopback request to active daemon, returning `200 OK` reload summary without requiring write access to `/etc/shb/schedules`.

---

## 4. Fixture Acceptance Smoke (Synthetic Test Fixtures)

Executed using disposable fixture tree at `/var/folders/zw/k5ybx0c55rs88r9d09kxly8w0000gp/T/shb-scheduler-verify-qr6zlch6` (synthetic test fixtures, not customer workloads):

- **Synthetic Input Provision**:
  - Synthetic 2-transaction ledger JSON mounted to container.
  - 12 disposable git repositories provisioned with both `README.md` and `SPEC_INDEX.md` committed.
  - Exact per-repository `safe.directory` configurations declared (`GIT_CONFIG_COUNT=12`, zero global `*` disables).
- **Execution Results**:
  - `shb-schedule run-now eod-settlement-recon`: Reported `BALANCED` (matched: 2, discrepancies: 0, orphans: 0).
  - `shb-schedule run-now daily-shb-docs-sync`: Reported `SUCCESS` (12 repositories synchronized).
  - `shb-schedule run-now nightly-compliance-scan`: Reported `SUCCESS` (12 repositories audited, 0 violations).
- **Database Durability & Schema Isolation**:
  - 13 DBOS system tables created in `shb_scheduler` schema.
  - 6 total workflow execution records persisted in `shb_scheduler.workflow_status`.
  - Stack stopped without `-v` (`docker compose down`) and restarted (`docker compose up -d`): all 6 records preserved, daemon acquired lock cleanly, and health endpoint returned `200 OK` with zero tracebacks.

---

## 5. Unit & Regression Test Suite

- **Test Framework**: `pytest` 9.1.1, Python 3.14.8 managed by `uv`.
- **Result**: 50 passed, 0 failures, 0 warnings (Starlette TestClient deprecation warning eliminated by adding official `httpx2>=2.13.1` dev dependency).
- **Linter**: `ruff check` passed with zero diagnostics.
- **Service Removal**:
  - `src/shb_schedule/service/launchd.py` deleted.
  - `service` sub-app removed from CLI.
  - Unit test `test_cli_service_subcommand_absent` asserts `service` command is rejected.

---

## 6. Correctness, Resiliency & Contract Alignment

- **Partial Repositories Fail-Closed Contract**: Fixed false `SUCCESS` in `daily-shb-docs-sync` and `nightly-compliance-scan`. Workflows now strictly require all 12 repositories to succeed with zero skips (`skipped == 0`) to report `SUCCESS`. If any repository is skipped (e.g. 1 succeeds, 11 missing) or unmounted, the workflow reports `PARTIAL`.
- **EOD Settlement Reconciliation Hardening**: `execute_settlement_reconciliation` and `_is_valid_transaction_list` enforce strict record validation: rejects `nan`, `inf`, `bool`, and `OverflowError` amounts; enforces finite signed numbers; requires non-empty, non-whitespace string `transaction_id`; enforces intra-ledger ID uniqueness to prevent silent record overwrite; rejects one-sided input ledgers with `ACTION_REQUIRED`; rejects empty ledgers with `ACTION_REQUIRED`; and safely handles malformed ledger files without uncaught exceptions, eliminating false `BALANCED` outputs.
- **Run-Now Identifiable Result & Exit Semantics**: `shb-schedule run-now` outputs identifiable execution metrics per workflow type with status-based color formatting (green for `SUCCESS`/`BALANCED`, yellow for `PARTIAL`/`ACTION_REQUIRED`/`VIOLATIONS_FOUND`, red for `FAILED`), catches unhandled callable exceptions, and raises non-zero exit code (`1`) on execution failures.
- **DBOS Executor ID Collision Remediation**: `DBOSRuntime` parameterizes `executor_id`, isolating the daemon (`shb-schedule-daemon`) from on-demand executions (`shb-schedule-run-now-<PID>`), ensuring concurrent or repeated CLI invocations do not hijack daemon workflow recovery.
- **Canonical PostgreSQL Advisory Lock Ownership Across Containers**: Replaced container-local flock with PostgreSQL session-level advisory locks (`pg_try_advisory_lock` with deterministic 32-bit namespace keys based on application name and schema). When multiple containers share the same database and schema, only the lock-holding container becomes leader and applies schedules; competing daemons exit cleanly with status code 0 (or serve read-only standby returning HTTP 503 if `--standby` is specified). Implemented bounded ownership liveness checking: severed database connections trigger immediate fail-closed transition to standby, stopping background sentinel watchers, tearing down `SIGUSR1` signal handlers, destroying DBOS runtime to halt task dispatch, releasing broken connection state, and returning HTTP 503 on reload and trigger endpoints. All mutation entrypoints (`POST /scheduler/reload`, sentinel file watcher polling, `SIGUSR1` signal trigger) invoke `is_leader_sync_check()` to verify the actual held lock liveness (`held.is_alive(timeout_seconds=2.0)`) before any candidate registry reconciliation, preventing split-brain mutations during transient lock loss windows.
- **Direct Dependency Pinning**: Explicitly declared `psycopg[binary]>=3.3.6` in `pyproject.toml` and verified against `uv.lock` at locked version 3.3.6, eliminating reliance on transitive DBOS package contracts for long-term maintainability.
- **Dev-Only TestClient Deprecation Resolution**: Declared official `httpx2>=2.13.1` in `pyproject.toml` dev dependencies (resolved in `uv.lock` to 2.13.1), completely eliminating `StarletteDeprecationWarning` in Starlette test client executions with zero runtime image footprint.
- **Hermetic Disabled Mode Passthrough**: Implemented plain unrecorded workflow orchestration helpers (`plain_eod_settlement_recon_workflow`, `plain_daily_shb_docs_sync_workflow`, `plain_nightly_compliance_scan_workflow`) reused by both DBOS-decorated workflow definitions and unrecorded execution. When `SHB_SCHEDULER_ENABLED=false`, `resolve_callable(enabled=False)` dispatches directly to the plain orchestration path without requiring an active scheduler database or initialized DBOS runtime. Verified in fresh subprocess execution that all 3 built-in workflows run with status `BALANCED` / `PARTIAL` with zero SQLite database files created.

---

## 7. Multi-Container Disposable Database & Ownership-Loss Acceptance

Executed against disposable PostgreSQL database in isolated test stack `shb-audit-kt0tlx3n`:

1. **Pre-Fix vs Post-Fix Multi-Container Ownership**:
   - **Before**: Two containers on the same PostgreSQL database/schema both acquired container-local `flock` and concurrently reported `is_leader=True` with healthy schedules.
   - **After**: Primary container acquired PostgreSQL advisory lock (`classid=1537252669`, `objid=3330688692`) and became leader. Competing secondary container exited cleanly with status code 0 (or in `--standby` mode served read-only health returning HTTP 503, rejecting `/scheduler/reload` and trigger requests with 503).
2. **Simulated Advisory Lock Backend Session Termination**:
   - Advisory lock backend session was terminated in PostgreSQL (`pg_locks` row PID 44).
   - Existing primary detected connection loss within bounded check (2.0s), demoted to standby mode, and returned HTTP 503 on `/scheduler/health`, `/scheduler/reload`, and trigger endpoints.
   - Background sentinel file watcher stopped, `SIGUSR1` handlers were unregistered, and DBOS runtime dispatchers were cleanly stopped.
   - A fresh contender started after primary stopped successfully acquired the PostgreSQL advisory lock and became active leader (`is_leader=True`, HTTP 200).
3. **Fail-Closed Workflow Validation**:
   - Unmounted repositories: `daily-shb-docs-sync` and `nightly-compliance-scan` reported `PARTIAL` (0 successful, 12 skipped).
   - 1 repository clean, 11 missing: reported `PARTIAL` (1 successful, 11 skipped), eliminating false `SUCCESS`.
   - Non-finite or invalid ledger data (`nan`, `inf`, `bool`, duplicate IDs, whitespace IDs): reported `ACTION_REQUIRED`, eliminating false `BALANCED`.
   - All 12 repositories present with clean worktrees + finite 2-transaction ledger: reported `SUCCESS` (12/12) and `BALANCED` (matched: 2, discrepancies: 0, orphans: 0).
4. **Durability & Clean-Down**:
   - All 13 DBOS system tables created cleanly; 6 execution records persisted in `shb_scheduler.workflow_status`.
   - Stack taken down preserving named volume `shb-scheduler-pgdata`.
- **Runtime Directory & Read-Only Mount Handling**: `config.py` `ensure_directories` accepts existing read-only `schedules_dir` mounts unchanged without attempting `mkdir` or `chmod`, avoids mutating external parent trees (e.g. `/tmp`), restricts `0700` permissions strictly to newly created private runtime dirs under `~/.shb`, and propagates `logs_dir` / `lock_file.parent` creation errors fail-closed. `reloader.py` initializes mtime tracking across all candidate sentinel locations.
- **Skill & Spec Contract Reconciliation**: `scheduler-skill/SKILL.md` was reconciled to document PostgreSQL persistence in `shb_scheduler` schema, valid `shb-schedule/v1` manifest schemas (including required `owner`), and containerized reload paths. The active delta spec (`specs/shb-schedule-engine/spec.md`) was updated with `MODIFIED Requirement` blocks reconciling containerized orchestration with baseline SQLite support, ownership locking, and hot-reload semantics.
