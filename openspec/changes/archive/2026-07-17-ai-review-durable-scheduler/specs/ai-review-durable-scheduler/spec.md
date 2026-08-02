# ai-review Durable Scheduler Spec

## Purpose

Define the contract for durable review dispatch in the `ai-review`
service, aligning it with the TDT ecosystem standard (DBOS) used
by `webhook-receiver` and documented in the
`centralized-scheduling-module` openspec change.

## ADDED Requirements

### Requirement: REQ-1: DBOS-aligned dispatch when scheduler is enabled

The FastAPI intake handler SHALL dispatch reviews
through a `DebouncerWrapper` registered with the `SchedulerEngine`,
keyed by `mr-{mr_iid}`, with the configured debounce period.
This requirement applies when `SCHEDULER_ENABLED=true` and a valid
`SCHEDULER_DBOS_DATABASE_URL` is configured.

#### Scenario: DBOS dispatch path

- **WHEN** the lifespan starts and `SchedulerEngine.from_env().initialize()`
  succeeds with `enabled=True`
- **AND** the intake handler receives a review request for `mr_iid=42`
- **THEN** the handler MUST call
  `debouncer.debounce("mr-42", payload, handoff_id, period_sec=N)`
- **AND** the dispatch MUST be pushed onto the asyncio default
  executor (because DBOS's `Debouncer.debounce` is sync and refuses
  to run inside an active asyncio loop)

### Requirement: REQ-2: Graceful passthrough when DBOS is not available

The service SHALL continue to serve reviews using the in-process
`asyncio.create_task` pattern, with the task tracked in a set so
the service can wait for it on shutdown.

#### Scenario: DBOS-disabled passthrough

- **WHEN** `SCHEDULER_ENABLED=false` in the env
- **AND** the intake handler receives a review request
- **THEN** the handler MUST spawn an `asyncio.create_task` for
  the review
- **AND** MUST NOT call the (None) debouncer
- **AND** the task MUST be tracked in `_tasks` so it can be
  awaited on shutdown

### Requirement: REQ-3: Lifespan-managed engine lifecycle

The FastAPI `lifespan` context MUST initialize the `SchedulerEngine`
on startup and shut it down on exit. Init failure MUST be logged
but MUST NOT prevent the service from starting.

#### Scenario: Scheduler shutdown on lifespan exit

- **WHEN** the FastAPI app shuts down
- **AND** the engine was successfully initialized
- **THEN** the lifespan MUST call `engine.shutdown()` to release
  DBOS resources

### Requirement: REQ-4: Health endpoint exposes scheduler state

The `/health` endpoint MUST include a `scheduler` key with at least
`enabled`, `initialized`, and `dbos_connected` boolean fields, and
a `review_debouncer` key with an `enabled` field. This allows
operators to verify DBOS is active without reading the logs.

#### Scenario: Health reports scheduler status

- **WHEN** an operator curls `/health`
- **THEN** the response MUST include a `scheduler` key with
  `enabled`, `initialized`, `dbos_connected` booleans
- **AND** a `review_debouncer` key with an `enabled` boolean

### Requirement: REQ-5: Per-service DBOS app namespace

Each service that uses DBOS MUST export a service-specific
`SCHEDULER_APP_NAME` in its runtime launcher. Sharing the default
`tdt-scheduler` namespace across services causes DBOS to route
workflows between processes arbitrarily, and the pickled workflow
args reference classes from the originating service's module path —
unpickling in the wrong process raises `ModuleNotFoundError` and
the workflow transitions to ERROR.

#### Scenario: service-specific app_name

- **WHEN** `ai-review` starts up
- **THEN** its runtime launcher MUST export `SCHEDULER_APP_NAME=tdt-ai-review`
- **AND** the DBOS Conductor MUST log `appname=tdt-ai-review`
  on startup (verifiable in `ai-review/logs/ai-review.stderr.log`)

#### Scenario: webhook-receiver counterpart

- **WHEN** `webhook-receiver` starts up
- **THEN** its runtime launcher MUST export `SCHEDULER_APP_NAME=tdt-webhook-receiver`
- **AND** the DBOS Conductor MUST log `appname=tdt-webhook-receiver`
  on startup (verifiable in `webhook-receiver/logs/webhook-receiver.stderr.log`)

### Requirement: REQ-6: Operational recovery from stale DBOS ERROR rows

The `tdt-scheduler cancel-stale-errors` CLI MUST exist and MUST cancel
ERROR rows from a previous `application_version` whose exception class is
one of `ModuleNotFoundError` / `AttributeError` / `ImportError` /
`UnpicklingError` OR whose workflow name is one of
`_dbos_debouncer_workflow`, `_dispatch_review_workflow`,
`_dispatch_mr_workflow`. This is the operational recovery
mechanism for the per-key debouncer lock contention described
in REQ-5.

#### Scenario: cancel stale errors after a deploy

- **WHEN** an operator runs `tdt-scheduler cancel-stale-errors`
  after a deploy that renamed a registered workflow function
- **THEN** the CLI MUST cancel all matching ERROR rows
- **AND** the count MUST be reported in the JSON output
- **AND** the affected per-key debouncer locks MUST be released
  so new dispatches for the same key can proceed

## Out of Scope

- Periodic / cron-scheduled workflows. Per the
  `centralized-scheduling-module` Phase 4 migration, periodic work
  (coverage scan, freshness refresh) runs in the Docker `scheduler`
  service, not in `ai-review`.
- Replacing `IdempotencyRegistry`. The DBOS debouncer's per-key
  dedup is a complement to the registry's logical-key dedup; the
  registry continues to handle the `accepted=true` vs `accepted=false`
  branching at the API layer.
- The `~run_in_executor` overhead is intentionally not measured
  or optimized; the same pattern is used in `webhook-receiver`
  and accepted there.

## Cross-references

- `centralized-scheduling-module` openspec — establishes DBOS as
  the TDT standard.
- `coverage-sweep` openspec — extends `webhook-receiver` with
  DBOS-scheduled self-test and DLQ reaper; the same patterns
  (lifespan-managed engine, `engine.debouncer`, run-in-executor
  for sync DBOS calls) are applied here.
