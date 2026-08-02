# Tasks: Ecosystem Alignment

## Phase 1: Critical -- Test Coverage

### Task 1.1: Measure current test coverage across all 8 services
- [ ] Run `go test -coverprofile=coverage.out ./...` for each service
- [ ] Record unit test coverage percentage per service
- [ ] Record integration test coverage percentage per service
- [ ] Record architecture test coverage percentage per service
- [ ] Compare against 90/90/80 thresholds and document gaps

### Task 1.2: Add unit tests for payment-service coverage gaps
- [ ] Identify untested domain logic and port adapters
- [ ] Write unit tests for payment aggregation, status transitions, and error paths
- [ ] Verify unit test coverage reaches 90%

### Task 1.3: Add unit tests for inventory-service coverage gaps
- [ ] Identify untested domain logic and port adapters
- [ ] Write unit tests for inventory reservation, release, and stock level calculations
- [ ] Verify unit test coverage reaches 90%

### Task 1.4: Add unit tests for shipping-service coverage gaps
- [ ] Identify untested domain logic and port adapters
- [ ] Write unit tests for shipping dispatch, tracking, and status transitions
- [ ] Verify unit test coverage reaches 90%

### Task 1.5: Add unit tests for customer-service coverage gaps
- [ ] Identify untested domain logic and port adapters
- [ ] Write unit tests for customer profile, GDPR export, and purge workflows
- [ ] Verify unit test coverage reaches 90%

### Task 1.6: Add unit tests for notification-service coverage gaps
- [ ] Identify untested domain logic and port adapters
- [ ] Write unit tests for notification dispatch, channel selection, and retry logic
- [ ] Verify unit test coverage reaches 90%

### Task 1.7: Add unit tests for catalog-service coverage gaps
- [ ] Identify untested domain logic and port adapters
- [ ] Write unit tests for catalog product, pricing snapshot, and price rollback
- [ ] Verify unit test coverage reaches 90%

### Task 1.8: Add unit tests for reporting-service coverage gaps
- [ ] Identify untested domain logic and port adapters
- [ ] Write unit tests for reporting projection and aggregation logic
- [ ] Verify unit test coverage reaches 90%

### Task 1.9: Add integration tests for non-order services
- [ ] Add Docker-backed integration tests for payment-service
- [ ] Add Docker-backed integration tests for inventory-service
- [ ] Add Docker-backed integration tests for shipping-service
- [ ] Add Docker-backed integration tests for customer-service
- [ ] Add Docker-backed integration tests for notification-service
- [ ] Add Docker-backed integration tests for catalog-service
- [ ] Add Docker-backed integration tests for reporting-service
- [ ] Verify integration test coverage reaches 90% for each service

### Task 1.10: Verify architecture test coverage
- [ ] Run architecture tests for all 8 services
- [ ] Identify services below 80% architecture test coverage
- [ ] Add architecture tests for hexagonal dependency enforcement, domain isolation, and contract compliance
- [ ] Verify architecture test coverage reaches 80% for each service

### Task 1.11: Update CI to enforce coverage thresholds
- [ ] Add coverage threshold checks to the CI pipeline
- [ ] Configure `make services-verify` to fail if any service is below threshold
- [ ] Document the coverage thresholds in the operational-readiness spec

## Phase 2: High -- ArgoCD and Worker Versioning

### Task 2.1: Fix ArgoCD repoURL placeholder
- [ ] Identify the actual Git repository URL for the project
- [ ] Update all ArgoCD Application manifests to use the real repoURL
- [ ] Validate ArgoCD sync against staging environment
- [ ] Verify the Application resources render correctly with `argocd app diff`

### Task 2.2: Wire Worker Versioning v2 for notification-service
- [ ] Add `UseVersioning: true` and `DeploymentSeriesName` to notification-service worker
- [ ] Add `UseVersioning: true` to notification-service `startWorkflow` calls
- [ ] Run replay tests to verify non-determinism safety
- [ ] Deploy to staging and verify workflow execution

### Task 2.3: Wire Worker Versioning v2 for catalog-service
- [ ] Add `UseVersioning: true` and `DeploymentSeriesName` to catalog-service worker
- [ ] Add `UseVersioning: true` to catalog-service `startWorkflow` calls
- [ ] Run replay tests to verify non-determinism safety
- [ ] Deploy to staging and verify workflow execution

### Task 2.4: Wire Worker Versioning v2 for inventory-service
- [ ] Add `UseVersioning: true` and `DeploymentSeriesName` to inventory-service worker
- [ ] Add `UseVersioning: true` to inventory-service `startWorkflow` calls
- [ ] Run replay tests to verify non-determinism safety
- [ ] Deploy to staging and verify workflow execution

### Task 2.5: Wire Worker Versioning v2 for payment-service
- [ ] Add `UseVersioning: true` and `DeploymentSeriesName` to payment-service worker
- [ ] Add `UseVersioning: true` to payment-service `startWorkflow` calls
- [ ] Run replay tests to verify non-determinism safety
- [ ] Deploy to staging and verify workflow execution

### Task 2.6: Wire Worker Versioning v2 for shipping-service
- [ ] Add `UseVersioning: true` and `DeploymentSeriesName` to shipping-service worker
- [ ] Add `UseVersioning: true` to shipping-service `startWorkflow` calls
- [ ] Run replay tests to verify non-determinism safety
- [ ] Deploy to staging and verify workflow execution

### Task 2.7: Wire Worker Versioning v2 for customer-service
- [ ] Add `UseVersioning: true` and `DeploymentSeriesName` to customer-service worker
- [ ] Add `UseVersioning: true` to customer-service `startWorkflow` calls
- [ ] Run replay tests to verify non-determinism safety
- [ ] Deploy to staging and verify workflow execution

### Task 2.8: Wire Worker Versioning v2 for reporting-service
- [ ] Add `UseVersioning: true` and `DeploymentSeriesName` to reporting-service worker
- [ ] Add `UseVersioning: true` to reporting-service `startWorkflow` calls
- [ ] Run replay tests to verify non-determinism safety
- [ ] Deploy to staging and verify workflow execution

### Task 2.9: Wire Worker Versioning v2 for order-service
- [ ] Ensure existing partial registration is complete with `UseVersioning: true` on both worker and caller
- [ ] Run replay tests to verify non-determinism safety
- [ ] Deploy to staging and verify workflow execution
- [ ] Deploy to production with monitoring

### Task 2.10: Add architecture test for Worker Versioning v2
- [ ] Add architecture test that scans all 8 services for `UseVersioning: true`
- [ ] Verify the test fails if any service is missing Worker Versioning v2 configuration
- [ ] Integrate the test into `make services-verify`

## Phase 3: Medium -- Kafka Retry and Circuit Breaker

### Task 3.1: Implement RetryConsumer for Kafka retry-topic chain
- [ ] Implement `RetryConsumer` that reads from retry topics, delays, and re-publishes to source topic
- [ ] Wire the retry-topic chain: `<source-topic>.retry.1000`, `.retry.8000`, `.retry.60000`, `.retry.300000`, `.retry.1800000`
- [ ] Implement DLQ routing after final retry attempt
- [ ] Preserve `traceparent`, `X-Correlation-Id`, `X-Request-Id`, `X-Causation-Id` headers across retries

### Task 3.2: Add retry-topic chain tests
- [ ] Unit test: RetryConsumer delays before re-publishing
- [ ] Unit test: Retry count increments correctly
- [ ] Unit test: DLQ routing after final attempt
- [ ] Integration test: End-to-end retry chain with Docker Compose Kafka
- [ ] Integration test: Non-retryable error routes directly to DLQ

### Task 3.3: Implement circuit breaker middleware for HTTP
- [ ] Select circuit breaker library (sony/gobreaker or equivalent)
- [ ] Implement HTTP middleware wrapper
- [ ] Configure thresholds: 5 failures, 30s recovery, 2 successes for HALF-OPEN to CLOSED
- [ ] Add metrics: `circuit_breaker_state`, `circuit_breaker_failures_total`

### Task 3.4: Implement circuit breaker interceptor for gRPC
- [ ] Implement gRPC interceptor using the same circuit breaker library
- [ ] Configure failure criteria: UNAVAILABLE, DEADLINE_EXCEEDED, INTERNAL as failures
- [ ] Add metrics: `circuit_breaker_state`, `circuit_breaker_failures_total`

### Task 3.5: Add circuit breaker tests
- [ ] Unit test: CLOSED to OPEN transition on failure threshold
- [ ] Unit test: OPEN to HALF-OPEN transition on recovery timeout
- [ ] Unit test: HALF-OPEN to CLOSED on success threshold
- [ ] Unit test: HALF-OPEN to OPEN on failure
- [ ] Integration test: Circuit breaker trips on downstream failure

### Task 3.6: Document circuit breaker usage
- [ ] Add circuit breaker configuration to platform documentation
- [ ] Document threshold tuning guidelines
- [ ] Add circuit breaker to operational runbooks

## Completion Criteria

- [ ] All 8 services meet 90/90/80 coverage thresholds (unit/integration/architecture)
- [ ] ArgoCD syncs successfully against staging with real repoURL
- [ ] All 8 Temporal workers register with Worker Versioning v2
- [ ] Kafka retry-topic chain processes retries with exponential backoff
- [ ] Circuit breaker trips and recovers correctly for HTTP and gRPC calls
- [ ] All tasks independently verifiable via `make services-verify`
