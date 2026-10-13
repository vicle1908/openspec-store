# Proposal: Modernize Go Microservices Toolchain, Dependencies, and Temporal Integration

## Why

The `go-microservices` repository (8 microservices + shared `platform/` module + tooling) is fully operational on its local verification baseline (`make dev-smoke`, `make newman-test`, and `make newman-e2e` passing 100%). However, an audit against official latest releases and architectural conventions reveals key areas of technical drift, duplication, and outdated patterns:

1. **Toolchain & Image Pin Drift**:
   - The repository pins Go toolchain `1.27.1` in `.go-version` and Dockerfiles, while host toolchains and current point releases have stabilized on Go `1.27.2` with stdlib runtime fixes.
   - Pinned third-party container images in `deploy/tools.env` lag behind verified official releases: `otel/opentelemetry-collector-contrib` is at `0.161.0` (target: `v0.162.0`), Temporal Server is at `1.32.0` (target: `1.32.1`), Prometheus is at `v3.15.0` (target: `v3.16.0`), and Mailpit is at `v1.31.3` (target: `v1.32.0`).

2. **Temporal Integration Packaging Inconsistency**:
   - Four services (`customer-service`, `notification-service`, `inventory-service`, `payment-service`) place Temporal workflow and activity implementations in `internal/application/orchestration/`, while `order-service`, `shipping-service`, and `reporting-service` place them in `internal/adapters/temporal/`, and `catalog-service` maintains a flat `temporal.go`.
   - Per Hexagonal Architecture standards enforced across the workspace, Temporal SDK bindings are driven secondary adapters and SHALL reside under `internal/adapters/temporal/`.

3. **Duplicated Worker Lifecycle & Saga Boilerplate**:
   - Services implement redundant custom `WorkerDriver` wrappers with bespoke mutexes and fatal channels, bypassing the reusable, fail-closed `platform/temporal.NewManagedWorker` lifecycle abstraction.
   - `order-service` implements custom slice-based compensation tracking in `workflow.go`, duplicating the platform-standard `platform/temporal/saga.go` engine.
   - Long-running saga state verification relies on repetitive polling loops (`GET /api/v1/orders/{id}`) instead of strongly-consistent Temporal Workflow Updates (`workflow.SetUpdateHandler`).

## What Changes

1. **Go Toolchain & Image Modernization**:
   - Upgrade `.go-version` from `1.27.1` to `1.27.2` across root, Dockerfiles, and all 18 `go.mod` files.
   - Upgrade `deploy/tools.env` pinned images:
     - `OTEL_COLLECTOR_VERSION`: `0.161.0` → `0.162.0`
     - `GO_IMAGE_VERSION`: `1.27.1-alpine` → `1.27.2-alpine`
     - `TEMPORAL_SERVER_VERSION`: `1.32.0` → `1.32.1`
     - `PROMETHEUS_VERSION`: `v3.15.0` → `v3.16.0`
     - `MAILPIT_VERSION`: `v1.31.3` → `v1.32.0`
   - Re-verify all image pins for `linux/arm64` and `linux/amd64` multi-arch availability via `scripts/verify-images.sh --arch both`.

2. **Go Dependencies & SDK Synchronization**:
   - Update Go dependencies in `platform/go.mod` and all services:
     - `go.temporal.io/api`: `v1.63.6` → `v1.63.7`
     - `github.com/go-chi/chi/v5`: `v5.3.2` → `v5.4.0`
     - `github.com/prometheus/client_golang`: `v1.24.1` → `v1.25.0`
     - `github.com/twmb/franz-go/pkg/kmsg`: `v1.14.0` → `v1.15.0`
     - `go.opentelemetry.io/otel/exporters/*`: `v1.46.0` → `v1.47.0`
     - `golang.org/x/tools`: `v0.51.0` → `v0.52.0`

3. **Temporal Integration Clean-Break Refactoring**:
   - Standardize all service Temporal adapters under `internal/adapters/temporal/` (moving out of `internal/application/orchestration/`).
   - Replace service-local custom `WorkerDriver` structs with `platformtemporal.NewManagedWorker`.
   - Refactor `order-service` fulfillment workflow to utilize `platformtemporal.NewSaga` for forward/rollback compensations.
   - Expose Workflow Update handlers for order cancellation and address updates.
   - Delete obsolete shims (`workflow_existence.go`, `reporting-service/wire.go`).

## Capabilities Affected

- `platform-go-runtime`: Go toolchain baseline (`1.27.2`) and runtime dependencies.
- `platform-temporal-versioning`: Unified saga execution, managed worker options, and workflow update standards.
- `per-service-temporal-registration`: Canonical adapter directory conventions and unified worker registration.

## Impact & Compatibility

- **Clean Break**: No backward-compatibility shims. Services adopt `internal/adapters/temporal/` directly.
- **API Impact**: Zero external HTTP/gRPC breaking changes; existing endpoints and schemas are preserved.
- **Operational Impact**: All 9 Temporal task queues retain their existing identifiers and deployment series.

## Rollback Strategy

If regressions occur during validation:
1. Revert `deploy/tools.env` and `.go-version` to baseline Git commit.
2. Re-run `make dev-up` and verify with `make dev-smoke`.
3. Worktree state is captured in git; no database schema modifications are introduced.

## Verification & Acceptance

1. `make compose-validate collector-validate`: Must pass with 0 errors.
2. `scripts/verify-images.sh --arch both`: Must verify multi-arch availability for all updated tags.
3. `make -C platform verify`: Platform tests and linting must pass.
4. `make dev-up`: Local 8-service topology must start and achieve healthy status within 600s.
5. `make dev-smoke`: All 13 smoke stages must pass.
6. `make newman-all`: Feature and E2E Postman suites must pass with 0 failures and 0 errors.
