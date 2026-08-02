## Why

Shipping dispatch currently has concurrency gaps that can invoke the carrier more
than once, regress a terminal operation, or report an idempotency conflict for an
exact duplicate. The canonical local readiness wrapper also cannot prove that it
owns the Compose project it destroys or that every retained artifact belongs to
the same run, so a passing or cleanup result is not yet trustworthy.

## What Changes

- Make the Shipping-owned `dispatch_operations` ledger the concurrency authority
  for both HTTP and Nexus with durable leases, compare-and-swap transitions,
  retained results, reconciliation-before-retry, and an application-owned
  fingerprint/idempotency contract.
- Qualify the handler Workflow ID with the operation fingerprint and explicitly
  use Temporal's running-workflow `USE_EXISTING` and closed-workflow
  `ALLOW_DUPLICATE` policies so exact concurrent duplicates attach while
  different requests never share a Workflow execution.
- Preserve the hexagonal boundary: Temporal/Nexus, PostgreSQL, HTTP, and carrier
  details remain adapters; the application port exposes only provider-neutral
  claim outcomes and typed errors; the Shipment aggregate remains the owner of
  lifecycle invariants and events.
- Make the shared local carrier stub safe under concurrent API and Worker use,
  and add race/concurrency coverage for exact duplicates, conflicting
  fingerprints, recovery, and terminal-state immutability.
- Register a redacted Shipping database readiness/startup check while keeping
  liveness independent of database and remote Kafka, Debezium, Temporal, and
  Nexus state.
- Give each canonical Compose-readiness invocation one collision-resistant run
  identity and one isolated project; bind preflight to that exact project, mark
  ownership only after absence is proven, clean up only owned resources, and
  treat cleanup failure as a failed run.
- Carry the exact run and Compose-project identity through smoke, Worker,
  Workflow, Shipping-pilot, acceptance, and cleanup evidence. Reject missing,
  stale, cross-project, or cross-run evidence instead of selecting a globally
  newest artifact.
- Correct canonical specification drift: Shipping owns the
  `dispatch_operations` table, the durable ledger rather than a Shipment column
  governs replay, and successful HTTP replay preserves the retained `201`
  response.
- Keep the work local and self-hosted. Staging, production, Argo CD convergence,
  cloud authorization, registry publication, and hosted rollback evidence remain
  deferred to `complete-cloud-deployment-and-cicd-readiness`.

Goals are one logical carrier effect, one aggregate transition, one outbox fact,
safe project lifecycle, and run-bound local evidence under retries, crashes, and
concurrency. Non-goals are exactly-once network invocation, replacing Kafka with
Nexus, sharing domain types between contexts, adding remote dependencies to API
readiness, or promoting cloud readiness.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `temporal-nexus-contracts`: Define fingerprint-qualified Workflow identity,
  exact-duplicate attachment, durable operation claims, lease recovery,
  terminal-state immutability, and the boundary between logical-effect
  guarantees and at-least-once provider calls.
- `shipping-service`: Make the dispatch ledger authoritative across HTTP and
  Nexus, correct schema/replay requirements, define concurrent public behavior,
  and require a concurrency-safe local carrier adapter.
- `platform-health`: Require Shipping database checks for readiness and startup,
  with dependency-free liveness and redacted failure responses.
- `local-compose-operational-readiness`: Require proven project ownership,
  fail-closed cleanup, run-scoped evidence, and exact identity validation across
  all retained artifacts.
- `local-development-orchestration`: Require collision-resistant isolated
  projects, exact-project preflight, per-run evidence mounts, and safe concurrent
  local invocations.
- `local-service-verification`: Require real concurrent Shipping operations and
  evidence-isolation acceptance with side-effect, aggregate, and outbox counts.

## Impact

Affected ownership boundaries are Shipping application/domain code and its
PostgreSQL schema, Shipping HTTP and Temporal/Nexus adapters, the local carrier
adapter, platform health registration, Compose orchestration scripts, smoke and
acceptance evidence schemas, and their tests and runbooks. Order remains a
caller through the producer-owned Nexus contract; Kafka and Debezium remain the
provider-owned fact path.

The database change is additive and requires a forward migration for lease and
attempt metadata. Public Protobuf payloads remain compatible. HTTP error mapping
adds stable conflict/in-progress/retryable responses but preserves the retained
success status/body. The pinned Go SDK and self-hosted Server versions remain
unchanged; implementation must use their documented policy semantics.

Rollout starts with the additive migration and compatible readers, then enables
claim/CAS behavior, explicit Workflow policies, health checks, and run-bound
evidence validation. Rollback first stops new Nexus starts, drains or cancels
in-flight operations, reverts application routing and validation code while
leaving additive columns in place, and never destroys a project whose ownership
was not proven.
