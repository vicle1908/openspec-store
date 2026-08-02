## Context

See `proposal.md` for motivation. The service fleet currently has divergent
configuration loaders and transport capabilities: four services expose some
Temporal TLS configuration, peer HTTP is plaintext and unauthenticated, Kafka
is configured without client authentication, and OTLP is explicitly insecure
in current environment overlays. PostgreSQL is authoritative and shared in
local development, while the normative ownership contract already requires
independent service credentials.

The design must preserve ports-and-adapters boundaries. Domain and application
packages cannot import TLS, secret-provider, Kafka, Temporal, PostgreSQL, or
HTTP infrastructure types. Existing public REST/Protobuf payloads, event
versions, Workflow histories, outbox transaction boundaries, at-least-once
delivery, and idempotency behavior remain unchanged.

Existing verification is uneven: configuration and adapter tests often prove
that a connection can be built, while smoke checks may use health endpoints,
direct database access, synthetic Kafka records, or terminal Workflow status.
Those checks do not prove that the authenticated identity can perform its
intended operation, nor that a wrong identity is rejected before a business
effect.

## Goals / Non-Goals

**Goals:**

- Give every independently deployed role the same security-mode and secret
  resolution semantics while leaving each service responsible for its typed
  configuration.
- Use transport-authenticated workload identity and least-privilege dependency
  policy in local production-contract and non-local environments.
- Make invalid security posture fail before a role accepts work and produce
  safe, classified diagnostics.
- Make every protected edge accountable to an allowed and denied purposeful
  operation with a durable before/after oracle.
- Support controlled migration from the current plaintext local configuration.

**Non-Goals:**

- A service mesh, SPIRE installation, cloud workload-identity provider, or
  production CA selection.
- Hot reload of every credential without process restart; rotation must be
  restart-safe and reconnect-safe, but provider-specific live reload is later
  work.
- Changing data models, APIs, event schemas, Temporal logic, or delivery
  guarantees.

## Decisions

### 1. Security mode is separate from deployment environment

Keep the existing deployment environment for telemetry and environment-specific
behavior. Add one explicit runtime security mode with three values:

| Mode | Valid environment | Readiness eligibility |
| --- | --- | --- |
| `local-fast` | local only | never |
| `production-contract` | local only | local production-contract evidence |
| `strict` | staging or production | non-local evidence after external gates |

Production-contract and strict use the same application validation rules. They
differ only in who supplies credentials, certificates, endpoints, and policy.
This prevents the overloaded word `local` from silently selecting insecure
behavior.

Alternative considered: infer security from `DEPLOYMENT_ENV`. Rejected because
local must support both a fast developer loop and authoritative secure evidence.

### 2. Each service owns typed configuration; platform provides narrow helpers

Each service retains its own configuration aggregate and validation. Shared
platform code may provide infrastructure-neutral helpers for reading a bounded
secret file, redacting sensitive values, and constructing validated TLS inputs,
but it will not introduce global service configuration or domain dependencies.
Every API, Worker, orchestrator, migration, CDC, initializer, and healthcheck
role validates only the inputs it actually uses.

The implementation will inventory the eight services and produce a checked
matrix of required settings per role and dependency. Validation returns typed
categories: configuration, authentication, authorization, trust, or transient
availability.

Alternative considered: one global configuration object shared by every
service. Rejected because it violates service ownership and couples release
cadence.

### 3. Secret-file references are the strict-mode boundary

Secret-bearing settings use a logical value plus a companion file reference.
Production-contract and strict accept the file reference only. Local-fast may
accept disposable direct values for compatibility. File reads are bounded,
trim only the documented trailing newline, reject empty content, and never
include content in an error.

This contract aligns a local ephemeral-secret directory with future Kubernetes
Secret or external-secret mounts without coupling applications to either
provider. Complete DSNs are treated as secrets when they contain credentials;
prefer separate endpoint, database, user, and password inputs as services are
migrated.

Alternative considered: environment variables in every environment. Rejected
because rendered Compose models, process inspection, and diagnostic dumps can
expose them.

### 4. Workload identity is transport-derived and provider-authorized

Every role receives a canonical identity composed from service and role. For
mTLS protocols, identity is derived from a verified certificate identity; for
credential protocols, it is derived from the authenticated principal. Request
payloads and propagation headers never establish authentication.

Providers own allow policies for their APIs, schemas, topics, groups, task
queues, endpoints, and telemetry receivers. Authorization occurs before a
business mutation, but provider-owned tenant or actor authorization still runs
inside the application when required.

Alternative considered: a shared bearer token for all services. Rejected
because it cannot express least privilege or attribute an audit event to a
specific caller.

### 5. Protocol security mechanisms are explicit

- **PostgreSQL:** TLS with server verification plus distinct SCRAM credentials.
  Each service uses `owner` (NOLOGIN), `app`, `migrate`, and when required `cdc`
  identities. `app` has only required DML/sequence rights; `migrate` may assume
  only its owner; `cdc` has replication and owned publication/outbox access.
- **Kafka:** TLS plus a distinct SASL/SCRAM principal for every runtime role,
  initializer, and CDC connector. ACLs scope topics, groups, transactional IDs,
  and necessary cluster metadata operations. Authorization denials are terminal
  security errors, not retry/DLQ records.
- **HTTP:** mutual TLS for service-to-service calls. The provider maps verified
  client identity to route-level policy. Existing idempotency and trace headers
  remain application metadata, not authentication.
- **Temporal/Nexus:** verified TLS plus explicit ClaimMapper and Authorizer.
  Production-contract cannot use the no-op Authorizer. Provider business
  authorization remains separate from Temporal transport authorization.
- **OTLP:** verified TLS, with client authentication where the receiver policy
  requires it. Exporter failure never weakens business authorization.
- **Redis:** reuse the existing TLS and per-service ACL contract rather than
  introducing a second Redis security model.

The design pins no new library or image version. Implementation must verify the
selected configuration against current official documentation and the exact
repository pins before adding syntax or dependencies.

### 6. Startup and health have role-specific security gates

Static validation completes before a role opens a listener or polls for work.
Dependency authentication checks participate in readiness when that dependency
is required for the role. A process may remain live to serve redacted health
diagnostics while readiness is false. Migration and initializer roles fail
non-zero instead of advertising readiness.

Authentication, authorization, and trust failures are non-retryable at the
business layer. Transport reconnection remains bounded and must reuse the
original idempotency key, operation ID, Kafka record identity, or Workflow
identity. No security failure changes transaction or delivery semantics.

### 7. Verification is tiered and operation-based

The checked cross-service matrix maps every service role and protected
dependency edge to one allowed and one denied purposeful operation. Verification
has three tiers:

1. configuration tests reject missing, conflicting, insecure, and secret-bearing
   inputs before startup;
2. adapter and container integration tests prove transport, identity mapping,
   policy enforcement, error classification, and reconnect behavior;
3. operation acceptance executes the owned business command through the
   deployed API, Worker, consumer, or Nexus boundary and asserts durable
   before/after state plus absence or presence of outbox, retry/DLQ, Workflow,
   provider, projection, notification, and telemetry effects as applicable.

Only tier three can satisfy production-contract security readiness. A TLS
handshake, readiness response, direct SQL mutation, direct Kafka injection, or
terminal Workflow state alone remains focused diagnostic evidence.

The operation matrix includes:

- owned runtime DML caused by service APIs, reviewed migrations, and owned CDC
  delivery, plus denied cross-schema, DDL, and foreign-publication access;
- Kafka events caused by owned transactions and consumed under canonical groups,
  plus denied foreign-topic, foreign-group, transactional-ID, and cluster-admin
  attempts;
- authorized Payment, Inventory, Shipping, and other internal HTTP commands,
  plus wrong-caller rejection before mutation;
- authorized Workflow polling and Nexus commands whose durable results are
  asserted, plus wrong-identity/endpoint denial without history or provider
  effect;
- Catalog/Notification Redis commands against owned keys and denied foreign or
  dangerous commands;
- OTLP export for the same correlation/trace identity as the business operation,
  plus wrong-client and wrong-Collector denial;
- restart and credential replacement during real work without duplicate logical
  effects.

Canonical state inspection uses public or provider-owned read APIs first. When
database inspection is required, the runner uses service-scoped read-only
diagnostic identities with an explicit table allowlist. It never uses a shared
administrative credential as evidence authority.

Generated evidence records mode, authenticated logical identity, dependency
class, purposeful operation and idempotency identity, policy result, source/run
identity, before/after durable states, relevant outbox/Kafka/Workflow/provider
identities, and a correlated trace ID without secret material.

### 8. No new local runtime image is required by this change

This change modifies service configuration and adapters, not the local
infrastructure topology. Existing service and infrastructure images remain the
selected linux/arm64-capable set. If implementation proposes a new helper image
or library, it must first verify official compatibility and image architecture;
otherwise the local-readiness change will generate ephemeral inputs using
repository-owned tooling.

## Risks / Trade-offs

- **Cross-service rollout temporarily creates mixed capabilities** → gate each
  service behind explicit mode support and do not enable production-contract
  orchestration until all eight matrices pass.
- **Certificate identity mapping differs between local and future cloud PKI** →
  contract on canonical service/role identity and trust semantics, not issuer
  implementation or certificate file layout.
- **Strict file-only secrets complicate developer use** → retain local-fast as
  an explicit non-evidentiary escape hatch and generate ephemeral files in the
  downstream local-readiness change.
- **Authentication failures accidentally enter existing retry paths** → add
  typed security categories and negative tests at HTTP, Kafka, and Temporal
  adapter boundaries before orchestration rollout.
- **Handshake checks pass while authorization or mutation ordering is broken** →
  require tier-three allowed/denied operation evidence before readiness.
- **Database privilege migration locks objects or breaks migrations** → create
  owner roles first, transfer ownership in reviewed order, verify grants, then
  switch runtime and migration DSNs independently.
- **mTLS increases certificate operational work** → require restart-safe
  rotation and defer provider-specific hot reload until evidence justifies it.

## Migration Plan

1. Add shared narrow secret/redaction/TLS helpers and the typed security-mode
   contract without changing existing default execution.
2. Add complete role-specific configuration and negative tests to each service,
   beginning with Order and one provider service as the reference cohort.
3. Add protocol authentication support and classified errors for PostgreSQL,
   Kafka, HTTP, Temporal/Nexus, Redis, and OTLP.
4. Create database identities and ownership migration tooling; prove grants and
   denials before switching any runtime DSN.
5. Enable production-contract support service by service while local-fast
   remains the explicit compatibility path.
6. Run all service verification gates, platform verification, the complete
   allowed/denied purposeful-operation matrix, and repository validation.
7. Hand the stable inputs to `establish-production-contract-local-readiness`;
   do not modify cloud environments in this change.

Rollback selects local-fast for local development and restores the previous
runtime connection inputs. Database owner roles and grants remain in place;
rollback does not reverse committed migrations, outbox records, events, or
Workflow history. Any partial identity migration must retain diagnostics and
reapply the prior grants before old credentials are re-enabled.
