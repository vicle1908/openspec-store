## ADDED Requirements

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
- **THEN** the scheduler SHALL remain healthy, report `dbos_connected=true`, generate the verified `20` schedule / `19` applied baseline (or record and justify an intentional manifest-count change), contain no `webhook-selftest` manifest entry, and emit no unregistered-workflow error

#### Scenario: Regression fixtures cover safe boundaries

- **WHEN** automated tests exercise stale schedule rows, stale workflow-status rows, current rows, ambiguous ownership, repeated reconciliation, dry-run, rollback, and injected database or registry failures
- **THEN** the tests SHALL demonstrate the required mutation, protection, idempotence, fail-closed, and recovery behavior without requiring an ambient developer database
