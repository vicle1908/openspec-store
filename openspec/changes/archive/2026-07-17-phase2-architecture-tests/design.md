# phase2-architecture-tests Design

## Context

The monorepo has 8 Go services. Phase 1 added 4 architecture test categories (layering, sole-writer, ports-are-interfaces, domain-purity) to the 7 non-order services. The `architecture-test-expansion` spec defines 12 categories total. Phase 2 adds the remaining 7 categories:

| Category | Services | Current state |
|---|---|---|
| adapter-implements-exactly-one-port | All 8 | Missing everywhere |
| no-peer-service-imports | All 8 | Missing everywhere |
| build-tag-isolation | All 8 | Missing everywhere |
| cache-keyspace | catalog-service only | Missing |
| worker-versioning | payment, inventory, shipping, notification, order | Missing |
| deterministic-workflow | payment, inventory, shipping, order | Missing |
| contract-versioning | All 8 | Missing everywhere |

The order-service has the most complete architecture test suite (layering, enforcement, phase2, adr_0006) but also lacks the 7 new categories.

## Goals / Non-Goals

**Goals:**
- Every service has architecture tests for all 12 applicable categories (or documented exceptions for non-applicable ones)
- Shared architecture test helpers are extracted to `platform/testutil/architecture/`
- Each service's `test/architecture/` imports shared helpers instead of duplicating logic
- All new tests pass `go test ./test/architecture/ -v -count=1`
- `verification/traceability.yaml` is updated for every new test

**Non-Goals:**
- Modifying service production code (tests are static analysis of existing code)
- Adding new services or changing service boundaries
- Changing the CI pipeline (existing `make verify-pr` already runs architecture tests)
- Phase 1 test category migrations (layering, sole-writer, ports, domain-purity stay as-is; shared helper extraction is a separate cleanup task)

## Decisions

### D1: Each new test category gets its own file per service

Rationale: The existing convention is one file per category (`layering_test.go`, `solewriter_test.go`, `ports_test.go`, `domain_test.go`). New categories follow the same pattern: `adapter_port_test.go`, `peer_import_test.go`, `build_tag_test.go`, `cache_keyspace_test.go`, `worker_version_test.go`, `deterministic_workflow_test.go`, `contract_version_test.go`. This keeps the test package organized and makes it easy to identify which category failed.

### D2: Shared helpers extracted to `platform/testutil/architecture/`

Rationale: The spec requires shared helpers. The package provides:
- `ModuleRoot(t *testing.T) string` -- resolves go.mod root
- `WalkGoFiles(root, pattern string) ([]string, error)` -- walks .go files
- `ParseImports(t *testing.T, file string) []string` -- extracts import paths
- `HasPortSuffix(name string) bool` -- checks port interface naming
- `VendorPatterns() []string` -- returns vendor SDK import prefixes
- `SchemaNameFromMigration(content string) string` -- extracts schema from SQL

Each service's tests import these helpers. The package has its own `helpers_test.go`.

### D3: Cross-service import test runs from root module

Rationale: `no-peer-service-imports` requires knowledge of every service module. The test lives in each service's `test/architecture/peer_import_test.go` but validates against the monorepo root's go.mod module paths. It parses the go.sum or uses `go list -m` to enumerate all service modules, then checks that no file under `internal/` imports another service's `internal/`.

### D4: Build-tag isolation test scans for vendor imports without build tags

Rationale: The test walks `internal/domain/`, `internal/application/`, and `internal/ports/` and fails if any file imports a vendor SDK (Stripe, SendGrid, Twilio, franz-go, etc.) that is NOT gated behind a `//go:build` tag. This prevents accidental vendor coupling in domain logic.

### D5: Worker-versioning test checks for `TaskQueue` and version registration

Rationale: The test verifies that `internal/runtime/worker.go` (or equivalent) configures a Temporal worker with a named task queue and registers workflow/activity versions. It scans for `worker.Options{TaskQueue: ...}` and `workflow.SetLogger` or version registration patterns.

### D6: Deterministic-workflow test scans for non-deterministic primitives

Rationale: The test walks `internal/application/orchestration/workflow.go` (or equivalent) and fails if it finds `time.Now()`, `math/rand`, `rand.Intn()`, UUID generation, or HTTP calls outside of activities. Temporal workflows must be deterministic; side effects belong in activities.

### D7: Contract-versioning test checks Protobuf package versioning

Rationale: The test scans `proto/` directories for `.proto` files and verifies: (1) each package has a version suffix (e.g., `v1`, `v2`), (2) no `BREAKING_CHANGE` annotations exist without a major version bump, (3) generated `.pb.go` files exist under `contracts/` matching the proto definitions.

### D8: Cache-keyspace test is catalog-service only

Rationale: Only catalog-service uses `platform/cache` (Redis). The test verifies that `internal/domain/` and `internal/ports/` do NOT import `github.com/redis` or `platform/cache` directly -- cache admission is controlled through the port interface.

### D9: Services with no Temporal worker skip worker-versioning and deterministic-workflow

Rationale: catalog-service, customer-service, and reporting-service (reporting has Temporal adapters but no workflows in `internal/application/`) skip these categories with a documented exception in `test/architecture/exceptions.go`.

Wait -- reporting-service has `internal/adapters/temporal/workflow.go`. Let me re-check. Reporting-service has Temporal adapters but the workflow is in adapters, not application. The deterministic-workflow test targets `internal/application/orchestration/` specifically. So reporting-service skips deterministic-workflow but may need worker-versioning if it has a worker.

Actually, reporting-service has `internal/adapters/temporal/worker.go` -- so it HAS a Temporal worker. It should get worker-versioning but not deterministic-workflow (no workflow in application layer).

## Risks / Trade-offs

### R1: Cross-service import test complexity
**Risk:** The `no-peer-service-imports` test needs to know all service module paths, which may change as services are added.
**Mitigation:** The test dynamically discovers service modules by scanning `services/*/go.mod` rather than hardcoding paths. Adding a new service automatically includes it in the check.

### R2: Build-tag vendor patterns may drift
**Risk:** New vendor SDKs added to the platform may not be in the test's pattern list.
**Mitigation:** The shared `VendorPatterns()` function in `platform/testutil/architecture/` is the single source of truth. Adding a new vendor pattern is a one-line change.

### R3: Deterministic-workflow false positives
**Risk:** The test may flag legitimate uses of `time.Now()` in workflow code (e.g., in comments or string literals).
**Mitigation:** The test parses Go AST and checks only import statements and function call expressions, not string contents. False positives from comments are avoided by using `ast.Inspect` with proper node type filtering.

### R4: Contract-versioning test may be too strict
**Risk:** Proto files with non-standard naming may cause false failures.
**Mitigation:** The test checks for version suffixes using a flexible regex (`v\d+`) and provides clear error messages showing the expected format. Services with custom proto layouts can document exceptions.
