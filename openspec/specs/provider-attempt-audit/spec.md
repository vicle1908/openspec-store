# provider-attempt-audit Specification

## Purpose
Define the durable provider-attempt intent lifecycle, schema-4 migration,
atomic terminal audit records, idempotent reconciliation, and restart recovery
rules for the standalone harness.
## Requirements
### Requirement: Every reconciled version-4 attempt has one authoritative terminal event

The harness SHALL record exactly one `event_type="provider_session"`, `action="provider_attempt_terminal"` occurrence for every reconciled headless provider attempt created under ledger schema version 4. The occurrence SHALL populate `events.provider_attempt_id`, use schema URI `urn:tdt:ai-harness:provider-attempt-audit:1`, and preserve reservation identity, terminal outcome, timing, authoritative usage, and available session identity.

#### Scenario: Successful attempt
- **WHEN** a reserved attempt returns a schema-valid structured result and authoritative usage
- **THEN** reconciliation records `succeeded` and the matching terminal event in one transaction

#### Scenario: Non-exception timeout
- **WHEN** the provider outcome has `timed_out=True` without raising
- **THEN** the attempt records `timed_out`, actual monotonic duration, and no fabricated result digest

#### Scenario: Provider exception
- **WHEN** invocation raises after reservation
- **THEN** the attempt records `failed`, bounded error classification, and harness-generated usage provenance

#### Scenario: Invalid structured result
- **WHEN** provider execution completes without schema-valid structured output and without an explicit process failure
- **THEN** the attempt records `invalid`
- **AND** the event claims no accepted artifact or revision

#### Scenario: Legacy terminal event
- **WHEN** a reader encounters a pre-v4 `provider_finished` event
- **THEN** it treats that occurrence as legacy terminal history
- **AND** does not require a version-4 terminal row for the old attempt

### Requirement: Ledger schema version 4 enforces terminal uniqueness

Schema version 4 SHALL add nullable `events.provider_attempt_id` and a unique partial index covering non-null provider-attempt IDs on provider-session events. Only authoritative version-4 terminal rows SHALL populate this column. Version-4 migration SHALL preserve all existing history and append-only triggers.

#### Scenario: New terminal uniqueness
- **WHEN** a second terminal event is inserted for the same provider attempt
- **THEN** the database uniqueness invariant rejects it

#### Scenario: Non-terminal provider event
- **WHEN** `provider_started` or session metadata is written
- **THEN** `events.provider_attempt_id` remains null and does not consume terminal uniqueness

#### Scenario: Legacy migration backfill
- **WHEN** schema-3 reconciled and reserved attempts are migrated
- **THEN** reconciled intent becomes `result_committed`, unreconciled intent becomes `unknown`, and legacy request/capability fields may remain null

#### Scenario: Legacy running stage without reservation
- **WHEN** post-migration recovery finds a schema-3 headless stage left running with no provider-attempt row
- **THEN** it records a bounded recovery event and returns the stage to pending without a terminal event or fabricated usage
- **AND** it retains the abandoned stage-attempt ordinal and uses a new ordinal on the next begin

#### Scenario: Chained migration from an older supported ledger
- **WHEN** initialization opens a supported schema-1 or schema-2 ledger
- **THEN** the existing validated migration reaches schema 3 before version-4 changes begin
- **AND** the guarded schema-3 backup and 3 -> 4 migration then run without losing legacy rows, triggers, or version metadata

#### Scenario: Unknown or inconsistent source version
- **WHEN** metadata and `PRAGMA user_version` disagree or identify an unsupported version
- **THEN** initialization fails before backup or mutation

#### Scenario: Repeated initialization
- **WHEN** an already migrated ledger is initialized again
- **THEN** migration is a no-op and existing data is unchanged

#### Scenario: Offline pre-migration prerequisite
- **WHEN** an operator deploys version-4 code against a schema-3 ledger
- **THEN** all schema-3 harness processes are stopped before first version-4 initialization
- **AND** mixed schema-3/schema-4 writers against one ledger are unsupported

#### Scenario: Pre-migration backup
- **WHEN** version-4 initialization opens a quiescent schema-3 ledger with no active/unexpired run lease
- **THEN** the harness holds an owner-only cross-process migration lock honored by every version-4 initializer/writer while a dedicated read connection with no active write transaction creates and verifies a WAL-consistent SQLite backup in a `0700` directory with a `0600` file under `$TDT_HOME/ai-harness/backups/`
- **AND** the backup connection closes before the guarded schema write transaction begins, while the external lock remains held through migration commit
- **AND** backup failure prevents migration without deleting any previously verified backup

#### Scenario: Active run prevents migration
- **WHEN** schema 3 contains an active unexpired lease
- **THEN** migration fails before backup or schema mutation and instructs the operator to quiesce the harness

#### Scenario: Backup cannot deadlock on its source transaction
- **WHEN** migration backup is created
- **THEN** the `Connection.backup()` source connection does not own `BEGIN IMMEDIATE`, `BEGIN EXCLUSIVE`, or another uncommitted write transaction
- **AND** concurrency/crash tests prove no schema-3 writer can write between verified backup completion and schema-4 commit

### Requirement: Invocation intent is durable before external execution

New headless begin SHALL atomically transition the current pending stage to running and reserve its provider attempt with the existing stage-request digest, digest kind, capability snapshot/digest, and `not_started` intent. The persisted request SHALL already contain finalized effective limits and SHALL be the exact request passed to the adapter without post-persistence mutation. Immediately before adapter invocation the harness SHALL atomically transition the reservation to `in_flight` and record its start timestamp.

#### Scenario: Reservation commits before start
- **WHEN** a headless stage is ready to invoke its provider
- **THEN** stage begin and durable request/capability reservation commit in one transaction before invocation can be marked `in_flight`

#### Scenario: Begin or reservation fails
- **WHEN** the atomic headless begin/reservation transaction fails
- **THEN** the stage remains pending, no attempt row exists, and no request slot is consumed

#### Scenario: Persisted request is invoked unchanged
- **WHEN** remaining policy determines effective token or cost limits for a headless attempt
- **THEN** those limits are finalized before `RunInputStore.save_stage_request()`
- **AND** the exact persisted request is passed to the adapter without replacement or mutation

#### Scenario: Crash before invocation start
- **WHEN** the process stops while intent is `not_started`
- **THEN** recovery distinguishes it from an invocation that may have reached the provider

#### Scenario: Response is lost
- **WHEN** recovery finds `in_flight` without reconciliation
- **THEN** the intent is non-terminal `unknown`, no terminal event exists, and no automatic retry occurs

### Requirement: Terminal reconciliation and event insertion are atomic and idempotent

One ledger operation SHALL prevalidate bounded terminal metadata, verify durable reservation identity, commit status/outcome/usage/session and `result_committed`, and insert the unique terminal event in one SQLite transaction. Equivalent replay SHALL return the existing record; conflicting replay SHALL raise `StateConflictError`.

#### Scenario: Event validation fails
- **WHEN** terminal metadata violates schema, bounds, or security policy
- **THEN** neither attempt reconciliation nor terminal insertion commits

#### Scenario: Equivalent replay
- **WHEN** a committed attempt is reconciled again with field-equivalent authoritative terminal data under the canonical D6 comparison
- **THEN** the existing record and original `audit_event_id` are returned without generating or comparing a new event ID, another event, or another usage count

#### Scenario: Conflicting replay
- **WHEN** replay differs in outcome, usage, session, digest, capability identity, timing, or error classification
- **THEN** reconciliation fails closed and preserves the first terminal record

### Requirement: Intent and terminal outcomes use distinct closed vocabularies

Intent state SHALL be one of `not_started`, `in_flight`, `unknown`, or `result_committed`. Terminal outcome SHALL be one of `succeeded`, `invalid`, `failed`, `timed_out`, `cancelled`, or `interrupted`. `unknown` SHALL NOT be a terminal outcome and SHALL NOT create a terminal event.

#### Scenario: Confirmed cancellation
- **WHEN** trusted recovery supplies bounded adapter-confirmation evidence for an abandoned attempt
- **THEN** terminal outcome is `cancelled`
- **AND** ordinary engine execution never synthesizes this outcome without that evidence

#### Scenario: Conclusive recovery interruption
- **WHEN** recovery policy conclusively closes an abandoned attempt without a provider result
- **THEN** terminal outcome is `interrupted` exactly once

#### Scenario: Uncertain abandoned attempt
- **WHEN** recovery cannot determine whether external execution completed
- **THEN** intent remains `unknown` and unreconciled

#### Scenario: Late result after unknown
- **WHEN** the original invocation supplies valid terminal data after recovery marked the attempt `unknown`
- **THEN** the same attempt may transition to `result_committed` without another invocation or request charge

#### Scenario: Safe not-started resume
- **WHEN** recovery finds `not_started` with its exact persisted request and no invocation-start record
- **THEN** it may transition that same attempt to `in_flight`
- **AND** it does not create another reservation or consume another request slot

### Requirement: Audit schemas and digest profiles are immutable and explicit

Terminal payloads SHALL resolve through the packaged local registry for `urn:tdt:ai-harness:provider-attempt-audit:1`. Readers SHALL preserve unknown-schema payloads opaquely or return an explicit unsupported result. Request digests SHALL reuse the exact persisted request bytes with digest kind `sha256:run-input-store-stage-request-v1`; validated structured-result digests SHALL use kind `sha256:stage-result-project-json-v1` and the documented project canonical JSON profile and SHALL NOT be described as RFC 8785/JCS. Capability snapshots SHALL use schema `urn:tdt:ai-harness:provider-capabilities:1`, contain the adapter name and every explicit boolean `ProviderCapabilities` field from the single shared probe result, exclude runtime/environment text, and hash the exact compact sorted UTF-8 bytes with one trailing newline.

#### Scenario: Known audit schema
- **WHEN** a version-1 terminal payload is read
- **THEN** the local registry selects its exact immutable validator

#### Scenario: Unknown audit schema
- **WHEN** a reader encounters an unrecognized schema URI
- **THEN** it does not parse it as version 1 or mutate its payload

#### Scenario: Existing request digest
- **WHEN** a terminal event references a request
- **THEN** it stores the digest produced by `RunInputStore.save_stage_request()` without recomputation
- **AND** the persisted bytes represent the exact request passed to the adapter

#### Scenario: Deterministic structured-result digest
- **WHEN** equivalent supported JSON-native result values have different mapping insertion order
- **THEN** the documented project profile produces identical bytes and SHA-256 digest

#### Scenario: Deterministic capability digest
- **WHEN** equivalent complete capability snapshots have different mapping insertion order
- **THEN** the documented capability profile produces identical bytes and SHA-256 digest
- **AND** missing, unknown, non-boolean, or protected fields are rejected

### Requirement: Provider execution and artifact acceptance remain separate

A provider-attempt terminal event SHALL describe provider execution only. Later mandatory validation, artifact materialization, revision acceptance, and stage transition SHALL remain separate records correlated by `provider_attempt_id`.

#### Scenario: Provider succeeds but validation rejects
- **WHEN** provider execution succeeds but harness validation rejects its result
- **THEN** provider outcome remains `succeeded`
- **AND** a bounded correlated rejection event is committed with no accepted revision
- **AND** the run remains active, the consumed attempt and request budget remain counted, and the stage returns to pending for a new attempt

#### Scenario: Rejection cleanup is interrupted
- **WHEN** a terminal result exists but acceptance and its rejection-state transition do not commit
- **THEN** restart recovery detects the running stage, terminal attempt, and missing accepted revision
- **AND** it returns the stage to pending without invoking the provider again

#### Scenario: Accepted revision
- **WHEN** the result passes all validation
- **THEN** the accepted revision references the same provider attempt

### Requirement: Payloads are bounded, secret-safe, and application-append-only

Terminal metadata SHALL pass existing depth, item, string, byte, and credential filters and SHALL exclude protected request/output content. SQLite triggers SHALL reject application updates/deletes, while documentation SHALL state that database replacement, schema alteration, and offline tampering are out of scope.

#### Scenario: Oversized or credential-like diagnostic
- **WHEN** provider-controlled text exceeds bounds or resembles a credential
- **THEN** the event stores only bounded classification and omission/redaction indicators or rejects before reconciliation

#### Scenario: Application mutation attempt
- **WHEN** application code attempts to update or delete a terminal event
- **THEN** SQLite rejects the mutation

#### Scenario: Security documentation
- **WHEN** operators review audit guarantees
- **THEN** documentation distinguishes transactional append-only behavior from cryptographic tamper evidence
