## Why

The platform is already on Temporal Server 1.31.2 and the Temporal Go SDK
1.46.0, which support Nexus, but the repository has no Nexus contracts,
endpoint lifecycle, callback routing, or self-hosted authorization model.
Repository audit also found that the proposed Shipping pilot does not yet have
a transaction-bound unit of work or a real atomic outbox, durable Workflow
payloads contain private domain types, peer HTTP clients live in the
application layer, and architecture tests can pass without scanning the
intended packages. Introducing Nexus before correcting those gaps would make
transport and Workflow details accidental domain APIs and would give false
assurance about aggregate ownership. We need a selective, contract-first
adoption path that makes bounded contexts explicit, restores the
inside/outside hexagonal boundary, preserves Kafka as the integration-event
backbone, and keeps ordinary HTTP for non-durable requests.

## What Changes

- Define Nexus as a durable command boundary used by an existing Temporal
  Workflow to invoke a versioned operation owned by another service or bounded
  context.
- Add an explicit context map for Order, Shipping, Payment, and Inventory that
  records ownership, ubiquitous language, commands, facts, upstream/downstream
  relationships, and anti-corruption mappings; a deployable service name alone
  SHALL NOT be treated as proof of a bounded context.
- Keep Kafka outbox events as the fact/event boundary and keep HTTP/gRPC for
  ordinary synchronous APIs and queries; do not make Nexus a universal
  replacement.
- Establish versioned Protobuf-backed Nexus service and operation contracts,
  stable endpoint ownership, handler workflow identity, at-least-once
  idempotency, timeout/cancellation, retry/circuit-breaker, and breaking-change
  rules.
- Re-establish hexagonal direction for the pilot: Nexus and Temporal handlers
  are driving adapters; HTTP/Nexus clients, Kafka, PostgreSQL, and carrier
  integrations are driven adapters; application commands and domain models
  remain transport-neutral.
- Repair architecture enforcement so import-prefix rules, real package
  traversal, and planted negative fixtures prove that the declared boundaries
  are actually checked.
- Gate the Shipping pilot on transaction-bound repositories, provider
  idempotency, domain invariants, and atomic aggregate/idempotency/outbox
  persistence. A Workflow logging an event is not an outbox implementation.
- Add self-hosted Nexus server configuration and lifecycle controls for
  local Docker Compose: routable HTTP callback traffic on port 7243,
  system callback URL configuration, endpoint provisioning, drift detection,
  readiness, and metrics.
- Make the local no-op authorization profile explicit and make configuration
  validation fail closed for any non-local profile. Deployment of mTLS,
  ClaimMapper/Authorizer plugins, secret injection, and non-local endpoint
  policy is deferred to a cloud-readiness change.
- Register and observe Nexus handlers only in services that advertise an
  operation, while keeping the existing one-namespace-per-environment and
  one-task-queue-per-service defaults.
- Pilot one collocated operation (prefer Shipping dispatch after its existing
  transaction, outbox, and idempotency paths are hardened), with an explicit
  single-active-path HTTP fallback and rollback switch. A mutating request
  SHALL never execute through Nexus and HTTP in parallel. Existing public
  REST, Kafka topics, and non-Nexus workflows remain compatible.
- Separate local readiness from remote dependency health: missing local
  handlers, pollers, or callback routing fail readiness, while a remote
  endpoint outage reports degraded dependency state without removing every
  otherwise healthy caller from service.
- Exclude standalone Nexus Operations, external-URL targets, multi-cluster
  Nexus, namespace-per-service migration, and wholesale replacement of the
  current Order saga.
- Exclude Kubernetes, cloud, staging, production, Argo CD, and managed-secret
  rollout evidence from this change. Those environments remain blocked until
  a follow-up change supplies their identity provider, TLS, policy, and
  deployment evidence.

## Capabilities

### New Capabilities

- `temporal-nexus-contracts`: Versioned Nexus service/operation contracts and
  DDD/hexagonal boundary rules for context ownership, callers, handlers,
  payloads, identities, transactions, idempotency, errors, timeouts,
  cancellation, retries, and evolution.
- `self-hosted-temporal-nexus`: Self-hosted server callback routing, endpoint
  registry/bootstrap, configuration, readiness, drift detection, and
  observability.
- `temporal-nexus-security`: Self-hosted Nexus authentication,
  authorization, endpoint access policy, and safe non-local defaults.

### Modified Capabilities

- `per-service-temporal-registration`: Services that advertise Nexus must
  register handlers/pollers and expose local registration failures through
  startup and readiness checks.
- `platform-health`: Health must distinguish local Nexus readiness,
  deployment-time registry validation, and runtime remote-dependency
  degradation.
- `platform-temporal-versioning`: Temporal versioning guidance must include
  independent contract, Service/Operation, Workflow implementation, and Worker
  build versions plus handler Workflow IDs, duplicate delivery, and the
  existing namespace-per-environment policy.
- `platform-hexagonal-enforcement`: Driving and driven adapters must be
  separated from transport-neutral application/domain code, integration
  contracts must be mapped through anti-corruption boundaries, transaction
  scopes must bind their repositories, and architecture tests must prove those
  rules with negative fixtures.

## Impact

- Affected services: Order as the initial caller; Shipping as the recommended
  pilot handler; Payment and Inventory as later candidates after their
  participant workflow and outbox correctness gaps are resolved.
- Affected DDD assets: a canonical context map and owning ADRs for the
  fulfillment relationships, commands, facts, ubiquitous language, and
  anti-corruption mappings.
- Affected platform areas: Temporal client/worker registration, Nexus contract
  adapters, application ports, HTTP fallback adapters, protobuf/Buf contract
  generation, architecture validation, health, metrics, structured logging,
  and integration-test harnesses.
- Affected deployment areas: `deploy/docker-compose.yaml`, local dynamic
  configuration, admin-tool/bootstrap jobs, local callback validation, and
  explicit local-only security configuration. Kubernetes and cloud manifests
  are not promoted by this change.
- Data ownership remains unchanged: each bounded context owns its aggregates
  and PostgreSQL transactions; Kafka remains at-least-once outbox CDC; Nexus
  does not create distributed transactions, shared tables, or cross-context
  domain imports.
- Compatibility impact is additive for existing REST/Kafka consumers. New
  Nexus endpoint and operation names are versioned public contracts; breaking
  changes use a new service/operation and task queue rather than in-place
  mutation.
- Rollout is local: repair and prove architecture enforcement, harden pilot
  domain/transaction correctness, deploy local callback/readiness controls,
  provision an endpoint, exercise separate bounded Nexus and HTTP cohorts, and
  prove rollback. Rollback disables new Nexus starts, drains or cancels
  in-flight operations, and returns to the existing HTTP/activity path;
  endpoint removal waits for all operations to drain. Non-local rollout is a
  separate follow-up.
- The architecture is durable intent. The currently validated Temporal
  Server/Go SDK versions are compatibility evidence, not a requested
  dependency upgrade.
