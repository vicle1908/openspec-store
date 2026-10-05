# Tasks

## 1. Planning and dependency boundary

- [x] 1.1 Confirm the stable `shb-tools` Python API or console entry point for `shb-docs-sync` (`DocsSynchronizer.audit_and_sync` and `shb-docs-sync check --root <path>`); do not use the TDT `agent-docs-sync` command
- [x] 1.2 Scaffold `~/Developer/shb/shb-schedule` as an independent Git repository with PEP 621 `pyproject.toml`, `hatchling` build backend, `requires-python = ">=3.14"`, `uv`, and modern dependency floors (`dbos>=3.1.0`, `pydantic>=2.13.5`, `typer>=0.27.2`, `rich>=15.0.0`, `croniter>=6.0.0`, `pyyaml>=6.0.3`)
- [x] 1.3 Add an import/dependency guard proving that runtime code does not depend on `tdt-core`, `tdt-scheduler`, `~/Developer/tdt/`, or `~/.tdt/`
- [x] 1.4 Validate the change strictly with `openspec validate introduce-shb-schedule-dbos-engine --strict --store openspec-store`

## 2. Configuration and persistence

- [x] 2.1 Implement configuration using modern `pydantic-settings` (`SettingsConfigDict(env_file="~/.shb/.env", env_file_encoding="utf-8")`) and document process-environment precedence
- [x] 2.2 Implement portable defaults based on `Path.home()` for `~/.shb/scheduler.db`, `~/.shb/schedules`, and `~/.shb/logs`; reject hardcoded workstation-user paths
- [x] 2.3 Configure SQLite WAL mode (`PRAGMA journal_mode = WAL;`, `synchronous = NORMAL`, `foreign_keys = ON`, `busy_timeout = 5000`), Python 3.12+ connection management (`sqlite3.connect(..., autocommit=False)`), restricted local permissions (`0700` dir / `0600` file), and PostgreSQL 18 dedicated schema (`shb_scheduler`)
- [x] 2.4 Add scheduler configuration entries to the SHB environment example without writing secrets

## 3. Manifest and registry lifecycle

- [x] 3.1 Define strict `shb-schedule/v1` validation using Pydantic v2 (`ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)`), `@field_validator`, and `@model_validator` for owner, version, cron, timezone, workflow, queue, timeout, retry, and `automatic_backfill: false`
- [x] 3.2 Implement non-evaluating regex environment substitution strictly matching `${VAR}` and `${VAR:-default}` without shell invocation
- [x] 3.3 Implement manifest discovery and approved callable resolution from `~/.shb/schedules/*.yaml` against an explicit allowlist
- [x] 3.4 Implement queue pre-registration in DBOS before schedule application
- [x] 3.5 Implement `.reload` mtime and `SIGUSR1` handling (`loop.add_signal_handler`) with transactional staging and last-known-good retention when candidate loading fails

## 4. Durable scheduler ownership and reconciliation

- [x] 4.1 Implement canonical scheduler identity (`app_name="shb-schedule"`) and OS-level kernel locking via `fcntl.flock` on `~/.shb/shb-schedule.lock` with clean exit/fail-closed behavior avoiding port 9110 binding
- [x] 4.2 Implement DBOS lifecycle via modern ASGI `lifespan` context manager, durable schedule application, and disabled-mode passthrough without weakening production ownership checks
- [x] 4.3 Implement startup and reload reconciliation between persisted DBOS dynamic schedule state (`workflow_schedules` table) and the accepted manifest registry
- [x] 4.4 Retire removed/renamed schedules via explicit `DBOS.delete_schedule` calls, cancel or quarantine obsolete queued/error work, preserve active valid runs, and emit auditable reconciliation results
- [x] 4.5 Add periodic stale-work maintenance without deleting required execution history

## 5. SHB-native flagship workflow & determinism invariants

- [x] 5.1 Implement the durable documentation-sync workflow strictly separating deterministic orchestration (`@DBOS.workflow` accepting `(scheduled_at: datetime, context: DBOSContext)`) from non-deterministic subprocess and clock operations (`@DBOS.step`)
- [x] 5.2 Execute the 12 existing SHB repositories sequentially with `@DBOS.step` checking `git status --porcelain` for dirty-worktree protection
- [x] 5.3 Enforce a 180-second overall timeout inside `@DBOS.step` using vector arguments (`shell=False`) for `shb-docs-sync check --root <path>` or `DocsSynchronizer.audit_and_sync`, inspect structured audit reports, and capture duration, success, skip, and drift findings
- [x] 5.4 Create the `daily-shb-docs-sync` manifest for 03:30 `Asia/Ho_Chi_Minh` execution with automatic backfill disabled

## 6. CLI, health, and service integration

- [x] 6.1 Implement `serve`, `list`, `run-now`, `validate`, and `reload` via modern Typer CLI using `typing.Annotated` options and Rich formatting
- [x] 6.2 Implement `/scheduler/health`, `/scheduler/schedules`, `/scheduler/schedules/{name}`, and `/scheduler/schedules/{name}/trigger` via Starlette/FastAPI with ASGI `lifespan` without credential disclosure
- [x] 6.3 Generate idempotent macOS LaunchAgent and Linux systemd user-service definitions with the canonical owner identity
- [x] 6.4 Verify service restart, duplicate-daemon, reload failure, and reboot/startup behavior

## 7. Verification and acceptance

- [x] 7.1 Add manifest tests covering Pydantic v2 schema errors, extra-field rejection, timezone handling, variable substitution, queue declarations, and no-backfill defaults
- [x] 7.2 Add engine tests covering SQLite WAL, `fcntl.flock` ownership conflict, retry, crash recovery, and durable execution identity
- [x] 7.3 Add reconciliation tests covering startup, deletion, rename, stale queued/error work, rollback on failure, and preservation of active runs
- [x] 7.4 Add workflow tests covering clean and dirty repositories, subprocess failures, timeout handling, and structured result logging
- [x] 7.5 Add CLI/service/health tests covering endpoint state, on-demand trigger, last-known-good reload, and generated service definitions
- [x] 7.6 Run code hygiene with `uv run ruff check` and strict type checks with `uv run mypy`
- [x] 7.7 Run the focused test suite with `uv run pytest -p no:cacheprovider`
- [x] 7.8 Run `openspec validate --all --strict --store openspec-store`
- [x] 7.9 Verify `shb-schedule run-now daily-shb-docs-sync` in a dry-run or disabled-database mode without modifying dirty worktrees
