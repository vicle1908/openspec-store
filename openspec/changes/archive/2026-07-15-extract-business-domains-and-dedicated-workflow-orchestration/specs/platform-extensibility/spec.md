## ADDED Requirements

### Requirement: New business domain services are first-class platform capabilities

The three new services introduced by the `extract-business-domains-and-dedicated-workflow-orchestration` change (`payment-service`, `inventory-service`, `shipping-service`) are first-class platform capabilities and SHALL each have an ADR at `services/<name>/docs/adr/0001-service-extraction.md` documenting the extraction rationale, the alternatives considered, and the data ownership boundary. The ADR SHALL follow the 5-point admission format (Problem / Considered Alternative / Owner / Integration Boundary / Failure Mode) used by `order-service/docs/adr/0004-optional-infrastructure.md`. The architecture test in each new service's `test/architecture/` SHALL assert the ADR file exists and contains the five required sections.

#### Scenario: All three new services have extraction ADRs

- **WHEN** the architecture test scans for `services/<name>/docs/adr/0001-service-extraction.md`
- **THEN** the test verifies that the file exists for `payment-service`, `inventory-service`, and `shipping-service`
- **AND** the test verifies that each file contains the `## Problem`, `## Considered Alternative`, `## Owner`, `## Integration Boundary`, `## Failure Mode` sections
- **AND** the test fails if any section is missing or empty

### Requirement: Cross-service contract package layout is a contract surface

The `services/<name>/proto/<domain>/v1/` (source `.proto` files) and `services/<name>/contracts/<domain>/v1/` (generated `.pb.go` files) package layout is a contract surface, matching the existing `services/order-service/proto/order/v1/` and `services/order-service/contracts/order/v1/` directory layout. A change to the package layout (renaming a directory, removing a `.proto` file, regenerating with a different `buf` configuration) SHALL require a new OpenSpec change. The `cross-service-workflow-contracts` capability is the canonical place to document any contract-layout change.

#### Scenario: Contract package layout is enforced by the architecture test

- **WHEN** the architecture test scans `services/<name>/proto/` and `services/<name>/contracts/`
- **THEN** the test verifies that each service has both `proto/<domain>/v1/` and `contracts/<domain>/v1/` subdirectories
- **AND** the test verifies each contains a `<domain>.proto` file and a `<domain>.pb.go` file respectively
- **AND** the test fails if the directory structure deviates from the convention

### Requirement: Docker-compose overlay pattern is a contract surface

The `deploy/docker-compose.<service>.yaml` overlay pattern (one file per service, merged with the top-level `docker-compose.yaml` via `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.<service>.yaml up -d`) is a contract surface. A new service SHALL add a new overlay file; the overlay SHALL include `<service>-migrate`, `<service>-api`, `<service>-worker`, `<service>-infrastructure-init`, and `<service>-topics-init` containers (the last is omitted for read-only services like `reporting-service` and `catalog-service`). The overlay SHALL set `<SERVICE>_TEMPORAL_ADDRESS=temporal:7233` and `<SERVICE>_TEMPORAL_TASK_QUEUE=<service-task-queue>`.

#### Scenario: All eight services have a docker-compose overlay

- **WHEN** the architecture test lists `deploy/docker-compose.*.yaml` files
- **THEN** the list contains overlays for `order-service`, `payment-service`, `inventory-service`, `shipping-service`, `notification-service`, `customer-service`, `reporting-service`, `catalog-service`
- **AND** each overlay's worker container has `depends_on: temporal: condition: service_healthy`

### Requirement: Makefile target pattern is a contract surface

The Makefile target pattern for each service (`<service>-build`, `<service>-compose-up`, `<service>-smoke-test`) is a contract surface. A new service SHALL add three Makefile targets: a build target that runs `go build -o bin/<service>-service ./services/<service>/cmd/<service>/`; a compose-up target that runs `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.<service>.yaml up -d`; a smoke-test target that runs the service's contract test in `tests/cross-service-smoke/`. The `make help` target SHALL list the new targets.

#### Scenario: All eight services have Makefile targets

- **WHEN** the architecture test scans the `Makefile` for `<service>-build`, `<service>-compose-up`, `<service>-smoke-test` patterns
- **THEN** the test verifies that all eight services have all three targets
- **AND** the test fails if any target is missing

### Requirement: Service module path convention is a contract surface

The Go module path for each new service SHALL be `github.com/victory1908/<name>` (matching `notification-service`, `customer-service`, `reporting-service`, `catalog-service`). The `go.mod` in `services/<name>/go.mod` SHALL declare this module path. A change to the module path (e.g., adding a new top-level segment) SHALL require a new OpenSpec change. The `order-service` is the historical exception (`github.com/victory1908/services/order-service`) and SHALL NOT be changed by this delta; new services SHALL use the `github.com/victory1908/<name>` form so the reserved-prefix test in `services/order-service/test/architecture/layering_test.go::TestHypotheticalPeerServiceCannotImportOrderInternals` (which lists `github.com/victory1908/payment-service/`, `github.com/victory1908/inventory-service/`, `github.com/victory1908/shipping-service/`) continues to work as-is.

#### Scenario: All eight service modules have the correct module path

- **WHEN** the architecture test scans `services/<name>/go.mod` for the `module` directive
- **THEN** the test verifies that `services/order-service/go.mod` declares `module github.com/victory1908/services/order-service` (the historical exception)
- **AND** the test verifies that the other seven service modules declare `module github.com/victory1908/<name>`
