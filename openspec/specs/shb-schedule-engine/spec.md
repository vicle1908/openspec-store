# shb-schedule-engine Specification

## Purpose
Establishes the durable task scheduling engine, declarative schedule manifests, single-owner concurrency governance, dynamic reconciliation, and multi-repo documentation synchronization for Saigon - Hanoi Bank (SHB).

## Requirements

### Requirement: Durable Workflow Execution and Determinism Invariants
The `shb-schedule` service SHALL provide durable workflow execution with recoverable execution history, retry behavior, and step replay semantics backed by `dbos>=3.1.0`. Workflows decorated with `@DBOS.workflow` SHALL accept `(scheduled_at, context)` positional parameters when dispatched on a schedule and SHALL remain strictly deterministic; all non-deterministic operations including system clock readings (`datetime.now(timezone.utc)`), filesystem mutations, and external subprocess execution SHALL be strictly encapsulated inside `@DBOS.step` functions with explicit timeouts. Local execution SHALL support an embedded user-home SQLite database in WAL mode (`PRAGMA journal_mode=WAL;`), and enterprise execution SHALL support PostgreSQL 18 in a dedicated `shb_scheduler` schema. External side effects SHALL be treated as idempotent-or-guarded operations; the service SHALL NOT claim transactional exactly-once behavior for arbitrary external subprocesses.

#### Scenario: Engine initialization and lifecycle
- **WHEN** `shb-schedule serve` is executed
- **THEN** the service SHALL load configuration using the SHB configuration convention, resolve the database path under the current user's `~/.shb/` directory (`0700` dir / `0600` file) unless explicitly configured, acquire a kernel-level single-owner lock, initialize DBOS via an ASGI lifespan context manager, perform persisted-state reconciliation, and expose the health endpoint on port `9110` by default

#### Scenario: Hermetic test passthrough
- **WHEN** `SHB_SCHEDULER_ENABLED=false` is set in the runtime environment
- **THEN** the service SHALL execute workflows without requiring an active scheduler database and SHALL make the disabled mode visible in diagnostics

### Requirement: Canonical Scheduler Ownership and Concurrency Locking
The SHB ecosystem SHALL have one canonical schedule owner. Only the active `shb-schedule` daemon SHALL apply recurring schedules. In containerized/PostgreSQL mode, leadership SHALL be governed by a non-blocking PostgreSQL session advisory lock; in local SQLite mode, via `fcntl.flock` on `~/.shb/shb-schedule.lock`. A second active daemon SHALL fail closed or expose read-only health state rather than applying schedules concurrently.

#### Scenario: Duplicate scheduler startup
- **WHEN** a second scheduler daemon starts while another owner holds the lock
- **THEN** it SHALL NOT replace or mutate the active schedule set
- **AND** it SHALL NOT attempt to bind to the primary daemon's HTTP health port (9110)
- **AND** it SHALL report the ownership conflict through logs and exit cleanly without terminating the primary process

#### Scenario: Multi-container PostgreSQL leadership governance
- **WHEN** multiple scheduler containers connect to the same PostgreSQL database and schema
- **THEN** only the container acquiring the database session advisory lock SHALL become leader and register schedules
- **AND** competing daemons SHALL exit cleanly with status code 0 (or serve read-only standby health returning 503 if configured)
- **AND** loss of database connectivity SHALL cause the leader to fail closed to standby mode within bounded time

### Requirement: Declarative Manifest System and Safe Hot-Reloading
The service SHALL discover and parse `shb-schedule/v1` YAML manifests, with automatic backfill disabled by default. Hot-reload SHALL be triggerable via loopback HTTP POST `/scheduler/reload`, `SIGUSR1` signal, or mtime changes on `.reload` sentinels across candidate paths including read-only mount locations and configured sentinel paths, retaining the last known-good registry on validation or reconciliation failure.

#### Scenario: Manifest validation and variable substitution
- **WHEN** a YAML manifest containing environment placeholders is loaded
- **THEN** the service SHALL substitute variables against `~/.shb/.env` without shell evaluation, validate the complete manifest set against the strict Pydantic v2 schema, resolve approved workflow callables, collect declared queues, and reject the candidate set if any manifest is invalid

#### Scenario: Hot-reload on sentinel file change
- **WHEN** the `.reload` sentinel is touched or `SIGUSR1` is received
- **THEN** the service SHALL validate and reconcile the complete candidate registry before applying it
- **AND** retain the last known-good registry if validation, import, queue, or reconciliation fails
- **AND** SHALL preserve active connections and valid running workflows

#### Scenario: Hot-reload via daemon HTTP endpoint
- **WHEN** a client issues `POST /scheduler/reload` or invokes `shb-schedule reload`
- **THEN** the service SHALL reconcile schedules against mounted manifests without requiring filesystem write access to the manifest directory
- **AND** return a summary response detailing added, updated, retired, and retained schedules

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

### Requirement: Banking Core Workload Bindings
The `shb-schedule` package SHALL provide durable workflow implementations and approved registry allowlist mappings for secondary core banking operational workloads, specifically end-of-day settlement reconciliation (`eod_settlement_recon_workflow`) and automated PCI-DSS compliance scanning (`nightly_compliance_scan_workflow`).

#### Scenario: Scheduled settlement reconciliation execution
- **WHEN** the `daily-eod-settlement-recon` schedule is triggered by cron (23:00 HCM) or on-demand
- **THEN** it executes `eod_settlement_recon_workflow`, sources internal and clearing transactions via `load_settlement_transactions`, and reconciles ledgers via `shb_tools.recon.engine.ReconciliationEngine`
- **AND** records matched transactions, discrepancies, and orphan counts in DBOS execution history

#### Scenario: Scheduled compliance scan execution
- **WHEN** the `daily-nightly-compliance-scan` schedule is triggered by cron (01:00 HCM) or on-demand
- **THEN** it executes `nightly_compliance_scan_workflow` delegating to `shb_tools.scanner.engine.ComplianceScanner`
- **AND** skips repositories with uncommitted changes while reporting scan violations in structured workflow telemetry

### Requirement: Containerized Orchestration via Docker Compose
The `shb-schedule` service SHALL provide standardized containerized orchestration through Docker Compose comprising a `postgres:18.6-alpine` database service and the scheduler container, eliminating dependencies on host init systems (`launchd`, `systemd`) while preserving opt-in local SQLite mode for development.

#### Scenario: Bringing up the scheduler stack
- **WHEN** an operator runs `docker compose up -d` within the `shb-schedule` project root
- **THEN** the Compose stack SHALL start a PostgreSQL 18.6 (Alpine) service and the `shb-schedule` application container
- **AND** the application container SHALL wait for the database service health check to report healthy before initializing the DBOS Transact runtime

#### Scenario: Database health gating
- **WHEN** the `db` service has not yet passed its health check
- **THEN** the `scheduler` service SHALL NOT begin initialization
- **AND** once the check passes, the `scheduler` service SHALL proceed without operator intervention

#### Scenario: Uniform cross-platform behavior
- **WHEN** the same `compose.yaml` is executed on macOS, Linux, or a CI runner with a running Docker daemon
- **THEN** the resulting scheduler behavior (manifest parsing, durable workflow execution, health endpoints) SHALL be identical across those platforms

### Requirement: PostgreSQL 18.6 Backend with Schema Isolation
The scheduler SHALL persist its durable execution history, schedule registry, and queue state in a PostgreSQL 18.6 database, with all DBOS system tables created under a dedicated `shb_scheduler` schema (or equivalent configurable schema name). The database SHALL be provisioned from a clean state on first launch with no external migration scripts required.

#### Scenario: Clean initialization
- **WHEN** the scheduler container first connects to an empty PostgreSQL `shb_scheduler` database
- **THEN** the DBOS Transact runtime SHALL apply its full system schema (tables, indexes, migrations) automatically
- **AND** the service SHALL report a healthy status without requiring operator-run migrations

#### Scenario: Data isolation
- **WHEN** the scheduler writes execution history or schedule state
- **THEN** it SHALL write only to the configured `shb_scheduler` schema and SHALL NOT modify other PostgreSQL schemas or databases on the same server

### Requirement: Lean Container Mount Policy
The production `shb-schedule` container SHALL mount only the schedule manifest directory (`~/.shb/schedules/*.yaml`) as a read-only volume. It SHALL NOT mount source-code repositories or host working trees in base production mode.

#### Scenario: Minimal host coupling in production
- **WHEN** the base `compose.yaml` (without local development override) is started
- **THEN** the running container SHALL have access to the manifest files at a stable in-container path
- **AND** the container SHALL NOT have bind-mounted access to `~/Developer/shb/*` repositories

#### Scenario: Local development override
- **WHEN** an operator starts the stack with `compose.override.yaml` present
- **THEN** the override MAY additionally mount the developer workspace read-only for local audit workloads
- **AND** the base production profile SHALL remain unchanged and portable

### Requirement: Health and Operability via Standard Interfaces
The containerized scheduler SHALL expose the HTTP health and schedule-status endpoints on host port `9110`, listening on `0.0.0.0` inside the container so the published port is reachable, and SHALL be triggerable via the existing CLI commands executed inside the container (`docker compose exec scheduler shb-schedule ...`).

#### Scenario: Health check visibility
- **WHEN** an operator queries `http://127.0.0.1:9110/scheduler/health` after `docker compose up`
- **THEN** the endpoint SHALL return ownership, persistence, and schedule status without exposing credentials

#### Scenario: Container-reachable binding
- **WHEN** the scheduler process starts inside the container
- **THEN** it SHALL bind port `9110` on the container's non-loopback interface so the host-published port mapping resolves

#### Scenario: On-demand trigger inside container
- **WHEN** an operator runs `docker compose exec scheduler shb-schedule run-now <job-name>`
- **THEN** the job SHALL be submitted through the durable execution path and return an identifiable execution result

### Requirement: Removal of Host Service Installers
The scheduler SHALL NOT expose a host service-installation command; operators SHALL manage the scheduler lifecycle through Docker Compose or explicit environment overrides.

#### Scenario: Service installer no longer offered
- **WHEN** an operator runs `shb-schedule --help`
- **THEN** the command help SHALL NOT list a `service` command group
- **AND** invoking `shb-schedule service install` SHALL fail as an unrecognized command
- **AND** the scheduler documentation SHALL describe containerized operation instead of host LaunchAgent or systemd installation

### Requirement: Fail-Closed Workflow Execution on Absent Input
Workflows dispatched by the scheduler SHALL execute fail-closed when prerequisite input data or target file systems are absent. Workflows SHALL NOT synthesize default sample records or report success when target environments are missing.

#### Scenario: Settlement reconciliation without input ledgers
- **WHEN** `eod-settlement-recon` is invoked without internal or clearing transaction data
- **THEN** the workflow SHALL report `ACTION_REQUIRED` status
- **AND** it SHALL NOT return `BALANCED` or fall back to hardcoded sample transactions

#### Scenario: Documentation and compliance workflows with unmounted workspaces
- **WHEN** `daily-shb-docs-sync` or `nightly-compliance-scan` is invoked with zero target repositories available
- **THEN** the workflow SHALL report `PARTIAL` status
- **AND** it SHALL NOT report `SUCCESS`

#### Scenario: Explicit fixture input provision
- **WHEN** input ledgers or repository workspaces are provided via manifest context or environment variables
- **THEN** the workflows SHALL process the provided data and report genuine evaluation status
