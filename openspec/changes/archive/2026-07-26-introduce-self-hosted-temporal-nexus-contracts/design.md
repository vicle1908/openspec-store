## Context

The repository has a Temporal worker per service, an environment-scoped
namespace policy, PostgreSQL-owned aggregates/outbox records, and Kafka
publication through Debezium. The Order workflow currently coordinates several
peer operations through Activities and HTTP; participant Workflows exist but
are not yet the authoritative cross-service command boundary. Temporal Server
1.31.2 and the Go SDK 1.46.0 are the validated compatibility pair, and the
Nexus SDK is already present transitively, but self-hosted deployment does not
expose or verify the Nexus HTTP callback path, provision endpoints, or define a
non-local authorization policy.

The audit found four pre-existing correctness problems that are pilot blockers:

- Shipping opens a PostgreSQL transaction but obtains repositories from the
  pool, so aggregate, idempotency, and outbox writes are not transaction-bound.
- Shipping performs the carrier call while the nominal transaction is open,
  and its event-recording Activity logs rather than writes an outbox row.
- Durable Workflow inputs use private Shipping domain types, while Order peer
  HTTP/Protobuf clients live in the application layer.
- Architecture validation uses exact import matches and incomplete directory
  traversal, allowing declared layering rules to pass without checking the
  intended packages.

The design preserves DDD ownership: domain code remains unaware of Temporal,
Nexus, Kafka, task queues, and transport DTOs. A Nexus handler is an
inbound/driving adapter that translates a versioned integration contract into
an owned application command or handler Workflow. Nexus/HTTP clients,
PostgreSQL, Kafka, and carriers are outbound/driven adapters behind
application-owned ports. PostgreSQL remains the source of truth for aggregate
state and idempotency; Kafka remains the fact/event transport. Nexus provides
durable command invocation between Temporal contexts.

## Goals / Non-Goals

**Goals:**

- Provide a stable, versioned Nexus contract that hides target Namespaces,
  Task Queues, and Workflow implementation details from callers.
- Make bounded-context ownership and ubiquitous language explicit instead of
  assuming every deployable service is automatically a valid context.
- Restore the hexagonal inside/outside boundary for the affected Order and
  Shipping paths and make architecture tests prove it.
- Preserve domain invariants, domain-event ownership, transaction-bound
  repositories, and atomic integration-event outbox persistence.
- Make self-hosted callback routing, endpoint registration, authentication,
  authorization, health, deployment validation, and metrics testable.
- Define at-least-once delivery, duplicate handling, cancellation, timeout,
  retry, circuit-breaker, error taxonomy, and breaking-change behavior.
- Preserve the current one-namespace-per-environment and one-task-queue-
  per-service defaults while allowing later security-driven Namespace splits.
- Enable one reversible, collocated pilot after DDD, transaction, outbox, and
  architecture-enforcement prerequisites have been proven.
- Complete and retain acceptance evidence for the local Docker Compose
  environment while explicitly deferring cloud and Kubernetes deployment.

**Non-Goals:**

- Replacing Kafka outbox events, REST, or ordinary short-lived RPC and queries.
- Starting Nexus operations directly from Kafka consumers or public HTTP
  requests as a substitute for the existing command/Workflow starter.
- Standalone Nexus Operations, external URL targets, multi-cluster Nexus, or
  namespace-per-service migration.
- Sharing databases, private domain types, generated transport types, or
  Temporal Workflow types across contexts.
- Moving every legacy Temporal package in the repository in this change. New
  or modified Nexus code and the Shipping pilot use the corrected adapter
  boundary; remaining legacy orchestration locations are inventoried, frozen,
  and assigned to a follow-up migration.
- Choosing a dependency upgrade solely to introduce Nexus.
- Deploying or approving Kubernetes, cloud, staging, production, Argo CD,
  non-local TLS, or an organization-specific identity provider.

## Decisions

### 1. Define bounded contexts before transport contracts

A canonical context map records each context's owner, aggregates, ubiquitous
language, commands, published facts, upstream/downstream relationships, and
anti-corruption mappings. Order, Shipping, Payment, and Inventory are initial
entries, but physical service boundaries are evidence rather than the
definition of the contexts.

Nexus Service and Operation names use the provider context's language. Callers
translate their local model into the provider contract; they do not share
domain entities or attempt to create one platform-wide domain model.

### 2. Use Nexus selectively at the durable-command boundary

An existing Temporal Workflow invokes a versioned Nexus operation when the
operation belongs to another context and benefits from durable progress,
cancellation, and retry. Same-context work remains a child Workflow or
Activity. Kafka remains the asynchronous fact boundary, and HTTP remains the
fallback and the choice for ordinary request/response APIs.

Queries use an owned read API or projection. Nexus is not used as a query bus,
except for a deliberately short Workflow Query/Update messaging operation that
fits the documented synchronous deadline and has no aggregate mutation.

### 3. Make contracts producer-owned and isolate durable payloads

Each advertised operation has a producer-owned Protobuf request/response
contract under the canonical Buf layout. A platform-managed endpoint maps a
stable endpoint name, such as `shipping`, to the provider Namespace and Task
Queue. Callers reference endpoint, Service, Operation, and contract version
only; they do not reference the target Namespace, Task Queue, or Go Workflow
type.

Generated Protobuf and Nexus DTOs are integration types. The caller adapter
maps its local application/domain values into them, and the handler adapter
maps them into a provider-owned application command. Temporal Event History
contains versioned durable DTOs, not private aggregate structs or domain-event
types. The contract carries stable operation, correlation, and causation
identities but never credentials.

Breaking changes publish a new Service/Operation version and Task Queue. An
endpoint target change is drained and verified before switching because
in-flight and retried calls can otherwise be duplicated.

### 4. Treat every handler as at-least-once and idempotent

The caller supplies a stable operation identity and business key. The handler
uses a database-backed inbox/idempotency record and, for long-running work, a
business-meaningful Workflow ID with duplicate rejection. Aggregate mutation,
retained result, and outbox record commit atomically in the owning context. No
design claim of exactly-once execution is made.

Synchronous operations are bounded to the documented 10-second handler
deadline; longer work uses an asynchronous Workflow-backed operation.
Cancellation is preferred to termination because termination can orphan the
handler and bypass compensation.

### 5. Separate database transactions from external side effects

Shipping dispatch uses a recoverable state machine instead of holding a
database transaction across a carrier call:

1. A short transaction claims the operation identity and persists the pending
   aggregate and operation intent.
2. A retry-safe Activity calls the carrier outside the database transaction
   with a provider idempotency key derived from the operation identity.
3. A short transaction reloads the aggregate, applies the provider result, and
   atomically commits the aggregate, retained idempotency result, and versioned
   outbox record.

Repositories and outbox writers used inside a unit of work are constructed
from the same transaction handle. If the provider outcome is unknown, the
operation enters a reconciling state; it is not blindly retried with a new key
or compensated as though the provider definitely failed. Aggregate methods
enforce address, carrier, and lifecycle invariants, receive time explicitly,
and decide which domain events occurred. The outbound adapter maps domain
events to provider-owned versioned integration facts before the existing
JSON outbox serialization; private domain event structs are never serialized
directly.

### 6. Classify Temporal and Nexus as adapters

Nexus handlers and Temporal Workflow/Activity wrappers are driving adapters
under `internal/adapters/temporal`; HTTP handlers and Kafka consumers are other
driving adapters. HTTP/Nexus clients, PostgreSQL, Kafka producers, and carrier
implementations are driven adapters behind purpose-named application ports.
Application commands coordinate domain objects and ports but contain no
`net/http`, Nexus/Temporal SDK, Kafka/pgx SDK, circuit-breaker library, or
peer-generated transport DTO.

The Shipping pilot and affected Order fulfillment fallback clients migrate to
this boundary before enablement. Existing
`internal/application/orchestration` packages outside the touched path are
inventoried as explicit legacy exceptions: architecture validation prevents
expansion, and a follow-up change migrates them without coupling Nexus adoption
to a repository-wide rewrite.

### 7. Use collocated Nexus workers first

The handler and its Nexus poller run with the provider's existing Temporal
worker and Task Queue. A router queue is reserved for a later need for
independent scaling, IAM isolation, or a legacy worker that cannot be changed.
This follows Temporal's default collocated pattern and keeps ownership beside
the application command.

### 8. Make self-hosted Nexus explicit in local deployment

Docker Compose configures a routable Temporal frontend HTTP port 7243, the
cluster HTTP address, and
`component.nexusoperations.useSystemCallbackURL: true` for Server 1.31+. The
deployment exposes and health-checks that path, provisions endpoint definitions
idempotently, and reports registry drift. Endpoint bootstrap is declarative and
environment-scoped; it does not silently change a target while operations are
in flight.

Kubernetes and cloud equivalents are deferred and SHALL NOT be inferred from
local success.

### 9. Make local security explicit and fail closed outside local

The local Compose profile explicitly identifies Temporal's no-op Authorizer as
insecure and local-only. Configuration validation rejects staging or production
profiles unless an explicit ClaimMapper/Authorizer selection and secret-backed
TLS inputs are provided. The actual non-local plugin, certificate, secret, and
identity-provider deployment belongs to the deferred cloud-readiness change.

The local pilot uses one explicitly named default Temporal Data Converter
profile on caller and handler. Encrypted Payload Codec deployment, encryption
key rotation, and historical encrypted-payload replay are part of that same
deferred non-local security change; local profile-name compatibility is not
evidence that those controls are deployed.

Transport authorization does not replace business authorization. The handler
maps verified caller identity or a contract actor reference into application
authorization context and re-evaluates provider-owned rules before mutation.
Untrusted payload fields never become authentication claims.

### 10. Separate readiness, dependency health, and deployment validation

Handler readiness fails when its local Nexus registration, poller, Task Queue,
or callback route is not operational. A caller records a remote endpoint
failure as degraded dependency/circuit state but remains ready if it can still
accept traffic and apply fallback or durable retry policy; this avoids a remote
outage removing every caller replica from service.

Endpoint existence, declared target, authorization, and callback routability
are deployment-convergence checks. A health check never executes a mutating
business operation. Non-production end-to-end validation uses an isolated,
non-mutating canary contract or disposable test operation.

### 11. Keep error semantics inside the provider boundary

The handler maps input/contract rejection and domain invariant rejection to
typed non-retryable failures. Transient infrastructure and worker-unavailable
failures are retryable. Unknown external-provider outcomes enter
reconciliation. Compensation failures are distinct operational outcomes that
require visibility and possibly human intervention. Internal error strings,
database errors, and carrier payloads do not become public Nexus contracts.

### 12. Version four independent dimensions

Protobuf schema version, Nexus Service/Operation version, handler Workflow
implementation version, and Worker build/deployment version evolve
independently. A compatible schema addition does not force a new Service name;
an incompatible business contract does. Workflow patching and Worker
Versioning protect Event History replay and do not substitute for public
contract versioning.

### 13. Pilot Shipping behind a mutually exclusive fallback

Shipping dispatch is the first candidate because it is a natural durable
command boundary, but it is not enabled until its domain invariants,
transaction/outbox behavior, provider idempotency, and duplicate/replay tests
pass. The Order caller selects Nexus or the existing HTTP/Activity path once
per operation identity.

Rollback first prevents new Nexus starts, then drains or cancels in-flight
operations, then restores the HTTP path without changing Kafka contracts. A
mutating dispatch is never sent through both paths for comparison; shadow
validation is limited to encoding and non-mutating checks.

## Risks / Trade-offs

- **[Duplicate handler execution]** → Require stable operation IDs, inbox
  records, duplicate-rejecting Workflow IDs, and duplicate/crash tests.
- **[External side effect succeeds before database finalize]** → Persist an
  operation intent first, reuse one provider idempotency key, and reconcile
  unknown outcomes before applying another side effect.
- **[Callback routing is reachable locally but not in production]** → Expose
  7243 through Service/NetworkPolicy, add a non-mutating callback test, and fail
  deployment convergence when the route is unusable.
- **[Endpoint registry drift or unsafe target changes]** → Reconcile
  declaratively, report exact drift, and require drain evidence before target
  change.
- **[No-op authorization leaks privileged operations]** → Reject staging and
  production startup without explicit auth/authorizer configuration.
- **[Nexus becomes a replacement for Kafka]** → Enforce the command/fact/query
  decision table and require an outbox fact for observable state changes.
- **[Architecture gates pass without inspecting intended packages]** → Use
  package-aware prefix matching, exact layer roots, cross-service scans, and
  planted violation fixtures with actionable diagnostics.
- **[Remote outage causes a readiness cascade]** → Fail readiness only for
  local inability to serve the role; report remote state as degraded.
- **[Dual-path rollout duplicates carrier dispatch]** → Make routing mutually
  exclusive per operation identity and prohibit mutating shadow execution.
- **[Legacy Temporal placement remains inconsistent]** → Freeze enumerated
  legacy exceptions, migrate the pilot path now, and use a separate change for
  the remaining packages.
- **[Arm64 image mismatch]** → Verify each changed image for `linux/arm64` and
  document tested emulation only when unavoidable.

## Migration Plan

1. Land the context map, owning ADR, corrected architecture validator, and
   planted violation tests.
2. Move the affected Order peer clients and Shipping Temporal wrappers behind
   application-owned ports/adapters without changing public behavior.
3. Harden Shipping invariants, transaction-bound repositories, provider
   idempotency, reconcilable operation state, and atomic outbox; prove
   duplicate, crash-boundary, and replay safety.
4. Deploy the local self-hosted callback, explicit local security profile,
   endpoint bootstrap, readiness, and metrics changes with Nexus invocation
   disabled.
5. Provision the endpoint and run callback, local policy-denial, canary, and
   drift tests in Docker Compose.
6. Enable Shipping for bounded synthetic traffic with one active route per
   operation; compare outcomes across separate Nexus and fallback cohorts.
7. Retain local acceptance evidence. Rollback prevents new
   Nexus starts, drains/cancels in-flight operations, and enables the HTTP path.
8. Defer Kubernetes, cloud, staging, production, TLS/identity-provider
   deployment, and promotion evidence to a follow-up change.

## Open Questions

- What production identity provider and ClaimMapper implementation will be
  used, and where will its policy be versioned?
- Should endpoint definitions live beside deployment manifests or in a
  separate platform registry repository using the same reconciler?
- What is the Shipping pilot's authoritative business key and idempotency
  retention period?
- Does the selected carrier provide native idempotency and result lookup, or
  must its adapter implement a provider-specific reconciliation ledger?
- Which metrics backend and alert thresholds distinguish endpoint failure from
  temporary throttling?
