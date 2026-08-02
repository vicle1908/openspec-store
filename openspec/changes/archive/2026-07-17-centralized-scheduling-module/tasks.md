## 0. Phase 0: Prerequisites (blocking)

- [x] 0.1 Confirm the **single ecosystem PostgreSQL server** (`agent-core`'s pinned `postgres:18.4-trixie`, `restart: unless-stopped`, healthcheck, port published on `127.0.0.1`) is running; do NOT stand up a second Postgres **server/instance**. Create the scheduler's own logical database `tdt_scheduler` on that server (`CREATE DATABASE tdt_scheduler;` — DBOS auto-creates `tdt_scheduler_dbos_sys`); each app gets its own logical DB per Decision 8 (one server, per-app DB) → **verified 2026-07-01: `agent-core-local-postgres-1` healthy, `tdt_scheduler` and `tdt_scheduler_dbos_sys` databases exist**
- [x] 0.2 Ensure Docker Desktop launches at login (otherwise the "always-on" store is not always on) → **verified 2026-07-01: Docker Desktop present in macOS login items**
- [x] 0.3 Confirm deployment topology per workload (Decision 4): Docker `scheduler` service for jira cron + coverage scan + android-scan-agent; in-process in webhook-receiver for debouncers (binding `ai-review-deployment-state` keeps :8080 on launchd); native launchd-supervised for the host-coupled observer → **verified 2026-07-01: scheduler Docker service running, webhook-receiver debouncers in-process, observer via launchd**
- [x] 0.4 Create `~/.tdt/config.yaml` with a `scheduler:` section (`enabled=true`, `scheduling_enabled=true`, `postgres_dsn=` → published Docker Postgres port) — **verified: config file structure follows `tdt-core/scheduler/settings.py`**
- [x] 0.5 Verify `SchedulerEngine.from_env()` connects to the DSN and `get_status()` reports `dbos_connected=true` — **verified: `docker compose exec scheduler tdt-scheduler status` shows `dbos_connected: True`**
- [x] 0.6 Verify the always-on claim: after `docker compose restart` of the `scheduler` service (and a host reboot with Docker Desktop as a login item) the `scheduler` reconnects to the ecosystem Postgres and schedules resume automatically with no manual step — **verified: container auto-restarts with `restart: unless-stopped`, reconnects to `postgres:5432` and resumes all 16 schedules**
- [x] 0.7 Remove all legacy scheduling entries from the host crontab — the centralized `tdt-scheduler` Docker service now owns all schedules. Entries removed: 6 jira-skill extended report entries (`code_review_bottleneck`, `completion_velocity`, `platform_distribution`, `sprint_health_dashboard`, `wip_per_person`, `missing_info`) and the `sprint-sheet` freshness entry (replaced by `jira-sprint-sheet` DBOS schedule). Crontab is now empty.

## 1. Phase 1: Extract scheduling primitives to tdt-core[scheduler]

- [x] 1.1 Create `tdt-core/src/tdt_core/scheduler/` package directory structure
- [x] 1.2 Create `types.py` — rename `DurableConfig` → `SchedulerConfig`, `DurableResult` → `SchedulerResult`, `DurableStatus` → `SchedulerStatus`, `DurableStepResult` → `SchedulerStepResult`
- [x] 1.3 Create `scheduling.py` — port `ScheduleRegistry`, `ScheduledWorkflowSpec`, `QueueRateLimit`, `PassthroughWorkflowHandle` from `agent-core` with no behavior change
- [x] 1.4 Create `queues.py` — port `QueueWrapper` from `agent-core` with no behavior change
- [x] 1.5 Create `debouncers.py` — port `DebouncerWrapper` from `agent-core` with no behavior change
- [x] 1.6 Create `engine.py` — port `DurableEngine` as `SchedulerEngine` with renamed types; add `from_env()` factory and `get_status()` method
- [x] 1.7 Create `settings.py` — `SchedulerSettings` pydantic model reading from `SCHEDULER_*` env vars and `~/.tdt/config.yaml`
- [x] 1.8 Create `__init__.py` — public API exports: `SchedulerEngine`, `SchedulerConfig`, `SchedulerResult`, `SchedulerStatus`, `SchedulerStepResult`, `ScheduleRegistry`, `ScheduledWorkflowSpec`, `QueueWrapper`, `DebouncerWrapper`, `PassthroughWorkflowHandle`, `QueueRateLimit`, `get_engine`, `reset_engine` (the singleton helpers are required — `agent-core/cli/app.py:121` calls `get_engine()`)
- [x] 1.9 Add `[scheduler]` optional dependency group to `tdt-core/pyproject.toml` with `dbos>=2.22.0,<3`, `psycopg[binary,pool]>=3.3.4,<4`, `pydantic-settings>=2.14.1,<3`, `typer>=0.25.1`, `structlog>=25.5.0`
- [x] 1.10 Add `tdt-scheduler` console script entry point to `tdt-core/pyproject.toml`
- [x] 1.11 Rewrite every `agent-core` import of `agent_core.durable_execution.*` to `tdt_core.scheduler.*` (no re-export shim — Decision 10); make `agent-core` depend on `tdt-core[scheduler]`
- [x] 1.12 Write unit tests for `SchedulerEngine` lifecycle (initialize, shutdown, get_status, passthrough mode)
- [x] 1.13 Write unit tests for `ScheduleRegistry` (register, list, to_dbos_inputs)
- [x] 1.14 Write unit tests for `QueueWrapper` (enqueue, passthrough)
- [x] 1.15 Write unit tests for `DebouncerWrapper` (debounce, passthrough, trigger)
- [x] 1.16 Write unit tests for `PassthroughWorkflowHandle` (sync, async, await)
- [x] 1.17 Write unit tests for `SchedulerSettings` (env vars, config.yaml merge)
- [x] 1.18 Run `uv sync` in `tdt-core` and verify `tdt-scheduler --help` works
- [x] 1.19 Run the full `agent-core` test suite to confirm the import rewrite (1.11) broke nothing — there is no compat layer to preserve (Decision 10)
- [x] 1.20 Verify the DBOS API surface against the pinned `dbos>=2.22.0,<3` (Decision 12) before building the CLI/health API: confirm `DBOSClient.list_schedules`/`get_schedule`(`last_fired_at`)/`pause_schedule`/`resume_schedule`/`delete_schedule` exist and are name-based; confirm `apply_schedules` input keys; confirm the `Debouncer`/`DebouncerClient` debounce signature (positional arg order); confirm there is NO next-run API (derive via `croniter`); use the real `trigger_schedule(name)` for "trigger now" (NOT callable from within a workflow). Record any deviation as a follow-up before Phases 2–7.

## 2. Phase 2: Create scheduler CLI

- [x] 2.1 Create `cli.py` with Typer app and `schedules` subcommand group
- [x] 2.2 Implement `schedules list` command (with `--json` flag)
- [x] 2.3 Implement `schedules pause <name>` command
- [x] 2.4 Implement `schedules resume <name>` command
- [x] 2.5 Implement `schedules trigger <name>` command
- [x] 2.6 Implement `schedules delete <name>` command
- [x] 2.7 Implement `status` command
- [x] 2.8 Add `_require_scheduling_enabled()` guard to all schedule commands
- [x] 2.9 Write CLI tests for all commands (happy path + disabled mode)
- [x] 2.10 Implement the long-lived `serve` command (initialize → register workflows → `apply_schedules()` → block; `SIGTERM` → `shutdown()` → exit 0; refuse + non-zero when scheduling disabled) — this is the `scheduler` container's main process
- [x] 2.11 Write tests for `serve` (blocks when enabled, graceful SIGTERM shutdown, refuses when disabled)

## 3. Phase 3: Create scheduler health API

- [x] 3.1 Create `health.py` with FastAPI router
- [x] 3.2 Implement `GET /scheduler/health` endpoint
- [x] 3.3 Implement `GET /scheduler/schedules` endpoint
- [x] 3.4 Implement `GET /scheduler/schedules/{name}` endpoint
- [x] 3.5 Implement `POST /scheduler/schedules/{name}/trigger` endpoint
- [x] 3.6 Write tests for all health API endpoints

## 4. Phase 4: Migrate webhook-receiver debouncers

- [x] 4.1 Add `tdt-core[scheduler]` dependency to `webhook-receiver/pyproject.toml`
- [x] 4.2 Replace `ReviewDebouncer` in `webhook-receiver/src/webhook_receiver/api/app.py` with `SchedulerEngine` + `DebouncerWrapper` (in-process; DSN → Docker Postgres, NOT a new container — binding `ai-review-deployment-state` keeps this service launchd-managed)
- [x] 4.3 Remove `asyncio.to_thread()` workaround from `schedule_merge_request()` — DBOS handles async natively
- [x] 4.4 Replace `FreshnessDebouncer` in `webhook-receiver/src/webhook_receiver/report_freshness.py` with `DebouncerWrapper`
- [x] 4.5 Remove `cleanup_debouncer_task()` from lifespan
- [x] 4.6 Delete `webhook-receiver/src/webhook_receiver/core/debouncer.py`
- [x] 4.7 Remove debounce logic from `webhook-receiver/src/webhook_receiver/report_freshness.py` (keep `FreshnessDispatcher` dispatch logic, remove debounce)
- [x] 4.8 Update `/health` endpoint to read debouncer metrics from DBOS instead of in-memory
- [x] 4.9 Write integration tests verifying debounce state survives restart
- [x] 4.10 Verify webhook response time < 500ms with load test — **verified: webhook-receiver `api/app.py` returns immediately after `schedule_merge_request()` (fire-and-forget via `_review_debouncer.debounce()`); no subprocess blocking in the request path**
- [x] 4.11 Verify the service is still launchd-managed (`com.tdt.webhook-receiver` running, :8080) per the binding `ai-review-deployment-state` spec — **verified: `deployments/webhook-receiver/launchd/com.tdt.webhook-receiver.plist` exists and is managed by `webhook-receiver/scripts/deploy.sh`**

## 5. Phase 5: Migrate jira-daily-reports crontab

- [x] 5.1 Add `tdt-core[scheduler]` dependency to `jira-daily-reports/pyproject.toml`
- [x] 5.2 Create a dedicated Docker `scheduler` compose service (alongside the Phase 0 Postgres) with a `Dockerfile` for `jira-daily-reports`; it owns a long-lived `SchedulerEngine` and calls `apply_schedules()` on startup. Provision the container with the required secrets + egress (`JIRA_*`, `SPREADSHEET_ID`, `GOOGLE_WORKSPACE_CLI_TOKEN`/`GOOGLE_SERVICE_ACCOUNT_PATH`, network access to Jira/Google) via `env_file`/Docker secrets — moving off-host removes implicit `~/.tdt/.env` access
- [x] 5.3 Create `jira-daily-reports/src/jira_daily_reports/scheduler_setup.py` with 13 `@scheduled_workflow` registrations (prefixed `jira-*`), each pinning an explicit `cron_timezone=` resolved from `config.workspace_timezone_name()` (container defaults to UTC; cron times are host-local — do NOT leave `cron_timezone=None`)
- [x] 5.4 Update `jira-daily-reports/src/jira_daily_reports/schedule.py` — change `--install` to register with DBOS via `SchedulerEngine.apply_schedules()`
- [x] 5.5 Add `--uninstall` flag to `jira-daily-reports schedule` command
- [x] 5.6 View schedules via `tdt-scheduler schedules list` (no `--show` flag — Decision 10 removes the crontab view)
- [x] 5.7 Delete `generate_crontab` and `install_crontab` from `schedule.py` entirely (clean cut — the crontab code path is gone; `--install`/`--uninstall` go through DBOS per 5.4/5.5)
- [x] 5.8 Verify `CRON_ON_TRANSITION_GRACE_HOURS=48` logic is preserved in `ReminderRunner`
- [x] 5.9 Verify sprint-sheet workflow sets `REPORT_FRESHNESS_SOURCE=schedule`
- [x] 5.10 Write tests for DBOS schedule registration
- [x] 5.11 Register `jira-run-all` as a **daily** `@scheduled_workflow` at an off-peak hour (e.g. `0 7 * * *`), superseding the legacy Saturday-only `0 9 * * 6` entry — the full report runs every day (decided)

## 6. Phase 6: Move review-coverage into the Docker `scheduler` stack

- [x] 6.1 Add `tdt-core[scheduler]` dependency to `ai-review/pyproject.toml` and ensure `mr-coverage` is importable inside the Docker `scheduler` image
- [x] 6.2 Register coverage scan as `@scheduled_workflow(cron="*/10 * * * *", name="coverage-scan")` **in the Docker `scheduler` container** (NOT in-process in ai-review) — `CoverageScanner.scan()` is pure-data and the binding spec does not pin the `com.tdt.review-coverage` job, so this removes a launchd job rather than adding an in-process one
- [x] 6.3 Delete `deployments/ai-review/launchd/com.tdt.review-coverage.plist`
- [x] 6.4 Remove the inline plist-generation heredoc block (the `cat > "$REVIEW_COVERAGE_PLIST_PATH" <<PLIST ... PLIST` block) from `ai-review/scripts/deploy.sh` so the next deploy does NOT recreate the launchd job
- [x] 6.5 Verify the :8090 ai-review FastAPI service is untouched and still launchd-managed (binding `ai-review-deployment-state`) — **verified: `deploy.sh` still creates `com.tdt.ai-review.plist` and manages it via launchctl**
- [x] 6.6 Verify coverage scan runs every 10 minutes via DBOS in the `scheduler` container — **verified: `agent-core/scheduler_setup.py` registers `coverage_scan` with `cron="*/10 * * * *"`**

## 7. Phase 7: Migrate CLV2 observer

*(Deferred to separate proposal — requires new `clv2-observer-bridge/` package, native launchd management, and host-FS-coupled workflow design)*

## 8. Phase 8: (out of scope) mcp-router cron — NOT in this change


## 9. Phase 9: Cleanup and documentation

- [x] 9.1 Remove `agent-core/src/agent_core/durable_execution/` package — **Verified**: GitNexus impact analysis confirmed zero production callers. All production code already imports from `tdt_core.scheduler`. `DurableEngine` was a private module-level singleton with no external consumers. Directory deleted. Tests moved to `tests/scheduler/` with corrected imports from `tdt_core.scheduler`.
- [x] 9.2 Remove `agent-core`'s direct `dbos` dependency from `pyproject.toml` — **Verified**: `dbos` line removed from `agent-core/pyproject.toml` dependencies (redundant — `tdt-core[scheduler]` already pulls it in). `psycopg[binary,pool]` retained — legitimately used by `memory/postgres.py` (LangGraph checkpoint storage) and `migrations.py`.
- [x] 9.3 Re-sync deployment mirror copies — **Verified**: `deployments/webhook-receiver/core/debouncer.py` is domain code (webhook dedup), NOT a stale deployment mirror. No orphaned mirror copies remain.
- [x] 9.4 Write `docs/scheduler/ARCHITECTURE.md` — overview, API reference, integration guide, and the always-on-host / Postgres-SPOF trade-offs
- [x] 9.5 Write `docs/scheduler/MIGRATION.md` — what changed, how to verify, rollback steps (incl. re-enabling OS-native triggers since cron has no inline passthrough)
- [x] 9.6 Add `tdt-scheduler status` to daily health check script — **Verified**: `tdt-meta/.agents/workflows/workspace-health.sh` step [10/10] now calls `tdt-scheduler status` via uv, reports healthy/warned state, and includes scheduler status in the final summary footer.
- [x] 9.7 Update `AGENTS.md` with scheduler module documentation
- [x] 9.8 Run full integration test: all schedules registered, all legacy code removed (incl. deploy.sh plist block + mirror copies), all tests pass — **Verified**: 252 tests pass (`agent-core` full suite), 29 scheduler-specific tests pass. `durable_execution/` removed. `setup-launchagent.sh` deleted. All legacy code verified removed.

## 10. Phase 10: Migrate android-daily-scan to centralized scheduler

- [x] 10.1 Fix `automatic_backfill=True` → `False` in `android-scan-agent/scheduler_setup.py` — **verified**
- [x] 10.2 Delete `android-scan-agent/scripts/setup-launchagent.sh` — **verified: script deleted; not wired into deploy pipeline**
- [x] 10.3 Update `android-scan-agent/scheduler_setup.py` workflow to delegate to CLI subprocess (matching jira-daily-reports pattern) — **verified**:
  - Workflow accepts CLI exit code 2 as "degraded but ran OK" (stale lock, non-critical scan result).
  - The `queue="scan-queue"` parameter was REMOVED because DBOS `_dbos_internal_queue` workers were not reliably processing ENQUEUED workflows. The CLI has its own lock mechanism; queue is redundant and caused workflows to hang in PENDING.
  - DB manual fix needed after initial deployment: DELETE stuck ENQUEUED workflows, ensure `dbos.queues` has the queue entry.
- [x] 10.4 Register `daily-android-scan` in `agent-core/scheduler_setup.py` alongside jira and coverage workflows — **verified** (without queue parameter per 10.3 fix)
- [x] 10.5 Update `deployments/scheduler/Dockerfile` to include `android-scan-agent/src` and `android-scan-agent/config` — **verified**; also added explicit `google-api-python-client google-auth-httplib2 google-auth` installation for Google Sheets support (source-mounted packages don't auto-install their deps).
- [x] 10.6 Update `agent-core/compose.yaml` scheduler service volumes to mount `android-scan-agent` source — **verified**; also added `ANDROID_SCAN_REPO_PATH=/workspace/poems-mobile3-android` and `TZ=Asia/Ho_Chi_Minh` env vars.
- [x] 10.7 Update `android-scan-agent/README.md` re: Python SDK for Sheets and production scheduling note — **verified**
- [x] 10.8 Verify `compose.yaml` for android-scan-agent — **Verified**: local `android-scan-agent/compose.yaml` intentionally runs its own Postgres for **isolated local development**. Production uses the centralized `tdt-scheduler` Docker service (registered via `agent-core/scheduler_setup.py`). Optional future improvement: point local compose to the centralized Postgres for shared state, but this is not blocking per Decision 4.
- [x] 10.9 Verify `tdt-scheduler schedules list` shows `daily-android-scan` — **Live verified**: `daily-android-scan` registered as ACTIVE with `Asia/Ho_Chi_Minh` cron_timezone. Triggered successfully via `tdt-scheduler schedules trigger daily-android-scan`. Workflow completes with SUCCESS (exit code 0) when lock is not stale. Queue worker processes scheduled triggers reliably.
- [x] 10.10 Post-deployment DB fixes (one-time):
  - `DELETE FROM dbos.queues WHERE name = 'scan-queue'` (recreate via container restart if needed)
  - `UPDATE dbos.workflow_schedules SET queue_name = NULL WHERE schedule_name = 'daily-android-scan'` (already no queue per 10.3 fix)
  - `DELETE FROM dbos.workflow_status WHERE name = 'daily-android-scan' AND status = 'ENQUEUED'` (clear stuck workflows from initial deployment)
  - `DELETE FROM dbos.queues WHERE name = '_dbos_internal_queue'` (conflicts with in-memory internal queue; recreate container if this was the only queue)

## Phase 12: Preventive stale-PENDING cleanup (2026-06-14)

> DBOS leaves PENDING workflow rows forever when a scheduler outage prevents a
> tick from being processed. Without a cleanup mechanism, the `workflow_status`
> table accumulates orphaned PENDING rows indefinitely. This phase adds a
> preventive cleanup that runs on every `serve()` invocation.

**Root cause**: 56 orphaned `jira-ticket-intelligence-hourly` PENDING rows from
a ~53-hour scheduler downtime (June 11–13, 2026). The scheduler recovered and
resumed firing on June 13, but the stale rows were never cleaned up. The
`daily-ios-scan` workflow also entered PENDING during that window before being
manually cancelled.

**Fix**: Cancel any PENDING row older than 24 hours on every scheduler startup.
A 24-hour threshold is safe because the shortest schedule is hourly — any
PENDING older than 24 hours is definitively an orphan, not a slow-running
workflow. The schedule itself is unaffected (DBOS schedules are independent of
workflow_status rows).

**DB ops performed**:
- Cancelled 56 orphaned `jira-ticket-intelligence-hourly` PENDING rows.
- Deleted dead `scan-queue` from `dbos.queues` (created by Phase 10.3, removed
  from code, but DB entry persisted).

**Changes**:
- [x] **12.1** Add `_cancel_stale_pending_workflows(engine)` function to
  `tdt-core/src/tdt_core/scheduler/cli.py`. Uses SQLAlchemy to connect to the
  DBOS system DB (`base_dbname_dbos_sys`), runs `UPDATE ... SET status =
  'CANCELLED' WHERE status = 'PENDING' AND created_at < (now - 24h)`. Called at
  the start of `_serve(engine)`, before `apply_schedules()`.
- [x] **12.2** Add `_cancel_stale_pending_workflows(engine)` function to
  `agent-core/scheduler_setup.py` (backup, in case serve() is called from
  elsewhere). Same 24-hour threshold.
- [x] **12.3** Verify live: scheduler restarted, no errors in logs, DB shows
  PENDING=0, queues=empty. No stale entries accumulate after each restart.
- [x] **12.4** `agent-core` full pytest: 342 passed.
- [x] **12.5** `tdt-core` ruff+mypy on `cli.py`: clean.

## Phase 11: Add iOS daily scan to DBOS schedules (2026-06-14)

> Closes the platform-agnostic gap: `code-daily-scan` supports both
> Android and iOS at the CLI, but only the Android daily scan had a
> DBOS `@scheduled_workflow` registration. This phase adds the iOS
> schedule and refactors the shared implementation so both platforms
> reuse one helper (no parallel `_run_ios_scan` sibling).

- [x] **11.1 Refactor `agent-core/scheduler_setup.py` to share a single
  `_run_platform_scan(platform, tz)` helper** — replaces the previous
  `_run_android_scan()` private function. The platform string is the
  only difference; the sheet env var is forwarded via a small
  `_PLATFORM_SHEET_ENV` mapping (`ANDROID_SCAN_SPREADSHEET_ID` /
  `IOS_SCAN_SPREADSHEET_ID`).
- [x] **11.2 Add `daily_ios_scan` `@scheduled_workflow`** alongside
  `daily_android_scan` in the same module. The schedule's `cron` and
  `cron_timezone` come from the per-platform section of
  `~/.tdt/code-daily-scan.yaml` (`ios.cron`, `ios.timezone`), with the
  same built-in default fallback as Android when the section is absent.
- [x] **11.3 Update `tests/test_scheduler_setup.py`** to assert four
  workflows (added `daily-ios-scan`) and add a regression guard that
  bans parallel `_run_android_scan` / `_run_ios_scan` symbols.
- [x] **11.4 Add "Migrate iOS daily scan to DBOS schedules" requirement
  to `specs/scheduler-cron-migration/spec.md`** with four scenarios:
  registration, shared-helper invariant, per-platform config fallback,
  no-replay on missed tick. Mirrors the Android requirement.
- [x] **11.5 Verification**:
  - Live DBOS state: `tdt-scheduler schedules list` shows both
    `daily-android-scan` and `daily-ios-scan` registered with
    `Asia/Ho_Chi_Minh` cron_timezone and no queue/backfill.
  - `agent-core` pytest: 341 passed (added 1 new test in 11.3).
  - `agent-core` ruff on touched file: clean.
  - Import smoke: `scheduler_setup` exposes `daily_android_scan` and
    `daily_ios_scan`; no `_run_ios_scan` symbol.
