## MODIFIED Requirements

### Requirement: Canonical full-stack Compose lifecycle

The platform SHALL expose one canonical root command that supplies the pinned
interpolation environment, selects the production-contract security profile,
combines the base data plane with all eight service overlays, optionally
includes supported tools and LGTM profiles, generates run-scoped secret and PKI
inputs, builds canonical local service images, and waits a bounded time for
required services to become healthy. The command SHALL create a
collision-resistant run ID from UTC time, process ID, and randomness; derive
one unique Compose project unless an exact safe override is supplied; pass that
identity to every initializer, validator, and operation; and retain redacted
resolved Compose, runtime-contract parity, image platform, security posture,
health, one-shot exit, and cleanup state in a per-run evidence directory. A
separately named local-fast command MAY preserve insecure convenience behavior
but MUST NOT produce canonical readiness evidence.

#### Scenario: Clean full-stack startup
- **WHEN** a developer runs the canonical full-stack command from a clean checkout with no project containers
- **THEN** Compose starts secure PostgreSQL, Kafka, Debezium, Temporal, OpenTelemetry, provider sandbox, and all required roles for the eight services using non-empty pinned image references
- **AND** the command exits zero only after required parity, security, health, and initializer gates pass and records the exact run/project identity

#### Scenario: Local-fast startup is explicit
- **WHEN** a developer invokes the separately named local-fast command
- **THEN** the supported convenience stack may start
- **AND** its output and artifacts identify that they cannot satisfy readiness

#### Scenario: Unresolved interpolation fails during validation
- **WHEN** a required image version, secret reference, trust input, runtime-contract field, or Compose input is absent
- **THEN** validation exits non-zero before creating containers and names the unresolved logical input without exposing a secret

#### Scenario: Slow dependency converges
- **WHEN** secure bootstrap or Debezium plugin discovery requires its documented budget
- **THEN** the lifecycle waits with progress and succeeds if the dependency converges before the budget expires

#### Scenario: One-shot initializer fails
- **WHEN** PKI, credential, role, migration, ACL, topic, connector, namespace, authorization, or Nexus reconciliation exits non-zero
- **THEN** the lifecycle exits non-zero and retains redacted initializer and dependency diagnostics under the exact run ID

#### Scenario: Full-stack rerun is idempotent
- **WHEN** the same project runs canonical startup twice with its owned run inputs
- **THEN** the second run exits zero without duplicating identities, grants, topics, connectors, namespaces, endpoints, migrations, or business side effects

#### Scenario: Two runs are isolated
- **WHEN** two readiness commands execute concurrently
- **THEN** they use different run IDs, Compose projects, secret roots, credentials, evidence directories, and container labels
- **AND** each acceptance manifest references only its own artifacts

