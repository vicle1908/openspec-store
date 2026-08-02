## ADDED Requirements

### Requirement: Role-subcommand entrypoint
The platform SHALL provide a `roles.Run(ctx, role)` dispatch that selects one of `api`, `worker`, `orchestrator`, `migrate`, `infrastructure init`, `replay-quarantine`, and `healthcheck`. The binary SHALL invoke exactly one role per container; combining roles in a single container is forbidden except for `healthcheck`, which is a sidecar-style probe used by Docker Compose.

#### Scenario: Entry with role `api` runs the API server
- **WHEN** the entrypoint receives the role argument `api`
- **THEN** the HTTP API server starts and the binary does not start Temporal workers or migration logic

#### Scenario: Entry with role `migrate` runs pending migrations
- **WHEN** the entrypoint receives the role argument `migrate`
- **THEN** the migration runner applies pending schema migrations and exits with code 0

#### Scenario: Entry with role `infrastructure init` provisions Kafka topics
- **WHEN** the entrypoint receives the role argument `infrastructure init`
- **THEN** the runner creates the configured Kafka topics with the documented partition counts and replication factors, registers Debezium connectors, and exits 0 on success

### Requirement: Fx composition helpers
The platform SHALL expose Fx `Option` constructors for observability, Kafka harness, health probes, and configuration. Each service composes its own root `fx.App` from these helpers plus its own domain, application, and adapter modules. The platform SHALL NOT prescribe which Fx modules a service must use; the helpers exist to reduce duplication.

#### Scenario: Fx app starts with observability and health options
- **WHEN** a service composes `runtime.NewApp(runtime.WithObservability(), runtime.WithHealth())`
- **THEN** the OTel SDK, Prometheus exporter, and HTTP probe server start before any service-specific providers

### Requirement: Graceful shutdown
The platform SHALL register SIGTERM and SIGINT handlers that trigger a graceful shutdown sequence: HTTP servers stop accepting new requests and complete in-flight requests, Kafka consumers commit final offsets and stop polling, Temporal workers finish the current workflow tick and stop polling, the OTel SDK flushes pending exports within 5 seconds, and the process exits 0. The total shutdown budget SHALL be 30 seconds; if any component exceeds it, the process exits non-zero with a structured log entry per stuck component.

#### Scenario: SIGTERM triggers graceful shutdown
- **WHEN** SIGTERM is received
- **THEN** the HTTP server stops accepting new connections, the Kafka consumer commits its offset, the Temporal worker stops polling, the OTel SDK flushes, and the process exits 0

#### Scenario: Stuck component causes non-zero exit
- **WHEN** a component does not stop within its budget
- **THEN** the structured log records `component=<name> reason=<reason> elapsed_ms=<n>` and the process exits non-zero

### Requirement: Typed configuration load
The platform SHALL expose a `config.Load[ConfigType](os.LookupEnv, prefix)` helper that reads environment variables matching `<PREFIX>_<KEY>`, parses them into the supplied struct, and validates required fields. The helper MUST reject unknown fields when `strict=true` and MUST NOT accept relative paths in production.

#### Scenario: Config loader applies env vars
- **WHEN** `ORDER_DATABASE_URL=postgres://example` is in the environment and the loader runs with prefix `ORDER`
- **THEN** the returned struct has `DatabaseURL = "postgres://example"`

#### Scenario: Config loader rejects missing required fields
- **WHEN** a required field is not in the environment
- **THEN** the loader returns a typed error listing the missing keys

#### Scenario: Config loader rejects unknown fields in strict mode
- **WHEN** `ORDER_UNKNOWN=value` is in the environment and the loader runs with strict mode
- **THEN** the loader returns a typed error `ErrUnknownConfigKey("UNKNOWN")`

### Requirement: Bootstrap order and lifecycle
The platform SHALL guarantee a deterministic bootstrap order: configuration loads first, observability providers start second, migrations apply third (when running with role `migrate` or as a one-shot before `infrastructure init`), Kafka topics and Debezium connectors provision fourth (when running with role `infrastructure init`), and the role-specific work (HTTP server, Temporal worker, Kafka consumer) starts fifth. Health probes become `ready` only after step 5 finishes.

#### Scenario: Bootstrap order is enforced across roles
- **WHEN** the entrypoint runs with role `api`
- **THEN** observability starts before the HTTP server, and the HTTP server starts before `/health/ready` returns 200

#### Scenario: Migrations apply before topics init
- **WHEN** a fresh compose stack starts
- **THEN** `order-migrate` and `customer-migrate` etc. run to completion before `*-infrastructure init` runs

### Requirement: One Fx app per role
Each role (`api`, `worker`, `orchestrator`, `migrate`, `infrastructure init`, `healthcheck`) constructs its own `fx.New(...)` call; no role combines into a single conditional Fx graph. The platform exposes `runtime.NewApp(role)` which builds the appropriate app per role. The benefits: a service's `api` container does NOT initialize Kafka consumers or Temporal workers, and a `worker` container does NOT initialize the HTTP API server. The platform's architecture test (`test/architecture/role_isolation_test.go`) enforces this by counting `OnStart` invocations per role: each role MUST start ≤ N providers (N is documented per role).

#### Scenario: API role does not initialize Kafka consumer
- **WHEN** the entrypoint runs with role `api` and Kafka is unavailable
- **THEN** the API server starts successfully and the role's startup does not depend on Kafka availability (Kafka is a separate role's concern)

#### Scenario: Worker role does not initialize HTTP server
- **WHEN** the entrypoint runs with role `worker`
- **THEN** the worker starts successfully and no HTTP listener binds (port 8080 is unused)

### Requirement: `app.Err()` SHALL be inspected as a pre-flight check
Before `app.Run()` the platform MUST inspect `app.Err()` (returned by `fx.New(opts...)`) and exit non-zero with a typed error listing the broken graph if the initialization error is non-nil. This catches duplicate-provider errors, missing-producer errors, and circular-dependency errors at startup rather than letting them surface as runtime panics. The validation MUST run as a separate function call in `cmd/<service>/main.go` so the failure mode is explicit.

> **Correction**: a previous draft of this requirement referenced
> `fx.ValidateApp(opts...)`. That API does not exist in
> `go.uber.org/fx v1.24.0`. The real Fx mechanism is to construct the
> app with `fx.New(opts...)` and inspect the `error` it returns (stored
> on the `*fx.App` and accessible via `app.Err()`). `fxtest.New(t,
> opts...)` also auto-validates and `t.Fatal`s on a broken graph.

#### Scenario: Duplicate provider is caught at startup
- **WHEN** a service's module declares two providers for the same concrete type
- **THEN** `fx.New(opts...)` returns a non-nil error, `app.Err()` exposes the duplicate-provider message, and the process exits non-zero before `app.Run()` is called

#### Scenario: Circular dependency is caught at startup
- **WHEN** service A's provider depends on B and B's provider depends on A
- **THEN** `fx.New(opts...)` returns a non-nil error and `app.Err()` describes the cycle; the process exits non-zero

### Requirement: `fxtest.New` SHALL be used for lifecycle tests
The platform SHALL require that every service's lifecycle test uses `fxtest.New(t, ...)`, `app.RequireStart()`, and `app.RequireStop()`. Tests that exercise the Fx graph MUST assert that `OnStart` and `OnStop` hooks run in the documented order (parent → child for OnStart, reverse for OnStop). The platform's `test/runtime/fxtest_helpers.go` SHALL expose helpers that wrap `fxtest.WithTestLogger(t)` (the Fx-native test logger) and assert hook ordering.

> **Correction**: a previous draft referenced
> `fxtest.WithRequireStartTimeout` / `fxtest.WithRequireStopTimeout`.
> Those helpers do not exist in `go.uber.org/fx v1.24.0`. The
> canonical test helpers are `fxtest.WithTestLogger(t)` (added v1.21.0)
> and `fxtest.EnforceTimeout` (added v1.22.0). The platform's helper
> module composes these.

#### Scenario: Lifecycle test asserts hooks fire
- **WHEN** a test uses `fxtest.New(t, ObservabilityModule, HealthModule)` and calls `app.RequireStart()`
- **THEN** the OTel SDK OnStart fires and the HTTP probe server OnStart fires (in dependency order); calling `app.RequireStop()` reverses the order

### Requirement: Fx `fx.StartTimeout` and `fx.StopTimeout` configure lifecycle budgets
The platform SHALL use `fx.StartTimeout(d)` and `fx.StopTimeout(d)` to set the lifecycle budget per role (default 30s, configurable). These are the Fx-native options; the previous draft referenced a non-existent `fx.WithTimeout(...)`.

> **Correction**: `fx.WithTimeout(...)` does not exist in Fx v1.24.0.
> The correct API names are `fx.StartTimeout` and `fx.StopTimeout`
> (both real and stable).

#### Scenario: API role uses 30s start and stop timeouts
- **WHEN** the entrypoint constructs the API role's `fx.New(opts...)`
- **THEN** the `opts` include `fx.StartTimeout(30 * time.Second)` and `fx.StopTimeout(30 * time.Second)`

### Requirement: Signal ownership is unambiguous — Fx owns signals for long-lived roles
For long-lived roles (`api`, `worker`, `orchestrator`), the platform's `runtime.NewApp(role)` uses Fx's `app.Run()` which owns SIGINT/SIGTERM signal handling. The platform MUST NOT also register `signal.NotifyContext` in the same role — that's dual signal ownership and causes races. For one-shot roles (`migrate`, `infrastructure init`, `healthcheck`), the platform's runner uses `signal.NotifyContext` (since Fx owns `Shutdowner` only for apps that `app.Run`).

#### Scenario: API role allows Fx to own signals
- **WHEN** the API role receives SIGTERM
- **THEN** Fx's signal handler triggers `app.Stop(stopCtx)`; no `signal.NotifyContext` is registered in the role's main

#### Scenario: Migrate role uses signal.NotifyContext for early cancellation
- **WHEN** the migrate role is executing a slow migration and SIGTERM is received
- **THEN** the signal context cancels and the runner exits cleanly before completion

### Requirement: Domain and application layers MUST NOT import Fx
The `domain/` and `application/` packages of every service SHALL contain zero imports of `go.uber.org/fx`. All `fx.Provide`, `fx.Invoke`, `fx.Lifecycle`, `fx.Hook` usage lives in `cmd/<service>/`, `internal/runtime/`, or in dedicated `*fx.go` adapter files alongside the adapter packages. The platform's architecture test (`test/architecture/domain_no_fx_dependency_test.go`) greps the import graph and fails the build if any domain or application source file imports Fx. This separation enables Fx-free unit tests against domain code and keeps the domain portable.

#### Scenario: Domain source has no Fx import
- **WHEN** the architecture test scans `internal/domain/order/order.go` and every file in `internal/domain/`
- **THEN** no `import "go.uber.org/fx"` is found; if found, the test fails with the offending file path

### Requirement: Role-scoped Fx modules SHALL compose infra + role-specific modules
The platform SHALL expose `runtime.RoleModule(role, appModule)` which composes the role-specific module (`appModule`) with the role's required infrastructure modules (`ObservabilityModule` always; `KafkaHarnessModule` for orchestrator; `HealthModule` for api/worker/orchestrator; `TemporalWorkerModule` for worker). The role-specific module's wiring SHALL be what differs per role; the platform MUST guarantee the same observability, health, and configuration modules attach to every role.

#### Scenario: API role composes observability + health + http module
- **WHEN** `runtime.RoleModule("api", appModule)` resolves
- **THEN** the resulting Fx graph contains `ObservabilityModule`, `HealthModule`, and the service's `appModule` (HTTP server); it does NOT contain `KafkaHarnessModule` or `TemporalWorkerModule`

### Requirement: Stop timeout honors Fx budget, not nested hardcoded budgets
Components registered with the Fx lifecycle use the Fx-managed `StopTimeout` (default 30 seconds, configurable per role) as their shutdown budget. The platform's runners MUST NOT introduce a hardcoded 5-second `context.WithTimeout` that wraps `app.Stop(ctx)` because that nested timeout (5 seconds) overrides the broader budget. Component-level shutdown behavior is configured via Fx's `fx.Hook.OnStop` returning a context that respects the Fx stop budget.

#### Scenario: Fx stop timeout is honored end-to-end
- **WHEN** the API role runs and SIGTERM is received, with `fx.StopTimeout(45 * time.Second)`
- **THEN** every `OnStop` hook has 45 seconds to finish; if any hook exceeds, Fx returns the error which the runner surfaces as a non-zero exit code

### Requirement: Temporal worker lifecycle uses `fx.StartStopHook` (not blocking Run)
The Temporal worker's `Start()` is non-blocking; the platform registers the worker via `fx.StartStopHook` so Fx owns the lifecycle. The platform SHALL NOT call `worker.Run(...)` from inside `OnStart` because `Run` blocks until interrupt and deadlocks Fx. The pattern is:

```go
lc.Append(fx.StartStopHook(
    func() error { return w.Start() },  // non-blocking
    func() { _ = w.Stop() },            // idiomatic
))
```

#### Scenario: Temporal worker hook does not block Fx startup
- **WHEN** the worker role runs `fx.New(...)` and `app.Run()`
- **THEN** `OnStart` returns quickly (within milliseconds) because `worker.Start()` is non-blocking; the worker keeps polling in its own goroutine until `OnStop` calls `worker.Stop()`