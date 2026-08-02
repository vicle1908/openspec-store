# phase2-architecture-tests

## Why

Phase 1 closed the unit test count floor (30+ per critical-gap service) and added four foundational architecture test categories (layering, sole-writer, ports-are-interfaces, domain-purity) to all 7 non-order services. However, the `architecture-test-expansion` spec requires 12 architecture test categories per service, and 7 categories remain unimplemented across the platform. This Phase 2 closes the remaining architecture test gaps so that every service's `test/architecture/` suite covers all applicable categories.

## What Changes

- Add `TestAdapterImplementsExactlyOnePort` to all 8 services
- Add `TestHypotheticalPeerServiceCannotImport*` cross-service import checks to all 8 services
- Add `TestBuildTagIsolation` to all 8 services (guards against vendor SDK leakage into domain/application/ports)
- Add `TestCacheAdmissionGateForbidsRedisImport` to catalog-service (only service using platform/cache)
- Add `TestWorkerVersioningIsConfigured` to payment-service, inventory-service, shipping-service, notification-service, and order-service (all have Temporal workers)
- Add `TestDeterministicWorkflowCode` to payment-service, inventory-service, shipping-service, and order-service (services with Temporal workflows)
- Add `TestContractVersioningCompliance` to all 8 services (all expose Protobuf contracts)
- Extract shared architecture test helpers to `platform/testutil/architecture/`
- Update `verification/traceability.yaml` for each service with new architecture test entries

## Capabilities

### New Capabilities

_None. This change implements existing specifications._

### Modified Capabilities

- `architecture-test-expansion`: Implement Phase 2 requirements -- adapter-implements-exactly-one-port, no-peer-service-imports, build-tag-isolation, cache-keyspace, worker-versioning, deterministic-workflow, and contract-versioning test categories across all services

## Impact

**Services affected:**
- `payment-service` -- 5 new architecture tests (adapter-port, peer-import, build-tag, worker-versioning, deterministic-workflow, contract-versioning)
- `inventory-service` -- 5 new architecture tests (adapter-port, peer-import, build-tag, worker-versioning, deterministic-workflow, contract-versioning)
- `shipping-service` -- 5 new architecture tests (adapter-port, peer-import, build-tag, worker-versioning, deterministic-workflow, contract-versioning)
- `notification-service` -- 5 new architecture tests (adapter-port, peer-import, build-tag, worker-versioning, contract-versioning)
- `order-service` -- 4 new architecture tests (adapter-port, peer-import, build-tag, worker-versioning, deterministic-workflow, contract-versioning)
- `catalog-service` -- 4 new architecture tests (adapter-port, peer-import, build-tag, cache-keyspace, contract-versioning)
- `customer-service` -- 3 new architecture tests (adapter-port, peer-import, build-tag, contract-versioning)
- `reporting-service` -- 4 new architecture tests (adapter-port, peer-import, build-tag, worker-versioning, contract-versioning)

**Platform module:**
- New shared package `platform/testutil/architecture/` with reusable helpers for module root detection, file walking, vendor pattern matching, port suffix lists, and schema name extraction

**CI pipeline:**
- `make verify-pr` continues to gate on architecture tests; no pipeline changes required (existing gate already runs all tests in `test/architecture/`)

**Dependencies:**
- None new -- all tests use stdlib `go/ast`, `go/parser`, and `go/token` for static analysis
