# Tasks: Ecosystem Alignment

## Phase 1: Critical -- Test Coverage

### Task 1.1: Measure current test coverage across all 8 services
- [x] [historical] Run `go test -coverprofile=coverage.out ./...` for each service
- [x] [historical] Record unit test coverage percentage per service
- [x] [historical] Record integration test coverage percentage per service
- [x] [historical] Record architecture test coverage percentage per service
- [x] [historical] Compare against 90/90/80 thresholds and document gaps

### Task 1.2: Add unit tests for payment-service coverage gaps
- [x] [historical] Identify untested domain logic and port adapters
- [x] [historical] Write unit tests for payment aggregation, status transitions, and error paths
- [x] [historical] Verify unit test coverage reaches 90%

### Task 1.3: Add unit tests for inventory-service coverage gaps
- [x] [historical] Identify untested domain logic and port adapters
- [x] [historical] Write unit tests for inventory reservation, release, and stock level calculations
- [x] [historical] Verify unit test coverage reaches 90%

### Task 1.4: Add unit tests for shipping-service coverage gaps
- [x] [historical] Identify untested domain logic and port adapters
- [x] [historical] Write unit tests for shipping dispatch, tracking, and status transitions
- [x] [historical] Verify unit test coverage reaches 90%

### Task 1.5: Add unit tests for customer-service coverage gaps
- [x] [historical] Identify untested domain logic and port adapters
- [x] [historical] Write unit tests for customer profile, GDPR export, and purge workflows
- [x] [historical] Verify unit test coverage reaches 90%

### Task 1.6: Add unit tests for notification-service coverage gaps
- [x] [historical] Identify untested domain logic and port adapters
- [x] [historical] Write unit tests for notification dispatch, channel selection, and retry logic
- [x] [historical] Verify unit test coverage reaches 90%

### Task 1.7: Add unit tests for catalog-service coverage gaps
- [x] [historical] Identify untested domain logic and port adapters
- [x] [historical] Write unit tests for catalog product, pricing snapshot, and price rollback
- [x] [historical] Verify unit test coverage reaches 90%

### Task 1.8: Add unit tests for reporting-service coverage gaps
- [x] [historical] Identify untested domain logic and port adapters
- [x] [historical] Write unit tests for reporting projection and aggregation logic
- [x] [historical] Verify unit test coverage reaches 90%

### Task 1.9: Add integration tests for non-order services
- [x] [historical] Add Docker-backed integration tests for payment-service
- [x] [historical] Add Docker-backed integration tests for inventory-service
- [x] [historical] Add Docker-backed integration tests for shipping-service
- [x] [historical] Add Docker-backed integration tests for customer-service
- [x] [historical] Add Docker-backed integration tests for notification-service
- [x] [historical] Add Docker-backed integration tests for catalog-service
- [x] [historical] Add Docker-backed integration tests for reporting-service
- [x] [historical] Verify integration test coverage reaches 90% for each service

### Task 1.10: Verify architecture test coverage
- [x] [historical] Run architecture tests for all 8 services
- [x] [historical] Identify services below 80% architecture test coverage
- [x] [historical] Add architecture tests for hexagonal dependency enforcement, domain isolation, and contract compliance
- [x] [historical] Verify architecture test coverage reaches 80% for each service

### Task 1.11: Update CI to enforce coverage thresholds
- [x] [historical] Add coverage threshold checks to the CI pipeline
- [x] [historical] Configure `make services-verify` to fail if any service is below threshold
- [x] [historical] Document the coverage thresholds in the operational-readiness spec

## Phase 2: High -- ArgoCD and Worker Versioning

### Task 2.1: Fix ArgoCD repoURL placeholder
- [x] [historical] Identify the actual Git repository URL for the project
- [x] [historical] Update all ArgoCD Application manifests to use the real repoURL
- [x] [historical] Validate ArgoCD sync against staging environment
- [x] [historical] Verify the Application resources render correctly with `argocd app diff`

### Task 2.2: Wire Worker Versioning v2 for notification-service
- [x] [historical] Add `UseVersioning: true` and `DeploymentSeriesName` to notification-service worker
- [x] [historical] Add `UseVersioning: true` to notification-service `startWorkflow` calls
- [x] [historical] Run replay tests to verify non-determinism safety
- [x] [historical] Deploy to staging and verify workflow execution

### Task 2.3: Wire Worker Versioning v2 for catalog-service
- [x] [historical] Add `UseVersioning: true` and `DeploymentSeriesName` to catalog-service worker
- [x] [historical] Add `UseVersioning: true` to catalog-service `startWorkflow` calls
- [x] [historical] Run replay tests to verify non-determinism safety
- [x] [historical] Deploy to staging and verify workflow execution

### Task 2.4: Wire Worker Versioning v2 for inventory-service
- [x] [historical] Add `UseVersioning: true` and `DeploymentSeriesName` to inventory-service worker
- [x] [historical] Add `UseVersioning: true` to inventory-service `startWorkflow` calls
- [x] [historical] Run replay tests to verify non-determinism safety
- [x] [historical] Deploy to staging and verify workflow execution

### Task 2.5: Wire Worker Versioning v2 for payment-service
- [x] [historical] Add `UseVersioning: true` and `DeploymentSeriesName` to payment-service worker
- [x] [historical] Add `UseVersioning: true` to payment-service `startWorkflow` calls
- [x] [historical] Run replay tests to verify non-determinism safety
- [x] [historical] Deploy to staging and verify workflow execution

### Task 2.6: Wire Worker Versioning v2 for shipping-service
- [x] [historical] Add `UseVersioning: true` and `DeploymentSeriesName` to shipping-service worker
- [x] [historical] Add `UseVersioning: true` to shipping-service `startWorkflow` calls
- [x] [historical] Run replay tests to verify non-determinism safety
- [x] [historical] Deploy to staging and verify workflow execution

### Task 2.7: Wire Worker Versioning v2 for customer-service
- [x] [historical] Add `UseVersioning: true` and `DeploymentSeriesName` to customer-service worker
- [x] [historical] Add `UseVersioning: true` to customer-service `startWorkflow` calls
- [x] [historical] Run replay tests to verify non-determinism safety
- [x] [historical] Deploy to staging and verify workflow execution

### Task 2.8: Wire Worker Versioning v2 for reporting-service
- [x] [historical] Add `UseVersioning: true` and `DeploymentSeriesName` to reporting-service worker
- [x] [historical] Add `UseVersioning: true` to reporting-service `startWorkflow` calls
- [x] [historical] Run replay tests to verify non-determinism safety
- [x] [historical] Deploy to staging and verify workflow execution

### Task 2.9: Wire Worker Versioning v2 for order-service
- [x] [historical] Ensure existing partial registration is complete with `UseVersioning: true` on both worker and caller
- [x] [historical] Run replay tests to verify non-determinism safety
- [x] [historical] Deploy to staging and verify workflow execution
- [x] [historical] Deploy to production with monitoring

### Task 2.10: Add architecture test for Worker Versioning v2
- [x] [historical] Add architecture test that scans all 8 services for `UseVersioning: true`
- [x] [historical] Verify the test fails if any service is missing Worker Versioning v2 configuration
- [x] [historical] Integrate the test into `make services-verify`

## Phase 3: Medium -- Kafka Retry and Circuit Breaker

### Task 3.1: Implement RetryConsumer for Kafka retry-topic chain
- [x] [historical] Implement `RetryConsumer` that reads from retry topics, delays, and re-publishes to source topic
- [x] [historical] Wire the retry-topic chain: `<source-topic>.retry.1000`, `.retry.8000`, `.retry.60000`, `.retry.300000`, `.retry.1800000`
- [x] [historical] Implement DLQ routing after final retry attempt
- [x] [historical] Preserve `traceparent`, `X-Correlation-Id`, `X-Request-Id`, `X-Causation-Id` headers across retries

### Task 3.2: Add retry-topic chain tests
- [x] [historical] Unit test: RetryConsumer delays before re-publishing
- [x] [historical] Unit test: Retry count increments correctly
- [x] [historical] Unit test: DLQ routing after final attempt
- [x] [historical] Integration test: End-to-end retry chain with Docker Compose Kafka
- [x] [historical] Integration test: Non-retryable error routes directly to DLQ

### Task 3.3: Implement circuit breaker middleware for HTTP
- [x] [historical] Select circuit breaker library (sony/gobreaker or equivalent)
- [x] [historical] Implement HTTP middleware wrapper
- [x] [historical] Configure thresholds: 5 failures, 30s recovery, 2 successes for HALF-OPEN to CLOSED
- [x] [historical] Add metrics: `circuit_breaker_state`, `circuit_breaker_failures_total`

### Task 3.4: Implement circuit breaker interceptor for gRPC
- [x] [historical] Implement gRPC interceptor using the same circuit breaker library
- [x] [historical] Configure failure criteria: UNAVAILABLE, DEADLINE_EXCEEDED, INTERNAL as failures
- [x] [historical] Add metrics: `circuit_breaker_state`, `circuit_breaker_failures_total`

### Task 3.5: Add circuit breaker tests
- [x] [historical] Unit test: CLOSED to OPEN transition on failure threshold
- [x] [historical] Unit test: OPEN to HALF-OPEN transition on recovery timeout
- [x] [historical] Unit test: HALF-OPEN to CLOSED on success threshold
- [x] [historical] Unit test: HALF-OPEN to OPEN on failure
- [x] [historical] Integration test: Circuit breaker trips on downstream failure

### Task 3.6: Document circuit breaker usage
- [x] [historical] Add circuit breaker configuration to platform documentation
- [x] [historical] Document threshold tuning guidelines
- [x] [historical] Add circuit breaker to operational runbooks

## Completion Criteria

- [x] [historical] All 8 services meet 90/90/80 coverage thresholds (unit/integration/architecture)
- [x] [historical] ArgoCD syncs successfully against staging with real repoURL
- [x] [historical] All 8 Temporal workers register with Worker Versioning v2
- [x] [historical] Kafka retry-topic chain processes retries with exponential backoff
- [x] [historical] Circuit breaker trips and recovers correctly for HTTP and gRPC calls
- [x] [historical] All tasks independently verifiable via `make services-verify`


---

> **Historical record:** This change was archived with 110 incomplete task(s) (0/110 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
