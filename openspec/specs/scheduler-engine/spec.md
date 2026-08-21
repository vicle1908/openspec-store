# scheduler-engine Specification

## Purpose
Define the durable, exactly-once workflow primitives exposed by `SchedulerEngine`: scheduled
workflows, queues, and debouncers. The engine wraps [DBOS](https://dbos.dev/) and owns its
lifecycle. `apply_schedules()` is restricted to the canonical scheduler service via the
ownership contract documented in `tdt-scheduler-ownership-contract`; this delta adds the
guard to the existing `apply_schedules()` requirement.

## Requirements

### Requirement: SchedulerEngine scheduled_workflow decorator

The system SHALL provide a `scheduled_workflow()` decorator that registers a
cron-triggered workflow with the `ScheduleRegistry`. The decorator and
`apply_schedules()` SHALL together enforce the ownership contract described in
`tdt-scheduler-ownership-contract`: `apply_schedules()` refuses to register
schedules when the engine's `app_name` is not `tdt-scheduler`, unless
`SCHEDULER_ENFORCE_OWNERSHIP=false`.

The decorator is the registration mechanism for `_stale_workflow_cleaner`,
which SHALL be registered by `agent-core/scheduler_setup.py` alongside the
existing `daily_android_scan` and `daily_ios_scan` scheduled workflows.

#### Scenario: Apply schedules activates all registered specs

- **WHEN** `engine.apply_schedules()` is called after registering multiple
  specs (including `_stale_workflow_cleaner`) and the engine's `app_name` is
  `tdt-scheduler`
- **THEN** all registered specs (including the cleaner) SHALL be atomically
  pushed to DBOS via `DBOS.apply_schedules()`

#### Scenario: Apply schedules refuses non-owner app_name

- **WHEN** `engine.apply_schedules()` is called and the engine's `app_name` is
  not `tdt-scheduler` and `SCHEDULER_ENFORCE_OWNERSHIP` is unset or `true`
- **THEN** the engine SHALL raise `SchedulerContractViolationError` whose
  message names the offending `app_name` and the canonical owner, and SHALL
  NOT register any schedules (including the cleaner)

#### Scenario: Apply schedules honors SCHEDULER_ENFORCE_OWNERSHIP=false

- **WHEN** `engine.apply_schedules()` is called with a non-owner `app_name`
  and `SCHEDULER_ENFORCE_OWNERSHIP=false` in the environment
- **THEN** the engine SHALL proceed with registration without raising

### Requirement: SchedulerEngine lifecycle management
The system SHALL provide a `SchedulerEngine` class that manages the DBOS runtime lifecycle with initialize/shutdown/get_status methods.

#### Scenario: Initialize with DBOS enabled
- **WHEN** `SchedulerEngine(SchedulerConfig(enabled=True, postgres_dsn="..."))` is created and `initialize()` is called
- **THEN** the DBOS runtime SHALL be launched and `initialized` SHALL return `True`

#### Scenario: Initialize with DBOS disabled (passthrough mode)
- **WHEN** `SchedulerEngine(SchedulerConfig(enabled=False))` is created and `initialize()` is called
- **THEN** the engine SHALL log "Running in passthrough mode" and `initialized` SHALL return `False`

#### Scenario: Shutdown gracefully
- **WHEN** `shutdown()` is called on an initialized engine
- **THEN** the DBOS runtime SHALL be destroyed and `initialized` SHALL return `False`

#### Scenario: Get status returns engine state
- **WHEN** `get_status()` is called
- **THEN** it SHALL return a dict with `enabled`, `scheduling_enabled`, `initialized`, `schedule_count`, and `dbos_connected` keys

### Requirement: SchedulerEngine workflow decorator
The system SHALL provide a `workflow()` decorator that marks an async function as a durable workflow with exactly-once semantics when DBOS is enabled.

#### Scenario: Workflow completes successfully
- **WHEN** a decorated workflow function runs and returns a value
- **THEN** the result SHALL be a `SchedulerResult` with `status=COMPLETED` and the correct `output`

#### Scenario: Workflow fails
- **WHEN** a decorated workflow function raises an exception
- **THEN** the result SHALL be a `SchedulerResult` with `status=FAILED` and the error message in `error`

#### Scenario: Workflow in passthrough mode
- **WHEN** DBOS is disabled and a decorated workflow runs
- **THEN** the function SHALL execute directly and return a `SchedulerResult` wrapping the output

### Requirement: SchedulerEngine step decorator
The system SHALL provide a `step()` decorator that marks an async function as a durable step with automatic retry when DBOS is enabled.

#### Scenario: Step succeeds
- **WHEN** a decorated step function runs and returns a value
- **THEN** the result SHALL be a `SchedulerStepResult` with `status=COMPLETED`

#### Scenario: Step fails and retries
- **WHEN** a decorated step function raises an exception
- **THEN** the step SHALL be retried up to `max_retries` times with `retry_interval_seconds` between attempts

### Requirement: SchedulerEngine scheduled_workflow registration
The system SHALL provide a `scheduled_workflow()` decorator that registers a cron-triggered workflow with the `ScheduleRegistry`.

#### Scenario: Register cron schedule
- **WHEN** `@engine.scheduled_workflow(cron="0 8 * * 1-5", name="jira-standup", cron_timezone="UTC")` is applied to a function
- **THEN** a `ScheduledWorkflowSpec` SHALL be registered in the `ScheduleRegistry` with the given cron, name, and cron timezone

#### Scenario: Schedule not registered when scheduling disabled
- **WHEN** `scheduling_enabled=False` and `@engine.scheduled_workflow()` is applied
- **THEN** the function SHALL run as a normal workflow and NO spec SHALL be registered

#### Scenario: Apply schedules activates all registered specs
- **WHEN** `engine.apply_schedules()` is called after registering multiple specs
- **THEN** all registered specs SHALL be atomically pushed to DBOS via `DBOS.apply_schedules()`

### Requirement: SchedulerEngine queue
The system SHALL provide a `queue()` method that creates a named workflow queue with configurable concurrency and rate limiting.

#### Scenario: Create queue with concurrency limit
- **WHEN** `engine.queue("reviews", concurrency=2)` is called
- **THEN** a `QueueWrapper` SHALL be returned with the given name and concurrency

#### Scenario: Enqueue workflow through queue
- **WHEN** `queue.enqueue(workflow_fn, arg1, arg2)` is called
- **THEN** the workflow SHALL be enqueued through DBOS when enabled, or called directly in passthrough mode

### Requirement: SchedulerEngine debouncer
The system SHALL provide a `debouncer()` method that creates a debouncer wrapping a workflow function.

#### Scenario: Create debouncer
- **WHEN** `engine.debouncer(workflow_fn, timeout_sec=30)` is called
- **THEN** a `DebouncerWrapper` SHALL be returned wrapping the given function

#### Scenario: Debounce triggers workflow
- **WHEN** `debouncer.debounce("key-1", period_sec=30)` is called
- **THEN** the workflow SHALL be debounced through DBOS when enabled, or called directly in passthrough mode

### Requirement: SchedulerEngine from_env factory
The system SHALL provide a `from_env()` class method that reads configuration from environment variables and `~/.tdt/config.yaml`.

#### Scenario: Load config from environment
- **WHEN** `SchedulerEngine.from_env()` is called with `SCHEDULER_ENABLED=true`, `SCHEDULER_SCHEDULING_ENABLED=true`, and one of `SCHEDULER_DBOS_DATABASE_URL`, `SCHEDULER_POSTGRES_DSN`, or `DBOS_DATABASE_URL` set
- **THEN** the engine SHALL be configured with `enabled=True`, `scheduling_enabled=True`, and the given database URL

#### Scenario: Load config from config.yaml
- **WHEN** `SchedulerEngine.from_env()` is called and `~/.tdt/config.yaml` has a `scheduler:` section
- **THEN** the engine SHALL merge `scheduler.enabled`, `scheduler.scheduling_enabled`, `scheduler.postgres_dsn`, and `scheduler.app_name` with environment variable overrides

### Requirement: ScheduleRegistry management
The system SHALL provide a `ScheduleRegistry` class for registering, listing, and converting schedule specs to DBOS input format.

#### Scenario: Register and list schedules
- **WHEN** multiple `ScheduledWorkflowSpec` objects are registered
- **THEN** `list()` SHALL return them in deterministic (sorted) order

#### Scenario: Convert to DBOS inputs
- **WHEN** `to_dbos_inputs()` is called
- **THEN** it SHALL return a list of dicts matching the DBOS `ScheduleInput` shape with keys `schedule_name`, `workflow_name`, `workflow_class_name`, `schedule`, `context`, `automatic_backfill`, `cron_timezone`, `queue_name`
- **AND** `workflow_name` SHALL reflect the registered workflow function name
- **AND** `workflow_class_name` SHALL be `null` for function-based registrations

### Requirement: Passthrough mode for on-demand primitives
When DBOS is disabled, the **on-demand** primitives (`queue`, `debouncer`) SHALL degrade gracefully by running their wrapped function inline without crashing. Passthrough is NOT a fallback for `scheduled_workflow` (Decision 7): with no DBOS clock there is nothing to fire, so a missed tick is simply missed — it is not run inline or queued for catch-up.

#### Scenario: Queue passthrough
- **WHEN** `queue.enqueue(fn)` is called with DBOS disabled
- **THEN** `fn` SHALL be called directly and a `PassthroughWorkflowHandle` SHALL be returned

#### Scenario: Debouncer passthrough
- **WHEN** `debouncer.debounce("key", period_sec=10)` is called with DBOS disabled
- **THEN** the wrapped function SHALL be called directly and a `PassthroughWorkflowHandle` SHALL be returned

#### Scenario: Scheduled workflows do NOT fire in passthrough
- **WHEN** DBOS is disabled and a `scheduled_workflow`-decorated function exists
- **THEN** no cron clock exists and the workflow SHALL NOT fire on a schedule (Decision 7) — it runs only if invoked directly as a normal workflow; a missed tick is simply missed, never queued for catch-up

#### Scenario: Passthrough handle get_result
- **WHEN** `PassthroughWorkflowHandle(result).get_result()` is called
- **THEN** it SHALL return the direct result, running an awaitable if needed

### Requirement: Persisted scheduler state SHALL be reconciled before activation

The canonical scheduler SHALL establish the current set of scheduler-owned schedule names and registered workflow references before any persisted schedule is allowed to enqueue work. It SHALL compare that set with persisted schedule records and actionable workflow-status records in the shared DBOS system database, remove or cancel only confirmed stale scheduler-owned references, retain all valid current state, and report the counts and identities of mutations without exposing serialized exception payloads or credentials. Existing `scheduler-engine` requirement and scenario identifiers remain unchanged by this delta.

#### Scenario: Retired webhook-selftest schedule is quarantined before its next tick

- **WHEN** the shared system database contains a persisted `webhook-selftest` schedule or actionable workflow row but the current scheduler registry contains no `webhook-selftest` workflow reference
- **THEN** startup SHALL prevent that reference from producing another scheduled execution, SHALL remove or cancel the confirmed stale scheduler-owned state, and SHALL record a bounded reconciliation result identifying the retired name

#### Scenario: Current schedules and workflow state are retained

- **WHEN** persisted schedule and workflow-status records correspond to the current scheduler registry and ownership boundary
- **THEN** reconciliation SHALL leave those records executable and SHALL report zero removals or cancellations for them

#### Scenario: Reconciliation is idempotent

- **WHEN** the scheduler performs reconciliation more than once against the same already-reconciled database state
- **THEN** later runs SHALL make no additional mutation, SHALL not create duplicate schedules or workflow rows, and SHALL return a successful no-op result

#### Scenario: Unrelated consumer state is protected

- **WHEN** the shared system database contains state that cannot be proven to belong to the canonical scheduler
- **THEN** reconciliation SHALL not remove, cancel, or rewrite that state and SHALL report the ownership ambiguity for operator review

### Requirement: Reconciliation failures SHALL fail closed without destructive mutation

If the scheduler cannot read the required persisted state, resolve the current registry, verify the expected DBOS schema, or prove ownership of a candidate row, it SHALL preserve the candidate state, emit an actionable bounded diagnostic, and keep schedule processing and readiness inactive until a safe reconciliation succeeds. Disabled or passthrough operation SHALL remain non-destructive and SHALL not attempt persisted-state cleanup.

#### Scenario: System-database access fails during startup

- **WHEN** reconciliation cannot connect to or query the shared DBOS system database
- **THEN** the scheduler SHALL not activate cron processing or advertise readiness, SHALL leave persisted rows unchanged, and SHALL expose the failure reason without leaking connection secrets

#### Scenario: Registry resolution is incomplete

- **WHEN** a manifest or registered workflow cannot be resolved unambiguously before reconciliation
- **THEN** the scheduler SHALL not guess whether persisted state is stale, SHALL leave candidate rows unchanged, and SHALL fail closed with the unresolved reference in diagnostics

#### Scenario: Passthrough mode is selected

- **WHEN** durable scheduling is disabled
- **THEN** the scheduler SHALL skip persisted-state mutation and SHALL preserve the existing passthrough behavior

### Requirement: Reconciliation migration SHALL be reversible and operationally bounded

The implementation SHALL provide a versioned migration path that supports dry-run reporting, captures the exact scheduler-owned rows selected for mutation, applies destructive changes atomically or with an equivalent recoverable boundary, and provides rollback that restores only the captured state. Migration and rollback SHALL be safe to repeat and SHALL never require truncating or recreating either scheduler database.

#### Scenario: Dry-run reports stale state without mutation

- **WHEN** an operator runs reconciliation in dry-run mode against a database containing stale and current records
- **THEN** the command or startup report SHALL identify the candidate schedule/workflow names and planned actions, SHALL distinguish protected state, and SHALL leave the database byte-for-byte unchanged for the selected tables

#### Scenario: Applied migration records a rollback point

- **WHEN** an operator applies the reconciliation migration after reviewing its dry-run report
- **THEN** the system SHALL persist or emit a versioned rollback point containing the affected scheduler-owned rows, apply only the approved stale-state changes, and report completion with counts

#### Scenario: Rollback restores only captured scheduler state

- **WHEN** an operator invokes rollback for a completed reconciliation migration
- **THEN** the system SHALL restore the captured schedule/workflow rows, preserve unrelated rows and newer valid scheduler state, and report whether the rollback completed or was refused due to a conflict

#### Scenario: Migration failure leaves a recoverable boundary

- **WHEN** a reconciliation migration fails before all selected mutations complete
- **THEN** the system SHALL either commit no destructive changes or automatically restore the captured rows, mark the migration incomplete, and keep schedule processing disabled until the state is verified

### Requirement: Scheduler acceptance SHALL prove stale-state cleanup and fresh-control health

The change SHALL include regression and real-runtime acceptance that exercise a shared database containing stale persisted scheduler state and a fresh PostgreSQL control. Acceptance SHALL verify bounded scheduler liveness, current schedule application, absence of the retired `webhook-selftest` manifest entry, and absence of `webhook-selftest is not a registered workflow function` after reconciliation.

#### Scenario: Shared stale database starts without unregistered-workflow errors

- **WHEN** the canonical scheduler starts against a reproducible shared database seeded with a retired `webhook-selftest` schedule or actionable state
- **THEN** reconciliation SHALL complete before schedule processing, the scheduler SHALL remain healthy for the bounded observation window, current schedules SHALL continue to apply, and logs SHALL contain no new unregistered-workflow error for `webhook-selftest`

#### Scenario: Fresh PostgreSQL control preserves the verified baseline

- **WHEN** the scheduler starts with fresh `tdt_scheduler` and `tdt_scheduler_dbos_sys` databases and is observed for at least 150 seconds
- **THEN** the scheduler SHALL remain healthy, report `dbos_connected=true`, generate the canonical `19` schedule / `19` applied baseline after the persisted legacy `stale_workflow_cleaner` is retired, contain no retired manifest entry, and emit no unregistered-workflow error

#### Scenario: Regression fixtures cover safe boundaries

- **WHEN** automated tests exercise stale schedule rows, stale workflow-status rows, current rows, ambiguous ownership, repeated reconciliation, dry-run, rollback, and injected database or registry failures
- **THEN** the tests SHALL demonstrate the required mutation, protection, idempotence, fail-closed, and recovery behavior without requiring an ambient developer database

### Requirement: ScheduleRegistryLoader bootstrap before schedule application

The scheduler runtime host SHALL execute `ScheduleRegistryLoader.apply_from_yaml(engine)` during process startup before invoking `engine.apply_schedules()`, ensuring all declarative manifests in `~/.tdt/schedules/` are registered into `ScheduleRegistry`.

#### Scenario: Bootstrap loads YAML manifests before DBOS schedule push

- **WHEN** `tdt-scheduler serve` starts up
- **THEN** `ScheduleRegistryLoader.apply_from_yaml(engine)` SHALL be called before `engine.apply_schedules()`
- **AND** all valid schedule manifests in `~/.tdt/schedules/` SHALL be loaded and pushed to DBOS atomically

#### Scenario: Schedule application aggregates decorator and YAML schedules

- **WHEN** both `@engine.scheduled_workflow` decorators and declarative YAML manifests exist
- **THEN** `apply_schedules()` SHALL activate the unified set of registered `ScheduledWorkflowSpec` entries in DBOS
