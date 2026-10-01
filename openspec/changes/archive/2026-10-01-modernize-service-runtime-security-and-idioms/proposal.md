# Proposal: Modernize Service Runtime Security, BuildKit Caching, Outbound Resilience, and Go Standard Library Idioms

## Why

Following the monorepo toolchain upgrade to Go `1.27.1` and container image updates, an exhaustive multi-agent exploration across all 8 microservices (`catalog`, `customer`, `inventory`, `notification`, `order`, `payment`, `reporting`, `shipping`), shared `platform/`, `tools/`, and `tests/` surfaced critical security exposures, resource leaks, build bottlenecks, and outdated idioms:

1. **Inbound HTTP Server Slowloris Vulnerability**:
   - Multiple microservice HTTP servers (`notification-service`, `customer-service`, `order-service`, `catalog-service`, `reporting-service`) instantiate `net/http.Server` with either zero timeouts or missing `ReadHeaderTimeout`.
   - Per official Go documentation (`net/http.Server`), omitting `ReadHeaderTimeout` allows malicious or degraded clients to trickle header bytes indefinitely at 1 byte every few seconds, exhausting worker goroutines and file descriptors without triggering `ReadTimeout`.
2. **Signal Handling Goroutine & Channel Leaks**:
   - 5 runtimes (`platform/runtime/roles.go`, `customer-service/cmd/customer-service/run.go`, `order-service/cmd/diag-consumer/main.go`, `order-service/internal/runtime/runtime.go`, `catalog-service/internal/runtime/runtime.go`) manually allocate signal channels (`make(chan os.Signal, 1)`) and launch background goroutines. If a context is cancelled before signal arrival, the goroutine leaks indefinitely, and signal handler unregistration (`signal.Stop`) is omitted.
   - Go 1.16+ introduced `signal.NotifyContext`, which provides deterministic, leak-free signal interception and context cancellation.
3. **Outbound HTTP Client Timeouts, Context Propagation & Missing Circuit Breakers**:
   - `platform/kafka/burrow.go`, `services/notification-service` (`recipient_resolver.go`, `httptest_provider.go`), and health check CLIs in `customer-service`, `reporting-service`, and `notification-service` fall back to `http.DefaultClient` or un-timeouted clients, risking thread hangs if upstream services stall.
   - `services/order-service/internal/runtime/healthcheck.go` constructs outbound probes with `http.NewRequest` instead of `http.NewRequestWithContext`.
   - `order-service` instantiates raw `&http.Client{}` for all HTTP peers, falling back to `http.DefaultTransport` (`MaxIdleConnsPerHost = 2`), causing persistent connection thrashing under load.
   - While `order-service` protects `PaymentClient`, `InventoryClient`, and `ShippingClient` with `gobreaker.CircuitBreaker`, `CustomerClient` and `CatalogClient` lack circuit breakers, risking cascade failures when customer or catalog services degrade.
4. **PostgreSQL Connection Pool Disparities & Runtime Bypasses**:
   - `services/payment-service/internal/adapters/postgres/pool.go` defines hardened pool settings (`MaxConns=20`, `Lifetime=30m`, `IdleTime=5m`), but `internal/runtime/fx.go:74`, `worker.go:56`, and `role_impl.go:39` bypass `paymentpg.NewPool` and call `pgxpool.New(ctx, cfg.Database.URL)` directly, running with default `MaxConns=4`.
   - `services/customer-service` defines pool configuration parameters in `config.go`, but `run.go` ignores them and passes only the raw DSN string, leaving connection limits and health checks unconfigured.
   - `inventory-service` and `shipping-service` call `pgxpool.New(ctx, cfg.Database.URL)` with raw DSNs, defaulting to 4 connections.
5. **Container Build Inefficiency**:
   - 3 Dockerfiles (`inventory-service`, `shipping-service`, and `tools/templates/Dockerfile.platform`) omit BuildKit cache mounts (`--mount=type=cache,target=/go/pkg/mod` and `--mount=type=cache,target=/root/.cache/go-build`), causing unnecessary dependency re-downloads and slower build cycles compared to the other 10 services.
6. **Legacy Stdlib Sorting & Reflection Overhead**:
   - 69 call sites use legacy `sort.Slice`, `sort.SliceStable`, and `sort.Strings`.
   - Go 1.21+ introduced the type-safe, non-reflective `slices.Sort`, `slices.SortFunc`, and `slices.SortStableFunc`, eliminating reflection overhead and index-closure boilerplate.
7. **Pre-Go 1.22 Idioms & Logging Discrepancies**:
   - 25 table-driven test files retain redundant loop variable copies (`tc := tc`), rendered obsolete by Go 1.22's per-iteration loop variable scoping.
   - 69 instances of verbose fallback branching (`if x == "" { x = "default" }`) can be modernized using Go 1.22's `cmp.Or`.
   - `services/customer-service/cmd/customer-service/main.go`, `run.go`, and `tools/workflowaudit/main.go` still use raw standard library `log` rather than structured `log/slog` integrated with OpenTelemetry context tracing.

## What Changes

- **Inbound HTTP Server Timeout Hardening**:
  - Enforce `ReadHeaderTimeout: 10 * time.Second` across all `http.Server` instances in `notification-service`, `customer-service`, `order-service`, `catalog-service`, and `reporting-service`.
  - Standardize API and metrics listener deadlines to `ReadTimeout: 30 * time.Second`, `WriteTimeout: 30 * time.Second`, and `IdleTimeout: 2 * time.Minute`.
- **Signal Handling Modernization**:
  - Replace manual `signal.Notify` channels and detached watcher goroutines in `platform/runtime/roles.go`, `customer-service/cmd/customer-service/run.go`, `order-service/cmd/diag-consumer/main.go`, `order-service/internal/runtime/runtime.go`, and `catalog-service/internal/runtime/runtime.go` with `signal.NotifyContext(ctx, os.Interrupt, syscall.SIGTERM)`.
- **Outbound HTTP Client Resilience & Peer Protection**:
  - Eliminate `http.DefaultClient` fallbacks in `platform/kafka/burrow.go`, `notification-service` recipient resolvers and SMTP mocks, and CLI health checks, replacing them with explicit `&http.Client{Timeout: ...}` and configured transports.
  - Fix `order-service/internal/runtime/healthcheck.go` to attach context via `http.NewRequestWithContext`.
  - Provide a shared, pooled peer transport (`MaxIdleConns: 100`, `MaxIdleConnsPerHost: 20`, `DialContext: 5s`, `TLSHandshakeTimeout: 5s`, `ResponseHeaderTimeout: 10s`) for `order-service` peer clients.
  - Equip `CustomerClient` and `CatalogClient` in `order-service/internal/adapters/httppeer` with `gobreaker.CircuitBreaker`, aligning them with payment, inventory, and shipping peers.
- **Database Connection Pool Normalization**:
  - Fix `payment-service` runtime wiring (`fx.go`, `worker.go`, `role_impl.go`) to invoke `paymentpg.NewPool` rather than bypassing the adapter via `pgxpool.New`.
  - Wire `MinConns`, `MaxConns`, and lifetime parameters in `customer-service`, `inventory-service`, `shipping-service`, and `notification-service`.
  - Enforce bounded context timeouts (`3 * time.Second`) across all database `Probe()` and `Ping()` functions.
- **BuildKit Cache Mount Alignment**:
  - Add `--mount=type=cache,target=/go/pkg/mod` and `--mount=type=cache,target=/root/.cache/go-build` to `services/inventory-service/Dockerfile.inventory-service`, `services/shipping-service/Dockerfile.shipping-service`, and `tools/templates/Dockerfile.platform`.
- **Standard Library Collections Modernization**:
  - Migrate all 69 `sort.Slice`, `sort.SliceStable`, and `sort.Strings` occurrences to `slices.Sort`, `slices.SortFunc`, and `slices.SortStableFunc`.
- **Go 1.22+ Idiom Clean-up & Logging Alignment**:
  - Remove all 25 redundant `tc := tc` / `c := c` loop variable copies in test files.
  - Simplify configuration and fallback defaults using `cmp.Or`.
  - Migrate raw `log` imports in `customer-service` and `tools/workflowaudit` to `log/slog`.

## Capabilities

### Modified Capabilities
- `platform-runtime`: Adds explicit HTTP server timeout requirements (`ReadHeaderTimeout` Slowloris hardening), database connection pool configuration standards, outbound HTTP client resilience standards, and standard library idiom conformance (`slices.Sort`, `cmp.Or`, `signal.NotifyContext`).

## Non-Goals

- Changing HTTP API route paths, payloads, or gRPC/Protobuf contracts.
- Altering PostgreSQL table schemas, indexes, or stored procedures.
- Replacing Uber Fx dependency injection with manual wiring.

## Impact

- **Affected Systems**:
  - `go-microservices`: `platform/`, `services/*`, `tools/*`, `tests/*`.
  - `openspec-store`: Change proposal tracking under `modernize-service-runtime-security-and-idioms`.
- **Security & Reliability**:
  - Eliminates Slowloris Denial-of-Service vectors on public and internal HTTP listeners.
  - Prevents goroutine leaks in signal listeners and ensures clean shutdown cascades.
  - Protects `order-service` from cascading failures when customer or catalog services experience degradation.
  - Prevents database connection starvation and connection leakages under load.
  - Accelerates container builds across all microservices via Docker BuildKit cache mounts.
