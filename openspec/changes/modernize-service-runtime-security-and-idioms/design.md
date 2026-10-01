# Design: Modernize Service Runtime Security, BuildKit Caching, and Go Standard Library Idioms

## Context

The `go-microservices` monorepo contains 8 independently deployable microservices (`catalog`, `customer`, `inventory`, `notification`, `order`, `payment`, `reporting`, `shipping`), a shared platform foundation (`platform/`), test suites (`tests/`), and operational tooling (`tools/`).

Following the toolchain upgrade to Go `1.27.1`, an exhaustive scan of the repository surfaced several implementation areas that lag official recommendations and security standards:
- **Missing HTTP Server Timeouts**: Omitting `ReadHeaderTimeout` on `http.Server` instances exposes services to Slowloris attacks.
- **Manual Signal Handling**: Spawning detached goroutines with manual `signal.Notify` channels risks goroutine leaks and uncoordinated shutdowns.
- **Missing BuildKit Cache Mounts**: 3 Dockerfiles lack `/go/pkg/mod` and build cache mounts.
- **Legacy Reflection-based Sorting**: 68 call sites use `sort.Slice` / `sort.Strings` instead of Go 1.21+ `slices.Sort` / `slices.SortFunc`.
- **Pre-Go 1.22 Idioms**: 25 redundant loop copies (`tc := tc`) and 69 repetitive fallback statements (`if x == "" { x = ... }`) add unnecessary boilerplate.

---

## Architectural Decisions & Migration Standards

### 1. HTTP Server Security Standards (Slowloris Hardening)

#### Rationale & Official Documentation
Per Go documentation for `net/http.Server`:
> `ReadHeaderTimeout` is the amount of time allowed to read request headers... If `ReadHeaderTimeout` is zero, the value of `ReadTimeout` is used. If both are zero, there is no timeout.

Without `ReadHeaderTimeout`, an attacker can send headers at 1 byte per several seconds, exhausting connections without triggering `ReadTimeout` until the headers are fully read.

#### Standard Configuration
Every `http.Server` in the monorepo (both API handlers and metrics/health listeners) SHALL be configured with:
```go
srv := &http.Server{
    Addr:              addr,
    Handler:           handler,
    ReadHeaderTimeout: 10 * time.Second,
    ReadTimeout:       30 * time.Second,
    WriteTimeout:      30 * time.Second,
    IdleTimeout:       2 * time.Minute,
}
```

#### Affected Services & Files
- `services/notification-service/internal/runtime/fx.go` (both API and metrics servers)
- `services/customer-service/cmd/customer-service/run.go`
- `services/order-service/internal/runtime/runtime.go` (`NewHTTPServer`)
- `services/catalog-service/internal/runtime/runtime.go` (`NewHTTPServer`)
- `services/reporting-service/internal/runtime/wire.go` (`NewHTTPServer`)

---

### 2. Signal Handling Modernization (`signal.NotifyContext`)

#### Rationale & Official Documentation
Per `os/signal.NotifyContext` (Go 1.16+):
> `NotifyContext` returns a copy of the parent context that is marked done (its `Done` channel is closed) when one of the listed signals arrives, when the returned `stop` function is called, or when the parent context's `Done` channel is closed.

Manual `ch := make(chan os.Signal, 1)` with background goroutines:
1. Causes goroutine leaks if context cancellation occurs before a signal arrives.
2. Can fail to unregister signal handlers properly if `signal.Stop` is not invoked.

#### Standard Pattern
```go
// Replace manual goroutines with idiomatic signal context:
ctx, stop := signal.NotifyContext(parentCtx, os.Interrupt, syscall.SIGTERM)
defer stop()
```

#### Affected Locations
- `platform/runtime/roles.go` (`WithSignal`)
- `services/customer-service/cmd/customer-service/run.go` (`withSignal`)
- `services/order-service/cmd/diag-consumer/main.go`
- `services/order-service/internal/runtime/runtime.go` (`NewShutdownSignalContext`)
- `services/catalog-service/internal/runtime/runtime.go` (`SignalContext`)

---

### 3. Container BuildKit Cache Mounts

#### Rationale & Official Documentation
Docker BuildKit `--mount=type=cache` mounts a persistent cache directory into the build container. In Go builds, caching `/go/pkg/mod` avoids re-downloading modules, and caching `/root/.cache/go-build` enables incremental compilation across Docker build invocations.

#### Standard Pattern
```dockerfile
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/service ./cmd/service
```

#### Target Dockerfiles
- `services/inventory-service/Dockerfile.inventory-service`
- `services/shipping-service/Dockerfile.shipping-service`
- `tools/templates/Dockerfile.platform`

---

### 4. Standard Library Collections (`slices.Sort`, `slices.SortFunc`)

#### Rationale & Official Documentation
Go 1.21 introduced `slices`:
- `slices.Sort` replaces `sort.Strings`, `sort.Ints`, and `sort.Float64s` using a non-allocating, type-safe introsort.
- `slices.SortFunc` replaces `sort.Slice` without reflection overhead or boxing.

#### Migration Patterns
- String slices:
  ```go
  // Before:
  sort.Strings(items)
  // After:
  slices.Sort(items)
  ```
- Struct slices with custom comparator:
  ```go
  // Before:
  sort.Slice(items, func(i, j int) bool { return items[i].Path < items[j].Path })
  // After:
  slices.SortFunc(items, func(a, b Item) int { return cmp.Compare(a.Path, b.Path) })
  ```

---

### 5. Go 1.22+ Idiom Clean-up (`cmp.Or` & Loop Variable Scoping)

#### Rationale & Official Documentation
1. **Loop Variable Scoping (Go 1.22)**:
   - In Go 1.22+, loop variables have per-iteration scope.
   - `tc := tc` or `c := c` lines inside `for ... range` loops are obsolete and should be pruned.
2. **Default Value Simplification (`cmp.Or`)**:
   - `cmp.Or(val1, val2, ...)` returns the first non-zero value.
   - Replaces verbose `if val == "" { val = defaultVal }`.

---

## Verification Strategy

1. **Static Analysis & Compilation**:
   - `go vet ./...` in `platform/` and all 8 services.
   - `golangci-lint` or `make verify-pr`.
2. **Unit & Architecture Tests**:
   - `make -C platform verify` to validate shared runtime and hexagonal contracts.
   - `go test ./...` in all 8 microservices.
3. **OpenSpec Governance**:
   - `openspec validate modernize-service-runtime-security-and-idioms --strict --store openspec-store`.
