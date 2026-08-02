## Why

The canonical local gate proves full-stack functionality, image identity,
initialization, and evidence ownership, but it does not prove the security,
identity, isolation, provider, or failure contracts required for production.
Local readiness must exercise the production application contract while still
making honest, explicit reductions for laptop topology and scale. The current
smoke path also treats direct synthetic outbox inserts, terminal Workflow state,
and unrelated health or telemetry samples as evidence; those checks do not
establish that one real business request caused the expected durable effects.

## What Changes

- Add a normalized runtime-contract manifest that defines environment-neutral
  roles, images, commands, probes, configuration classes, dependency protocols,
  workload identities, data ownership, provider mode, and security invariants.
- Validate the manifest against merged Docker Compose and rendered local kind
  resources without requiring raw YAML equality or copying current production
  overlays as the source of truth.
- Add a production-contract local profile with ephemeral per-run PKI and
  secrets, PostgreSQL role isolation and TLS, Kafka TLS/SASL and ACLs,
  Temporal/Nexus authenticated authorization, mutual-TLS internal HTTP, secure
  Redis and OTLP, segmented networks, and hardened containers.
- **BREAKING**: make the canonical `make dev-up` path select the secure
  production-contract profile after migration; retain the existing fast
  plaintext/stub behavior only through an explicitly named `make dev-fast-up`
  path that cannot produce readiness evidence.
- Extend `make local-operational-readiness` with negative authorization,
  cross-schema, wrong-trust, credential-replacement, dependency restart,
  graceful-shutdown, replay/idempotency, and provider-sandbox acceptance.
- Make the canonical acceptance workload execute happy-path, compensation,
  idempotency, authorization, and recovery operations through owning APIs,
  Workers, consumers, and Nexus boundaries, then assert their exact durable
  business outcomes. Direct table writes and direct Kafka injection remain
  supplemental diagnostics or focused fixtures and cannot establish readiness.
- Retain a per-operation causal ledger linking request, correlation, idempotency,
  aggregate, Workflow, outbox, Kafka, receipt, projection, provider-effect,
  notification, trace, and before/after state identities across the full stack.
- Use a networked protocol-faithful Shipping sandbox in production-contract
  mode so readiness exercises the real carrier adapter and unknown-outcome
  reconciliation path rather than the in-process stub.
- Record every permitted local reduction—single replicas, one PostgreSQL
  server, one Kafka broker, replication factor one, one Temporal server, and
  local certificate/secret providers—in retained evidence.

### Goals

- Make the authoritative local stack representative of production behavior,
  security controls, and failure semantics.
- Prove that representative customer, catalog, inventory, order, payment,
  shipping, notification, and reporting operations complete or compensate with
  one causally attributable logical effect.
- Preserve a bounded fast inner loop without allowing it to become readiness
  evidence accidentally.
- Produce exact-revision evidence that a later cloud change can consume without
  claiming cloud IAM, HA, autoscaling, multi-zone, GitOps, or rollback proof.

### Non-Goals

- Updating staging or production resources, External Secrets backends, cloud
  IAM, Argo CD, promotion workflows, or live rollback.
- Reproducing managed-service control planes, multi-region behavior, zonal
  failure, production load, or production data volume on a laptop.
- Changing business APIs, events, Workflow histories, data ownership, or
  application delivery guarantees.

## Capabilities

### New Capabilities

- `local-production-contract-readiness`: Defines the canonical runtime contract,
  secure local profiles, allowed topology reductions, negative/failure tests,
  evidence, and boundaries of local readiness claims.

### Modified Capabilities

- `local-development-orchestration`: Make secure production-contract startup
  canonical and move insecure convenience behavior behind `dev-fast-up`.
- `local-compose-operational-readiness`: Expand full-stack evidence from
  functional operations to security, provider, failure, and recovery contracts.
- `platform-extensibility`: Clarify that Compose is not production HA but its
  canonical readiness profile must preserve production application contracts.
- `redis-security`: Replace reusable environment credentials and committed
  certificate paths with per-run secret files and production-contract TLS/ACL
  evidence while retaining local-fast compatibility.
- `shipping-service`: Require a networked sandbox through the real provider
  adapter in production-contract readiness and restrict the in-process stub to
  local-fast.

## Impact

- **Deployment:** Compose base and overlays, local kind resources, network
  segmentation, container policies, ephemeral PKI/secrets, infrastructure
  initialization, health checks, image validation, and Make targets.
- **Validation:** a new runtime-contract inventory and parity validator, updated
  deployment validation, security/fault acceptance, evidence schemas,
  operation-led smoke cohorts, causal-ledger aggregation, diagnostics, cleanup,
  and traceability.
- **Services:** consumes the completed
  `standardize-service-runtime-security-contract` inputs; Inventory and Shipping
  Dockerfiles also need canonical role-aware healthchecks.
- **Compatibility:** developer startup gains secure bootstrap prerequisites and
  may take longer; `dev-fast-up` is the explicit rollback/compatibility path.
  Persistent application data is not migrated by profile selection.
- **Rollout:** finish and verify the service-security change, introduce the
  production-contract profile alongside existing behavior, pass full evidence,
  then switch canonical targets. Rollback restores target aliases and retains
  diagnostics without weakening evidence classification.
- **Cloud boundary:** the active cloud-readiness change remains deferred and
  must later be updated to validate its overlays against this contract.
