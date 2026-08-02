# architecture-test-expansion Specification

## Purpose

Most services in the platform have only a single architecture test file (`layering_test.go`) covering 1-2 of the 12+ required architecture test categories defined in `platform-hexagonal-enforcement`. Only `order-service` has comprehensive architecture tests (layering, enforcement, phase2, adr_0006), and only `reporting-service` has a sole-writer test beyond layering. This delta expands every service's architecture test suite to cover all applicable categories from the canonical list, wires them into the CI gate, and makes coverage trackable in the verification manifest.

## Requirements

> **Status**: PARTIAL. Order-service and payment-service have architecture tests; other services lack comprehensive category coverage. Shared helpers partially extracted.
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

### Requirement: Architecture tests SHALL be executable via make verify-pr

> **Status**: PARTIAL. Makefile exists with verify targets; architecture test integration is partial.

Every architecture test in `test/architecture/` SHALL be invoked by the `make verify-pr` target. The architecture tests SHALL run before unit tests so that a layering violation fails fast. The architecture tests SHALL run as part of the service's CI pipeline and SHALL block merge on failure. The `make verify-pr` target SHALL execute `go test ./test/architecture/ -v -count=1` (or the equivalent test path) and SHALL exit non-zero if any architecture test fails.

#### Scenario: make verify-pr runs architecture tests first
- **WHEN** `make verify-pr` runs for any service
- **THEN** the architecture tests in `test/architecture/` complete before the unit tests in `internal/` start

#### Scenario: make verify-pr fails on architecture violation
- **WHEN** a developer introduces a layering violation (e.g., an import from `internal/adapters/` in `internal/domain/`)
- **THEN** `make verify-pr` exits non-zero and the failure message identifies the violating file, line, and category

#### Scenario: make verify-pr succeeds with no violations
- **WHEN** `make verify-pr` runs against a service with no architecture violations
- **THEN** the architecture tests all pass and the pipeline proceeds to unit tests

### Requirement: New services SHALL include architecture tests before merge

> **Status**: DEFERRED. No CI gate enforcement found for new service architecture tests.

Every new service SHALL include architecture tests covering all applicable categories from the category table before its first merge to `main`. A pull request that adds a new service under `services/` MUST NOT be merged unless the service's `test/architecture/` directory contains at minimum the domain-purity, sole-writer, layering, and no-peer-service-imports tests. The CI pipeline SHALL reject a new service PR that lacks these minimum architecture tests.

#### Scenario: New service PR is blocked without architecture tests
- **WHEN** a pull request adds a new service directory (e.g., `services/loyalty-service/`) without `test/architecture/` tests
- **THEN** the CI pipeline fails the PR gate with a message indicating missing architecture tests for the new service

#### Scenario: New service PR passes with minimum architecture tests
- **WHEN** a pull request adds a new service with `test/architecture/` containing at least domain-purity, sole-writer, layering, and no-peer-service-imports tests
- **THEN** the CI pipeline passes the architecture test gate for the new service

#### Scenario: New service with Temporal worker includes temporal categories
- **WHEN** a pull request adds a new service that includes a Temporal worker and workflow code
- **THEN** the service's `test/architecture/` directory MUST include `TestWorkerVersioningIsConfigured` and `TestDeterministicWorkflowCode` before merge

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

### Requirement: Shared architecture test helpers SHALL be extracted to the platform module

> **Status**: PARTIAL. platform/testutil/architecture exists; shared helpers extraction is partial.

Common architecture test utilities (module root detection, file walking, vendor pattern matching, port suffix lists, schema name extraction) SHALL be extracted to a shared package under `platform/testutil/architecture/` (or equivalent). Each service's `test/architecture/` tests SHALL import the shared utilities rather than duplicating helper logic. The shared utilities SHALL be unit-tested in the platform module.

#### Scenario: Services import shared architecture test helpers
- **WHEN** the inventory-service's `test/architecture/layering_test.go` is inspected
- **THEN** it imports `platform/testutil/architecture` (or equivalent shared path) for `moduleRoot()`, `hasPortSuffix()`, and vendor pattern lists instead of defining them locally

#### Scenario: Shared helpers are themselves tested
- **WHEN** the platform module's `testutil/architecture` package is inspected
- **THEN** it contains a `helpers_test.go` that verifies `moduleRoot()` resolves correctly, `hasPortSuffix()` matches expected suffixes, and vendor pattern lists are non-empty

#### Scenario: Existing services are migrated to shared helpers
- **WHEN** a service's `test/architecture/helpers_test.go` is inspected after migration
- **THEN** the local `moduleRoot()`, `hasPortSuffix()`, and vendor pattern definitions are removed or reduced to thin wrappers around the shared package
