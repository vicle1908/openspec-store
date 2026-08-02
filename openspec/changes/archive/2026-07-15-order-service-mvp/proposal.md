## Why

Modern e-commerce and order management systems require reliable, event-driven architectures that preserve local transactional consistency while coordinating long-running work across service boundaries. Synchronous-only approaches leave fragile failure windows when databases, brokers, and downstream services cannot commit atomically.

This project establishes the foundation for a Go-based Order Service using Domain-Driven Design (DDD), Temporal for durable workflow orchestration, Kafka (via Debezium CDC) for event streaming, and PostgreSQL for persistence. By combining these technologies, we get:

- **Temporal**: Durable execution, automatic retries, saga patterns, and human-in-the-loop workflows
- **Debezium CDC**: Reliable, low-latency event capture from PostgreSQL WAL without application-layer complexity
- **Protobuf**: Strongly-typed, evolvable contracts across services
- **DDD**: Clear domain boundaries and business logic encapsulation

Starting with a working MVP (Order Service) enables validating patterns before scaling to a full multi-service platform.

## What Changes

- Create a new Go microservice: **Order Service**
- Implement DDD architecture with Order Aggregate
- Add PostgreSQL persistence with pgx/v5 connection pooling
- Add Transactional Outbox pattern via **Debezium CDC** (reads PostgreSQL WAL → streams to Kafka)
- Integrate Temporal for Order Fulfillment Workflow
- Define Protobuf contracts for all events
- Docker Compose for local development (PostgreSQL 18.4, Kafka 4.3.1, Debezium 3.6.0, Temporal CLI dev server 1.6.1); production targets Temporal Server 1.31.2 or Temporal Cloud
- REST API for MVP order commands and queries; gRPC is deferred

## Capabilities

### New Capabilities

- `order-aggregate`: Order-owned state machine, invariants, optimistic concurrency, and domain events
- `order-command-handler`: Idempotent application commands that atomically persist aggregate changes and outbox records
- `order-repository-port`: Order-specific persistence contract with a PostgreSQL adapter and no cross-service table access
- `order-outbox-cdc`: Protobuf event envelope transported through PostgreSQL outbox, Debezium, and Kafka with at-least-once delivery
- `order-temporal-workflow`: Durable fulfillment orchestration with deterministic evolution, owned task queues, and compensation
- `order-protobuf-contracts`: Versioned public commands and events protected by Buf lint and breaking-change checks
- `order-rest-api`: Versioned HTTP commands and queries with idempotency, pagination, and stable error contracts
- `platform-extensibility`: Service ownership, extraction, observability, configuration, and compatibility rules for future services
- `platform-verification`: Requirement traceability, deterministic CI, compatibility, fault recovery, security, performance, and release evidence gates

### Modified Capabilities

_(None - new project)_

## Impact

### New Code
- `internal/domain/order/` - Order aggregate, value objects, domain events
- `internal/application/commands/` - Command handlers
- `internal/application/queries/` - Order-owned query handlers
- `internal/adapters/` - HTTP, PostgreSQL, and Temporal boundary adapters
- `internal/ports/` - Order repository, unit-of-work, clock, and workflow interfaces
- `contracts/order/v1/` - versioned public Protobuf contracts; no shared domain package
- `proto/` - Protobuf definitions
- `cmd/order-service/` - Main entrypoint
- `deploy/docker-compose.yaml` - Local development stack

### Dependencies
- Go **1.26.5** pinned across module, CI, and containers (pgx v5.10.0 requires Go 1.25+). 1.26.5 is the current patched release as of 2026-07-07 and carries the latest `crypto/tls` and `os` security fixes; pin only through a gated dependency and verification change.
- `go.temporal.io/sdk v1.46.0` - durable workflows and workers
- `github.com/jackc/pgx/v5 v5.10.0` - PostgreSQL driver and pool. 5.10.0 is the current release as of 2026-06-03 and is the minimum version that fully addresses CVE-2026-33815 and CVE-2026-33816 (CVSS 9.8 memory-safety vulnerabilities fixed in 5.9.0); older 5.x versions MUST NOT be accepted.
- `github.com/go-chi/chi/v5 v5.3.1` - HTTP router
- `github.com/twmb/franz-go v1.21.5` - Kafka consumer for durable workflow initiation
- `buf v1.71.0` - Protobuf lint, generation, and compatibility tooling
- `go.uber.org/fx v1.24.0` - process composition and lifecycle
- `go.uber.org/zap v1.28.0` - structured logging
- `github.com/spf13/viper v1.21.0` - configuration management
- `github.com/oklog/ulid/v2 v2.1.1` - canonical service identifiers
- `github.com/testcontainers/testcontainers-go v0.43.0` - isolated integration testing
- `github.com/pressly/goose/v3 v3.27.2` - embedded, service-owned PostgreSQL migrations
- `golang.org/x/vuln/cmd/govulncheck v1.6.0` - reachable Go vulnerability analysis
- `grafana/k6 v1.8.0` - version-controlled API and asynchronous-latency release thresholds
- `aquasec/trivy v0.72.0` - repository, image, configuration, secret, and SBOM verification
- Optional only when a measured caching/idempotency use case appears: `github.com/redis/go-redis/v9 v9.21.0`
- Debezium PostgreSQL Connector **3.6.0.Final** (Jul 2026)
- Apache Kafka **4.3.1**
- PostgreSQL **18.4** (Current stable - Jun 2026)
- Temporal Server **v1.31.2** (Jul 2026) — current production self-hosted release; Temporal Cloud is an equivalent managed target. v1.31.2 was verified against the published release index on 2026-07-14; the production compatibility target MUST be re-confirmed whenever a new minor is cut.

### Configuration
- Environment-based configuration with startup validation and secret indirection
- Liveness, readiness, startup, metrics, and correlation propagation
- Graceful shutdown and dependency-specific readiness
- Per-service database credentials, Kafka topic namespace, Temporal task queue, and independently deployable process
