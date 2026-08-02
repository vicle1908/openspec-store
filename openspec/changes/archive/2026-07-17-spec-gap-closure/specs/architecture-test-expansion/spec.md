# architecture-test-expansion Specification (delta)

## Purpose

Most services in the platform have only a single architecture test file (`layering_test.go`) covering 1-2 of the 12+ required architecture test categories defined in `platform-hexagonal-enforcement`. Only `order-service` has comprehensive architecture tests (layering, enforcement, phase2, adr_0006), and only `reporting-service` has a sole-writer test beyond layering. This delta expands every service's architecture test suite to cover all applicable categories from the canonical list, wires them into the CI gate, and makes coverage trackable in the verification manifest.

## ADDED Requirements

### Requirement: Every service SHALL have architecture tests for all applicable categories

Each service SHALL maintain architecture tests in `test/architecture/` that cover every category from the following table for which the service is applicable. A service is "applicable" to a category when the category's prerequisite applies (e.g., cache-keyspace only applies when the service uses the platform cache; worker-versioning and deterministic-workflow only apply when the service has a Temporal worker; contract-versioning only applies when the service exposes or consumes Protobuf contracts).

| Category | Test function pattern | Applicability |
|---|---|---|
| domain-purity | `TestDomainDoesNotImportAdapters` | All services |
| sole-writer | `TestSoleWriterRule` / `TestDatabaseTablesOwnedBySingleService` | All services with a Postgres schema |
| ports-are-interfaces | `TestPortsAreInterfaces` | All services with `internal/ports/` |
| adapter-implements-exactly-one-port | `TestAdapterImplementsExactlyOnePort` | All services with `internal/adapters/` |
| no-peer-service-imports | `TestHypotheticalPeerServiceCannotImport*` | All services |
| build-tag-isolation | `TestBuildTagIsolation` | All services with vendor SDK imports in domain/application/ports |
| layering | `TestDomainDoesNotImportAdaptersOrApplicationOrPorts` | All services |
| cache-keyspace | `TestCacheAdmissionGateForbidsRedisImport` | Services using `platform/cache` |
| worker-versioning | `TestWorkerVersioningIsConfigured` | Services with a Temporal worker |
| deterministic-workflow | `TestDeterministicWorkflowCode` | Services with Temporal workflows |
| domain-invariants | `TestDomainInvariantsAreEnforced` | All services with aggregate roots |
| contract-versioning | `TestContractVersioningCompliance` | Services exposing or consuming Protobuf contracts |

A service MUST NOT skip an applicable category without a documented exception in `test/architecture/exceptions.go` and an entry in the traceability manifest. The list of categories per service SHALL be maintained in the service's `test/architecture/README.md` or inline comments in the test package.

#### Scenario: Service with minimal infrastructure has at least seven test categories
- **WHEN** the notification-service (which has no Kafka adapter, no Temporal worker, no Redis cache, and no Protobuf contracts) architecture test suite is inspected
- **THEN** it contains tests for domain-purity, sole-writer, ports-are-interfaces, adapter-implements-exactly-one-port, no-peer-service-imports, build-tag-isolation, layering, and domain-invariants (8 categories minimum)

#### Scenario: Service with Temporal worker has at least ten test categories
- **WHEN** the order-service architecture test suite is inspected
- **THEN** it contains tests for all 12 categories: domain-purity, sole-writer, ports-are-interfaces, adapter-implements-exactly-one-port, no-peer-service-imports, build-tag-isolation, layering, cache-keyspace, worker-versioning, deterministic-workflow, domain-invariants, and contract-versioning

#### Scenario: Service with cache but no Temporal skips worker categories
- **WHEN** the catalog-service (which uses `platform/cache` but has no Temporal worker) architecture test suite is inspected
- **THEN** it contains tests for all categories except worker-versioning and deterministic-workflow, and the cache-keyspace test IS present

#### Scenario: Applicable category without a test fails the gate
- **WHEN** a new service is added with `internal/ports/` but no `TestPortsAreInterfaces` test
- **THEN** `make verify-pr` exits non-zero with a message identifying the missing category

### Requirement: Architecture tests SHALL be executable via make verify-pr

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

Every architecture test SHALL have a corresponding entry in the service's `verification/traceability.yaml` manifest. Each entry SHALL identify the architecture test category, the test function name, the tier (`architecture`), and the status (`implemented`, `planned`, or `deferred`). A service MUST NOT have an architecture test category marked as `implemented` in the spec without a corresponding passing verification entry. The traceability manifest SHALL be updated whenever an architecture test is added, removed, or its status changes.

#### Scenario: Architecture test has a traceability entry
- **WHEN** the notification-service adds `TestPortsAreInterfaces` to `test/architecture/`
- **THEN** `verification/traceability.yaml` contains an entry with `id: "AT-NOTIF-NNN"`, `capability: "architecture-test-expansion"`, `scenario: "ports-are-interfaces"`, `tier: "architecture"`, `target: "test/architecture/"`, and `status: "implemented"`

#### Scenario: Traceability manifest is checked by verify-pr
- **WHEN** `make verify-pr` runs and a new architecture test exists without a traceability entry
- **THEN** the pipeline emits a warning (or fails, per the platform-verification spec's traceability enforcement) indicating the unmapped architecture test

#### Scenario: Deferred category has a traceability entry with rationale
- **WHEN** the catalog-service defers `TestWorkerVersioningIsConfigured` because it has no Temporal worker
- **THEN** `verification/traceability.yaml` contains an entry with `status: "deferred"` and a `rationale` field stating "no Temporal worker in catalog-service"

### Requirement: Shared architecture test helpers SHALL be extracted to the platform module

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
