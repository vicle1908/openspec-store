# deploy-consolidation Specification

## Purpose

Document the two-layer Docker Compose deployment structure: standalone stacks in `order-service/deploy/` for local development, and composable overlays in root `deploy/` for composed environments.

## ADDED Requirements

### Requirement: Two-layer deploy structure

The repository SHALL have two deployment configuration layers serving different purposes:

| Layer | Location | Purpose | Use Case |
|-------|----------|---------|----------|
| Standalone stack | `order-service/deploy/` | Complete self-contained stack | Local dev (no other services needed) |
| Composable overlays | `deploy/` | Infrastructure + service overlays | Full fleet, CI/CD |

```
STANDALONE (order-service/deploy/)
═══════════════════════════════════════════════════════════════════
order-service/deploy/
├── docker-compose.yaml              # Complete stack: postgres, kafka, debezium, temporal, app
├── docker-compose.test.yaml        # Test profile
├── docker-compose.tools.yaml       # Local dev tools
├── docker-compose.cross-service.yaml # Cross-service integration
├── debezium-connector.json        # Debezium config
├── provision-topics.sh           # Topic provisioning
└── init-scripts/                  # DB initialization

COMPOSABLE (deploy/)
═══════════════════════════════════════════════════════════════════
deploy/
├── docker-compose.yaml             # Base: postgres, kafka, temporal, otel
├── docker-compose.order-service.yaml # Order service overlay
├── docker-compose.tools.yaml         # Tools overlay
├── docker-compose.lgtm.yaml         # Observability overlay
└── ...
```

#### Scenario: Using standalone stack for order-service development
- **WHEN** developer works on order-service locally without other services
- **THEN** run: `docker compose -f order-service/deploy/docker-compose.yaml up -d`
- **AND** the complete stack (DB, Kafka, Temporal, app) starts

#### Scenario: Using composed stack for full fleet
- **WHEN** developer needs full 5-service fleet
- **THEN** run: `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.order-service.yaml ... up -d`
- **AND** the base infrastructure + services start

### Requirement: Service-level deploy purpose documentation

Each service-level `deploy/` directory SHALL serve standalone development and SHALL be documented as such.

#### Scenario: Standalone deploy for new service
- **WHEN** a new service is created under `services/`
- **THEN** it SHOULD have a `deploy/` directory with a complete stack
- **AND** the README in that directory SHOULD document standalone usage

### Requirement: Root deploy serves composed environments

The root `deploy/` directory SHALL contain composable overlays for:

1. **Base infrastructure**: postgres, kafka, temporal, otel-collector
2. **Per-service overlays**: extending base with service containers
3. **Tooling overlays**: pgadmin, kafka-ui, etc.
4. **Observability overlays**: grafana, prometheus, loki

#### Scenario: Compose base + specific services
- **WHEN** developer needs order-service + catalog-service only
- **THEN** run: `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.order-service.yaml -f deploy/docker-compose.catalog-service.yaml up -d`

### Requirement: Documentation of deploy structure

The `deploy/README.md` SHALL document the two-layer structure and clarify:

1. When to use standalone vs composed
2. How to combine overlays for different use cases
3. Migration path if standalone deploys are deprecated

#### Scenario: Developer reads deploy README
- **WHEN** a new developer reads `deploy/README.md`
- **THEN** they SHALL understand the two-layer structure
- **AND** they SHALL know when to use standalone vs composed deployment
