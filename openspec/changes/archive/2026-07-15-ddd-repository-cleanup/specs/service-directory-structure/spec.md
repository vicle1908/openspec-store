# service-directory-structure Specification

## Purpose

Document the standardized service directory structure: all services now live under `services/` for consistency.

## ADDED Requirements

### Requirement: Service directory structure

All services in this repository SHALL be located under the `services/` directory:

```
DIRECTORY STRUCTURE
═══════════════════════════════════════════════════════════════════
services/
├── order-service/
├── customer-service/
├── catalog-service/
├── notification-service/
└── reporting-service/
```

#### Scenario: Finding a service
- **WHEN** a developer looks for any service
- **THEN** they find it under `services/<name>-service/`
- **AND** the Go module path follows the pattern `github.com/victory1908/services/<name>-service`

### Requirement: Consistent internal structure

All services SHALL follow consistent internal structure:

```
<service>/
├── internal/
│   ├── domain/          Domain layer (entities, value objects, aggregates)
│   ├── application/    Application layer (commands, queries, handlers)
│   ├── adapters/       Infrastructure adapters (DB, Kafka, HTTP, Temporal)
│   └── ports/          Port interfaces (repository, messaging, etc.)
├── cmd/                 Entry points (roles: api, worker, migrate, etc.)
├── contracts/           Domain events/commands (Protobuf or Go interfaces)
├── deploy/              Standalone Docker Compose (if service supports standalone dev)
├── migrations/          Database migrations
├── proto/               Protobuf definitions
└── Makefile            Service-specific build targets
```

#### Scenario: New service follows consistent structure
- **WHEN** a new service is created
- **THEN** it SHALL follow the internal structure above
- **AND** it SHALL be placed under `services/<name>-service/`

### Requirement: Service platform integration

All services SHALL import and use the shared `platform/` module for:

1. Health check infrastructure (`platform/health`)
2. Runtime wiring patterns (`platform/runtime`)
3. Observability utilities (`platform/observability`)

#### Scenario: Service uses platform components
- **WHEN** a service needs health checks
- **THEN** it SHALL use `platform/health.Registry`
- **AND** it SHALL NOT implement service-local health infrastructure
