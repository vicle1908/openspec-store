# Spec Delta

## ADDED Requirements

### Requirement: Durable Workflow Execution and Determinism Invariants

The `shb-schedule` service SHALL provide durable workflow execution with recoverable execution history, retry behavior, and step replay semantics backed by `dbos>=3.1.0`. Workflows decorated with `@DBOS.workflow` SHALL accept `(scheduled_at, context)` positional parameters when dispatched on a schedule and SHALL remain strictly deterministic; all non-deterministic operations including system clock readings (`datetime.now(timezone.utc)`), filesystem mutations, and external subprocess execution SHALL be strictly encapsulated inside `@DBOS.step` functions with explicit timeouts. Local execution SHALL support an embedded user-home SQLite database in WAL mode (`PRAGMA journal_mode=WAL;`), and enterprise execution SHALL support PostgreSQL 18 in a dedicated `shb_scheduler` schema. External side effects SHALL be treated as idempotent-or-guarded operations; the service SHALL NOT claim transactional exactly-once behavior for arbitrary external subprocesses.

#### Scenario: Engine initialization and lifecycle
- **WHEN** `shb-schedule serve` is executed
- **THEN** the service SHALL load configuration using the SHB configuration convention, resolve the database path under the current user's `~/.shb/` directory (`0700` dir / `0600` file) unless explicitly configured, acquire a kernel-level single-owner lock, initialize DBOS via an ASGI lifespan context manager, perform persisted-state reconciliation, and expose the health endpoint on port `9110` by default

#### Scenario: Hermetic test passthrough
- **WHEN** `SHB_SCHEDULER_ENABLED=false` is set in the runtime environment
- **THEN** the service SHALL execute workflows without requiring an active scheduler database and SHALL make the disabled mode visible in diagnostics

### Requirement: Canonical Scheduler Ownership and Concurrency Locking

The SHB ecosystem SHALL have one canonical schedule owner. Only the active `shb-schedule` daemon SHALL apply the recurring schedule set. The daemon SHALL acquire a non-blocking kernel lock via `fcntl.flock` on `~/.shb/shb-schedule.lock`. A second active daemon SHALL fail closed or expose read-only health state rather than applying schedules concurrently.

#### Scenario: Duplicate scheduler startup
- **WHEN** a second scheduler daemon starts while another owner holds the lock
- **THEN** it SHALL NOT replace or mutate the active schedule set
- **AND** it SHALL NOT attempt to bind to the primary daemon's HTTP health port (9110)
- **AND** it SHALL report the ownership conflict through logs and exit cleanly without terminating the primary process
### Requirement: Declarative Manifest System and Safe Hot-Reloading

The service SHALL discover and parse manifests adhering to `shb-schedule/v1` from `~/.shb/schedules/*.yaml`. Manifest models SHALL be defined with Pydantic v2 (`ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)`), supporting cron expressions, explicit IANA timezones (default `Asia/Ho_Chi_Minh`), execution timeouts, retry backoffs, queue declarations, and non-evaluating `${VAR:-default}` substitution. Automatic backfill SHALL be disabled by default. Reload requests via `~/.shb/schedules/.reload` mtime changes or `SIGUSR1` signals SHALL be handled asynchronously via `loop.add_signal_handler` and be transactional from the observer's perspective.

#### Scenario: Manifest validation and variable substitution
- **WHEN** a YAML manifest containing environment placeholders is loaded
- **THEN** the service SHALL substitute variables against `~/.shb/.env` without shell evaluation, validate the complete manifest set against the strict Pydantic v2 schema, resolve approved workflow callables, collect declared queues, and reject the candidate set if any manifest is invalid

#### Scenario: Hot-reload on sentinel file change
- **WHEN** the `.reload` sentinel is touched or `SIGUSR1` is received
- **THEN** the service SHALL validate and reconcile the complete candidate registry before applying it
- **AND** retain the last known-good registry if validation, import, queue, or reconciliation fails
- **AND** SHALL preserve active connections and valid running workflows

### Requirement: Persisted Schedule-State Reconciliation

The service SHALL reconcile persisted scheduler state with the accepted manifest registry at startup and before an accepted registry replacement. Dynamic schedules SHALL be reconciled against the DBOS persistent schedule table. Removed or renamed schedules SHALL be retired, obsolete queued/error work SHALL be cancelled or quarantined according to its identity, and active valid runs SHALL remain unaffected. Reconciliation SHALL produce an auditable result.

#### Scenario: Removed schedule reconciliation
- **WHEN** a previously registered schedule is absent from the accepted manifest set
- **THEN** the service SHALL stop future dispatch for that schedule
- **AND** SHALL explicitly delete the schedule record from the persistent `workflow_schedules` table via `DBOS.delete_schedule`
- **AND** SHALL clean up or quarantine obsolete persisted work without deleting required execution history
### Requirement: Health and Operational Visibility

The service SHALL expose health and schedule-state information via an ASGI HTTP service on port `9110`, sufficient to distinguish owner status, database readiness, manifest reload status, and registered jobs, using modern Starlette/FastAPI lifespan event handling.

#### Scenario: Health and schedule inspection
- **WHEN** an operator requests `/scheduler/health`, `/scheduler/schedules`, or `/scheduler/schedules/{name}`
- **THEN** the service SHALL return current ownership, persistence, reload, and schedule information without exposing credentials

#### Scenario: On-demand trigger
- **WHEN** an operator invokes `shb-schedule run-now <job_name>` or the supported trigger endpoint
- **THEN** the service SHALL submit the job through the durable execution path, enforce ownership, and return an identifiable execution result

### Requirement: Daily Multi-Repo SHB Documentation Sync Workflow

The service SHALL implement a durable workflow for the existing SHB-native `shb-docs-sync` capability from `shb-tools` (`DocsSynchronizer.audit_and_sync`), executing at 03:30 in `Asia/Ho_Chi_Minh` across the 12 existing SHB repositories. For each repository, the workflow SHALL execute an atomic `@DBOS.step` checking `git status --porcelain` and skip repositories with uncommitted changes with recorded reasons, before executing synchronization with a 180-second per-repository timeout.

#### Scenario: Scheduled execution with dirty worktree protection
- **WHEN** the daily documentation sync workflow is triggered by cron or on-demand via `shb-schedule run-now daily-shb-docs-sync`
- **THEN** it SHALL evaluate each configured SHB repository root with `git status --porcelain`
- **AND** skip mutation or drift remediation on dirty worktrees while recording the reason
- **AND** execute the documentation audit via `DocsSynchronizer.audit_and_sync` or `shb-docs-sync check --root <path>`
- **AND** inspect structured audit status and record findings without failing on code-0 audit responses
