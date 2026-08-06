# Tasks: Fix Pre-existing Verification Issues

## Section 1: Customer Worker Workflow Implementations

- [x] 1.1 Create `services/customer-service/internal/application/orchestration/purge_workflow.go` with `PurgeWorkflow` function that accepts `PurgeWorkflowInput` and returns nil.
  - **Verification**: `cd services/customer-service && go build ./...`

- [x] 1.2 Create `services/customer-service/internal/application/orchestration/export_workflow.go` with `GDPRExportWorkflow` function that accepts `GDPRExportInput` and returns nil.
  - **Verification**: `cd services/customer-service && go build ./...`

- [x] 1.3 Update `services/customer-service/cmd/customer-service/run.go` to register workflow function references instead of string constants.
  - **Verification**: `cd services/customer-service && go build ./cmd/customer-service/...`

- [x] 1.4 Build and restart customer-worker container to verify no panic.
  - **Verification**: `docker build -f services/customer-service/Dockerfile.customer-service --build-arg SERVICE_PATH=services/customer-service -t customer-service:local . && docker restart go-microservices-platform-customer-worker-1 && docker ps | grep customer-worker | grep -v Restarting`

## Section 2: Inventory GenerateReservationID

- [x] 2.1 Add `GenerateReservationID()` function to `services/inventory-service/internal/application/orchestration/activities.go`.
  - **Verification**: `cd services/inventory-service && go build ./...`

- [x] 2.2 Run inventory-service tests to verify the function works.
  - **Verification**: `cd services/inventory-service && go test ./internal/application/orchestration/... -run TestGenerateReservationID -v`

## Section 3: Reporting Service Test Path Resolution

- [x] 3.1 Fix `reportingRepositoryRoot()` in `services/reporting-service/test/architecture/temporal_verification_test.go` to use `strings.Contains` instead of exact match.
  - **Verification**: `cd services/reporting-service && go test ./test/architecture/... -run TestWorkerVersioningIsConfigured -v`

- [x] 3.2 Run all reporting-service architecture tests.
  - **Verification**: `cd services/reporting-service && go test ./test/architecture/... -count=1`

## Section 4: Validation Script collectDiagnostics

- [x] 4.1 Implement `collectDiagnostics` method on `runner` struct in `scripts/validation/main.go`.
  - **Verification**: `cd scripts/validation && go build .`

- [x] 4.2 Run validation script with `--diagnostics-only` flag.
  - **Verification**: `cd scripts/validation && go run . --root ../.. --diagnostics-only`

## Section 5: Catalog Service Coverage

- [x] 5.1 Add unit tests for uncovered config parsing paths in catalog-service.
  - **Verification**: `cd services/catalog-service && go test ./internal/... -count=1`

- [x] 5.2 Verify catalog-service coverage meets 80% gate.
  - **Verification**: `make -C services/catalog-service check-coverage`

## Section 6: Full Verification

- [x] 6.1 Rebuild all affected service images and restart containers.
  - **Verification**: All 8 API services return HTTP 200 on `/health/ready`

- [x] 6.2 Run architecture tests for all 8 services.
  - **Verification**: `for svc in order payment inventory shipping notification customer catalog reporting; do cd services/${svc}-service && go test ./test/architecture/... -count=1 -short && cd ~/Developer/go-microservices; done`

- [x] 6.3 Run integration tests against live stack.
  - **Verification**: `for svc in catalog order payment shipping notification customer reporting; do cd services/${svc}-service && go test -tags integration ./test/integration/... -count=1 -short && cd ~/Developer/go-microservices; done`

- [x] 6.4 Run OpenSpec validation.
  - **Verification**: `openspec validate --all --store openspec-store`
