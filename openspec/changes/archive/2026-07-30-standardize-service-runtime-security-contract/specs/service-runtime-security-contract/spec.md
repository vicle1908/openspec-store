## Purpose

Define one externally testable runtime-security contract for every service role
so local production-contract, staging, and production deployments exercise the
same identity, secret, transport, authorization, and fail-closed behavior.

## ADDED Requirements

### Requirement: Runtime security mode is explicit and environment compatible

Every service role SHALL require an explicit runtime security mode. Local
development MAY select `local-fast` or `production-contract`; staging and
production MUST select `strict`. `production-contract` and `strict` SHALL apply
the same application-level security requirements. An absent, unknown, or
environment-incompatible mode MUST fail configuration validation before any
listener, Worker poller, migration, consumer, or initializer becomes ready.

#### Scenario: Production-contract mode starts with complete inputs
- **WHEN** a service role selects `production-contract` and supplies every required secure dependency and identity input
- **THEN** configuration validation succeeds and startup may continue

#### Scenario: Production selects local-fast
- **WHEN** a service role selects `local-fast` while its deployment environment is production
- **THEN** startup fails before the role becomes live or ready
- **AND** diagnostics identify the incompatible mode without exposing a secret

#### Scenario: Security mode is omitted
- **WHEN** any service role starts without an explicit runtime security mode
- **THEN** configuration validation fails instead of inferring an insecure default

### Requirement: Secret values are resolved through a common precedence contract

Every secret-bearing setting SHALL support a file reference distinct from its
non-secret configuration. In `production-contract` and `strict`, a required
secret MUST be read from its referenced file and MUST NOT be accepted from a
reusable value embedded in a Compose file, ConfigMap, command argument, or
committed environment file. Missing, unreadable, empty, or conflicting secret
sources SHALL fail before dependency connection. Secret values, private keys,
complete credential-bearing DSNs, and authorization tokens MUST be redacted
from logs, health responses, metrics, traces, rendered manifests, and retained
evidence.

#### Scenario: Secret file is valid
- **WHEN** a required credential references a readable non-empty file
- **THEN** the service uses the file content without exposing it in observable output

#### Scenario: Secret file is unreadable
- **WHEN** a required secret file is absent or unreadable
- **THEN** startup fails before attempting the dependency connection
- **AND** diagnostics identify only the logical setting and file path

#### Scenario: Direct and file secret sources conflict
- **WHEN** both a reusable direct value and a file reference are supplied in production-contract mode
- **THEN** validation fails instead of choosing one implicitly

### Requirement: Every service role presents an authorized workload identity

Each independently deployed API, Worker, orchestrator, migration, CDC, and
initializer role SHALL have a stable workload identity distinct from human and
infrastructure administrator identities. In `production-contract` and
`strict`, callers SHALL authenticate that identity to protected dependencies,
and providers SHALL authorize it against an explicit least-privilege policy.
Identity SHALL derive from verified transport or credential context and MUST
NOT be trusted from an unverified request field.

#### Scenario: Authorized workload reaches a dependency
- **WHEN** a role presents a valid identity permitted for the requested operation
- **THEN** the dependency admits the operation and records non-secret caller identity in audit telemetry

#### Scenario: Wrong workload identity is presented
- **WHEN** a valid identity is not authorized for the requested service, topic, schema, queue, endpoint, or telemetry pipeline
- **THEN** the request is denied before the protected operation executes
- **AND** denial telemetry contains no credential material

#### Scenario: Payload attempts to override caller identity
- **WHEN** a request payload or propagation header claims an identity different from the authenticated transport context
- **THEN** authorization uses the authenticated identity and ignores the claim as an authentication source

### Requirement: Protected dependency transport is encrypted and verified

In `production-contract` and `strict`, PostgreSQL, Kafka, Temporal/Nexus,
service-to-service HTTP, Redis, and OTLP connections SHALL use encrypted
transport, validate the peer against an explicit trust root and expected
identity, and present client authentication when the dependency policy requires
it. Plaintext endpoints, disabled certificate verification, anonymous clients,
and wildcard trust SHALL fail configuration validation.

#### Scenario: Verified secure dependency connection succeeds
- **WHEN** the endpoint, trust root, expected peer identity, and client authentication are valid
- **THEN** the connection succeeds and dependency readiness may become healthy

#### Scenario: Peer certificate is signed by an untrusted authority
- **WHEN** a protected dependency presents a certificate outside the configured trust chain
- **THEN** the connection fails and readiness remains false

#### Scenario: Plaintext endpoint is configured
- **WHEN** production-contract mode receives a plaintext endpoint for a protected dependency
- **THEN** startup fails before sending application or credential data

### Requirement: Security failures are classified without unsafe retry

Authentication, authorization, trust, and invalid-security-configuration
failures SHALL be classified separately from transient dependency failures.
They MUST NOT enter business retries, Kafka retry topics, DLQs, Temporal
Activity retries, or circuit-breaker success accounting. Readiness SHALL remain
false until corrected, while liveness MAY remain healthy when the process can
still report diagnostics safely.

#### Scenario: Authorization denial occurs during a command
- **WHEN** a dependency rejects an operation because the workload is unauthorized
- **THEN** the caller returns a typed non-retryable security failure
- **AND** no business side effect or retry record is created

#### Scenario: Dependency certificate becomes invalid
- **WHEN** a new connection cannot verify the dependency certificate
- **THEN** readiness becomes false and bounded reconnect attempts preserve the original operation identity
- **AND** no duplicate side effect is claimed as successful

### Requirement: Security posture is observable without disclosing secrets

Every service SHALL expose non-secret posture evidence containing service,
role, deployment environment, runtime security mode, authenticated dependency
classes, and validation outcome. Logs and metrics SHALL distinguish
configuration, authentication, authorization, and trust failures while
preserving trace and correlation identifiers where a request existed.

#### Scenario: Production-contract role becomes ready
- **WHEN** configuration and required dependency authentication checks pass
- **THEN** readiness evidence records the secure mode and dependency classes without recording secret values or certificate private material

#### Scenario: Authentication fails
- **WHEN** a dependency rejects a credential or certificate
- **THEN** telemetry identifies the service, role, dependency class, and failure category
- **AND** the credential and complete DSN remain redacted

### Requirement: Security acceptance uses purposeful operations

Every production-contract security control SHALL be verified through an
authorized and unauthorized operation that exercises the protected business or
operational capability. The authorized case SHALL prove its exact durable
effect and authenticated caller identity. The unauthorized case SHALL prove
denial before domain mutation, outbox creation, retry or DLQ publication,
Workflow or Nexus effect, provider invocation, notification, projection, or
telemetry admission as applicable. A health response, transport handshake,
configuration dump, direct database mutation, direct Kafka injection, or
uncorrelated signal MUST NOT by itself satisfy security acceptance.

Durable-state inspection SHALL use owning read APIs or service-scoped read-only
diagnostic identities. A shared administrator or migration identity MUST NOT be
used as the canonical operation runner or evidence oracle.

#### Scenario: Authorized purposeful operation executes
- **WHEN** the canonical workload identity performs an operation permitted by its PostgreSQL, Kafka, HTTP, Temporal/Nexus, Redis, provider, and OTLP policies
- **THEN** the operation completes with its expected durable state and records the authenticated identity, operation identity, and correlated trace without secret material

#### Scenario: Wrong identity repeats the operation
- **WHEN** a valid but unauthorized workload identity attempts the same purposeful operation
- **THEN** the protected boundary denies it before any prohibited durable or external effect
- **AND** evidence proves the relevant before and after states are unchanged

#### Scenario: Only a connection probe succeeds
- **WHEN** secure connection, readiness, or handshake checks pass but no purposeful allowed and denied operation pair has been executed
- **THEN** the result remains focused diagnostic evidence and cannot satisfy production-contract security readiness

#### Scenario: Administrative identity is used for acceptance
- **WHEN** the acceptance runner attempts a business mutation or cross-service state assertion through a shared administrator or migration identity
- **THEN** evidence validation rejects the cohort as non-representative

### Requirement: Local-fast cannot establish readiness

`local-fast` SHALL be an explicit developer-convenience mode. It MAY use
plaintext transports, no-op local authorization, inline disposable credentials,
or in-process provider fallbacks, but every process and artifact SHALL label the
mode insecure and local-only. Evidence produced from `local-fast` MUST NOT be
accepted as production-contract local readiness, deployment readiness, staging
readiness, or production readiness.

#### Scenario: Local-fast developer stack starts
- **WHEN** a developer explicitly selects local-fast
- **THEN** the supported convenience stack may start with an insecure-mode warning

#### Scenario: Local-fast evidence is submitted to a readiness gate
- **WHEN** a readiness validator receives evidence produced in local-fast mode
- **THEN** validation fails and identifies the incompatible evidence class
