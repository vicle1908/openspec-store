# architecture-test-expansion Delta -- Phase 2 Implementation

## MODIFIED Requirements

### Requirement: Every service SHALL have architecture tests for all applicable categories

> **Status**: IN PROGRESS. Phase 2 implements the remaining 7 architecture test categories.

The following test categories are missing from all or most services and SHALL be added in Phase 2:

| Category | Test function | Missing from | Applicability |
|---|---|---|---|
| adapter-implements-exactly-one-port | `TestAdapterImplementsExactlyOnePort` | All 8 services | All services with `internal/adapters/` |
| no-peer-service-imports | `TestHypotheticalPeerServiceCannotImport*` | All 8 services | All services |
| build-tag-isolation | `TestBuildTagIsolation` | All 8 services | All services |
| cache-keyspace | `TestCacheAdmissionGateForbidsRedisImport` | catalog-service | Services using `platform/cache` |
| worker-versioning | `TestWorkerVersioningIsConfigured` | payment, inventory, shipping, notification, order | Services with a Temporal worker |
| deterministic-workflow | `TestDeterministicWorkflowCode` | payment, inventory, shipping, order | Services with Temporal workflows in `internal/application/` |
| contract-versioning | `TestContractVersioningCompliance` | All 8 services | All services exposing or consuming Protobuf contracts |

#### Scenario: Adapter implements exactly one port interface
- **WHEN** `TestAdapterImplementsExactlyOnePort` runs against a service with `internal/adapters/`
- **THEN** the test verifies that each adapter package under `internal/adapters/<kind>/` implements exactly one port interface from `internal/ports/`
- **AND** the test fails if an adapter implements zero ports or more than one port

#### Scenario: No peer-service internal imports
- **WHEN** `TestHypotheticalPeerServiceCannotImport*` runs for any service
- **THEN** the test walks every `.go` file under `internal/` and confirms no import path matches `services/<peer-service>/internal/`
- **AND** the test dynamically discovers all service modules from `services/*/go.mod`

#### Scenario: Build-tag isolation for vendor SDKs
- **WHEN** `TestBuildTagIsolation` runs against a service
- **THEN** the test scans `internal/domain/`, `internal/application/`, and `internal/ports/` for imports matching known vendor SDK patterns (Stripe, SendGrid, Twilio, franz-go, etc.)
- **AND** the test fails if any vendor SDK import is found without a `//go:build` tag gating it

#### Scenario: Cache admission gate for catalog-service
- **WHEN** `TestCacheAdmissionGateForbidsRedisImport` runs against catalog-service
- **THEN** the test verifies that `internal/domain/` and `internal/ports/` do NOT import `github.com/redis` or `platform/cache` directly
- **AND** cache access is mediated through the port interface in `internal/ports/cache.go`

#### Scenario: Worker versioning is configured
- **WHEN** `TestWorkerVersioningIsConfigured` runs against a service with a Temporal worker
- **THEN** the test verifies that `internal/runtime/worker.go` (or equivalent) configures a named `TaskQueue` in `worker.Options`
- **AND** the test verifies that workflow and activity versions are registered

#### Scenario: Deterministic workflow code
- **WHEN** `TestDeterministicWorkflowCode` runs against a service with Temporal workflows
- **THEN** the test scans `internal/application/orchestration/workflow*.go` for non-deterministic primitives (`time.Now()`, `math/rand`, `rand.Intn()`, UUID generation, HTTP calls)
- **AND** the test fails if any non-deterministic call is found outside of activity functions

#### Scenario: Contract versioning compliance
- **WHEN** `TestContractVersioningCompliance` runs against a service with Protobuf contracts
- **THEN** the test verifies that each `.proto` file under `proto/` has a package name with a version suffix (e.g., `v1`, `v2`)
- **AND** the test verifies that generated `.pb.go` files exist under `contracts/` matching the proto definitions

### Requirement: Shared architecture test helpers SHALL be extracted to the platform module

> **Status**: IN PROGRESS. Phase 2 implements the shared helper extraction.

The following helpers SHALL be provided by `platform/testutil/architecture/`:

| Helper | Purpose |
|---|---|
| `ModuleRoot(t *testing.T) string` | Resolves the repository root by walking up to `go.mod` |
| `WalkGoFiles(root, pattern string) ([]string, error)` | Walks `.go` files matching a glob pattern |
| `ParseImports(t *testing.T, file string) []string` | Extracts import paths from a Go source file |
| `HasPortSuffix(name string) bool` | Checks if a type name ends with a port suffix (`er`, `Reader`, `Writer`, `Repository`, `Store`, `Gateway`, `Publisher`, `Subscriber`) |
| `VendorPatterns() []string` | Returns known vendor SDK import prefixes |
| `SchemaNameFromMigration(content string) string` | Extracts schema name from SQL migration content |

#### Scenario: Services import shared architecture test helpers
- **WHEN** any service's `test/architecture/` test file is inspected
- **THEN** it imports `platform/testutil/architecture` for `ModuleRoot()`, `HasPortSuffix()`, `VendorPatterns()`, and other shared utilities

#### Scenario: Shared helpers are themselves tested
- **WHEN** the platform module's `testutil/architecture` package is inspected
- **THEN** it contains a `helpers_test.go` that verifies `ModuleRoot()` resolves correctly, `HasPortSuffix()` matches expected suffixes, and `VendorPatterns()` is non-empty

### Requirement: Architecture test coverage SHALL be tracked in verification/traceability.yaml

> **Status**: IN PROGRESS. Phase 2 adds traceability entries for all new architecture test categories.

Each new architecture test category SHALL have a corresponding entry in the service's `verification/traceability.yaml` manifest with:
- `id`: `AT-<SERVICE>-<NNN>` (sequential numbering per service)
- `capability`: `architecture-test-expansion`
- `scenario`: the category name (e.g., `adapter-implements-exactly-one-port`)
- `tier`: `architecture`
- `target`: `test/architecture/`
- `status`: `implemented` (or `deferred` with rationale for non-applicable categories)

#### Scenario: Deferred category has documented exception
- **WHEN** a service does not apply to a category (e.g., catalog-service has no Temporal worker)
- **THEN** `test/architecture/exceptions.go` contains a comment documenting the exception
- **AND** `verification/traceability.yaml` has an entry with `status: "deferred"` and a `rationale` field
