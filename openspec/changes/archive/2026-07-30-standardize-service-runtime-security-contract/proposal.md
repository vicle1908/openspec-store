## Why

The eight services do not expose one production-grade security configuration
contract: PostgreSQL, Kafka, Temporal/Nexus, peer HTTP, and OTLP support differ
by service, and several local-only plaintext or stub fallbacks can currently be
selected without a distinct non-readiness profile. A uniform, fail-closed
contract is required before a local stack can provide production-contract
readiness evidence or cloud manifests can safely consume the same settings.
Configuration validation and successful handshakes are necessary but are not
sufficient: each control must be proven while an authorized or unauthorized
workload attempts the purposeful business operation the control protects.

## What Changes

- Define one typed runtime-security contract for all eight services covering
  deployment profile, secret-file resolution, workload identity, trust roots,
  certificate/key references, and dependency-specific authentication.
- Require encrypted and authenticated PostgreSQL, Kafka, Temporal/Nexus,
  service-to-service HTTP, Redis, and OTLP connections in the
  `production-contract`, `staging`, and `production` profiles.
- Require production-contract startup to fail before readiness when a required
  identity, credential, trust root, secure endpoint, authorization policy, or
  non-stub provider is absent or internally inconsistent.
- Separate runtime and migration database identities and give each service an
  independently authorized Kafka principal and workload identity.
- Restrict plaintext transports, no-op authorization, reusable inline secrets,
  and in-process provider fallbacks to an explicitly selected `local-fast`
  profile that cannot emit readiness evidence.
- Require operation-based positive and negative acceptance for every protected
  dependency class. Authorized workloads must complete an attributable durable
  operation; wrong workloads must be denied before mutation, outbox creation,
  retry/DLQ publication, Workflow effect, or provider invocation.
- Restrict direct SQL and broker inspection in canonical acceptance to
  service-scoped read-only diagnostic identities after an owned operation;
  shared administrative credentials and synthetic mutation cannot establish
  the security contract.
- Preserve public REST, Protobuf, event-version, Temporal Workflow, and database
  ownership contracts; this changes transport and startup behavior rather than
  public business payloads.

### Goals

- Make secure configuration behavior consistent and testable across all eight
  service binaries and every independently deployed role.
- Prove authorization, rotation, and recovery through the same purposeful
  customer, order, payment, inventory, shipping, notification, reporting, and
  telemetry operations used by production-contract acceptance.
- Provide a stable application-facing contract that local Compose, local kind,
  and later cloud environments can supply through different secret and
  certificate providers.
- Keep credentials, private keys, bearer tokens, and complete DSNs out of logs,
  rendered evidence, and committed configuration.

### Non-Goals

- Provisioning staging or production infrastructure, cloud IAM, cert-manager,
  External Secrets backends, or Argo CD promotion.
- Selecting new dependency versions or a production certificate authority.
- Changing domain ownership, public APIs, event schemas, Workflow histories, or
  delivery guarantees.

## Capabilities

### New Capabilities

- `service-runtime-security-contract`: Defines the common secure configuration,
  workload identity, secret resolution, dependency authentication, fail-closed
  startup, observability, and local-fast exception contract for all services.

### Modified Capabilities

- `platform-extensibility`: Strengthen independent data ownership into separate
  owner, migration, runtime, and CDC identities with negative isolation proof.
- `platform-kafka-harness`: Require authenticated encrypted clients, scoped
  principals, and authorization failures that do not enter retry/DLQ handling.
- `platform-observability`: Require authenticated TLS OTLP outside local-fast
  while retaining trace propagation and redaction behavior.
- `temporal-nexus-security`: Limit the no-op Authorizer to local-fast and require
  the production-contract local profile to exercise real transport identity and
  endpoint authorization.
- `order-remote-activities`: Limit in-process HTTP fallbacks to local-fast and
  require authenticated peer identity in the production-contract profile.

## Impact

- **Services and platform:** typed config loaders, validation, HTTP servers and
  clients, PostgreSQL pools and migration runners, Kafka clients, Temporal
  clients/workers, OTLP exporters, health behavior, and redaction tests across
  all eight services and shared platform adapters.
- **Verification:** a role/dependency/operation matrix, allowed-and-denied
  purposeful operation cohorts, causal security evidence, and read-only
  service-scoped diagnostic access.
- **Data ownership:** one physical local PostgreSQL instance remains allowed,
  but service runtime, migration, owner, and CDC permissions become distinct.
- **Cross-service dependencies:** callers and providers authenticate workload
  identity; provider-owned authorization and idempotency remain authoritative.
- **Compatibility:** existing plaintext local behavior moves behind
  `local-fast`; canonical production-contract callers must supply new secret and
  trust references. Rollout is service-by-service behind explicit profiles,
  followed by removal of implicit insecure defaults. Rollback restores the
  previous profile selection without reverting database or event data.
- **Downstream sequencing:** `establish-production-contract-local-readiness`
  consumes this contract. The deferred cloud-readiness change must later adopt
  the same logical inputs rather than treating current overlays as authoritative.
