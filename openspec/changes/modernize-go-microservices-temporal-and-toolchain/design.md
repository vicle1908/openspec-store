# Design: Modernize Go Microservices Toolchain, Dependencies, and Temporal Integration

## Overview

This design formalizes the modernization, de-duplication, and operational hardening of the `go-microservices` repository. The change updates the Go toolchain to `1.27.2`, aligns pinned third-party container images with verified official releases, upgrades Go ecosystem dependencies, standardizes all Temporal adapters into driven hexagonal layers (`internal/adapters/temporal/`), consolidates redundant worker lifecycle management onto `platform/temporal.ManagedWorker`, replaces ad-hoc compensation slices with the platform `Saga` engine, mitigates cascading dual-retry storms in activities, and guarantees backward replay determinism via `worker.WorkflowReplayer`.

## Component & Version Matrix

| Tier | Component / Module | Current Baseline | Target Version | Verification Check |
| :--- | :--- | :--- | :--- | :--- |
| **Toolchain** | Go compiler & standard library | `1.27.1` | `1.27.2` | `go version`, root `.go-version`, `Makefile` |
| **Toolchain** | Go Docker build base image | `golang:1.27.1-bookworm` | `golang:1.27.2-bookworm` | Multi-arch manifest inspection |
| **Infrastructure**| OTel Collector Contrib | `0.161.0` | `0.162.0` | `make collector-validate` |
| **Infrastructure**| Temporal Server & Admin Tools | `1.32.0` | `1.32.1` | Temporal Web UI & worker poller probes |
| **Infrastructure**| Prometheus | `v3.15.0` | `v3.16.0` | Container startup & OTLP metric ingress |
| **Infrastructure**| Mailpit | `v1.31.3` | `v1.32.0` | SMTP ingress & API health probe |
| **Go Dependency**| `go.temporal.io/sdk` | `v1.49.0` | `v1.49.0` (Latest stable) | `go list -m go.temporal.io/sdk` |
| **Go Dependency**| `go.temporal.io/api` | `v1.63.6` | `v1.63.7` | Compilation across all 8 services |
| **Go Dependency**| `github.com/go-chi/chi/v5` | `v5.3.2` | `v5.4.0` | HTTP route unit tests |
| **Go Dependency**| `github.com/prometheus/client_golang` | `v1.24.1` | `v1.25.0` | Metric export verification |
| **Go Dependency**| `github.com/twmb/franz-go/pkg/kmsg` | `v1.14.0` | `v1.15.0` | Kafka producer/consumer compilation |
| **Go Dependency**| `go.opentelemetry.io/otel/exporters/*` | `v1.46.0` | `v1.47.0` | Trace/metric/log exporter tests |

---

## Architecture & Refactoring Plan

### 1. Hexagonal Adapter Standardization

Across all 8 microservices, Temporal workflow and activity implementations are standardized strictly as driven secondary adapters under `internal/adapters/temporal/`:
- Relocate `services/customer-service/internal/application/orchestration/` → `services/customer-service/internal/adapters/temporal/`
- Relocate `services/notification-service/internal/application/orchestration/` → `services/notification-service/internal/adapters/temporal/`
- Relocate `services/inventory-service/internal/application/orchestration/` → `services/inventory-service/internal/adapters/temporal/`
- Relocate `services/payment-service/internal/application/orchestration/` → `services/payment-service/internal/adapters/temporal/`
- Refactor `services/catalog-service/internal/application/orchestration/temporal.go` → `services/catalog-service/internal/adapters/temporal/workflow.go`

Domain models and application ports remain isolated in `internal/domain` and `internal/ports`, preventing any leaking of `go.temporal.io/sdk` types into application cores.

### 2. Consolidated Worker Lifecycle via `ManagedWorker`

Eliminate redundant, hand-rolled `WorkerDriver` structs in `order-service`, `notification-service`, and `customer-service`. Each service's worker role constructs its worker using `platformtemporal.NewManagedWorker` with:
- Bounded graceful termination (`30s` timeout).
- Atomic fail-closed readiness tracking.
- Unified fatal error channels.
- Worker Versioning v2 (`platformtemporal.DeploymentVersion()`, `VersioningBehaviorAutoUpgrade`).

```go
func NewWorker(tc client.Client, cfg Config, activities *Activities) (*platformtemporal.ManagedWorker, error) {
    opts := worker.Options{
        DeploymentOptions: worker.DeploymentOptions{
            UseVersioning:             true,
            Version:                   platformtemporal.DeploymentVersion(),
            DefaultVersioningBehavior: workflow.VersioningBehaviorAutoUpgrade,
        },
        OnFatalError: func(err error) {
            slog.Error("fatal temporal worker failure", "error", err)
        },
    }
    w := worker.New(tc, cfg.TaskQueue, opts)
    w.RegisterWorkflowWithOptions(FulfillmentWorkflow, workflow.RegisterOptions{Name: WorkflowTypeV1})
    w.RegisterActivity(activities)

    return platformtemporal.NewManagedWorker(w, 30*time.Second)
}
```

### 3. Unified Saga Compensation Engine & Pruning Slice Hacks

`order-service/internal/adapters/temporal/workflow.go` previously tracked compensation rollback steps via an ad-hoc local slice of closures (`registerCompensation`, `awaitActivity`). This is replaced with the robust, reusable `platformtemporal.NewSaga` engine:
- Forward activities and rollback compensations are declared in paired positions.
- When an activity returns `platformtemporal.NewCompensationApplicationError`, the saga engine automatically invokes registered compensations in strict inverse order of completed forward steps.

### 4. Dual-Retry Storm Mitigation & Activity Heartbeating

- **Mitigation of Cascading Retries**: HTTP/gRPC client adapters invoked inside Temporal activities MUST disable internal retry loops (or cap them to 1 immediate attempt). Transient retries are delegated exclusively to Temporal's server-managed `RetryPolicy` (`InitialInterval: 1s, BackoffCoefficient: 2.0, MaximumAttempts: 5`). This prevents thread starvation and cascading exponential backoff delays.
- **Heartbeating Standard**: Long-running activities (>30s) MUST invoke `activity.RecordHeartbeat(ctx)` periodically and configure explicit `HeartbeatTimeout` in activity options.

### 5. Strongly Consistent Workflow Update Adoption

To eliminate asynchronous Signal-and-Query polling loops, `OrderFulfillmentWorkflow` exposes a strongly-consistent Workflow Update handler (`workflow.SetUpdateHandler`):

```go
err := workflow.SetUpdateHandler(ctx, "updateShippingAddress", func(ctx workflow.Context, req UpdateShippingInput) (UpdateShippingOutput, error) {
    if state.Status == OrderStatusShipped {
        return UpdateShippingOutput{}, temporalsdk.NewApplicationError("order already shipped", "INVALID_STATE")
    }
    state.ShippingAddress = req.NewAddress
    return UpdateShippingOutput{Accepted: true}, nil
})
```

### 6. Workflow Determinism & Replay Compatibility Invariant

Modernization of workflow definitions MUST NOT break existing event histories:
- Replay tests in `services/shipping-service/test/replay/` and `services/notification-service/test/replay/` using `worker.WorkflowReplayer` MUST continue to replay stored history fixtures (`fixtures/temporal/.../history.json`) without non-determinism errors.
- The module-aware determinism gate `make temporal-verify` and upstream `workflowcheck` must pass with zero violations.

---

## Multi-Architecture Validation Contract

All updated image tags must verify against `linux/arm64` and `linux/amd64` using `docker manifest inspect`. Validation is gated by `scripts/verify-images.sh --arch both` before updating `deploy/tools.env`.
