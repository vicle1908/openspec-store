# Proposal: Modernize Service Runtime Security, BuildKit Caching, and Go Standard Library Idioms

## Why

Following the monorepo toolchain upgrade to Go `1.27.1` and container image updates, an exploration of the codebase surfaced several operational vulnerabilities, build performance bottlenecks, and legacy idioms:
1. **Network Security Vulnerability (Slowloris)**: Several microservice HTTP servers (`notification-service`, `customer-service`, `order-service`, `catalog-service`, `reporting-service`) instantiate `net/http.Server` with either zero timeouts or missing `ReadHeaderTimeout`. Per official Go documentation (`net/http.Server`), omitting `ReadHeaderTimeout` allows malicious or degraded clients to trickle header bytes indefinitely, exhausting worker goroutines and file descriptors.
2. **Signal Handling Goroutine Leaks**: 5 runtimes (`platform/runtime`, `customer-service`, `order-service`, `catalog-service`) manually allocate signal channels (`make(chan os.Signal, 1)`) and spawn background goroutines that outlive cancellation or lack explicit deregistration. Go 1.16+ introduced `signal.NotifyContext`, which provides deterministic, leak-free signal interception and context cancellation.
3. **Container Build Inefficiency**: While 10 Dockerfiles utilize BuildKit cache mounts (`--mount=type=cache,target=/go/pkg/mod` and `--mount=type=cache,target=/root/.cache/go-build`), 3 Dockerfiles (`inventory-service`, `shipping-service`, and `tools/templates/Dockerfile.platform`) omit them, causing unnecessary dependency re-downloads and slower CI/local build cycles.
4. **Legacy Stdlib Sorting & Reflection Overhead**: 68 occurrences of legacy `sort.Slice` and `sort.Strings` remain in the codebase. Go 1.21+ introduced the type-safe, non-reflective `slices.Sort` and `slices.SortFunc` packages, which offer superior performance and eliminate index-closure boilerplate.
5. **Pre-Go 1.22 Idioms & Verbose Boilerplate**:
   - 25 table-driven test files retain redundant loop variable copies (`tc := tc`), which became obsolete with Go 1.22's per-iteration loop variable semantics.
   - 69 instances of repetitive fallback branching (`if x == "" { x = "default" }`) can be modernized using Go 1.22's standard `cmp.Or`.
6. **Logging Standard Discrepancies**: `customer-service` and `tools/workflowaudit` still use raw standard library `log` calls rather than structured logging integrated with OpenTelemetry context tracing.

## What Changes

- **HTTP Server Timeout Hardening**:
  - Enforce `ReadHeaderTimeout: 10 * time.Second` across all `http.Server` instances in `notification-service`, `customer-service`, `order-service`, `catalog-service`, and `reporting-service`.
  - Standardize API and metrics listener deadlines to `ReadTimeout: 30 * time.Second`, `WriteTimeout: 30 * time.Second`, and `IdleTimeout: 2 * time.Minute`.
- **Signal Handling Modernization**:
  - Replace manual `signal.Notify` channels and detached watcher goroutines in `platform/runtime/roles.go`, `customer-service/cmd/customer-service/run.go`, `order-service/internal/runtime/runtime.go`, and `catalog-service/internal/runtime/runtime.go` with `signal.NotifyContext(ctx, os.Interrupt, syscall.SIGTERM)`.
- **BuildKit Cache Mount Alignment**:
  - Add `--mount=type=cache,target=/go/pkg/mod` and `--mount=type=cache,target=/root/.cache/go-build` to `services/inventory-service/Dockerfile.inventory-service`, `services/shipping-service/Dockerfile.shipping-service`, and `tools/templates/Dockerfile.platform`.
- **Standard Library Collections Modernization**:
  - Migrate all 68 `sort.Slice` and `sort.Strings` occurrences to `slices.Sort` and `slices.SortFunc(..., cmp.Compare)`.
- **Go 1.22+ Idiom Clean-up**:
  - Remove all 25 redundant `tc := tc` / `c := c` loop variable copies in test files.
  - Simplify configuration and fallback defaults using `cmp.Or`.
- **Logging Alignment**:
  - Modernize `customer-service` entrypoint logging to use `slog` / `platformobservability.Logger`.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `platform-runtime`: Adds explicit HTTP server timeout requirements (`ReadHeaderTimeout` Slowloris hardening) and standard library idiom conformance (`slices.Sort`, `cmp.Or`, `signal.NotifyContext`).

## Non-Goals

- Changing HTTP API route paths, payloads, or gRPC/Protobuf contracts.
- Altering domain business logic or database schema definitions.
- Replacing Uber Fx dependency injection with manual wiring.

## Impact

- **Affected Systems**:
  - `go-microservices`: `platform/`, `services/*`, `tools/*`, `tests/*`.
  - `openspec-store`: Change proposal tracking under `modernize-service-runtime-security-and-idioms`.
- **Security & Performance**:
  - Eliminates Slowloris Denial-of-Service vectors on public and internal HTTP listeners.
  - Eliminates potential signal listener goroutine leaks.
  - Accelerates container builds across all microservices via Docker BuildKit cache mounts.
