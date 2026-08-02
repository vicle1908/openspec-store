## Purpose

Ensure platform module documentation accurately reflects current implementation, including security packages, Temporal integration, and health contracts.

## ADDED Requirements

### Requirement: Security packages documented in architecture.md

`platform/docs/architecture.md` SHALL document all security packages.

#### Scenario: Security packages section exists
- **WHEN** a developer reads `platform/docs/architecture.md`
- **THEN** they find a "Security packages" section covering pgroles, pgownership, pgconn, Redis TLS, HTTP mTLS, Kafka TLS/SASL, OTLP TLS, and Temporal security

### Requirement: Temporal security documented

`platform/docs/temporal.md` SHALL document Temporal security configuration.

#### Scenario: Temporal TLS documented
- **WHEN** a developer reads `platform/docs/temporal.md`
- **THEN** they find documentation for TLS configuration, Nexus endpoint security, workflow identity, and task queue isolation

### Requirement: Health contracts documented

`platform/docs/health.md` SHALL document health probe contracts.

#### Scenario: Health probe contracts documented
- **WHEN** a developer reads `platform/docs/health.md`
- **THEN** they find documentation for health probe contracts (live/ready/startup), per-service endpoints, and dependency checks

### Requirement: Documentation index accurate

`platform/docs/README.md` SHALL correctly reference all existing documentation files.

#### Scenario: No broken references
- **WHEN** a developer reads `platform/docs/README.md`
- **THEN** every file listed in the table exists in `platform/docs/`
