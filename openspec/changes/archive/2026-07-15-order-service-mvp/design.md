## Context

We are building a Go microservices platform starting with an Order Service MVP. The system must handle order lifecycle management with:

- **DDD Architecture**: Clear separation of domain logic from infrastructure
- **Event-Driven**: Orders emit domain events that flow through Kafka
- **Durable Workflows**: Order fulfillment orchestrated by Temporal
- **Reliable Messaging**: Debezium CDC captures database changes → Kafka
- **Type Safety**: Protobuf contracts for all inter-service communication

### Technology Stack (Latest Versions as of July 2026)

| Component | Version | Notes |
|-----------|---------|-------|
| Go | **1.26.5** | Current stable security-patched release; pin exactly across `go.mod`, CI, and containers |
| Temporal Go SDK | **v1.46.0** | Workflows, activities, updates/signals, child workflows, worker versioning |
| pgx/v5 | **v5.10.0** | PostgreSQL driver and `pgxpool`; minimum Go 1.25, verified with pinned Go 1.26.5 |
| Buf CLI | **v1.71.0** | Protobuf generation, linting, and breaking-change enforcement |
| Debezium Connect | **3.6.0.Final** | PostgreSQL CDC plus Outbox Event Router SMT |
| PostgreSQL | **18.4** | Order persistence; supported through Nov 2030 |
| Apache Kafka | **4.3.1** | KRaft broker for local event transport |
| Temporal CLI dev server | **v1.6.1** | Local orchestration backend with SQLite persistence and bundled UI |
| Temporal Server | **v1.31.2** | Production self-hosted compatibility target; not used by local Compose |
| chi/v5 | **v5.3.1** | HTTP routing; trusted proxy behavior configured explicitly |
| franz-go | **v1.21.5** | Order-owned Kafka consumer for durable workflow initiation |
| Fx | **v1.24.0** | In-process composition and lifecycle only; not a service locator |
| Zap | **v1.28.0** | Structured application logging |
| Viper | **v1.21.0** | Configuration loading with explicit decode and validation |
| Testcontainers for Go | **v0.43.0** | Isolated PostgreSQL/Kafka integration tests |
| Goose | **v3.27.2** | Embedded, service-owned PostgreSQL migrations and migration validation |
| govulncheck | **v1.6.0** | Reachability-aware Go vulnerability gate |
| k6 | **v1.8.0** | API and end-to-end latency threshold gates |
| Trivy | **v0.72.0** | Repository, image, configuration, secret, and SBOM verification |
| go-redis | **v9.21.0 optional** | Correct module path is `github.com/redis/go-redis/v9`; add only for a measured use case |

### Constraints

- Start as one independently deployable Order Service, organized as modules that can be extracted without shared tables
- Protobuf is the canonical public contract; domain types remain private to their owning service
- Debezium CDC transports the transactional outbox with at-least-once delivery
- Temporal orchestrates long-running work; each extracted service owns its workers and task queue
- Local Compose is a development topology, not a production availability design
- Optional infrastructure is introduced only when a capability requires it

## Goals / Non-Goals

**Goals:**
- Implement a production-ready Order Aggregate with DDD patterns
- Demonstrate transactional outbox → Debezium CDC → Kafka flow
- Create a Temporal workflow for order fulfillment with saga compensation
- Provide a working Docker Compose stack for local development
- Establish clean architecture with clear port/adapter boundaries

**Non-Goals:**
- Multi-service orchestration (Phase 2)
- Full CQRS with separate read models
- Kubernetes deployment manifests (Phase 2)
- gRPC gateway (REST only for MVP)
- Full OpenTelemetry instrumentation (minimal tracing only)

## Decisions

### 1. DDD Aggregate Structure

**Decision:** Order is the aggregate root containing OrderLineItem entities, Address value objects, and payment/fulfillment references. Payment provider state remains outside the aggregate so a future Payment Service can own it.

```
Order (Aggregate Root)
├── OrderID (ULID) - identity
├── CustomerID - reference
├── Status - state machine
├── LineItems []OrderLineItem - entities
├── ShippingAddress Address - value object
├── BillingAddress Address - value object
├── PaymentReference - external capability reference
├── TotalAmount Money - value object
├── CreatedAt, UpdatedAt - timestamps
└── Events []DomainEvent - emitted on state changes
```

**Rationale:** Order is a natural aggregate boundary - it groups items, addresses, and payment that must be consistent together.

**Alternatives:**
- Separate OrderHeader/OrderLines: More complex, no clear benefit for MVP
- No aggregate: Would scatter business logic across services

### 2. Outbox Pattern: Debezium CDC (Not Polling)

**Decision:** Use Debezium to read PostgreSQL WAL and publish to Kafka, rather than polling-based outbox processor.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Application │───▶│ PostgreSQL  │───▶│   WAL Log   │───▶│  Debezium   │
│   writes    │    │  (orders,  │    │   (binary)  │    │  Connector  │
└─────────────┘    │   outbox)   │    └─────────────┘    └──────┬──────┘
                   └─────────────┘                               │
                                                                    │
                                                                    ▼
                                                             ┌─────────────┐
                                                             │   Kafka     │
                                                             │  (topics)   │
                                                             └─────────────┘
```

**Rationale:**
- Zero application overhead for CDC
- Near real-time (sub-second latency)
- No polling overhead on database
- Atomic persistence of aggregate changes and outbox records
- At-least-once publication without a database polling loop
- Consumers deduplicate by immutable event ID; ordering is guaranteed only per aggregate key
- Schema compatibility is enforced in source control, not delegated to Debezium

**Alternatives:**
- Polling-based outbox: Simpler but higher latency, more DB load
- Transactional outbox pattern in-app: More complex, reinventing CDC

### 3. Temporal Workflow Design

**Decision:** Single OrderFulfillmentWorkflow with typed signals for updates.

```
StartOrderFulfillment(orderID)
    │
    ▼
┌─────────────────────┐
│ ValidateInventory   │──── (retry 3x, exponential backoff)
│                     │
│ If fails:           │
│   Signal: CancelOrder
└────────┬────────────┘
         │ success
         ▼
┌─────────────────────┐
│ ProcessPayment      │──── (retry 3x)
│                     │
│ If fails:           │
│   Execute: Refund (saga compensation)
│   Signal: PaymentFailed
└────────┬────────────┘
         │ success
         ▼
┌─────────────────────┐
│ ReserveInventory    │──── (retry 3x)
│                     │
│ If fails:           │
│   Execute: Refund (saga compensation)
│   Execute: ReleaseInventory (saga compensation)
│   Signal: InventoryFailed
└────────┬────────────┘
         │ success
         ▼
┌─────────────────────┐
│ MarkOrderShipped    │──── (retry 3x)
│                     │
│ On Signal:          │
│   UpdateShippingInfo
└────────┬────────────┘
         │ complete
         ▼
    Workflow Complete
```

**Rationale:**
- Single workflow keeps saga logic co-located
- Typed signals allow external updates (tracking number, etc.)
- Activity retries handle transient failures
- Compensation activities handle permanent failures

**Alternatives:**
- Child workflows: More complex, harder to track in UI
- No saga: Would require compensating logic elsewhere

### 4. Protobuf Schema Strategy

**Decision:** Use buf for protobuf management with separate packages per domain.

```
proto/
├── buf.yaml
├── buf.lock
├── order/
│   ├── v1/
│   │   ├── order.proto
│   │   ├── commands.proto
│   │   └── events.proto
│   └── buf.gen.yaml
└── google/
    └── api/
        └── annotations.proto
```

**Event Schema:**
```protobuf
message OrderCreatedEvent {
  string order_id = 1;
  string customer_id = 2;
  repeated OrderLineItem items = 3;
  Address shipping_address = 4;
  Money total_amount = 5;
  google.protobuf.Timestamp created_at = 6;
}
```

**Rationale:**
- buf.yaml provides linting, breaking change detection, version management
- Separate packages enable independent service evolution
- Generated Go code integrates with Temporal's protobuf activity inputs

**Alternatives:**
- JSON events: Less type safety, harder to evolve
- Single proto file: Namespace collisions as services grow

### 5. Repository Port Design

**Decision:** Use a narrow Order-specific repository plus a unit-of-work boundary. The repository returns domain objects and exposes optimistic concurrency; it does not expose generic CRUD or infrastructure transaction types.

```go
type OrderRepository interface {
    Save(ctx context.Context, order *Order) error
    FindByID(ctx context.Context, id OrderID) (*Order, error)
    FindByCustomerID(ctx context.Context, customerID CustomerID) ([]*Order, error)
}
```

**Rationale:**
- Ports define boundaries between domain and infrastructure
- Enables testing with in-memory adapter
- Domain never depends on infrastructure

**Alternatives:**
- ORM (GORM): Too opinionated, leaks persistence into domain
- Generic CRUD repository: Doesn't capture domain semantics

### 6. Validated Code Snippets

#### pgx/v5 Connection Pool (v5.10.0; requires Go 1.25+, project pins Go 1.26.5)

```go
import (
    "context"
    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/jackc/pgx/v5"
)

// NewPool creates a connection pool with validated settings
func NewPool(ctx context.Context, connString string) (*pgxpool.Pool, error) {
    config, err := pgxpool.ParseConfig(connString)
    if err != nil {
        return nil, fmt.Errorf("parse config: %w", err)
    }

    // Connection pool settings
    config.MaxConns = 20
    config.MinConns = 5
    config.MaxConnLifetime = time.Hour
    config.MaxConnIdleTime = 30 * time.Minute
    config.HealthCheckPeriod = time.Minute

    // Statement caching (enabled by default in pgx/v5)
    config.ConnConfig.DefaultQueryExecMode = pgx.QueryExecModeCacheStatement

    pool, err := pgxpool.NewWithConfig(ctx, config)
    if err != nil {
        return nil, fmt.Errorf("create pool: %w", err)
    }

    // Verify connectivity
    if err := pool.Ping(ctx); err != nil {
        pool.Close()
        return nil, fmt.Errorf("ping: %w", err)
    }

    return pool, nil
}
```

#### chi/v5 HTTP Router (v5.3.1)

```go
func NewRouter(handler *OrderHandler) http.Handler {
    r := chi.NewRouter()
    r.Use(middleware.RequestID)
    r.Use(middleware.Recoverer)
    r.Use(middleware.Timeout(30 * time.Second))

    // Local development has no trusted reverse proxy. Production selects exactly
    // one ClientIP middleware based on its ingress trust boundary.
    r.Use(middleware.ClientIPFromRemoteAddr)

    r.Route("/api/v1/orders", func(r chi.Router) {
        r.With(IdempotencyKey).Post("/", handler.Create)
        r.Get("/{orderID}", handler.Get)
        r.Get("/", handler.List)
        r.Post("/{orderID}/cancel", handler.Cancel)
    })
    return r
}
```

Structured request logging is implemented as an application-owned middleware using Zap; chi does not provide a `httplog` package. Do not use deprecated `middleware.RealIP`, and never trust forwarded headers without an explicit ingress trust policy.

#### Optional Redis Adapter

Redis is not part of the MVP dependency graph. If a later capability demonstrates a need for distributed caching, rate limiting, or ephemeral coordination, add `github.com/redis/go-redis/v9 v9.21.0` behind a capability-specific port. PostgreSQL remains the authority for orders, idempotency keys, and consumer receipts.

#### Temporal Go SDK v1.46.0

```go
func OrderFulfillmentWorkflow(ctx workflow.Context, in FulfillmentInput) error {
    ctx = workflow.WithActivityOptions(ctx, workflow.ActivityOptions{
        StartToCloseTimeout: 5 * time.Minute,
        RetryPolicy: &temporal.RetryPolicy{
            InitialInterval:    time.Second,
            BackoffCoefficient: 2,
            MaximumInterval:    30 * time.Second,
            MaximumAttempts:    5,
        },
    })

    if err := workflow.ExecuteActivity(ctx, ReserveInventory, in).Get(ctx, nil); err != nil {
        return err
    }
    if err := workflow.ExecuteActivity(ctx, CapturePayment, in).Get(ctx, nil); err != nil {
        _ = workflow.ExecuteActivity(ctx, ReleaseInventory, in).Get(ctx, nil)
        return err
    }
    return workflow.ExecuteActivity(ctx, MarkOrderProcessing, in.OrderID).Get(ctx, nil)
}
```

Workflow code uses only deterministic SDK APIs. Future Payment and Inventory services receive their own task queues or Nexus endpoints; the Order workflow depends on versioned inputs/results, not their implementation packages. Worker deployment versioning protects in-flight executions, and incompatible workflow changes use SDK-supported versioning or a new workflow type.

#### Zap v1.28.0

```go
func NewLogger(serviceName, environment string) (*zap.Logger, error) {
    cfg := zap.NewProductionConfig()
    cfg.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
    return cfg.Build(zap.Fields(
        zap.String("service.name", serviceName),
        zap.String("deployment.environment", environment),
    ))
}
```

Request middleware adds request ID, trace ID, and authenticated subject as fields. Release-specific pre-write hooks are unnecessary for the MVP.

#### Fx v1.24.0 Lifecycle

```go
func RegisterHTTPServer(lc fx.Lifecycle, server *http.Server, log *zap.Logger) {
    lc.Append(fx.Hook{
        OnStart: func(context.Context) error {
            go func() {
                if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
                    log.Error("http server stopped", zap.Error(err))
                }
            }()
            return nil
        },
        OnStop: server.Shutdown,
    })
}
```

Fx composes one process and owns startup/shutdown. `fxevent.BeforeRun` is an emitted diagnostic event in v1.24.0, not a field on `fx.Hook`.

### 7. Project Structure

**Decision:** Clean Architecture with DDD terminology.

```
order-service/
├── cmd/order-service/          # api | orchestrator | worker subcommands
├── contracts/
│   ├── order/v1/
│   └── platform/events/v1/
├── internal/
│   ├── domain/order/           # aggregate, value objects, private facts
│   ├── application/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── orchestration/      # consumes OrderCreated and starts workflow
│   ├── ports/                  # repository, unit of work, clock, IDs, workflow
│   └── adapters/
│       ├── http/
│       ├── postgres/           # aggregate, outbox, idempotency, receipts
│       ├── kafka/              # franz-go consumer only; no outbox producer
│       └── temporal/           # starter, workflows, activities, workers
├── migrations/order/
├── deploy/
│   ├── docker-compose.yaml
│   └── debezium-connector.json
├── go.mod
├── buf.yaml
└── buf.gen.yaml
```

**Rationale:**
- DDD terminology (domain, application, infrastructure) matches the mental model
- Ports separate interfaces from implementations
- cmd/ follows Go best practices

### 8. Evolution to Multiple Services

**Decision:** Build the MVP as an independently deployable Order Service with strong internal module boundaries. Extract a module only when it needs independent ownership, scaling, availability, data retention, security, or release cadence.

```
                         Public API / clients
                                |
                         Order Service API
                                |
             +------------------+------------------+
             |                  |                  |
        Order domain       Order workflow      Order queries
             |                  |                  |
       Order PostgreSQL    Temporal contracts   Order-owned views
             |
       Outbox -> Debezium -> Kafka
             |
     +-------+---------+----------+------------+
     |                 |          |            |
 Inventory         Payment     Shipping    Notification
 (future owner)  (future owner) (future)      (future)
```

Future service boundaries:

| Capability | Owns | Primary integration | Extraction trigger |
|---|---|---|---|
| Order | Order lifecycle, line snapshots, customer reference | REST commands, Order events | MVP owner; never shares writable tables |
| Inventory | Stock, reservations, allocation | Temporal activity/Nexus operation plus Inventory events | Independent stock contention or scaling |
| Payment | Payment intent, capture, refund, provider tokens | Temporal activity/Nexus operation plus Payment events | PCI/security boundary or provider release cadence |
| Shipping | Shipment, carrier label, tracking | Temporal operation plus Shipment events | Multiple carriers or fulfillment teams |
| Notification | Templates and delivery attempts | Kafka consumer | Independent retries/channels; no workflow blocking |
| Customer | Customer profile and addresses | API plus customer events; Order stores snapshots | Independent identity/privacy lifecycle |
| Catalog/Pricing | Product and price authority | API plus catalog events; Order stores purchase snapshot | Independent merchandising/price changes |
| Reporting/Search | Denormalized projections | Kafka consumers | Query volume or retention differs from command model |

Rules that preserve extractability:

1. A service is the sole writer of its database/schema. Other services use APIs, events, or Temporal operations.
2. Public contracts live under `contracts/<domain>/vN`; domain and persistence packages remain private.
3. Events describe completed facts and use an immutable envelope containing `event_id`, `event_type`, `event_version`, `aggregate_id`, `aggregate_version`, `occurred_at`, `producer`, `correlation_id`, `causation_id`, and binary Protobuf payload.
4. Kafka records are keyed by aggregate ID. Ordering is only promised for one aggregate; consumers persist processed event IDs in the same transaction as their state change.
5. Commands use idempotency keys. Aggregate writes use optimistic concurrency through the aggregate version.
6. Temporal workflow code contains orchestration only. Business authority remains in the owning service/activity, and every activity/compensation is idempotent.
7. Each future worker deployment owns a stable task queue such as `payment.v1` or `inventory.v1`. Worker deployment versioning protects in-flight workflow executions.
8. Cross-service libraries may contain generated contracts, telemetry setup, and test utilities only. They MUST NOT contain domain models, repositories, configuration globals, or database clients.
9. New services receive independent credentials, migrations, health endpoints, deployment units, consumer groups, and resource budgets even when local Compose uses one physical PostgreSQL or Kafka broker.

### 9. Contract and Event Evolution

**Decision:** Protobuf is the canonical event payload. The outbox stores serialized Protobuf bytes and metadata columns; Debezium Outbox Event Router transports the bytes using `BinaryDataConverter` with a `JsonConverter` delegate for non-payload Debezium events. JSON remains the REST representation only.

```protobuf
syntax = "proto3";

package platform.events.v1;

import "google/protobuf/timestamp.proto";

message EventEnvelope {
  string event_id = 1;
  string event_type = 2;
  uint32 event_version = 3;
  string aggregate_id = 4;
  uint64 aggregate_version = 5;
  google.protobuf.Timestamp occurred_at = 6;
  string producer = 7;
  string correlation_id = 8;
  string causation_id = 9;
  bytes payload = 10;
}
```

Compatibility policy:

- Existing field numbers are never reused; removed fields are reserved.
- Additive fields are preferred. Semantic breaking changes create a new event type/version and coexist during migration.
- CI runs `buf lint` and `buf breaking` against the main branch.
- Consumers ignore unknown fields and are tested against both current and immediately previous contract fixtures.
- Topic names are stable and domain-owned (`orders.events.v1`); event type is carried in a Kafka header and envelope.
- No consumer reads Debezium table-change envelopes directly. Only routed outbox records are public integration events.
- `BinaryDataConverter` passes outbox payload bytes through unchanged, but Debezium-internal events (heartbeat, transaction metadata, schema change) cannot be serialized by it. The connector MUST declare a JsonConverter delegate (`value.converter.delegate.converter.type=org.apache.kafka.connect.json.JsonConverter`, `value.converter.delegate.converter.type.schemas.enable=false`) so non-payload events are emitted as plain JSON instead of failing the connector or silently stopping emission.

### 10. Reliability and Operations Baseline

- Delivery is **at least once**, not exactly once end-to-end.
- The API commits aggregate state and outbox records without synchronously calling Kafka or Temporal.
- An Order-owned `order-orchestration.v1` consumer claims a `pending` event receipt, starts workflow `order/<order-id>` with ID reuse rejected, marks the receipt `started`, then commits the Kafka offset. Redelivery reconciles every intermediate state.
- The outbox insert and aggregate mutation commit in one PostgreSQL transaction.
- Consumer inbox/receipt records and consumer state changes commit in one local transaction.
- Retryable failures use bounded exponential backoff; poison events are quarantined with original bytes and diagnostics for replay.
- Liveness checks process health only. Readiness checks required dependencies with short timeouts and becomes false before shutdown.
- Logs, traces, metrics, events, and workflow search attributes carry correlation identifiers without putting secrets or payment data into baggage.
- Outbox lag, replication-slot retained WAL, Kafka consumer lag, Temporal task latency, workflow failures, and compensation failures are monitored.
- Backups and restore tests cover each authoritative database; Kafka and Temporal are not substitutes for Order database backups.

### 11. Verification Architecture and Release Gates

**Decision:** Requirements are accepted through executable evidence, not task completion alone. `verification/traceability.yaml` is the machine-readable index from every normative scenario to one or more stable verification IDs. CI validates that every in-scope scenario is mapped, every referenced test exists, and no required result is skipped.

#### Verification layout

- Package-local `*_test.go`: domain, application, adapter, configuration, and workflow unit tests.
- `test/integration/`: PostgreSQL, migration, repository, Kafka consumer, and Temporal adapter tests. Testcontainers creates isolated dependencies with health/log wait strategies, a user-defined network, and per-test cleanup.
- `test/compatibility/`: current/previous Protobuf fixtures, previous database schema fixture, connector configuration validation, and Temporal histories under `testdata/temporal-histories/`.
- `test/e2e/`: black-box Compose tests for API → PostgreSQL/outbox → Debezium → Kafka → orchestrator → Temporal worker → final Order state.
- `test/faults/`: deterministic failpoints at named durability boundaries. Failpoints are compiled or enabled only for tests and MUST NOT be accepted from production requests.
- `test/performance/`: k6 scenarios and a probe that measures committed-order-to-workflow-start latency by correlation ID.
- `verification/`: traceability manifest, coverage policy, vulnerability exceptions, reference-environment declaration, and evidence schema.
- `artifacts/verification/<commit-sha>/`: generated CI evidence; artifacts are not committed except compatibility fixtures.

#### Canonical commands

The repository Makefile SHALL expose these stable entry points so local and CI execution remain identical:

```bash
make generate-check       # regenerate contracts and fail on a dirty diff
make verify-static        # format, vet, architecture, config, and traceability checks
make test-unit            # uncached unit tests, shuffle seed, Go JSON, and coverage
make test-race            # race-enabled concurrent package suites
make test-integration     # isolated PostgreSQL/Kafka/Temporal adapter tests
make test-compatibility   # Buf, migrations, connector config, and workflow replay
make test-e2e             # clean and retained-volume Compose smoke/recovery paths
make test-security        # govulncheck, Trivy, secret scan, image scan, and SBOM
make test-performance     # k6 smoke/reference thresholds on declared environment
make verify-pr            # generate-check + static + unit + race + required integration
make verify-release       # all gates; emits the release evidence index
```

Release-significant Go runs use `-count=1`, a recorded `-shuffle` seed, `-json`, bounded `-timeout`, and `-covermode=atomic`. Race runs use `go test -race` on packages with goroutines, shared state, command concurrency, consumer processing, and lifecycle code. Fuzz targets cover JSON request decoding, ULID/cursor parsing, Protobuf envelope decoding, money and address validation, and idempotency fingerprint canonicalization; seed corpora include all compatibility fixtures.

Coverage is diagnostic and a backstop, not proof of behavior. Domain and application packages SHALL each maintain at least 90% statement coverage, the repository-wide Go package aggregate SHALL maintain at least 80%, and no critical invariant or fault checkpoint may rely on coverage alone. Generated code, migrations, command entrypoints, and test utilities are excluded from threshold calculation by an explicit version-controlled policy.

#### Fault and recovery matrix

The deterministic failure suite SHALL stop or terminate the relevant process at these checkpoints:

1. Before and after aggregate/outbox transaction commit.
2. After commit but before Debezium publication.
3. After Kafka delivery but before receipt claim.
4. After receipt claim but before Temporal start.
5. After Temporal start but before receipt transition to `started`.
6. After receipt transition but before Kafka offset commit.
7. During retryable and terminal workflow activities and each compensation.
8. During graceful shutdown with active HTTP requests, Kafka records, and Temporal activities.

For every checkpoint, the assertion is eventual convergence after restart: committed domain state remains authoritative, no committed public event is lost, duplicate delivery causes no repeated committed business effect, aggregate order is detectable, and terminal data is diagnosable or quarantined.

#### Gate cadence

- **Developer/commit:** generation, formatting, focused unit tests, and architecture checks.
- **Pull request:** `verify-pr`, Buf breaking comparison against main, migration from empty and previous schema, required workflow histories, `govulncheck`, repository/configuration/secret scan, and an image build.
- **Nightly:** full integration matrix, repeated race run, bounded fuzzing, all fault checkpoints, clean/retained Compose cycles, arm64/amd64 image checks, backup/restore, and dependency scan refresh.
- **Release candidate:** immutable image by digest, full compatibility and replay corpus, SBOM, image vulnerability scan, complete recovery suite, k6 reference gate, rollback rehearsal, and signed evidence index.

A flaky required test remains a failure. Quarantine requires an issue, owner, expiry no later than 14 days, and a replacement verification path; quarantined tests do not satisfy normative traceability. Vulnerability exceptions use the same owner/expiry model and additionally require severity, reachability, rationale, and compensating control.

#### Reference performance gate

The MVP gate runs against an otherwise idle, declared reference environment after a warm-up period. k6 sustains 25 successful `POST /api/v1/orders` operations per second for five minutes with HTTP error rate below 1%, HTTP p95 below 500 ms, and p99 below 1 second. A correlation-aware observer requires committed-order-to-workflow-start p95 below 10 seconds and zero lost events. The evidence records CPU/memory limits, host architecture, image digests, partition count, database settings, and dataset size. These numbers are regression gates for the reference environment, not production SLOs; production SLOs require capacity tests on the production-like topology.

#### Evidence and phase acceptance

Each gate writes a manifest containing commit SHA, dirty state, command, verification IDs, tool versions, image digests, architecture, seed, timestamps, result, and artifact checksums. Evidence includes Go JSON/JUnit, coverage summaries, Buf output, migration and replay reports, scanner results and SBOM, Compose state and failure logs, fault checkpoint outcomes, and k6 summaries. Pull-request evidence is retained for at least 30 days and release evidence for at least one year.

Phase 1 is complete only when all in-scope tasks are checked, the traceability validator reports zero unmapped normative scenarios, all PR/compatibility/smoke/security/recovery/performance gates pass, rollback is rehearsed, documentation and runbooks match the executable commands, and every exception is reviewed and unexpired. Phase 2 services inherit the manifest schema and canonical targets while owning their own fixtures, credentials, migrations, consumer groups, task queues, and release evidence.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Debezium/outbox schema evolution complexity | CDC stops on an incompatible table or connector change | Use expand/contract migrations, version-controlled connector configuration, and staged compatibility tests |
| BinaryDataConverter without delegate | Heartbeat, transaction-metadata, or schema-change events are not serializable by `BinaryDataConverter` and can fail the connector or stall emission | Configure `value.converter.delegate.converter.type=org.apache.kafka.connect.json.JsonConverter` and `value.converter.delegate.converter.type.schemas.enable=false`; add a `verify-static` jq assertion that both keys are present in `deploy/debezium-connector.json` |
| BinaryDataConverter risk closed by task 7.2.4 | Heartbeat, transaction-metadata, or schema-change events are not serializable by `BinaryDataConverter` and can fail the connector or stall emission | `deploy/debezium-connector.json` now declares `value.converter.delegate.converter.type=org.apache.kafka.connect.json.JsonConverter` with `value.converter.delegate.converter.type.schemas.enable=false`; `make verify-static` enforces both keys via `jq`. Closed by task 7.2.4 (evidence: connector JSON committed; smoke stack ran end-to-end) |
| Temporal workflow version upgrades | Workflows in-flight during deploy | Use worker deployment versioning and SDK-supported workflow versioning |
| Protobuf breaking changes | Service incompatibility | buf breaking change detection in CI |
| Single-service bottleneck | Can't scale individual operations | Design for extraction to Phase 2 services |
| PostgreSQL WAL retention | Debezium lag if consumer slow | Monitor lag; configure sufficient retention |
| Saga compensation race conditions | Partial compensation possible | Idempotent compensation; compensating events |
| Go module circular dependencies | Build failures | Architecture linter in CI |

## Docker Compose Stack (Reference topology)

### Compatibility notes
Debezium Connect **3.6.0.Final** was built and tested by upstream against Kafka Connect/brokers **4.3.0**. The stack pins brokers at **4.3.1**, a forward patch release; compatibility is preserved but is one minor ahead of the Debezium-tested baseline. Any upgrade to **4.4.x** or later MUST be re-validated against the then-current Debezium release notes before pinning.

### Apple Silicon Compatibility

Manifest inspection on macOS Apple Silicon confirmed native `linux/arm64` support for every required pinned image:

| Component | Image | linux/arm64 |
|---|---|---|
| PostgreSQL | `postgres:18.4-bookworm` | Native |
| Kafka | `apache/kafka:4.3.1` | Native |
| Debezium Connect | `quay.io/debezium/connect:3.6.0.Final` | Native |
| Temporal CLI dev server | `temporalio/temporal:1.6.1` | Native |
| k6 verification runner | `grafana/k6:1.8.0` | Native |
| Trivy verification runner | `aquasec/trivy:0.72.0` | Native |

Compose MUST use the multi-architecture tags without a `platform: linux/amd64` override. The Order Service Dockerfile MUST use multi-architecture Go builder/runtime images and MUST not hard-code `GOARCH=amd64`; BuildKit selects the target architecture. Any future optional tool image requires an immutable tag and a manifest check before it enters the stack.

### Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  DOCKER COMPOSE STACK (Reference topology Jul 2026)       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐            │
│  │ PostgreSQL  │    │    Kafka     │    │  Debezium    │            │
│  │   18.4      │    │   4.3.1      │    │   3.6.0      │            │
│  │  (wal=     │    │   KRaft      │    │   Connect    │            │
│  │  logical)  │    │   mode       │    │              │            │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘            │
│         │                   │                   │                      │
│         │  WAL Log          │   Kafka Topics   │  REST API            │
│         └───────────────────┴───────────────────┘                      │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │             Temporal CLI development server 1.6.1                  │  │
│  │          gRPC 7233 · UI 8233 (host 8088) · metrics 9090              │  │
│  │          Local SQLite persistence; never production topology       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │       One Order image, three long-running runtime roles             │  │
│  │  order-api :8080  ·  order-orchestrator  ·  order-worker             │  │
│  │  Independent health, shutdown, restart, and horizontal scaling      │  │
│  │                                                                       │  │
│  │  Plus two one-shot roles that gate the long-running ones:            │  │
│  │  order-migrate           `migrate up` on the database                │  │
│  │  order-topics-init       Idempotent Kafka topic provisioning         │  │
│  │  order-infrastructure-init Registers/updates the Debezium           │  │
│  │                          connector via the Connect REST API         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Docker Compose Specification (deploy/docker-compose.yaml)

```yaml
# Order Service MVP - Docker Compose Stack (Reference topology Jul 2026)
# Local versions: PostgreSQL 18.4, Kafka 4.3.1, Debezium 3.6.0,
# Temporal CLI dev server 1.6.1. Production target: Server 1.31.2 or Cloud.

services:
  # ─────────────────────────────────────────────────────────────────────
  # PostgreSQL 18.4 - With Logical Replication for Debezium CDC
  # ─────────────────────────────────────────────────────────────────────
  postgres:
    image: postgres:18.4-bookworm
    container_name: order-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: orders
      POSTGRES_PASSWORD: orders_secret
      POSTGRES_DB: orders
      POSTGRES_INITDB_ARGS: "--data-checksums --auth-host=scram-sha-256"
    command: >
      postgres
      -c wal_level=logical
      -c max_wal_senders=10
      -c max_replication_slots=10
      -c shared_buffers=256MB
      -c max_connections=100
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/18/docker
      - ./init-scripts:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U orders -d orders"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - order-network

  # ─────────────────────────────────────────────────────────────────────
  # Apache Kafka 4.3.1 - KRaft Mode (No Zookeeper)
  # ─────────────────────────────────────────────────────────────────────
  kafka:
    image: apache/kafka:4.3.1
    container_name: order-kafka
    restart: unless-stopped
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: INTERNAL://:29092,EXTERNAL://:9092,CONTROLLER://:9093
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka:29092,EXTERNAL://localhost:9092
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_NUM_PARTITIONS: 3
      CLUSTER_ID: 'MkU3OEVBNTcwNTJENDM2Qk'
    ports:
      - "9092:9092"
    volumes:
      - kafka_data:/var/lib/kafka/data
    healthcheck:
      test: ["CMD-SHELL", "/opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:29092"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - order-network

  # ─────────────────────────────────────────────────────────────────────
  # Debezium Connect 3.6.0 - PostgreSQL CDC
  # ─────────────────────────────────────────────────────────────────────
  debezium:
    image: quay.io/debezium/connect:3.6.0.Final
    container_name: order-debezium
    restart: unless-stopped
    environment:
      GROUP_ID: 1
      CONFIG_STORAGE_TOPIC: debezium_configs
      OFFSET_STORAGE_TOPIC: debezium_offsets
      STATUS_STORAGE_TOPIC: debezium_status
      CONFIG_STORAGE_REPLICATION_FACTOR: 1
      OFFSET_STORAGE_REPLICATION_FACTOR: 1
      STATUS_STORAGE_REPLICATION_FACTOR: 1
      KEY_CONVERTER: org.apache.kafka.connect.storage.StringConverter
      VALUE_CONVERTER: io.debezium.converters.BinaryDataConverter
      BOOTSTRAP_SERVERS: kafka:29092
      ADVERTISED_HOST_NAME: debezium
      HEAP_OPTS: -Xms512M -Xmx2G
    ports:
      - "8083:8083"  # Kafka Connect REST API
    depends_on:
      kafka:
        condition: service_healthy
      postgres:
        condition: service_healthy
    networks:
      - order-network

  # ─────────────────────────────────────────────────────────────────────
  # Temporal development server - local-only SQLite persistence + UI
  # Production targets Temporal Server 1.31.2 or Temporal Cloud and manages
  # SQL schemas outside the application Compose stack.
  # ─────────────────────────────────────────────────────────────────────
  temporal:
    image: temporalio/temporal:1.6.1
    container_name: order-temporal
    restart: unless-stopped
    command:
      - server
      - start-dev
      - --ip=0.0.0.0
      - --port=7233
      - --ui-port=8233
      - --db-filename=/var/lib/temporal/temporal.db
      - --namespace=order-dev
      - --metrics-port=9090
    ports:
      - "7233:7233"
      - "8088:8233"
      - "9090:9090"
    volumes:
      - temporal_data:/var/lib/temporal
    healthcheck:
      test: ["CMD", "temporal", "workflow", "list", "--address", "localhost:7233", "--namespace", "order-dev", "--limit", "1"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 10s
    networks:
      - order-network

  # ─────────────────────────────────────────────────────────────────────
  # Optional broker UI belongs in a Compose `tools` profile and MUST use a
  # separately validated immutable image tag; it is not a runtime dependency.

  # ─────────────────────────────────────────────────────────────────────
  # One application image, independently runnable roles
  # ─────────────────────────────────────────────────────────────────────
  order-migrate:
    image: order-service:local
    build:
      context: ../..
      dockerfile: order-service/Dockerfile
    command: ["migrate", "up"]
    restart: "no"
    environment:
      DB_DSN: postgres://orders:orders_secret@postgres:5432/orders?sslmode=disable
    depends_on:
      postgres:
        condition: service_healthy
    networks: [order-network]

  order-infrastructure-init:
    image: order-service:local
    command: ["infrastructure", "init"]
    restart: "no"
    environment:
      DB_DSN: postgres://orders:orders_secret@postgres:5432/orders?sslmode=disable
      KAFKA_BROKERS: kafka:29092
      DEBEZIUM_CONNECT_URL: http://debezium:8083
      DEBEZIUM_CONNECTOR_CONFIG: /config/debezium-connector.json
    volumes:
      - ./debezium-connector.json:/config/debezium-connector.json:ro
    depends_on:
      order-migrate:
        condition: service_completed_successfully
      kafka:
        condition: service_healthy
      debezium:
        condition: service_started
    networks: [order-network]

  order-api:
    image: order-service:local
    command: ["api"]
    restart: unless-stopped
    environment:
      APP_ENV: development
      APP_PORT: 8080
      DB_DSN: postgres://orders:orders_secret@postgres:5432/orders?sslmode=disable
    ports:
      - "8080:8080"
    depends_on:
      order-migrate:
        condition: service_completed_successfully
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "/order-service", "healthcheck", "--url=http://localhost:8080/health/ready"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 20s
    networks: [order-network]

  order-orchestrator:
    image: order-service:local
    command: ["orchestrator"]
    restart: unless-stopped
    environment:
      APP_ENV: development
      DB_DSN: postgres://orders:orders_secret@postgres:5432/orders?sslmode=disable
      KAFKA_BROKERS: kafka:29092
      KAFKA_CONSUMER_GROUP: order-orchestration.v1
      TEMPORAL_HOST: temporal:7233
      TEMPORAL_NAMESPACE: order-dev
    depends_on:
      order-infrastructure-init:
        condition: service_completed_successfully
      temporal:
        condition: service_healthy
    networks: [order-network]

  order-worker:
    image: order-service:local
    command: ["worker"]
    restart: unless-stopped
    environment:
      APP_ENV: development
      DB_DSN: postgres://orders:orders_secret@postgres:5432/orders?sslmode=disable
      TEMPORAL_HOST: temporal:7233
      TEMPORAL_NAMESPACE: order-dev
      TEMPORAL_TASK_QUEUE: order-fulfillment.v1
    depends_on:
      order-migrate:
        condition: service_completed_successfully
      postgres:
        condition: service_healthy
      temporal:
        condition: service_healthy
    networks: [order-network]

# ─────────────────────────────────────────────────────────────────────────
# Networks
# ─────────────────────────────────────────────────────────────────────────
networks:
  order-network:
    driver: bridge
    name: order-network

# ─────────────────────────────────────────────────────────────────────────
# Volumes
# ─────────────────────────────────────────────────────────────────────────
volumes:
  postgres_data:
    name: order-postgres-data
  kafka_data:
    name: order-kafka-data
  temporal_data:
    name: order-temporal-data
```

### Order Database Migration and CDC Grants

The application migration tool owns Order tables. A separate privileged bootstrap step creates the replication role, and a post-migration step creates the publication after `outbox` exists. The local Temporal dev server uses SQLite and requires no PostgreSQL database.

```sql
-- Privileged local bootstrap; production credentials come from secret management.
CREATE USER orders_replication WITH REPLICATION ENCRYPTED PASSWORD 'orders_replication_secret';

-- Application migration begins here.

-- Create a least-privilege replication user for the outbox publication.
-- Grant privileges to existing orders user
GRANT ALL PRIVILEGES ON DATABASE orders TO orders;
GRANT ALL PRIVILEGES ON SCHEMA public TO orders;

-- Create outbox table for Debezium CDC
CREATE TABLE IF NOT EXISTS outbox (
    id CHAR(26) PRIMARY KEY,
    aggregate_type TEXT NOT NULL,
    aggregate_id CHAR(26) NOT NULL,
    aggregate_version BIGINT NOT NULL,
    event_type TEXT NOT NULL,
    event_version INTEGER NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    correlation_id CHAR(26),
    causation_id CHAR(26),
    payload BYTEA NOT NULL
);

CREATE INDEX idx_outbox_aggregate ON outbox(aggregate_id, aggregate_version);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id CHAR(26) PRIMARY KEY,
    customer_id CHAR(26) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_amount_minor BIGINT NOT NULL CHECK (total_amount_minor >= 0),
    currency CHAR(3) NOT NULL,
    shipping_address JSONB NOT NULL,
    billing_address JSONB,
    payment_reference TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1
);

-- Create order line items table
CREATE TABLE IF NOT EXISTS order_line_items (
    id CHAR(26) PRIMARY KEY,
    order_id CHAR(26) NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id CHAR(26) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_minor BIGINT NOT NULL CHECK (unit_price_minor >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at);
CREATE INDEX idx_line_items_order ON order_line_items(order_id);

-- Grant table permissions to orders user
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO orders;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO orders;

-- Debezium reads only the integration outbox.
GRANT USAGE ON SCHEMA public TO orders_replication;
GRANT SELECT ON TABLE public.outbox TO orders_replication;
CREATE PUBLICATION order_outbox_publication FOR TABLE public.outbox;
```

### Debezium Connector Configuration (deploy/debezium-connector.json)

The connector routes `public.outbox` to `orders.events.v1` with the aggregate ID as the Kafka key. The `BinaryDataConverter` propagates the Protobuf payload bytes untouched. A `JsonConverter` delegate is required because Debezium-internal events (heartbeat, transaction metadata, schema change) cannot be serialized by `BinaryDataConverter` and would otherwise cause connector failure or stall emission.

```json
{
  "name": "order-source-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "orders_replication",
    "database.password": "orders_replication_secret",
    "database.dbname": "orders",
    "topic.prefix": "order-cdc",
    "table.include.list": "public.outbox",
    "publication.name": "order_outbox_publication",
    "publication.autocreate.mode": "disabled",
    "slot.name": "order_outbox_slot",
    "plugin.name": "pgoutput",
    "snapshot.mode": "no_data",
    "tombstones.on.delete": "false",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "io.debezium.converters.BinaryDataConverter",
    "value.converter.delegate.converter.type": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.delegate.converter.type.schemas.enable": "false",
    "transforms": "outbox",
    "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
    "transforms.outbox.table.field.event.id": "id",
    "transforms.outbox.table.field.event.key": "aggregate_id",
    "transforms.outbox.table.field.event.type": "event_type",
    "transforms.outbox.table.field.event.payload": "payload",
    "transforms.outbox.route.topic.replacement": "orders.events.v1"
  }
}
```

## Migration Plan

### Phase 1 MVP (This Change)
1. Implement Order Service with all components
2. Run full Docker Compose stack locally
3. End-to-end test order creation → workflow → completion
4. Verify Debezium CDC captures all events

### Phase 2: Multi-Service (Future)
1. Add Payment Service
2. Add Inventory Service
3. Extract workflow orchestration to separate Workflow Service
4. Add Kubernetes manifests
5. Add OpenTelemetry

**Rollback:** Application rollback requires a previously compatible image, backward-compatible database migrations, compatible event contracts, and Temporal worker routing for in-flight executions. Docker Compose restart alone is not a rollback strategy.

## Resolved Decisions

1. **Identifiers**: Use canonical 26-character ULIDs for Order, line item, event, correlation, and causation identifiers across every boundary.
2. **Aggregate consistency**: Use `READ COMMITTED` transactions plus optimistic concurrency on the aggregate version. Retry a bounded number of serialization or version conflicts at the command boundary.
3. **Event evolution**: Every public event carries immutable `event_type` and `event_version` fields in the Protobuf envelope. Breaking semantic changes create a new event version and coexist during migration.
4. **Workflow state**: Temporal is authoritative for orchestration state. PostgreSQL stores only Order domain state and durable idempotency/correlation records updated by activities.
5. **Poison events**: The MVP quarantines terminal consumer failures with original bytes and diagnostics. Automated replay tooling may follow in Phase 2.
6. **Health endpoints**: Expose `/health/live`, `/health/ready`, and `/health/startup`; only readiness evaluates required dependencies.
