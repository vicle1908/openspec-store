# Spec Delta: Testcontainers Aggregate Evidence Schema Alignment

## Purpose

Aligns the aggregate Testcontainers evidence validator with the post-rename module schema (`go-microservices.testcontainers-aggregate/v1`) while preserving backward-compatible parsing for historical runs.

## MODIFIED Requirements

### Requirement: Testcontainers evidence is exact and independently classified

Every service integration and focused ecosystem run SHALL write a
schema-versioned `go-microservices.testcontainers-ecosystem/v1` manifest. The
aggregate verification gate SHALL validate that the aggregate evidence manifest
matches either `go-microservices.testcontainers-aggregate/v1` or
`microservices.testcontainers-aggregate/v1`. The manifest MUST record source
revision, dirty state, run identity, cohort, evidence class, host platform,
declared and resolved images, selected topology, required checks, child
artifacts and hashes, start and finish times, redacted diagnostics, ownership,
and cleanup. The only accepted classes SHALL be `service-integration` and
`focused-ecosystem`.

#### Scenario: Passing service integration evidence is retained

- **WHEN** all required adapter operations pass and owned resources are cleaned up
- **THEN** the manifest reports `service-integration`, identifies the exact service and source revision, lists every required check as passed, and records successful cleanup

#### Scenario: Cross-run child artifact is supplied

- **WHEN** a manifest references a child artifact whose run identity, stack identity, source revision, or hash does not match
- **THEN** validation exits non-zero and identifies the mismatched field

#### Scenario: Focused evidence is offered as full readiness

- **WHEN** a caller supplies `focused-ecosystem` evidence where canonical full-stack Compose evidence is required
- **THEN** validation rejects it and requires a passing `canonical-full-stack` manifest

#### Scenario: Evidence contains a secret-shaped value

- **WHEN** manifest or retained log validation detects a credential, password-bearing DSN, Docker authentication value, or provider payload
- **THEN** the selected target fails evidence validation and retains only a redacted diagnostic category

#### Scenario: Post-rename aggregate evidence is validated

- **WHEN** the aggregate evidence collector outputs a manifest with schema `go-microservices.testcontainers-aggregate/v1`
- **THEN** the evidence validator SHALL accept the schema and proceed with child manifest integrity validation

#### Scenario: Legacy aggregate evidence remains accepted

- **WHEN** an aggregate evidence manifest with schema `microservices.testcontainers-aggregate/v1` is validated
- **THEN** the evidence validator SHALL accept the schema without emitting an unsupported schema error

#### Scenario: Unrecognized schema is rejected

- **WHEN** an aggregate manifest specifies an unknown schema version
- **THEN** the validator SHALL fail closed and report an unsupported schema error
