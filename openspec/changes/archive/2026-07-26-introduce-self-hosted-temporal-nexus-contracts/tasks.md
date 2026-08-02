## 1. Establish bounded-context and rollout evidence

- [x] 1.1 Create the canonical Order, Shipping, Payment, and Inventory context
  map, recording each context's owner, aggregates, ubiquitous language,
  commands, published facts, upstream/downstream relationships, and
  anti-corruption mappings.
- [x] 1.2 Add or update the owning ADR with the command/fact/query decision
  table: Nexus for selected cross-context durable commands, Kafka outbox
  events for facts, and owned HTTP/read projections for ordinary requests and
  queries.
- [x] 1.3 Inventory every Temporal Workflow, Activity, client, and worker
  package by driving or driven adapter role; enumerate the legacy
  `internal/application/orchestration` exceptions that this change freezes
  from expansion.
- [x] 1.4 Record the first Shipping dispatch contract's provider vocabulary,
  authoritative business key, caller-to-provider mapping, and the decisions
  needed for idempotency retention and carrier reconciliation.

## 2. Make architecture enforcement trustworthy

- [x] 2.1 Change the shared architecture validator to match forbidden import
  prefixes, not only exact module paths, and to recognize the repository's
  actual `internal/domain`, `internal/application`, `internal/adapters`, and
  contract roots.
- [x] 2.2 Make each architecture suite report the packages and files scanned
  and fail when a configured layer, service, or cross-service rule has zero
  scan coverage.
- [x] 2.3 Add planted negative fixtures for a Temporal SDK subpackage, HTTP
  and circuit-breaker imports in application code, generated peer DTOs in
  domain/application code, a peer `internal` import, and a misplaced
  transaction/outbox adapter; assert actionable diagnostics for each.
- [x] 2.4 Replace Shipping's incorrect `domain` and `application` scan roots
  with its real `internal/...` roots, and make the cross-service architecture
  test assert the complete service inventory.
- [x] 2.5 Run the platform and per-service architecture suites, preserve
  unrelated baseline failures separately, and retain evidence that removing a
  planted fixture turns every formerly false-positive suite green.

## 3. Restore the affected hexagonal boundaries

- [x] 3.1 Define purpose-named, transport-neutral application ports and
  application DTOs for Shipping dispatch, carrier execution, transaction
  scope, idempotency, outbox persistence, and time.
- [x] 3.2 Move the affected Order fulfillment HTTP/Protobuf clients and
  circuit-breaker construction out of `internal/application/clients` into
  driven adapters, keeping the existing application-facing behavior behind
  the new ports.
- [x] 3.3 Move the touched Shipping Temporal Workflow, Activity,
  registration, and Nexus wrapper code under `internal/adapters/temporal`;
  keep orchestration decisions in application handlers without importing
  Temporal or Nexus SDK types.
- [x] 3.4 Map caller domain/application values to producer-owned integration
  contracts in the caller adapter and map provider contract values to
  Shipping application commands in the handler adapter.
- [x] 3.5 Add application tests using in-memory ports that exercise the
  affected Order and Shipping use cases without Temporal, Nexus, HTTP, Kafka,
  PostgreSQL, carrier SDKs, or generated peer contract types.

## 4. Repair Shipping domain and transaction correctness

- [x] 4.1 Strengthen the Shipping aggregate to reject invalid address,
  carrier, and lifecycle transitions, including cancellation after delivery;
  pass time explicitly and have aggregate methods record the domain events
  caused by accepted state changes.
- [x] 4.2 Redesign the PostgreSQL unit of work so its repositories,
  idempotency store, and outbox writer are created from and cannot escape the
  same transaction handle.
- [x] 4.3 Add the Shipping operation-intent and retained-result persistence
  needed for pending, completed, failed, and reconciling states, including
  operation identity, business key, contract version, request fingerprint,
  provider idempotency key, result, and retention metadata.
- [x] 4.4 Implement the first short transaction that validates the command,
  claims or replays the operation identity, and atomically persists pending
  aggregate state and operation intent before any carrier call.
- [x] 4.5 Execute the carrier side effect outside a database transaction,
  reusing a provider idempotency key derived from the stable operation
  identity on every retry.
- [x] 4.6 Implement the final short transaction that reloads and transitions
  the aggregate and atomically commits aggregate state, retained operation
  result, and a versioned outbox record derived from the aggregate's domain
  events.
- [x] 4.7 Replace the logging-only event Activity with real outbox
  persistence and make failure observable to the Workflow; do not acknowledge
  successful dispatch before the final transaction commits.
- [x] 4.8 Implement provider result lookup or a provider-specific
  reconciliation ledger for unknown outcomes, and prevent another carrier
  side effect until reconciliation resolves the operation.
- [x] 4.9 Add container-backed crash-boundary tests for failure before the
  carrier call, after provider success, during final commit, during outbox
  publication, and during duplicate delivery; prove one retained outcome and
  no second side effect.

## 5. Define and implement the Nexus contract boundary

- [x] 5.1 Define the producer-owned Protobuf request/response contract for the
  versioned Shipping dispatch operation with operation, business,
  correlation, causation, actor-reference, contract-version, result, and
  stable error fields, but no credentials, private domain types, Namespace,
  Task Queue, or Workflow type.
- [x] 5.2 Generate and validate the Buf artifacts, enable compatibility
  checks, and document the stable endpoint, Service, and Operation naming
  owned by Shipping.
- [x] 5.3 Define versioned durable Workflow DTOs that are independent of
  Shipping aggregate structs and integration-event types, with explicit
  mapping tests and Event History replay fixtures.
- [x] 5.4 Implement the collocated Shipping Nexus handler as a driving
  adapter backed by the owned handler Workflow and application command; use a
  business-meaningful Workflow ID and duplicate rejection plus the
  database-backed idempotency record.
- [x] 5.5 Map invalid contracts and domain rejections to typed
  non-retryable failures, transient infrastructure failures to retryable
  failures, unknown provider outcomes to reconciliation, and compensation
  failures to visible operational outcomes without exposing internal errors.
- [x] 5.6 Keep any synchronous handler below the documented 10-second
  deadline and use the asynchronous Workflow-backed operation for dispatch;
  propagate cancellation and test the documented termination/orphan risk.
- [x] 5.7 Implement the Order Nexus caller as a driven adapter with bounded
  timeout, retry, and circuit policy, referencing only endpoint, Service,
  Operation, and contract version.
- [x] 5.8 Add contract and integration tests for supported and unsupported
  versions, request-fingerprint conflict, replayed result, retry, timeout,
  cancellation, termination, worker unavailability, and correlation
  propagation.

## 6. Make route selection safe and reversible

- [x] 6.1 Select the Nexus or existing HTTP/Activity route once per operation
  identity behind an environment- and cohort-scoped flag, and persist enough
  routing evidence to keep retries on the same path.
- [x] 6.2 Reject any attempt to execute a mutating dispatch through both
  routes; restrict shadow comparison to serialization and isolated
  non-mutating canary checks.
- [x] 6.3 Add tests proving retries, restarts, flag changes, and circuit
  transitions cannot switch an in-flight operation to the other route or
  produce two carrier calls.
- [x] 6.4 Implement rollback controls that stop new Nexus starts, expose and
  drain or cancel in-flight operations, then re-enable the HTTP path without
  changing REST, Kafka, or existing Workflow contracts.

## 7. Enable self-hosted Nexus callback and endpoint lifecycle

- [x] 7.1 Update Temporal Server 1.31.2 Compose configuration with the cluster
  HTTP address, `component.nexusoperations.useSystemCallbackURL: true`, a
  routable frontend HTTP port 7243, and separate gRPC and callback checks.
- [x] 7.2 Record Kubernetes, cloud, staging, and production callback routing,
  probes, NetworkPolicies, and promotion evidence as deferred follow-up scope;
  local completion SHALL rely only on the Compose model and tested
  `linux/arm64` images.
- [x] 7.3 Implement environment-scoped, declarative endpoint bootstrap and
  reconciliation with idempotent create/update/list/delete behavior and exact
  missing, extra, and mismatched-target drift reporting.
- [x] 7.4 Require drain evidence before changing or deleting an active
  Namespace/Task Queue target, and make partial reconciliation safely
  repeatable.
- [x] 7.5 Add registry and callback integration tests for bootstrap reruns,
  missing targets, unreachable callbacks, active-target drift, interrupted
  reconciliation, and deletion after drain.
- [x] 7.6 Add an isolated, non-mutating Nexus canary operation for
  non-production convergence validation; health and deployment checks must
  never invoke a mutating business operation.

## 8. Enforce self-hosted authentication and authorization

- [x] 8.1 Label the Compose no-op profile as insecure and local-only, retain
  fail-closed validation for incomplete non-local TLS, caller identity,
  ClaimMapper, Authorizer, certificate, and secret-injection configuration,
  and defer deployment of those non-local components.
- [x] 8.2 Reject staging and production deployment validation when the
  default no-op Authorizer or an incomplete identity policy is active; expose
  no-op mode only through a clearly labeled local development profile.
- [x] 8.3 Enforce the local acceptance caller Namespace-to-endpoint policy and
  re-evaluate Shipping-owned business authorization in the handler using a
  validated actor reference; do not represent the local harness as a deployed
  Temporal Authorizer.
- [x] 8.4 Add local allow/deny integration tests for caller Namespace,
  endpoint, unauthorized business actors, mismatched codec profiles, and
  redacted diagnostics. Invalid/expired credential testing is deferred with
  non-local identity deployment.
- [x] 8.5 Verify compatible default payload converter and codec profile
  configuration on local caller and handler workers. Encrypted-key rotation
  and historical replay under non-local codecs are deferred.

## 9. Separate readiness, dependency health, and deployment convergence

- [x] 9.1 Advertise Nexus operations explicitly and register the Shipping
  handler and poller on the provider's existing task queue with a bounded
  worker stop timeout and build identity.
- [x] 9.2 Fail provider readiness when an advertised local handler,
  registration, poller, task queue, or callback route cannot serve; include
  exact failed components in redacted diagnostics.
- [x] 9.3 Report a caller's remote endpoint failure as degraded dependency and
  circuit state while keeping the caller ready when it can still accept work
  and apply its configured fallback or durable-retry policy.
- [x] 9.4 Validate endpoint existence, declared target, authorization, canary
  callback, and poller convergence as deployment state separate from runtime
  readiness.
- [x] 9.5 Emit structured logs, traces, and metrics for schedule-to-start and
  execution latency, retries, duplicate detection, reconciliation,
  cancellation, failures, endpoint/circuit state, operation identity,
  contract version, and Worker build without payload secrets.
- [x] 9.6 Add outage tests proving provider-local faults fail provider
  readiness, remote faults degrade callers without a readiness cascade, and
  recovery closes the circuit and restores deployment convergence.

## 10. Validate, document, and stage the pilot

- [x] 10.1 Document the context map, port/adapter classification, durable
  payload mapping, transaction protocol, error taxonomy, four version
  dimensions, idempotency retention, carrier reconciliation, cancellation,
  and termination/orphan behavior in the owning ADRs and runbooks.
- [x] 10.2 Document endpoint bootstrap, drift remediation, TLS and Authorizer
  rotation, callback networking, canary use, route selection, drain, and
  rollback procedures.
- [x] 10.3 Run `make -C platform verify`,
  `make -C services/shipping-service verify-pr`, and
  `make -C services/order-service verify-pr`; identify unrelated baseline
  failures separately and retain the focused architecture, domain, contract,
  replay, duplicate, and crash-test evidence.
- [x] 10.4 Run `make validate-deployment` and the exact local Compose callback,
  endpoint, security, canary, and `linux/arm64` checks against the candidate
  worktree; retain its validation manifest. Kubernetes/cloud evidence is
  deferred.
- [x] 10.5 Deploy locally with Nexus invocation disabled, reconcile the
  endpoint, and pass callback, authorization-denial, duplicate, outage, drift,
  cancellation, and rollback acceptance tests in Docker Compose.
- [x] 10.6 Enable separate bounded synthetic Nexus and HTTP cohorts locally
  with one active route per operation, compare latency, duplicate, retry,
  reconciliation, and failure outcomes, and stop the local pilot
  automatically when agreed thresholds are exceeded.
- [x] 10.7 Verify no public REST route, Kafka topic/schema, existing non-Nexus
  Workflow contract, or source-of-truth ownership regressed before retaining
  approval evidence or proposing Payment and Inventory operations.
