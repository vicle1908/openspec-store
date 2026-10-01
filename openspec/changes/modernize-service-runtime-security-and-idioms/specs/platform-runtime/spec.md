## ADDED Requirements

### Requirement: HTTP server Slowloris hardening and timeout standards

The platform and all service HTTP servers SHALL configure immutable timeout bounds to mitigate Slowloris and connection starvation attacks. Every `http.Server` instance MUST explicitly set `ReadHeaderTimeout: 10 * time.Second`, `ReadTimeout: 30 * time.Second`, `WriteTimeout: 30 * time.Second`, and `IdleTimeout: 2 * time.Minute`. Unbounded or zero timeout configurations on HTTP API or metrics listeners are strictly prohibited.

#### Scenario: HTTP server enforces ReadHeaderTimeout
- **WHEN** an HTTP client establishes a TCP connection but sends request headers slowly or stalls
- **THEN** the server terminates the connection after 10 seconds, freeing the file descriptor and worker goroutine

#### Scenario: HTTP server bounds read and write deadlines
- **WHEN** an HTTP server receives a legitimate request
- **THEN** request body reads are bounded by 30 seconds, response writes are bounded by 30 seconds, and idle keep-alive connections are closed after 2 minutes

### Requirement: Standard library idiom and collections conformance

The platform and services SHALL adhere to modern Go standard library idioms:
1. Slice and collection sorting SHALL use `slices.Sort` or `slices.SortFunc` from the standard `slices` package (Go 1.21+), deprecating reflection-based `sort.Slice` and legacy `sort.Strings`.
2. Fallback configuration and default value assignments SHALL use `cmp.Or` (Go 1.22+) instead of manual `if x == "" { x = ... }` branching.
3. Test suites SHALL NOT include redundant per-iteration loop variable copies (`tc := tc`), conforming to Go 1.22+ per-iteration loop variable semantics.
4. Signal handling in standalone runtimes SHALL use `signal.NotifyContext` to avoid goroutine and channel leaks.

#### Scenario: Slices sorting avoids reflection
- **WHEN** a slice of strings or ordered structs is sorted
- **THEN** `slices.Sort` or `slices.SortFunc` is used, producing type-safe sorting without runtime reflection or interface boxing

#### Scenario: Configuration defaulting uses cmp.Or
- **WHEN** a configuration string or numeric field has a default value fallback
- **THEN** `cmp.Or(val, defaultVal)` evaluates the first non-zero value concisely

#### Scenario: Signal handling uses NotifyContext
- **WHEN** a standalone runtime or tool registers for termination signals
- **THEN** `signal.NotifyContext` binds context cancellation to SIGINT and SIGTERM without leaking watcher goroutines
