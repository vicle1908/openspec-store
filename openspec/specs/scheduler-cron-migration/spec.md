# scheduler-cron-migration Specification

## Purpose

Scheduler cron migration moves all legacy host crontab scheduling entries into the centralized DBOS scheduler, ensuring a single authoritative scheduler owns all cron jobs across the ecosystem.
## Requirements

_(Baseline: no requirements defined. All requirements are introduced by the `centralized-scheduling-module` change.)_

### Requirement: Migrate jira-daily-reports crontab to DBOS schedules
All 13 cron entries in `jira-daily-reports` SHALL be migrated from macOS crontab to DBOS `@scheduled_workflow` registrations.

#### Scenario: All 13 reports registered as DBOS schedules
- **WHEN** `tdt-scheduler schedules list` is run after migration
- **THEN** all 13 reports SHALL appear: jira-standup, jira-missing-info, jira-blocked, jira-velocity, jira-platform, jira-priority, jira-code-review, jira-sprint-health, jira-wip, jira-remind, jira-sprint-sheet, jira-wip-age, jira-cycle-time

#### Scenario: Each schedule has correct cron expression
- **WHEN** each schedule's details are inspected
- **THEN** the cron expression SHALL match the current scheduler definition (e.g., jira-standup=`0 8 * * 1-5`, jira-sprint-sheet=`0 * * * *`)

#### Scenario: Sprint sheet tagged as schedule source
- **WHEN** the sprint-sheet workflow runs
- **THEN** `REPORT_FRESHNESS_SOURCE=schedule` SHALL be set in the environment

#### Scenario: run-all runs daily as jira-run-all
- **WHEN** the crontab is migrated
- **THEN** the legacy `run-all` entry (previously Saturday-only `0 9 * * 6`) SHALL be registered as a `jira-run-all` `@scheduled_workflow` on a **daily** cron at an off-peak hour (e.g. `0 7 * * *`) so the full report is produced every day — it SHALL NOT be dropped or left weekly

### Requirement: Schedule count accounts for jira-skill overlap (no duplicates)
The 13 `jira-daily-reports` schedules are the **canonical** registrations. If `jira-skill` cron also defines any of the same report types, it MUST NOT register a duplicate schedule name.

#### Scenario: No duplicate schedule names across reporting suites
- **WHEN** all reporting schedules are registered
- **THEN** no two schedules SHALL share the same `schedule_name`
- **AND** the system SHALL prefer the canonical schedule names defined by this change for overlapping report types

### Requirement: jira-daily-reports schedule CLI updated
The `jira-daily-reports schedule` command SHALL register schedules with DBOS instead of writing to crontab.

#### Scenario: --install registers with DBOS
- **WHEN** `jira-daily-reports schedule --install` is run
- **THEN** all 13 schedules SHALL be registered with DBOS via `SchedulerEngine.apply_schedules()`

#### Scenario: Schedules are viewable via the unified CLI
- **WHEN** an operator wants to see the jira report schedules
- **THEN** `tdt-scheduler schedules list` SHALL display them (the legacy crontab `--show` view is removed per Decision 10 — there is no `generate_crontab`/`--show`/`--install` crontab path)

#### Scenario: --uninstall removes from DBOS
- **WHEN** `jira-daily-reports schedule --uninstall` is run
- **THEN** all 13 schedules SHALL be removed from DBOS

### Requirement: CRON_ON_TRANSITION_GRACE_HOURS preserved
The `CRON_ON_TRANSITION_GRACE_HOURS=48` safety net in `ReminderRunner` SHALL be preserved exactly.

#### Scenario: Cron safety net still active
- **WHEN** the remind schedule runs
- **THEN** it SHALL skip issues with recent transitions (within 48 hours) as before

### Requirement: Migrate review-coverage launchd to DBOS schedule
The `com.tdt.review-coverage` launchd plist (`StartInterval=600`) SHALL be replaced with a DBOS `@scheduled_workflow(cron="*/10 * * * *", name="coverage-scan")` hosted in the Docker `scheduler` service.

#### Scenario: Coverage scan runs every 10 minutes
- **WHEN** the `coverage-scan` schedule is registered
- **THEN** it SHALL run every 10 minutes via DBOS, equivalent to the old `StartInterval=600`

#### Scenario: Coverage scan hosted in the Docker scheduler service
- **WHEN** the coverage scan is migrated
- **THEN** it SHALL run inside the Docker `scheduler` container (alongside the jira cron workflows), NOT in-process in the ai-review FastAPI service
- **AND** the ai-review :8090 service SHALL remain launchd-managed and otherwise untouched (binding spec `ai-review-deployment-state`)

#### Scenario: Launchd plist removed
- **WHEN** the migration is complete
- **THEN** `deployments/ai-review/launchd/com.tdt.review-coverage.plist` SHALL be deleted

#### Scenario: Inline plist generation removed from deploy.sh
- **WHEN** the migration is complete
- **THEN** the heredoc block in `ai-review/scripts/deploy.sh` that writes `com.tdt.review-coverage.plist` SHALL be removed, so a subsequent deploy does NOT recreate the launchd job

### Requirement: Migrate android daily scan to DBOS schedules
The `code-daily-scan` Android daily technical-debt scan (previously named `android-scan-agent` before the `unified-code-daily-scan` refactor) SHALL be registered as a DBOS `@scheduled_workflow` and hosted in the Docker `scheduler` execution path. The legacy LaunchAgent fallback and any host-local timer SHALL not be used.

#### Scenario: Android daily scan is registered with DBOS
- **WHEN** the scheduler stack starts with `SCHEDULER_ENABLED=true`, `SCHEDULER_SCHEDULING_ENABLED=true`, and one of `SCHEDULER_DBOS_DATABASE_URL`, `SCHEDULER_POSTGRES_DSN`, or `DBOS_DATABASE_URL` configured
- **THEN** the `daily-android-scan` schedule SHALL be registered with `cron="0 7 * * *"`, `cron_timezone="Asia/Ho_Chi_Minh"`, no dedicated queue (`queue_name=NULL`), and `automatic_backfill=False`
- **AND** `tdt-scheduler schedules list` SHALL show the schedule

#### Scenario: Schedule name maps to the unified scanner
- **WHEN** an operator looks up the `daily-android-scan` schedule
- **THEN** it SHALL be implemented in `code-daily-scan` (the platform-agnostic scanner), NOT a standalone `android-scan-agent` package
- **AND** any historical mention of `android-scan-agent` in the schedule workflow function name is a legacy alias — the authoritative binary is the `code-daily-scan` CLI run with `--platform android`

#### Scenario: Missed tick is not replayed
- **WHEN** the scheduler service is offline at 07:00 AM ICT and comes back later
- **THEN** the missed `daily-android-scan` tick SHALL NOT be replayed by a local fallback
- **AND** the next execution SHALL occur on the next scheduled DBOS cron tick

### Requirement: Migrate iOS daily scan to DBOS schedules
The `code-daily-scan` iOS daily technical-debt scan SHALL be registered as a DBOS `@scheduled_workflow` and hosted in the Docker `scheduler` execution path. The legacy LaunchAgent fallback and any host-local timer SHALL not be used. The iOS workflow SHALL share a single implementation helper with the Android daily scan (the platform-agnostic `code-daily-scan` CLI is the authoritative binary); it MUST NOT introduce a parallel implementation path.

#### Scenario: iOS daily scan is registered with DBOS
- **WHEN** the scheduler stack starts with `SCHEDULER_ENABLED=true`, `SCHEDULER_SCHEDULING_ENABLED=true`, and one of `SCHEDULER_DBOS_DATABASE_URL`, `SCHEDULER_POSTGRES_DSN`, or `DBOS_DATABASE_URL` configured
- **THEN** the `daily-ios-scan` schedule SHALL be registered alongside `daily-android-scan` in the same `agent-core/scheduler_setup.py` module
- **AND** `tdt-scheduler schedules list` SHALL show the schedule

#### Scenario: iOS daily scan uses the same unified helper
- **WHEN** the iOS daily scan runs
- **THEN** it SHALL be implemented in `code-daily-scan` (the platform-agnostic scanner) and invoked via the shared `_run_platform_scan(platform, tz)` helper
- **AND** the implementation MUST NOT be a parallel copy of the Android workflow (no `_run_ios_scan` / `_ios_scan_command` siblings)

#### Scenario: iOS daily scan cron/timezone per-platform config
- **WHEN** the operator's `~/.tdt/code-daily-scan.yaml` contains an `ios:` section with `cron` and `timezone`
- **THEN** the `daily-ios-scan` schedule SHALL use those values
- **AND** when the `ios:` section is absent, the schedule SHALL fall through to the built-in default cron/timezone (not silently use the Android section's values)

#### Scenario: iOS missed tick is not replayed
- **WHEN** the scheduler service is offline at the iOS daily tick and comes back later
- **THEN** the missed `daily-ios-scan` tick SHALL NOT be replayed by a local fallback
- **AND** the next execution SHALL occur on the next scheduled DBOS cron tick

### Requirement: Schedule name prefixing
All migrated schedules SHALL use service-prefixed names to avoid collisions.

#### Scenario: Prefixed schedule names
- **WHEN** schedules are listed
- **THEN** they SHALL use prefixes: `jira-standup`, `jira-blocked`, `coverage-scan`, `daily-android-scan`, etc.

### Requirement: Scheduled workflows pin an explicit cron timezone
Crontab fires in the host's local time, but the Docker `scheduler` container defaults to UTC. Every migrated `@scheduled_workflow` SHALL set an explicit `cron_timezone=` so report times do not silently shift by the UTC offset. The cron timezone SHALL be resolved from the existing `jira_daily_reports.config.workspace_timezone_name()` (which reads `PERSON_CAPACITY_TIMEZONE`/`TDT_TIMEZONE`/`TZ`, then host, then UTC).

#### Scenario: Standup fires at the intended local 8 AM
- **WHEN** `jira-standup` is registered from crontab `0 8 * * 1-5`
- **THEN** the `scheduled_workflow` SHALL be registered with `cron="0 8 * * 1-5"` AND an explicit `cron_timezone` equal to the resolved workspace timezone, so it fires at 08:00 local — not 08:00 UTC

#### Scenario: Cron timezone is consistent across all migrated schedules
- **WHEN** the 13 jira schedules and the coverage scan are registered
- **THEN** each SHALL carry the same resolved `cron_timezone` value, and a test SHALL assert no schedule is registered with `cron_timezone=None`

### Requirement: Scheduled workflows disable automatic backfill (default policy)
Every migrated `@scheduled_workflow` SHALL register with `automatic_backfill=False` by default.

**DBOS validation (2026):** DBOS supports optional automatic backfill of missed schedule ticks (`automatic_backfill=True`) and manual backfill over a date range (`backfill_schedule`).

**TDT policy (this change):** Default backfill is OFF for all migrated schedules in this change.

**Rationale:** After an outage, backfill would replay a burst of missed ticks (e.g. 13+ stale reports at once), which is undesirable for notification/report workflows. Instead, each workflow’s next run MUST be idempotent and reconcile its target window.

#### Scenario: No schedule enables backfill by default
- **WHEN** the jira schedules, `jira-run-all`, and the coverage scan are registered
- **THEN** a test SHALL assert every registered spec has `automatic_backfill=False`

### Requirement: Docker scheduler has the credentials and network egress to run its workloads
The `scheduler` container SHALL be provisioned with every secret and network route its hosted workloads need at runtime, because moving jira-daily-reports and the coverage scan off the host removes their implicit access to `~/.tdt/.env` and host networking. At minimum: `JIRA_*` (filter/board/project + auth), `SPREADSHEET_ID`, Google credentials (`GOOGLE_WORKSPACE_CLI_TOKEN` or `GOOGLE_SERVICE_ACCOUNT_PATH`), and egress to the Jira and Google Sheets endpoints.

#### Scenario: Reports can authenticate from inside the container
- **WHEN** a jira report or the sprint-sheet workflow runs inside the `scheduler` container
- **THEN** the required `JIRA_*`/`SPREADSHEET_ID`/`GOOGLE_*` values SHALL be present in the container environment (e.g. via `env_file: ~/.tdt/.env`, Docker secrets, or an explicit `environment:` block) and outbound network access to Jira/Google SHALL succeed

#### Scenario: Missing credentials fail loudly, not silently
- **WHEN** a required credential is absent in the container
- **THEN** the workflow SHALL fail with a clear error surfaced via `tdt-scheduler` / the health API — it SHALL NOT silently skip the run

