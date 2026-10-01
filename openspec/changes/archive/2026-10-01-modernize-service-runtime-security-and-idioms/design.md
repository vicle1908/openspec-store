# Design: Modernize Service Runtime Security, BuildKit Caching, Outbound Resilience, and Go Standard Library Idioms

## Context

The `go-microservices` monorepo contains 8 independently deployable microservices (`catalog`, `customer`, `inventory`, `notification`, `order`, `payment`, `reporting`, `shipping`), a shared platform foundation (`platform/`), test suites (`tests/`), and operational tooling (`tools/`).

Following the toolchain upgrade to Go `1.27.1`, an exhaustive multi-agent research audit across all 8 services and platform tooling identified systemic areas for hardening and modernization:
1. Inbound HTTP server Slowloris vulnerability due to missing `ReadHeaderTimeout` or unconstrained listeners.
2. Unbounded outbound HTTP clients and `http.DefaultClient` fallbacks lacking connection pooling and timeout isolation.
3. Asymmetric peer resilience in `order-service` (`PaymentClient`, `InventoryClient`, `ShippingClient` use circuit breakers, whereas `CustomerClient` and `CatalogClient` do not).
4. PostgreSQL connection pool bypasses and defaults (`payment-service` runtime bypasses its own hardened pool; `customer`, `inventory`, `shipping`, `notification` run with default 4-connection caps or unbounded ping contexts).
5. Signal listener goroutine leaks from manual `signal.Notify` channels.
6. BuildKit caching disparities across 3 Dockerfiles.
7. Legacy reflection-based sorting (`sort.Slice`), redundant loop variable shadowing (`tc := tc`), and raw standard library logging.

---

## Architecture Standards & Technical Designs

### 1. Inbound HTTP Server Hardening (Slowloris Mitigation)

#### Rationale
Per Go documentation for `net/http.Server`:
> `ReadHeaderTimeout` is the amount of time allowed to read request headers. The connection's read deadline is reset after reading the headers... If `ReadHeaderTimeout` is zero, the value of `ReadTimeout` is used. If both are zero, there is no timeout.

Without `ReadHeaderTimeout`, an attacker or degraded client can trickle headers byte-by-byte (e.g. 1 byte every 5 seconds), exhausting server file descriptors and worker goroutines indefinitely.

#### Standard Server Specification
Every production HTTP server (API, metrics, and health probe servers) MUST enforce explicit deadlines:
```go
srv := &http.Server{
    Addr:              cfg.HTTPAddr,
    Handler:           handler,
    ReadHeaderTimeout: 10 * time.Second,
    ReadTimeout:       30 * time.Second,
    WriteTimeout:      30 * time.Second,
    IdleTimeout:       2 * time.Minute,
}
```

#### Affected Target Locations
- `services/notification-service/internal/runtime/fx.go` (both API and metrics servers)
- `services/customer-service/cmd/customer-service/run.go`
- `services/order-service/internal/runtime/runtime.go` (`NewHTTPServer`)
- `services/catalog-service/internal/runtime/runtime.go` (`NewHTTPServer`)
- `services/reporting-service/internal/runtime/wire.go` (`newHTTPServer`)
- `services/inventory-service/internal/runtime/fx.go` (inject full `ReadTimeout`, `WriteTimeout`, `IdleTimeout`)
- `services/payment-service/internal/runtime/fx.go` (inject full `ReadTimeout`, `WriteTimeout`, `IdleTimeout`)
- `services/shipping-service/internal/runtime/fx.go` & `worker.go` (inject full timeouts; standardize worker health server to 10s header timeout)

---

### 2. Outbound HTTP Client Resilience & Peer Protection

#### Rationale
- Using `http.DefaultClient` or package-level `http.Get`/`http.Post` in production code is dangerous because `http.DefaultClient` has zero timeout. A stalled upstream connection will hang the calling goroutine indefinitely.
- Raw `&http.Client{}` instances default to `http.DefaultTransport`, which caps idle connections at `MaxIdleConnsPerHost: 2`. Under concurrent peer RPC load, this triggers frequent connection closure and TLS renegotiation.
- In `order-service`, if customer or catalog services stall, un-breaker-protected calls will pile up and exhaust worker resources.

#### Standards & Patterns
1. **Eliminate DefaultClient Fallbacks**:
   - `platform/kafka/burrow.go`: Create a dedicated `defaultBurrowClient` with 10s timeout and bounded transport.
   - `notification-service/internal/adapters/http/recipient_resolver.go` & `httptest_provider.go`: Provide explicit fallback clients with timeouts.
   - CLI health checks (`customer-service`, `reporting-service`, `notification-service`): Use `&http.Client{Timeout: flags.timeout}`.
2. **Context Propagation on Probes**:
   - `order-service/internal/runtime/healthcheck.go`: Bind context with `context.WithTimeout` and attach via `http.NewRequestWithContext`.
3. **Shared Peer Transport Pooling**:
   - In `order-service/cmd/order-service/roles.go`, instantiate a shared `*http.Transport` with `MaxIdleConns: 100`, `MaxIdleConnsPerHost: 20`, `DialContext: 5s`, `TLSHandshakeTimeout: 5s`, and `ResponseHeaderTimeout: 10s`, and inject it into all peer clients.
4. **Circuit Breaker Alignment**:
   - Add `gobreaker.NewCircuitBreaker` to `CustomerClient` and `CatalogClient` in `order-service/internal/adapters/httppeer`, matching the breaker policy (`MaxRequests: 3`, `Interval: 60s`, `Timeout: 15s`, `ConsecutiveFailures > 5`) used by Payment, Inventory, and Shipping. Only 5xx status codes and network dial errors trip the breaker; 4xx client errors (e.g. 404 Customer Not Found) do not trip the breaker.
5. **Response Body Draining**:
   - Ensure all client error paths drain the body (`io.Copy(io.Discard, resp.Body)`) before calling `resp.Body.Close()`, preserving TCP keep-alive connection reuse.

---

### 3. PostgreSQL Connection Pool Normalization & Lifecycle Parameters

#### Rationale
- `pgxpool.Pool` defaults to `MaxConns = max(4, runtime.NumCPU())` when unconfigured. For microservices handling concurrent REST requests and Temporal workflow activities, 4 connections causes immediate query queueing under modest concurrency.
- If runtime bootstrapping bypasses the adapter constructor (as in `payment-service`), hardened settings in adapter files are completely ignored.
- Database probes without explicit timeout contexts can block indefinitely if PostgreSQL hangs on locks or fails to respond.

#### Standards & Settings Matrix
Across all services, pool configuration SHALL conform to:
```go
cfg, err := pgxpool.ParseConfig(dsn)
if err != nil {
    return nil, err
}

// 1. Connection Limits
cfg.MaxConns = 20                   // Max 20 connections per service instance
cfg.MinConns = 2                    // Maintain warm pool, avoiding cold-start latency

// 2. Connection Lifecycles
cfg.MaxConnLifetime = 30 * time.Minute       // Cycle connections before network intermediate timeouts
cfg.MaxConnLifetimeJitter = 2 * time.Minute // Prevent thundering herd reconnection spikes
cfg.MaxConnIdleTime = 5 * time.Minute        // Reclaim idle connections during off-peak periods
cfg.HealthCheckPeriod = 30 * time.Second     // Actively evict dead backend connections

// 3. Dial Timeouts & Instrumentation
cfg.ConnConfig.ConnectTimeout = 5 * time.Second
cfg.ConnConfig.Tracer = otelpgx.NewTracer()
```

#### Connection Budgeting
- Monorepo Topology: 8 microservices.
- At 20 max connections per service instance, a single complete replica set utilizes at most `8 * 20 = 160` connections.
- PostgreSQL 18 server default is configured for `max_connections = 300` in `deploy/docker-compose.yaml`, leaving abundant headroom for admin tools, migrations, and Debezium CDC slots.

#### Target Remediations
- `payment-service`: Update `internal/runtime/fx.go:74`, `worker.go:56`, and `role_impl.go:39` to invoke `paymentpg.NewPool(...)` instead of raw `pgxpool.New(...)`.
- `customer-service`: Wire `cfg.Database.MaxConnections` and `MinConnections` into `adapters/postgres/pool.go`, and apply `context.WithTimeout(ctx, 3*time.Second)` on health probe pings.
- `inventory-service` & `shipping-service`: Replace raw `pgxpool.New(ctx, url)` with an adapter constructor enforcing `MaxConns=20`, `MinConns=2`, and bounded health checks.
- `notification-service`: Apply explicit pool limits and add 3s deadline to health probe pings.

---

### 4. Signal Handling Lifecycle Modernization (`signal.NotifyContext`)

#### Rationale
Manual `ch := make(chan os.Signal, 1)` with a detached `go func() { <-ch; cancel() }`:
1. Leaks the goroutine permanently if the context is cancelled by a parent or timeout before a signal arrives.
2. Leaks the signal notification registration in the Go runtime signal table if `signal.Stop` is not deferred.

#### Standard Pattern
```go
func SignalContext(ctx context.Context) (context.Context, context.CancelFunc) {
    return signal.NotifyContext(ctx, os.Interrupt, syscall.SIGTERM)
}
```

#### Target Locations
- `platform/runtime/roles.go` (`WithSignal`)
- `services/customer-service/cmd/customer-service/run.go` (`withSignal`)
- `services/order-service/cmd/diag-consumer/main.go`
- `services/order-service/internal/runtime/runtime.go` (`NewShutdownSignalContext`)
- `services/catalog-service/internal/runtime/runtime.go` (`SignalContext`)

---

### 5. Dockerfile BuildKit Cache Mounts

#### Standard Pattern
For every multi-stage Go build Dockerfile:
```dockerfile
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /out/service ./cmd/service
```

#### Target Locations
- `services/inventory-service/Dockerfile.inventory-service`
- `services/shipping-service/Dockerfile.shipping-service`
- `tools/templates/Dockerfile.platform`

---

### 6. Standard Library Collections & Go 1.22+ Modernization

#### 1. Sorting Modernization
- **Strings**: `sort.Strings(s)` → `slices.Sort(s)`.
- **Custom Slices**:
  ```go
  // Before:
  sort.Slice(items, func(i, j int) bool { return items[i].ID < items[j].ID })
  // After:
  slices.SortFunc(items, func(a, b Item) int { return cmp.Compare(a.ID, b.ID) })
  ```
- **Stable Sorts**: `sort.SliceStable(...)` → `slices.SortStableFunc(...)` (e.g. in `tests/cross-service-smoke/smoke/orchestration.go`).
- **Sorted Checks**: `sort.StringsAreSorted(s)` → `slices.IsSorted(s)`.

#### 2. Redundant Loop Variable Pruning
In Go 1.22+, loop variables have per-iteration scope. Safely delete all 25 identified instances of `tc := tc`, `tt := tt`, and `c := c`.

#### 3. Default Configuration Values (`cmp.Or`)
Simplify fallback branching across `platform/temporal`, `platform/observability`, `services/customer-service`, `services/order-service`, and `services/notification-service` using `cmp.Or(val, defaultVal)`.

#### 4. Structured Logging (`log/slog`)
Migrate raw standard library `"log"` imports in `services/customer-service/cmd/customer-service/main.go`, `run.go`, and `tools/workflowaudit/main.go` to `log/slog` and structured logging.

---

## Verification & Guardrail Strategy

1. **Temporal Determinism Protection**:
   - Slices and sorting updates in workflow execution paths must preserve exact sort ordering.
   - Run `verification/fixtures/temporal-determinism/` fixtures and `make -C platform verify` to confirm deterministic replay.
2. **Architecture & Boundary Verification**:
   - Verify that adding circuit breakers to `CustomerClient` and `CatalogClient` does not violate hexagonal boundaries (`test/architecture/adapter_port_test.go`).
3. **Uncached Test Execution**:
   - Execute `go test -count=1 ./...` across all 8 services and `platform/`.
4. **OpenSpec Governance**:
   - Execute `openspec validate modernize-service-runtime-security-and-idioms --strict --store openspec-store`.
