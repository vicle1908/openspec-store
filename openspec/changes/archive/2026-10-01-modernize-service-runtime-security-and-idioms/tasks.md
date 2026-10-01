# Tasks: Modernize Service Runtime Security, BuildKit Caching, Outbound Resilience, and Go Standard Library Idioms

## 1. High-Severity Inbound HTTP Server Hardening & Signal Lifecycle (P0)

- [x] 1.1 Inject `ReadHeaderTimeout: 10 * time.Second` and standard deadlines (`ReadTimeout: 30s`, `WriteTimeout: 30s`, `IdleTimeout: 2m`) into `services/notification-service/internal/runtime/fx.go` for both the main API and metrics HTTP servers. Verification: unit tests pass and timeout properties verified in test.
- [x] 1.2 Inject `ReadHeaderTimeout: 10 * time.Second` and standard deadlines into `services/customer-service/cmd/customer-service/run.go`. Verification: run `go test ./cmd/customer-service/...`.
- [x] 1.3 Add `ReadHeaderTimeout: 10 * time.Second` to `NewHTTPServer` in `services/order-service/internal/runtime/runtime.go`. Verification: run `go test ./internal/runtime/...` in `order-service`.
- [x] 1.4 Add `ReadHeaderTimeout: 10 * time.Second` to `NewHTTPServer` in `services/catalog-service/internal/runtime/runtime.go`. Verification: run `go test ./internal/runtime/...` in `catalog-service`.
- [x] 1.5 Add `ReadHeaderTimeout: 10 * time.Second` to `newHTTPServer` in `services/reporting-service/internal/runtime/wire.go`. Verification: run `go test ./internal/runtime/...` in `reporting-service`.
- [x] 1.6 Standardize timeouts across `inventory-service`, `payment-service`, and `shipping-service` (`fx.go` and `worker.go`). Verification: run `go test ./internal/runtime/...` across all three services.
- [x] 1.7 Refactor `platform/runtime/roles.go` `WithSignal` to use `signal.NotifyContext(ctx, os.Interrupt, syscall.SIGTERM)` instead of manual channels and uncoordinated goroutines. Verification: run `go test ./runtime/...` in `platform/`.
- [x] 1.8 Refactor `services/customer-service/cmd/customer-service/run.go` `withSignal` to use `signal.NotifyContext`. Verification: run `go test ./cmd/customer-service/...`.
- [x] 1.9 Refactor `services/order-service/internal/runtime/runtime.go` `NewShutdownSignalContext` and `cmd/diag-consumer/main.go` to use `signal.NotifyContext`. Verification: run `go test ./internal/runtime/...` in `order-service`.
- [x] 1.10 Refactor `services/catalog-service/internal/runtime/runtime.go` `SignalContext` to use `signal.NotifyContext`. Verification: run `go test ./internal/runtime/...` in `catalog-service`.

## 2. Outbound HTTP Client Resilience & Peer Protection (P1)

- [x] 2.1 Replace `http.DefaultClient` in `platform/kafka/burrow.go` with a dedicated, bounded `defaultBurrowClient`. Verification: run `go test ./kafka/...` in `platform/`.
- [x] 2.2 Replace `http.DefaultClient` fallbacks in `services/notification-service` (`recipient_resolver.go` and `httptest_provider.go`) with bounded clients. Verification: run `go test ./internal/adapters/...` in `notification-service`.
- [x] 2.3 Attach bounded context to `services/order-service/internal/runtime/healthcheck.go` via `http.NewRequestWithContext`. Verification: run `go test ./internal/runtime/...` in `order-service`.
- [x] 2.4 Configure shared `*http.Transport` connection pooling in `services/order-service/cmd/order-service/roles.go` (`MaxIdleConns: 100`, `MaxIdleConnsPerHost: 20`, `DialContext: 5s`, `ResponseHeaderTimeout: 35s/10s`) and pass to peer client constructors. Verification: run `go build ./cmd/order-service/...`.
- [x] 2.5 Equip `CustomerClient` and `CatalogClient` in `services/order-service/internal/adapters/httppeer` with `gobreaker.CircuitBreaker`, matching the resilience policy of Payment/Inventory/Shipping. Verification: run `go test ./internal/adapters/httppeer/...`.

## 3. PostgreSQL Connection Pool Normalization & Health Checks (P1)

- [x] 3.1 Fix `services/payment-service` runtime wiring (`fx.go:74`, `worker.go:56`, `role_impl.go:39`) to construct hardened pools (`MaxConns=20`, `MinConns=2`, `Lifetime=30m`, `Idle=5m`, `Check=30s`) without eager blocking ping. Verification: run `go test ./internal/runtime/...` in `payment-service`.
- [x] 3.2 Wire `MinConnections` and `MaxConnections` from config in `services/customer-service/cmd/customer-service/run.go` into `adapters/postgres/pool.go`, and apply `context.WithTimeout(ctx, 3*time.Second)` on health probe pings. Verification: run `go test ./internal/adapters/postgres/...` in `customer-service`.
- [x] 3.3 Replace raw `pgxpool.New(ctx, url)` in `inventory-service` and `shipping-service` with adapter constructors enforcing `MaxConns=20`, `MinConns=2`, and bounded health check pings. Verification: run `go test ./...` in both services.
- [x] 3.4 Ensure all database `Probe()` and `Ping()` methods across all services enforce bounded `context.WithTimeout` (3s). Verification: run adapter tests across all services.

## 4. Container BuildKit Cache Mounts (P2)

- [x] 4.1 Add `--mount=type=cache,target=/go/pkg/mod` and `--mount=type=cache,target=/root/.cache/go-build` to `services/inventory-service/Dockerfile.inventory-service`. Verification: `git diff services/inventory-service/Dockerfile.inventory-service`.
- [x] 4.2 Add `--mount=type=cache,target=/go/pkg/mod` and `--mount=type=cache,target=/root/.cache/go-build` to `services/shipping-service/Dockerfile.shipping-service`. Verification: `git diff services/shipping-service/Dockerfile.shipping-service`.
- [x] 4.3 Add BuildKit cache mounts to `tools/templates/Dockerfile.platform`. Verification: `git diff tools/templates/Dockerfile.platform`.

## 5. Standard Library Collections & Go 1.22+ Modernization (P2)

- [x] 5.1 Replace `sort.Slice` and `sort.Strings` with `slices.Sort` and `slices.SortFunc` across `tools/agentguide/validator.go`, `tools/doccheck/validator.go`, `platform/architecture/architecture.go`, `platform/cdc/register.go`, and `platform/health/probe.go`. Verification: run tests across `tools/` and `platform/`.
- [x] 5.2 Replace `sort.Slice`, `sort.SliceStable`, and `sort.Strings` across all 8 microservices, using `slices.SortStableFunc` where order stability is required. Verification: run `go vet ./...` across all services.
- [x] 5.3 Remove all 25 redundant `tc := tc` / `c := c` loop variable copies in test files across `platform/temporal`, `platform/observability`, `platform/kafka`, and services. Verification: run `go test ./...` in `platform/`.
- [x] 5.4 Simplify configuration default assignments using `cmp.Or` across `platform/temporal`, `platform/observability`, `customer-service`, `order-service`, and `notification-service`. Verification: run `go test ./...`.
- [x] 5.5 Migrate raw `log` imports in `services/customer-service/cmd/customer-service/main.go`, `run.go`, and `tools/workflowaudit/main.go` to `log/slog`. Verification: run `go build` on `customer-service` and `tools/workflowaudit`.

## 6. Multi-Service Verification & OpenSpec Governance (P3)

- [x] 6.1 Run `make -C platform verify` to ensure all platform contracts and architecture checks pass. Verification: command exits 0.
- [x] 6.2 Run unit tests across all 8 microservices (`go test ./...`). Verification: all tests pass.
- [x] 6.3 Run strict OpenSpec validation for `modernize-service-runtime-security-and-idioms`. Verification: `openspec validate modernize-service-runtime-security-and-idioms --strict --store openspec-store` exits 0 with no errors.
