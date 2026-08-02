## MODIFIED Requirements

### Requirement: Nexus handlers are at-least-once and idempotent

Every mutating handler SHALL tolerate duplicate delivery. The caller SHALL
provide a stable operation identity and business key, and the producer SHALL
persist a canonical request fingerprint, state, lease ownership, attempt
metadata, and retained result in its own database. The database operation
ledger SHALL be the correctness authority shared by HTTP, Temporal Activities,
and Nexus. Long-running handlers SHALL use a deterministic Workflow ID formed
from the operation identity and full request fingerprint, with
`WorkflowIDConflictPolicy=USE_EXISTING` and
`WorkflowIDReusePolicy=ALLOW_DUPLICATE`. The platform SHALL guarantee one
logical provider effect, one aggregate transition, and one outbox fact for a
request fingerprint, but SHALL NOT claim exactly-once network invocation.

#### Scenario: Exact duplicate attaches while the first operation is running

- **WHEN** two Nexus starts use the same operation identity and canonical
  request fingerprint concurrently
- **THEN** both starts resolve to the same deterministic handler Workflow ID
- **AND** the second start attaches to the existing running Workflow
- **AND** the carrier, Shipment, and outbox each observe one logical effect

#### Scenario: Exact duplicate arrives after completion

- **WHEN** an operation with the same identity and fingerprint is delivered
  after the first handler Workflow has completed
- **THEN** a newly started handler consults the retained ledger outcome
- **AND** it returns the retained result without a carrier call, aggregate
  transition, or second outbox fact

#### Scenario: Identity is reused with different input

- **WHEN** an operation identity is reused with a different canonical request
  fingerprint
- **THEN** the ledger returns a typed non-retryable idempotency conflict
- **AND** the request performs no carrier call, Shipment mutation, or outbox
  append even if Temporal created a distinct Workflow execution

#### Scenario: Active lease is encountered

- **WHEN** a matching operation has a non-expired lease owned by another
  worker
- **THEN** the application returns a typed retryable `operation_in_progress`
  outcome
- **AND** the caller observes the documented retry interval

#### Scenario: Expired lease is recovered

- **WHEN** a matching operation lease is expired after a worker crash
- **THEN** one worker acquires a new opaque lease by compare-and-swap
- **AND** it calls provider lookup before issuing any new provider request

#### Scenario: Terminal outcome is immutable

- **WHEN** a stale worker attempts to update an operation already completed or
  definitively failed
- **THEN** the compare-and-swap rejects the stale transition
- **AND** the retained terminal result and outbox count remain unchanged

### Requirement: External effects use a recoverable transaction protocol

A mutating Nexus handler SHALL NOT hold a PostgreSQL transaction open across
an external network side effect. It SHALL first persist a pending operation
intent and a lease, call the external provider with a stable provider
idempotency key, and then atomically commit the aggregate transition, retained
result, and outbox fact through repositories bound to one transaction. Only
the current lease holder SHALL finalize or move an operation to reconciliation.
The protocol SHALL use provider lookup before retrying an unknown outcome and
SHALL preserve at-least-once recovery semantics.

#### Scenario: Provider succeeds and finalization commits

- **WHEN** the provider returns a successful dispatch result
- **THEN** the handler applies the result to the aggregate and commits the
  aggregate, operation result, and outbox fact in one transaction
- **AND** the Nexus operation completes only after that transaction commits

#### Scenario: Finalization fails after provider success

- **WHEN** the provider succeeds but the final database transaction fails
- **THEN** a later lease holder performs provider lookup using the same stable
  key before any execute request
- **AND** no second carrier dispatch is created

#### Scenario: Provider outcome is unknown

- **WHEN** the provider request times out without a definitive outcome
- **THEN** the operation enters a reconciling state under the current lease
- **AND** the handler does not claim failure, issue a new provider key, or
  publish a success fact until reconciliation completes

#### Scenario: External call is not held inside a database transaction

- **WHEN** a provider call is in progress
- **THEN** no PostgreSQL transaction remains open on behalf of that call
- **AND** the final transaction contains only the aggregate, ledger, and
  outbox commit

### Requirement: Nexus failures use a stable error taxonomy

The handler SHALL map contract/input rejection, authorization rejection,
fingerprint conflict, and domain invariant rejection to typed non-retryable
failures. It SHALL map transient infrastructure failures and active
operation ownership to typed retryable failures, unknown provider outcomes to
reconciliation, and compensation failures to a distinct operator-visible
outcome. Public failures SHALL NOT expose internal error strings, SQL details,
provider payloads, DSNs, or credentials.

#### Scenario: Domain rejects a command

- **WHEN** the application command violates a provider-owned invariant
- **THEN** the caller receives the documented non-retryable business error
- **AND** retry policy does not repeat the command

#### Scenario: Temporary infrastructure failure occurs

- **WHEN** the handler cannot reach a required local infrastructure dependency
- **THEN** it returns a typed retryable failure
- **AND** retry/circuit metrics identify the endpoint and Operation without
  sensitive details

#### Scenario: Operation is actively owned

- **WHEN** a matching operation has a non-expired lease held by another worker
- **THEN** the caller receives `operation_in_progress` as a retryable outcome
- **AND** the response contains no internal database or provider details

### Requirement: Nexus execution is correlated and observable

The platform SHALL expose operation latency, schedule-to-start latency,
execution failures, retries, duplicate attachments, fingerprint conflicts,
lease acquisition/expiry, provider lookup/execute results, reconciliation
state, terminal regressions rejected, and end-to-end outcomes. Logs, traces,
metrics, Workflow memo/search attributes, outbox envelopes, and retained
results SHALL propagate operation, canonical fingerprint, correlation, and
causation identities without payload secrets. Local evidence SHALL also carry
the exact readiness `run_id` and `compose_project` when an operation is part of
a Compose acceptance run.

#### Scenario: Operation completes

- **WHEN** a Nexus command commits successfully
- **THEN** the caller Workflow, handler Workflow, aggregate transaction, and
  Kafka fact are traceable through correlation and causation identities
- **AND** the evidence records the operation identity and exact run/project
  identity

#### Scenario: Duplicate or stale transition is rejected

- **WHEN** a duplicate request attaches or a stale lease CAS fails
- **THEN** the outcome and reason are recorded in metrics and structured logs
- **AND** no request payload or credential is emitted
