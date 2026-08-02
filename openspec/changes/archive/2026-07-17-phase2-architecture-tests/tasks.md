# Phase 2: Architecture Tests -- Implementation Tasks

## 1. Shared Helpers -- platform/testutil/architecture

### 1.1 Create shared architecture test helper package
- [x] Create `platform/testutil/architecture/helpers.go` -- `ModuleRoot()`, `WalkGoFiles()`, `ParseImports()`, `HasPortSuffix()`, `VendorPatterns()`, `SchemaNameFromMigration()`
- [x] Create `platform/testutil/architecture/helpers_test.go` -- unit tests for all shared helpers

## 2. adapter-implements-exactly-one-port (All 8 Services)

### 2.1 payment-service
- [x] Create `services/payment-service/test/architecture/adapter_port_test.go` -- `TestAdapterImplementsExactlyOnePort`

### 2.2 inventory-service
- [x] Create `services/inventory-service/test/architecture/adapter_port_test.go` -- `TestAdapterImplementsExactlyOnePort`

### 2.3 shipping-service
- [x] Create `services/shipping-service/test/architecture/adapter_port_test.go` -- `TestAdapterImplementsExactlyOnePort`

### 2.4 notification-service
- [x] Create `services/notification-service/test/architecture/adapter_port_test.go` -- `TestAdapterImplementsExactlyOnePort`

### 2.5 customer-service
- [x] Create `services/customer-service/test/architecture/adapter_port_test.go` -- `TestAdapterImplementsExactlyOnePort`

### 2.6 catalog-service
- [x] Create `services/catalog-service/test/architecture/adapter_port_test.go` -- `TestAdapterImplementsExactlyOnePort`

### 2.7 reporting-service
- [x] Create `services/reporting-service/test/architecture/adapter_port_test.go` -- `TestAdapterImplementsExactlyOnePort`

### 2.8 order-service
- [x] Create `services/order-service/test/architecture/adapter_port_test.go` -- `TestAdapterImplementsExactlyOnePort`

## 3. no-peer-service-imports (All 8 Services)

### 3.1 payment-service
- [x] Create `services/payment-service/test/architecture/peer_import_test.go` -- `TestNoPeerServiceImports`

### 3.2 inventory-service
- [x] Create `services/inventory-service/test/architecture/peer_import_test.go` -- `TestNoPeerServiceImports`

### 3.3 shipping-service
- [x] Create `services/shipping-service/test/architecture/peer_import_test.go` -- `TestNoPeerServiceImports`

### 3.4 notification-service
- [x] Create `services/notification-service/test/architecture/peer_import_test.go` -- `TestNoPeerServiceImports`

### 3.5 customer-service
- [x] Create `services/customer-service/test/architecture/peer_import_test.go` -- `TestNoPeerServiceImports`

### 3.6 catalog-service
- [x] Create `services/catalog-service/test/architecture/peer_import_test.go` -- `TestNoPeerServiceImports`

### 3.7 reporting-service
- [x] Create `services/reporting-service/test/architecture/peer_import_test.go` -- `TestNoPeerServiceImports`

### 3.8 order-service
- [x] Create `services/order-service/test/architecture/peer_import_test.go` -- `TestNoPeerServiceImports`

## 4. build-tag-isolation (All 8 Services)

### 4.1 payment-service
- [x] Create `services/payment-service/test/architecture/build_tag_test.go` -- `TestBuildTagIsolation`

### 4.2 inventory-service
- [x] Create `services/inventory-service/test/architecture/build_tag_test.go` -- `TestBuildTagIsolation`

### 4.3 shipping-service
- [x] Create `services/shipping-service/test/architecture/build_tag_test.go` -- `TestBuildTagIsolation`

### 4.4 notification-service
- [x] Create `services/notification-service/test/architecture/build_tag_test.go` -- `TestBuildTagIsolation`

### 4.5 customer-service
- [x] Create `services/customer-service/test/architecture/build_tag_test.go` -- `TestBuildTagIsolation`

### 4.6 catalog-service
- [x] Create `services/catalog-service/test/architecture/build_tag_test.go` -- `TestBuildTagIsolation`

### 4.7 reporting-service
- [x] Create `services/reporting-service/test/architecture/build_tag_test.go` -- `TestBuildTagIsolation`

### 4.8 order-service
- [x] Create `services/order-service/test/architecture/build_tag_test.go` -- `TestBuildTagIsolation`

## 5. cache-keyspace (catalog-service Only)

### 5.1 catalog-service
- [x] Create `services/catalog-service/test/architecture/cache_keyspace_test.go` -- `TestCacheAdmissionGateForbidsRedisImport`
- [x] Create `services/catalog-service/test/architecture/exceptions.go` -- document deferred categories (worker-versioning, deterministic-workflow)

## 6. worker-versioning (5 Services with Temporal Workers)

### 6.1 payment-service
- [x] Create `services/payment-service/test/architecture/worker_version_test.go` -- `TestWorkerVersioningIsConfigured`

### 6.2 inventory-service
- [x] Create `services/inventory-service/test/architecture/worker_version_test.go` -- `TestWorkerVersioningIsConfigured`

### 6.3 shipping-service
- [x] Create `services/shipping-service/test/architecture/worker_version_test.go` -- `TestWorkerVersioningIsConfigured`

### 6.4 notification-service
- [x] Create `services/notification-service/test/architecture/worker_version_test.go` -- `TestWorkerVersioningIsConfigured`

### 6.5 order-service
- [x] Create `services/order-service/test/architecture/worker_version_test.go` -- `TestWorkerVersioningIsConfigured`

## 7. deterministic-workflow (4 Services with Temporal Workflows)

### 7.1 payment-service
- [x] Create `services/payment-service/test/architecture/deterministic_workflow_test.go` -- `TestDeterministicWorkflowCode`

### 7.2 inventory-service
- [x] Create `services/inventory-service/test/architecture/deterministic_workflow_test.go` -- `TestDeterministicWorkflowCode`

### 7.3 shipping-service
- [x] Create `services/shipping-service/test/architecture/deterministic_workflow_test.go` -- `TestDeterministicWorkflowCode`

### 7.4 order-service
- [x] Create `services/order-service/test/architecture/deterministic_workflow_test.go` -- `TestDeterministicWorkflowCode`

## 8. contract-versioning (All 8 Services)

### 8.1 payment-service
- [x] Create `services/payment-service/test/architecture/contract_version_test.go` -- `TestContractVersioningCompliance`

### 8.2 inventory-service
- [x] Create `services/inventory-service/test/architecture/contract_version_test.go` -- `TestContractVersioningCompliance`

### 8.3 shipping-service
- [x] Create `services/shipping-service/test/architecture/contract_version_test.go` -- `TestContractVersioningCompliance`

### 8.4 notification-service
- [x] Create `services/notification-service/test/architecture/contract_version_test.go` -- `TestContractVersioningCompliance`

### 8.5 customer-service
- [x] Create `services/customer-service/test/architecture/contract_version_test.go` -- `TestContractVersioningCompliance`

### 8.6 catalog-service
- [x] Create `services/catalog-service/test/architecture/contract_version_test.go` -- `TestContractVersioningCompliance`

### 8.7 reporting-service
- [x] Create `services/reporting-service/test/architecture/contract_version_test.go` -- `TestContractVersioningCompliance`

### 8.8 order-service
- [x] Create `services/order-service/test/architecture/contract_version_test.go` -- `TestContractVersioningCompliance`

## 9. Exception Documentation (Non-Applicable Categories)

### 9.1 Create exceptions files for services skipping categories
- [x] Create `services/catalog-service/test/architecture/exceptions.go` -- defer worker-versioning, deterministic-workflow (no Temporal worker)
- [x] Create `services/customer-service/test/architecture/exceptions.go` -- defer worker-versioning, deterministic-workflow, cache-keyspace (no Temporal, no cache)
- [x] Create `services/reporting-service/test/architecture/exceptions.go` -- defer deterministic-workflow (Temporal worker exists but no workflow in application layer)

## 10. Traceability Manifest Updates

### 10.1 Update verification/traceability.yaml for each service
- [x] Update `services/payment-service/verification/traceability.yaml` -- add entries for adapter-port, peer-import, build-tag, worker-versioning, deterministic-workflow, contract-versioning
- [x] Update `services/inventory-service/verification/traceability.yaml` -- add entries for adapter-port, peer-import, build-tag, worker-versioning, deterministic-workflow, contract-versioning
- [x] Update `services/shipping-service/verification/traceability.yaml` -- add entries for adapter-port, peer-import, build-tag, worker-versioning, deterministic-workflow, contract-versioning
- [x] Update `services/notification-service/verification/traceability.yaml` -- add entries for adapter-port, peer-import, build-tag, worker-versioning, contract-versioning; defer deterministic-workflow
- [x] Update `services/customer-service/verification/traceability.yaml` -- add entries for adapter-port, peer-import, build-tag, contract-versioning; defer worker-versioning, deterministic-workflow, cache-keyspace
- [x] Update `services/catalog-service/verification/traceability.yaml` -- add entries for adapter-port, peer-import, build-tag, cache-keyspace, contract-versioning; defer worker-versioning, deterministic-workflow
- [x] Update `services/reporting-service/verification/traceability.yaml` -- add entries for adapter-port, peer-import, build-tag, worker-versioning, contract-versioning; defer deterministic-workflow
- [x] Update `services/order-service/verification/traceability.yaml` -- add entries for adapter-port, peer-import, build-tag, worker-versioning, deterministic-workflow, contract-versioning

## 11. Verification

- [x] Run `go test ./test/architecture/ -v -count=1` for all 8 services -- all pass
- [x] Run `make verify-pr` for all 8 services -- all pass
- [x] Verify shared helpers compile: `go build ./platform/testutil/architecture/`
- [x] Verify shared helper tests pass: `go test ./platform/testutil/architecture/ -v`
- [x] Verify each service's architecture test count matches expected categories
