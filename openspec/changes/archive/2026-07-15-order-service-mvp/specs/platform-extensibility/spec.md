## ADDED Requirements

### Requirement: Services own data and deployment
Each service SHALL be the sole writer of its authoritative data and SHALL have independent credentials, migrations, configuration validation, health endpoints, and deployment lifecycle.

#### Scenario: Shared local PostgreSQL instance
- **WHEN** multiple services use one PostgreSQL container in local development
- **THEN** each service still uses a distinct database or schema owner and cannot write another service's tables

### Requirement: Shared libraries remain infrastructure neutral
Cross-service libraries SHALL be limited to generated contracts, telemetry setup, and test utilities. They MUST NOT contain domain models, repositories, global configuration, or database clients.

#### Scenario: New Payment service
- **WHEN** developers create the Payment service
- **THEN** it defines its own domain and persistence model while reusing only approved contract and platform utilities

### Requirement: Extraction follows operational need
A module SHALL be extracted into a service only when independent ownership, scaling, availability, security, retention, or release cadence justifies the distributed-system cost.

#### Scenario: Notification growth
- **WHEN** notification volume and retry behavior need independent scaling
- **THEN** the Notification module can become a Kafka consumer service without changing Order table ownership

### Requirement: Optional infrastructure is capability driven
Redis, search stores, schema registries, gateways, and other infrastructure SHALL be introduced only with an owned capability, failure model, operational metric, and removal strategy.

#### Scenario: Cache proposal
- **WHEN** a read cache is proposed
- **THEN** the design identifies the authority, invalidation policy, stale-read tolerance, observability, and fallback behavior before adding Redis

### Requirement: Observability is consistent across services
Every service SHALL emit structured logs, traces, and metrics with service identity, environment, request/correlation context, and dependency outcomes while excluding secrets and sensitive payment data.

#### Scenario: Cross-service failure
- **WHEN** fulfillment fails across Order and Inventory boundaries
- **THEN** operators can correlate the API request, workflow, activity, and integration event using shared identifiers

### Requirement: Local Compose is not production topology
The Docker Compose stack SHALL provide reproducible local development with pinned images, health checks, internal/external listener separation, persistent volumes where useful, and optional tools profiles. It SHALL NOT be represented as a production HA deployment.

#### Scenario: Fresh local startup
- **WHEN** a developer starts the stack with empty volumes
- **THEN** migrations, topics, publication, and Debezium connector initialize idempotently before dependent runtimes start, without manual database or broker steps
