## Context

The Shipping module already has a provider-owned Shipment aggregate, a
`dispatch_operations` ledger, HTTP and Nexus entry points, a PostgreSQL
unit-of-work abstraction, a carrier port, and an outbox-to-Debezium-to-Kafka
fact path. The current handler reads and creates an operation without a
durable claim, calls the carrier outside the transaction, and finalizes by
operation ID alone. Under concurrent delivery this permits duplicate provider
calls or a terminal-state regression. The local stub is shared by the API and
Worker but is not synchronized.

The local readiness wrapper starts and cleans a caller-selected Compose project
while scanning shared artifact roots for the newest report. Its preflight does
not prove that the project was absent before startup, and the artifact schemas
do not carry one identity through smoke, worker, workflow, pilot, acceptance,
and cleanup. This makes unrelated local work capable of being deleted or
mistakenly accepted as evidence.

The accepted Nexus ADR requires Shipping to own its state and facts, with
Nexus/Temporal, HTTP, PostgreSQL, Kafka, and carriers behind adapters. It also
requires local readiness to remain separate from hosted deployment evidence.
The implementation must retain the pinned Shipping Go SDK `v1.46.0`, pgx
`v5.10.0`, and self-hosted Temporal Server `v1.31.2`; no dependency upgrade is
needed for this change. Current official SDK documentation states that
workflow-backed Nexus operations require deterministic IDs, default to a
running-workflow conflict of `Fail`, and support `USE_EXISTING` to attach
callers. `WorkflowIDReusePolicy` defaults to `ALLOW_DUPLICATE`. Temporal Server
`v1.31.0` removed the Nexus feature flag and made Nexus enabled by default;
`v1.31.2` is the retained patch pin.

## Goals / Non-Goals

**Goals:**

- Make the Shipping ledger the durable concurrency and idempotency authority
  shared by HTTP, legacy Temporal Activities, and Nexus.
- Guarantee one logical carrier effect, one Shipment transition, and one
  committed dispatch outbox fact for a request fingerprint, while explicitly
  retaining at-least-once provider invocation and recovery semantics.
- Preserve DDD and hexagonal boundaries, provider-owned vocabulary, contract
  versioning, typed errors, and Kafka/Debezium fact ownership.
- Make the local carrier stub race-safe and observable under concurrent use.
- Fail readiness when Shipping cannot reach its database while keeping liveness
  independent of dependency state and keeping remote Nexus/Kafka state out of
  process readiness.
- Make local Compose lifecycle ownership and evidence identity explicit,
  collision-resistant, run-scoped, and safe for concurrent invocations.
- Produce implementation and acceptance tests that exercise real HTTP,
  Temporal/Nexus, PostgreSQL, Kafka, and CDC behavior.

**Non-Goals:**

- Exactly-once carrier network invocation; a crash after an external request
  can require a retry with the same provider idempotency key.
- Replacing Kafka/Debezium facts with Nexus, moving all Temporal code, or
  sharing private domain types or database tables across contexts.
- Adding a distributed lock service, PostgreSQL advisory lock protocol, or
  process-local singleflight as the correctness mechanism.
- Making remote Temporal, Nexus, Kafka, Debezium, or cloud deployment
  convergence part of API liveness/readiness.
- Changing public Protobuf versions, current runtime pins, or claiming staging
  or production readiness.

## Decisions

### 1. Durable claim protocol is application-owned

Shipping adds an additive migration for `dispatch_operations` lease metadata:
an opaque `lease_token`, `lease_expires_at`, and `attempt_count`. The
application ports expose provider-neutral claim outcomes such as `execute`,
`replay`, `in_progress`, `reconcile`, and `fingerprint_conflict`; they do not
expose pgx, SQL, Temporal, or Nexus types.

The initial claim and fallback reload occur in short PostgreSQL transactions:

1. Validate the command and compute one canonical request fingerprint.
2. Insert the Shipment and pending operation together when the operation is
   absent. `INSERT ... ON CONFLICT DO NOTHING` is the database arbiter.
3. If a concurrent insert wins, roll back the losing transaction's redundant
   Shipment and reload the existing operation in a fresh transaction.
4. For a matching non-terminal operation, acquire a new opaque lease only when
   the current lease is expired; use a compare-and-swap predicate on operation
   ID, expected non-terminal state, and prior token.
5. Treat a live matching lease as `in_progress`; treat a live different
   fingerprint as a typed conflict.

No transaction remains open during carrier I/O. The carrier request uses the
stable `shipping-dispatch/<operation-id>` provider key. Unknown outcomes first
enter `reconciling` and always call `LookupDispatch` before a new execute. Only
the holder of the current lease token can mark reconciling, complete, or
record a definitive failure. Completion atomically updates Shipment,
`dispatch_operations`, and the versioned outbox record. Terminal outcomes are
immutable. The lease TTL is configured longer than the bounded provider call
plus recovery margin and is measured/alerted rather than used as a hidden
exactly-once guarantee.

This is preferred over advisory locks because a database transaction or session
lock cannot span external I/O safely; over an in-memory singleflight because it
does not coordinate processes or survive crashes; and over a version-only CAS
because an opaque lease token makes stale-worker ownership explicit.

### 2. Nexus identity separates exact duplicates from conflicts

The Nexus handler remains a driving adapter and maps the versioned request to
the same application command as HTTP. It starts a Workflow with:

`shipping-dispatch/<operation-id>/<full-canonical-fingerprint>`

and explicitly sets `WorkflowIDConflictPolicy=USE_EXISTING` and
`WorkflowIDReusePolicy=ALLOW_DUPLICATE`. Thus concurrent identical requests
attach to one running Workflow, while a different fingerprint never attaches
to the same execution. A completed duplicate may start a fresh Workflow, but
the ledger returns the retained result without a provider call. A conflicting
request is rejected by the ledger with a typed non-retryable error.

The route, endpoint, namespace, task queue, and SDK options stay in the
adapter. Operation identity, canonical fingerprint, provider key, and error
taxonomy stay in the application contract. Retryable infrastructure,
`in_progress`, and reconciliation errors remain retryable; contract,
authorization, fingerprint, and domain errors remain non-retryable. Workflow
memo/search attributes carry only redacted operation, correlation, causation,
route, and fingerprint identifiers.

This policy follows the current Go SDK contract:
[WorkflowRunOperation](https://github.com/temporalio/sdk-go/blob/v1.46.0/temporalnexus/operation.go)
documents deterministic IDs and `USE_EXISTING`, while
[StartWorkflowOptions](https://github.com/temporalio/sdk-go/blob/v1.46.0/internal/client.go)
documents `ALLOW_DUPLICATE` as the reuse default. The self-hosted pin remains
compatible with Nexus being always enabled from Temporal Server 1.31.0 onward;
the local callback and authorization settings remain deployment configuration,
not domain behavior.

### 3. Shared adapters and health retain boundary ownership

`carrier.StubAdapter` receives a `sync.RWMutex`; every read, write, and
snapshot is protected, with private locked helpers preventing nested-lock
deadlocks. The port remains the only application dependency. Race tests cover
same-key execute, different-key execute, cancel, lookup, and snapshots.

Shipping runtime wiring registers a redacted `database` check backed by
`pgxpool.Pool.Ping` for readiness and startup. The health registry's liveness
handler remains dependency-free. Error bodies contain a generic database
failure category and no DSN, password, or host. Remote Nexus endpoint health,
Kafka, Debezium, and deployment convergence remain separately labeled evidence
and do not make an otherwise serving API fail readiness.

### 4. Compose ownership is proven before cleanup

The readiness wrapper creates a run ID from UTC time, PID, and cryptographic
randomness. It derives a unique, label-safe Compose project and passes both
`VALIDATION_RUN_ID` and `VALIDATION_COMPOSE_PROJECT` to every preflight and
validation call. The project starts with `owned=false`; ownership becomes true
only after exact preflight proves no matching containers, networks, or volumes
existed. An operator-provided project name is accepted only when the same
absence check passes.

Cleanup is project-scoped and runs on every exit. It removes resources only
when owned, records `removed`, `retained-by-request`,
`skipped-not-owned`, or `failed`, and makes cleanup failure fail the overall
run even when the workload passed. `KEEP_READINESS_STACK=true` records
`retained-by-request` without destructive cleanup. The outer summary is written
after cleanup so the result includes cleanup status.

### 5. Evidence is run-scoped and validated by exact identity

The wrapper creates a per-run evidence directory and bind-mounts it into
containers through `COMPOSE_RUN_EVIDENCE_DIR`. Smoke, Worker, Workflow,
Shipping-pilot, and acceptance manifests all include `schema_version`,
`run_id`, `compose_project`, and the operation cohort. Filenames include the
exact run ID; the acceptance validator receives explicit paths and never
searches a shared root for the newest file. Every referenced artifact must
match both identities and freshness constraints. Missing or mismatched
identity is a hard failure, not a warning.

The existing evidence class distinction remains: focused Nexus pilot evidence
cannot satisfy the canonical eight-service readiness gate. Cloud and hosted
artifacts are not inputs to this local contract.

### 6. Migration, observability, and compatibility

The additive migration is backward-compatible with readers that ignore the new
columns. Metrics and logs include operation ID, route, claim outcome, lease
age, attempt count, provider lookup/execute result, duplicate/conflict count,
and cleanup outcome without payload values. Outbox versioning remains unchanged
and Kafka delivery remains at-least-once.

The implementation changes HTTP status mapping only for new stable outcomes:
exact replay keeps the retained `201` response/body; fingerprint conflict is
`409`; active work is `409` with `Retry-After`; reconciliation and transient
infrastructure use a documented retryable status. Existing typed validation,
authorization, not-found, and domain responses remain compatible.

All local images must be verified for `linux/arm64` and `linux/amd64` by
preflight. If an image lacks native arm64 support, the acceptance manifest must
record the explicitly approved emulation fallback and its performance trade-off;
no silent image substitution is permitted.

## Risks / Trade-offs

- **[Risk]** A process can crash after the carrier accepts a request but before
  finalization. → **Mitigation:** stable provider key, lease expiry,
  lookup-before-execute reconciliation, and integration tests that inject the
  crash window.
- **[Risk]** A lease TTL shorter than provider latency permits a second worker to
  claim. → **Mitigation:** configure TTL above the bounded call plus margin,
  expose lease-age metrics, and test slow-provider behavior.
- **[Risk]** `ALLOW_DUPLICATE` permits a new Workflow after completion. →
  **Mitigation:** the database ledger, not Temporal history, is the result
  authority; completed duplicates are replayed without provider I/O.
- **[Risk]** A conflicting fingerprint creates a distinct Workflow before the
  ledger rejects it. → **Mitigation:** the first application claim is
  side-effect-free and returns a typed non-retryable conflict; tests assert no
  carrier, aggregate, or outbox mutation.
- **[Risk]** Run-scoped evidence directories increase artifact volume. →
  **Mitigation:** retain only the manifest and failure diagnostics by policy,
  and record cleanup status without deleting retained evidence.
- **[Risk]** Concurrent local readiness runs consume workstation resources. →
  **Mitigation:** preflight checks resource budget, project names are unique,
  and the acceptance suite includes two concurrent invocations.
- **[Risk]** The existing legacy operation schema or callers assume a
  `shipments.operation_id` column. → **Mitigation:** inventory and update all
  readers in one migration, add compatibility tests, and keep the ledger as
  the sole source of idempotency truth.

## Migration Plan

1. Add and verify the additive Shipping migration and port/model changes while
   retaining read compatibility.
2. Deploy the claim/CAS path and concurrency tests; monitor duplicate,
   reconciliation, lease-expiry, and terminal-regression metrics.
3. Enable fingerprint-qualified Nexus Workflow IDs and explicit policies for
   new operation identities; drain existing identities before changing route.
4. Enable the database health check and run-scoped Compose evidence validator.
5. Run the focused and full local acceptance gates, including concurrent
   operations and two concurrent readiness invocations, and retain manifests.

Rollback stops new Nexus starts, drains or cancels in-flight operations, routes
new identities through the compatible HTTP/Activity path, and reverts only
application/validation code. Additive lease columns remain for forward
compatibility. A project is never reset unless this run proved ownership.

## Open Questions

- What production carrier reconciliation API and maximum provider latency
  should determine the initial lease TTL? The implementation must make the
  value configurable and use a conservative local default until the provider
  contract is supplied.
- Should the long-term retained-result policy use a fixed 90-day window or a
  domain-specific retention class? This change keeps the existing retention
  configuration and requires the expiry behavior to be observable.
- Which non-local Authorizer and callback routing configuration will the cloud
  change provide? This local change records the boundary but does not select or
  provision those credentials.
