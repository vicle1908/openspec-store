# Tasks: Implement Remaining Deferred Items

## Phase 1: Critical -- Test Coverage Gap Closure

### Task 1.1: Add unit tests for inventory-service coverage gaps
- [x] Identify untested domain logic and application handlers in inventory-service
- [x] Write unit tests for inventory reservation, release, and stock level calculations
- [x] Verify unit test count reaches 30+ in domain/application layers
- [x] Verify unit test coverage reaches 90% for domain and application packages

### Task 1.2: Add unit tests for shipping-service coverage gaps
- [x] Identify untested domain logic and application handlers in shipping-service
- [x] Write unit tests for shipping dispatch, tracking, and status transitions
- [x] Verify unit test count reaches 30+ in domain/application layers
- [x] Verify unit test coverage reaches 90% for domain and application packages

### Task 1.3: Add integration tests for payment-service
- [x] Add Docker-backed integration tests for payment-service postgres adapter
- [x] Cover payment record persistence and retrieval paths
- [x] Verify integration test coverage reaches 90% for payment-service

### Task 1.4: Add integration tests for shipping-service
- [x] Add Docker-backed integration tests for shipping-service postgres adapter
- [x] Cover shipment record persistence and retrieval paths
- [x] Verify integration test coverage reaches 90% for shipping-service

### Task 1.5: Add integration tests for customer-service
- [x] Add Docker-backed integration tests for customer-service postgres adapter
- [x] Cover customer profile CRUD and GDPR export/purge workflows
- [x] Verify integration test coverage reaches 90% for customer-service

### Task 1.6: Add integration tests for notification-service
- [x] Add Docker-backed integration tests for notification-service
- [x] Cover notification dispatch and channel selection logic
- [x] Verify integration test coverage reaches 90% for notification-service

### Task 1.7: Add integration tests for catalog-service
- [x] Add Docker-backed integration tests for catalog-service postgres adapter
- [x] Cover product CRUD and pricing snapshot persistence
- [x] Verify integration test coverage reaches 90% for catalog-service

### Task 1.8: Add integration tests for reporting-service
- [x] Add Docker-backed integration tests for reporting-service
- [x] Cover projection and aggregation logic
- [x] Verify integration test coverage reaches 90% for reporting-service

### Task 1.9: Expand cross-service smoke tests
- [x] Add smoke test for customer-service protobuf contract (customer lookup)
- [x] Add smoke test for notification-service protobuf contract (dispatch)
- [x] Add smoke test for catalog-service protobuf contract (product/pricing queries)
- [x] Add smoke test for reporting-service protobuf contract (order event envelope)
- [x] Verify all smoke tests pass in CI

### Task 1.10: Verify architecture test coverage across all 8 services
- [x] Run architecture tests for all 8 services
- [x] Identify services below 80% architecture test coverage
- [x] Add architecture tests for hexagonal dependency enforcement, domain isolation, and contract compliance where missing
- [x] Verify architecture test coverage reaches 80% for each service

### Task 1.11: Update CI to enforce coverage thresholds
- [x] Add coverage threshold checks to the CI pipeline
- [x] Configure `make services-verify` to fail if any service is below threshold
- [x] Document the coverage thresholds in the operational-readiness spec

## Phase 2: High -- ArgoCD repoURL

### Task 2.1: Fix ArgoCD repoURL placeholder
- [x] Identify the actual Git repository URL for the project
- [x] Update all ArgoCD Application manifests to use the real repoURL
- [x] Validate ArgoCD sync against staging environment
- [x] Verify the Application resources render correctly with `argocd app diff`

## Phase 3: Medium -- Worker Versioning v2 and Kafka Retry

### Task 3.1: Wire Worker Versioning v2 for notification-service
- [x] Add `UseVersioning: true` and `DeploymentSeriesName` to notification-service worker
- [x] Add `UseVersioning: true` to notification-service `startWorkflow` calls
- [x] Run replay tests to verify non-determinism safety
- [x] Deploy to staging and verify workflow execution

### Task 3.2: Wire Worker Versioning v2 for catalog-service
- [x] Add `UseVersioning: true` and `DeploymentSeriesName` to catalog-service worker
- [x] Add `UseVersioning: true` to catalog-service `startWorkflow` calls
- [x] Run replay tests to verify non-determinism safety
- [x] Deploy to staging and verify workflow execution

### Task 3.3: Wire Worker Versioning v2 for inventory-service
- [x] Add `UseVersioning: true` and `DeploymentSeriesName` to inventory-service worker
- [x] Add `UseVersioning: true` to inventory-service `startWorkflow` calls
- [x] Run replay tests to verify non-determinism safety
- [x] Deploy to staging and verify workflow execution

### Task 3.4: Wire Worker Versioning v2 for payment-service
- [x] Add `UseVersioning: true` and `DeploymentSeriesName` to payment-service worker
- [x] Add `UseVersioning: true` to payment-service `startWorkflow` calls
- [x] Run replay tests to verify non-determinism safety
- [x] Deploy to staging and verify workflow execution

### Task 3.5: Wire Worker Versioning v2 for shipping-service
- [x] Add `UseVersioning: true` and `DeploymentSeriesName` to shipping-service worker
- [x] Add `UseVersioning: true` to shipping-service `startWorkflow` calls
- [x] Run replay tests to verify non-determinism safety
- [x] Deploy to staging and verify workflow execution

### Task 3.6: Wire Worker Versioning v2 for customer-service
- [x] Add `UseVersioning: true` and `DeploymentSeriesName` to customer-service worker
- [x] Add `UseVersioning: true` to customer-service `startWorkflow` calls
- [x] Run replay tests to verify non-determinism safety
- [x] Deploy to staging and verify workflow execution

### Task 3.7: Wire Worker Versioning v2 for reporting-service
- [x] Add `UseVersioning: true` and `DeploymentSeriesName` to reporting-service worker
- [x] Add `UseVersioning: true` to reporting-service `startWorkflow` calls
- [x] Run replay tests to verify non-determinism safety
- [x] Deploy to staging and verify workflow execution

### Task 3.8: Wire Worker Versioning v2 for order-service
- [x] Ensure existing partial registration is complete with `UseVersioning: true` on both worker and caller
- [x] Run replay tests to verify non-determinism safety
- [x] Deploy to staging and verify workflow execution
- [x] Deploy to production with monitoring

### Task 3.9: Add architecture test for Worker Versioning v2
- [x] Add architecture test that scans all 8 services for `UseVersioning: true`
- [x] Verify the test fails if any service is missing Worker Versioning v2 configuration
- [x] Integrate the test into `make services-verify`

### Task 3.10: Implement RetryConsumer for Kafka retry-topic chain
- [x] Implement `RetryConsumer` that reads from retry topics, delays, and re-publishes to source topic
- [x] Wire the retry-topic chain: `<source-topic>.retry.1000`, `.retry.8000`, `.retry.60000`, `.retry.300000`, `.retry.1800000`
- [x] Implement DLQ routing after final retry attempt
- [x] Preserve `traceparent`, `X-Correlation-Id`, `X-Request-Id`, `X-Causation-Id` headers across retries

### Task 3.11: Add retry-topic chain tests
- [x] Unit test: RetryConsumer delays before re-publishing
- [x] Unit test: Retry count increments correctly
- [x] Unit test: DLQ routing after final attempt
- [x] Integration test: End-to-end retry chain with Docker Compose Kafka
- [x] Integration test: Non-retryable error routes directly to DLQ

## Completion Criteria

- [x] All 8 services meet 90/90/80 coverage thresholds (unit/integration/architecture)
- [x] ArgoCD syncs successfully against staging with real repoURL
- [x] All 8 Temporal workers register with Worker Versioning v2
- [x] Kafka retry-topic chain processes retries with exponential backoff
- [x] All tasks independently verifiable via `make services-verify`
