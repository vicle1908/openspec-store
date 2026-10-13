# Tasks

## 1. Toolchain & Pinned Container Images

- [x] 1.1 Upgrade Go toolchain to `1.27.2` in `.go-version`, root `Makefile`, and verify with `go version`
- [x] 1.2 Update container build base images in `Dockerfile.*` files to `golang:1.27.2-bookworm` / `alpine:3.24.2` and verify Dockerfile linting
- [x] 1.3 Upgrade pinned third-party images in `deploy/tools.env` (`OTEL_COLLECTOR_VERSION=0.162.0`, `GO_IMAGE_VERSION=1.27.2-alpine`, `TEMPORAL_SERVER_VERSION=1.32.1`, `PROMETHEUS_VERSION=v3.16.0`, `MAILPIT_VERSION=v1.32.0`) and verify multi-architecture availability with `scripts/verify-images.sh --arch both`
- [x] 1.4 Validate Compose topologies and OTel Collector configurations with `make compose-validate collector-validate`

## 2. Core Go Dependencies & SDK Alignment

- [x] 2.1 Upgrade `platform/go.mod` dependencies (`go.temporal.io/api v1.63.7`, `github.com/go-chi/chi/v5 v5.4.0`, `github.com/prometheus/client_golang v1.25.0`, `github.com/twmb/franz-go/pkg/kmsg v1.15.0`, `go.opentelemetry.io/otel/exporters/* v1.47.0`, `golang.org/x/tools v0.52.0`) and verify with `go mod tidy` in `platform/`
- [x] 2.2 Propagate upgraded platform versions and align `go.mod` directives across all 8 service modules (`services/*/go.mod`), verifying with `make health-check`
- [x] 2.3 Run platform module verification via `make -C platform verify` and verify all platform unit and integration tests pass

## 3. Temporal Packaging Standardization & De-duplication

- [ ] 3.1 Migrate Temporal workflow and activity implementations in `customer-service`, `notification-service`, `inventory-service`, and `payment-service` from `internal/application/orchestration/` to `internal/adapters/temporal/` and verify package compilation
- [x] 3.2 Refactor `catalog-service/internal/application/orchestration/temporal.go` to `internal/adapters/temporal/workflow.go` and verify all catalog unit tests pass
- [x] 3.3 Consolidate custom `WorkerDriver` structs across services to use `platformtemporal.NewManagedWorker` and verify worker startup options and graceful shutdown tests pass
- [x] 3.4 Purge obsolete shims (`order-service` `workflow_existence.go`, `reporting-service` `wire.go`) and verify `git status` reports no broken references

## 4. Saga Compensation Engine, Replay Safety & Workflow Updates

- [x] 4.1 Refactor `order-service` fulfillment saga to consume declarative `platformtemporal.NewSaga` and verify deterministic compensation replay with `go test ./services/order-service/test/replay/...`
- [x] 4.2 Standardize activity retry policies to eliminate nested HTTP/gRPC client retry loops and configure explicit heartbeating on activities exceeding 30s
- [x] 4.3 Implement Temporal Workflow Update handler (`workflow.SetUpdateHandler`) for strongly-consistent order address updates and verify update validation unit tests
- [x] 4.4 Run backward replay test suite (`worker.WorkflowReplayer`) across all checked-in history fixtures and verify `make temporal-verify` reports zero nondeterminism findings

## 5. End-to-End System Verification & Evidence Retention

- [x] 5.1 Rebuild all services and restart local full Compose stack via `make dev-up` and verify all 26+ containers reach healthy status within timeout
- [x] 5.2 Execute complete cross-service smoke workload via `make dev-smoke` and verify 13/13 stages pass with retained JSON artifact
- [x] 5.3 Execute Newman feature integration test suite via `make newman-test` and verify 44 suites pass with 0 failures
- [x] 5.4 Execute Newman end-to-end saga test suite via `make newman-e2e` and verify complete order-to-delivery lifecycle passes with 0 failures
- [x] 5.5 Synchronize coverage documentation via `make sync-coverage-docs` and verify pre-push gate passes via `make pre-push`

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
- Verify the archived result.
