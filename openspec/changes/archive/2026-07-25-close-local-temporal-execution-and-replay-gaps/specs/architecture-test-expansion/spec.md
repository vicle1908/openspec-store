## MODIFIED Requirements

### Requirement: Every service SHALL have architecture tests for all applicable categories

Each service SHALL maintain architecture tests in `test/architecture/` for
every applicable category in the canonical architecture-test matrix. Temporal
`worker-versioning` and `deterministic-workflow` categories SHALL apply to
every service present in the canonical Temporal inventory.

`TestWorkerVersioningIsConfigured` SHALL invoke the canonical inventory
validator scoped to the owning service and SHALL fail for missing or mismatched
Workflow registration, Activity registration, Auto Upgrade behavior, worker
safety options, or replay metadata. `TestDeterministicWorkflowCode` SHALL run
the same scoped inventory check and the upstream Temporal workflow checker
against the service's actual Workflow source directory. Import-presence tests,
skips, and string searches that cannot detect Workflow API calls MUST NOT
satisfy either category.

The following category applicability remains canonical:

| Category | Applicability |
|---|---|
| domain-purity | All services |
| sole-writer | Services with a PostgreSQL schema |
| ports-are-interfaces | Services with `internal/ports/` |
| adapter-implements-exactly-one-port | Services with `internal/adapters/` |
| no-peer-service-imports | All services |
| build-tag-isolation | Services with vendor SDK imports |
| layering | All services |
| cache-keyspace | Services using platform cache |
| worker-versioning | Every inventoried Temporal worker owner |
| deterministic-workflow | Every inventoried Workflow owner |
| domain-invariants | Services with aggregate roots |
| contract-versioning | Services exposing or consuming versioned contracts |

A service MUST NOT skip an applicable category without a documented exception
and traceability entry. Each service's `verify-pr` SHALL run its architecture
suite before unit tests or otherwise fail before the unit-test phase.

#### Scenario: All current Temporal owners run real worker verification

- **WHEN** the architecture suites for order, payment, inventory, shipping,
  notification, customer, reporting, and catalog run
- **THEN** each suite contains and executes
  `TestWorkerVersioningIsConfigured`
- **AND** the test validates only that service through the canonical inventory

#### Scenario: All current Workflow owners run upstream determinism verification

- **WHEN** any of the eight service `verify-pr` gates runs
- **THEN** `TestDeterministicWorkflowCode` invokes the upstream Temporal
  workflow checker against that service's inventoried Workflow directory
- **AND** a nondeterministic API call fails the service gate with its source
  diagnostic

#### Scenario: Superficial Temporal test is rejected

- **WHEN** an architecture test only detects that some source file imports a
  Temporal package or searches import strings for `time.Now()`
- **THEN** it does not satisfy worker-versioning or deterministic-workflow
  coverage
- **AND** the service must use the canonical validator and upstream checker

#### Scenario: Non-applicable category remains documented

- **WHEN** a service does not use a cache or another optional capability
- **THEN** the corresponding category may remain inapplicable with a truthful
  documented rationale
- **BUT** an inventoried Temporal category cannot be deferred

### Requirement: Architecture test coverage SHALL be tracked in verification/traceability.yaml

Every architecture test SHALL have a corresponding entry in the owning
service's verification traceability manifest. Each entry SHALL identify its
category, concrete test function, and implemented, planned, or deferred status.
An implemented entry MUST name an existing passing test, and a deferred entry
MUST state a currently true non-applicability rationale.

For every service in the canonical Temporal inventory, worker-versioning and
deterministic-workflow SHALL be marked implemented and mapped respectively to
`TestWorkerVersioningIsConfigured` and `TestDeterministicWorkflowCode`.
Statements that catalog, customer, notification, or reporting lack a Temporal
worker or Workflow SHALL be removed.

#### Scenario: Temporal traceability matches implementation

- **WHEN** traceability is validated for an inventoried service
- **THEN** worker-versioning and deterministic-workflow are implemented
- **AND** both mapped test functions exist in `test/architecture/`

#### Scenario: Stale Temporal deferral fails review

- **WHEN** a traceability manifest or exception file says an inventoried
  service has no Temporal worker or Workflow
- **THEN** the documentation and spec synchronization gate fails
- **AND** the stale deferral cannot be retained for archive

#### Scenario: Implemented test is missing

- **WHEN** traceability marks a category implemented but the named test
  function is absent
- **THEN** the owning service verification gate exits non-zero
