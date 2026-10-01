## ADDED Requirements

### Requirement: HTTP server Slowloris hardening and timeout standards

The platform and all service HTTP servers SHALL configure immutable timeout bounds to mitigate Slowloris and connection starvation attacks. Every `http.Server` instance MUST explicitly set `ReadHeaderTimeout: 10 * time.Second`, `ReadTimeout: 30 * time.Second`, `WriteTimeout: 30 * time.Second`, and `IdleTimeout: 2 * time.Minute`. Unbounded or zero timeout configurations on HTTP API, metrics, and health probe listeners are strictly prohibited.

#### Scenario: HTTP server enforces ReadHeaderTimeout
- **WHEN** an HTTP client establishes a TCP connection but sends request headers slowly or stalls
- **THEN** the server terminates the connection after 10 seconds, freeing the file descriptor and worker goroutine

#### Scenario: HTTP server bounds read and write deadlines
- **WHEN** an HTTP server receives a legitimate request
- **THEN** request body reads are bounded by 30 seconds, response writes are bounded by 30 seconds, and idle keep-alive connections are closed after 2 minutes

### Requirement: PostgreSQL connection pool and health check standards

All services utilizing PostgreSQL SHALL construct connection pools using `pgxpool.NewWithConfig` with explicit lifecycle bounds. The pool configuration MUST specify `MaxConns` (default 20, minimum 2), `MinConns` (default 2), `MaxConnLifetime` (default 30 minutes), `MaxConnIdleTime` (default 5 minutes), and `HealthCheckPeriod` (default 30 seconds). Database health check probes and ping routines MUST enforce a bounded context timeout (maximum 3 seconds). Long-lived services MUST NOT bypass adapter pool constructors with unconfigured `pgxpool.New` calls.

#### Scenario: Service enforces connection pool bounds
- **WHEN** a service initializes its PostgreSQL connection pool
- **THEN** the pool enforces `MaxConns = 20`, maintains warm connections with `MinConns = 2`, and evicts stale connections according to the configured lifetime and idle policies

#### Scenario: Database health check probe times out cleanly
- **WHEN** PostgreSQL backend experiences locking delays or becomes unresponsive during a health check
- **THEN** the probe fails after 3 seconds without blocking the calling HTTP or worker thread

### Requirement: Outbound HTTP client and peer resilience standards

All outbound HTTP calls SHALL use explicit, timeout-bounded `*http.Client` instances. Usages of `http.DefaultClient` and package-level `http.Get`/`http.Post`/`http.Head` in production runtime code are strictly prohibited. Inter-service HTTP peer clients in `order-service` SHALL utilize a shared `*http.Transport` with connection pooling (`MaxIdleConns: 100`, `MaxIdleConnsPerHost: 20`) and MUST protect remote peer invocations with `gobreaker.CircuitBreaker`. All outbound requests MUST be created with `http.NewRequestWithContext` to ensure context cancellation and timeout propagation.

#### Scenario: Outbound call avoids thread hanging
- **WHEN** an external HTTP dependency stalls or drops packets
- **THEN** the outbound client aborts the request after its configured timeout deadline, preventing goroutine starvation

#### Scenario: Degraded peer trips circuit breaker
- **WHEN** an HTTP peer returns 5 consecutive 5xx errors or network dial failures
- **THEN** the circuit breaker transitions to open state, failing fast on subsequent requests for 15 seconds without overloading the degraded peer

### Requirement: Standard library idiom and collections conformance

The platform and services SHALL adhere to modern Go standard library idioms:
1. Slice and collection sorting SHALL use `slices.Sort`, `slices.SortFunc`, or `slices.SortStableFunc` from the standard `slices` package (Go 1.21+), deprecating reflection-based `sort.Slice` and legacy `sort.Strings`.
2. Fallback configuration and default value assignments SHALL use `cmp.Or` (Go 1.22+) instead of manual `if x == "" { x = ... }` branching.
3. Test suites SHALL NOT include redundant per-iteration loop variable copies (`tc := tc`), conforming to Go 1.22+ per-iteration loop variable semantics.
4. Signal handling in standalone runtimes SHALL use `signal.NotifyContext` to avoid goroutine and channel leaks.
5. Service entrypoints and operational tools SHALL use structured `log/slog` logging rather than raw standard library `log`.

#### Scenario: Slices sorting avoids reflection
- **WHEN** a slice of strings or ordered structs is sorted
- **THEN** `slices.Sort` or `slices.SortFunc` is used, producing type-safe sorting without runtime reflection or interface boxing

#### Scenario: Configuration defaulting uses cmp.Or
- **WHEN** a configuration string or numeric field has a default value fallback
- **THEN** `cmp.Or(val, defaultVal)` evaluates the first non-zero value concisely

#### Scenario: Signal handling uses NotifyContext
- **WHEN** a standalone runtime or tool registers for termination signals
- **THEN** `signal.NotifyContext` binds context cancellation to SIGINT and SIGTERM without leaking watcher goroutines
