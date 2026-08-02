## MODIFIED Requirements

### Requirement: Hexagonal layer isolation

Every service's Go code SHALL conform to the repository's hexagonal layering.
Architecture verification SHALL evaluate direct imports of every package in
the selected layer when deciding whether application source imports an
infrastructure framework. It MAY evaluate the transitive dependency graph for
domain purity and in-repository layer-direction rules, but it MUST NOT report a
third-party SDK's transitive dependencies as direct application imports.

The canonical boundaries are:

| Layer | MAY import | MUST NOT directly import |
|---|---|---|
| `internal/domain/` | stdlib, pure contracts and value types | adapters, ports, application, infrastructure frameworks, peer internals |
| `internal/application/` | owned domain and ports; approved platform abstractions | owned adapters, peer internals, Fx, Zap, OTel, pgx, Kafka, or Redis SDKs |
| `internal/application/orchestration/` | application imports plus Temporal `workflow`, `activity`, `temporal`, and required client contract APIs and `platform/temporal` policy helpers | owned adapters, Fx, Zap, OTel, pgx, Kafka, Redis, or direct external I/O from Workflow code |
| `internal/ports/` | owned domain, stdlib, generated contracts | adapters and infrastructure implementations |
| `internal/adapters/` | owned ports/application/domain, vendor SDKs, approved platform adapters | another adapter kind except a documented composition boundary |
| `cmd/` and `internal/runtime/` | all owned layers required for composition | peer-service internals |

Temporal Workflow determinism and worker safety SHALL be enforced by the
canonical Temporal inventory validator and upstream workflow checker rather
than inferred from the third-party dependency closure.

#### Scenario: Direct application infrastructure import fails

- **WHEN** an application package directly imports Fx, Zap, OTel, pgx, Kafka,
  Redis, or an owned adapter
- **THEN** the architecture suite fails with the package and direct import
- **AND** the violation cannot be hidden behind another application package

#### Scenario: Temporal transitive dependency is not misreported

- **WHEN** `internal/application/orchestration` imports an approved Temporal
  Workflow API or `platform/temporal`
- **AND** that dependency transitively uses Fx, Zap, or OTel internally
- **THEN** the application infrastructure-import test does not report those
  transitive packages as direct imports
- **AND** canonical Temporal worker and determinism verification still runs

#### Scenario: Domain purity remains transitive

- **WHEN** domain code reaches an infrastructure package through an
  intermediate dependency
- **THEN** the domain-purity gate fails
- **AND** the diagnostic identifies the forbidden dependency

#### Scenario: Application cannot import owned adapters

- **WHEN** any package under `internal/application/` directly imports
  `internal/adapters/` or the legacy service-local `adapters/` path
- **THEN** the application-layer gate fails
- **AND** runtime composition remains outside the application layer
