## ADDED Requirements

### Requirement: Capability-gated admission of an external cache
The platform SHALL expose a `platform/cache` module whose API is reachable from any service, but the platform SHALL NOT include a Redis or Valkey client dependency in the platform module itself. The `go.sum` for the platform module SHALL list zero cache-related packages. A service SHALL admit a cache client (`github.com/redis/go-redis/v9` or `github.com/valkey-io/valkey-glide/go`) into its own module only after (1) authoring an ADR that satisfies the five-point test in `order-service/docs/adr/0004-optional-infrastructure.md` (document the problem, demonstrate PG/Kafka/Debezium/Temporal cannot solve it, define ownership, define the integration boundary, define the failure mode); (2) registering the cache as a deployment dependency in that service's `deploy/docker-compose.yaml`; and (3) declaring the cache keyspace and TTL policy in `verification/tools.env`.

#### Scenario: Platform module imports no cache client
- **WHEN** `go list -m all` runs against the platform module
- **THEN** the output contains no cache-related modules (no `redis`, `valkey`, `bigcache`, `ristretto`, `freecache`)

#### Scenario: Service without an ADR may not import a cache client
- **WHEN** the architecture tests run against a service that imports `github.com/redis/go-redis/v9`
- **THEN** the test fails unless `docs/adr/<NNNN>-<capability>-cache.md` exists with the required five sections

#### Scenario: Cache ADR documents the five required points
- **WHEN** a service authors a cache ADR
- **THEN** the ADR's "Decision" section names the problem in one sentence, names the PG/Kafka/Debezium/Temporal alternative that was considered and why it was rejected, names the cache owner (which service owns the keyspace), names the integration boundary (which code path uses the cache), and names the failure mode (cache outage vs cache corruption vs cache divergence)

### Requirement: Cache interface abstraction
The platform SHALL define a `Cache` interface with methods `Get(ctx, key) ([]byte, bool, error)`, `Set(ctx, key, value, ttl) error`, `SetNX(ctx, key, value, ttl) (bool, error)`, `Del(ctx, keys...) error`, and `Incr(ctx, key) (int64, error)`. The interface SHALL NOT leak any vendor type. Adapters implementing `Cache` SHALL live under `<service>/internal/adapters/cache/<vendor>/` and SHALL be selected at startup via Fx based on configuration. A service that imports a cache client but does not implement the `Cache` interface SHALL fail the architecture test.

#### Scenario: Cache interface omits vendor types
- **WHEN** a service imports the `platform/cache` package
- **THEN** no vendor type appears in any service signature that crosses a package boundary

#### Scenario: Missing adapter fails the architecture test
- **WHEN** a service imports `github.com/redis/go-redis/v9` but does not provide a `Cache` adapter
- **THEN** `test/architecture/cache_test.go::TestCacheAdapterImplementsCacheInterface` fails

### Requirement: Cache keyspace declaration
Every service that uses a cache SHALL declare its keyspace in a single file `internal/adapters/cache/keys.go` exposing typed key constructors. The keyspace SHALL use the prefix `<service>:<purpose>:<scope>:<id>` where `<service>` is the service name, `<purpose>` is the cache use (e.g., `quote`, `idempotency`, `ratelimit`), `<scope>` is the tenant or aggregate, and `<id>` is the ULID or hash. The keyspace SHALL be reviewed in the architecture test that scans every `cache.Set` and `cache.SetNX` call site.

#### Scenario: All cache keys include the service prefix
- **WHEN** the architecture test scans every cache-write call site
- **THEN** each key matches the regex `^[a-z][a-z0-9-]+:[a-z][a-z0-9-]+:[a-z][a-z0-9-]+:[a-zA-Z0-9_-]+$` (the canonical 4-segment shape `<service>:<purpose>:<scope>:<id>` where `<id>` is a ULID or hash with no further colon segments). Hash-tagged keys (used for atomic multi-key operations on Redis Cluster) MAY contain a single `{<tag>}` substring inside the scope segment; see the Multi-key operations and hash tags requirement.

#### Scenario: Key collisions between services are detected
- **WHEN** two services declare the same `<purpose>` for different domains
- **THEN** the cross-service architecture test fails the build

### Requirement: TTL policy enforcement
Every cache write SHALL specify a TTL via the platform's `TTL` type. The platform SHALL define five canonical TTL bands with constants `TTLShort (5s)`, `TTLMedium (60s)`, `TTLLong (10m)`, `TTLDay (24h)`, `TTLWeek (7d)`. Services SHALL NOT specify an arbitrary numeric TTL; the architecture test rejects `Set(..., time.Duration(<arbitrary>), ...)`. Cache writes without a TTL SHALL fail the architecture test.

#### Scenario: Cache write without TTL is rejected
- **WHEN** the architecture test scans every cache-write call site
- **THEN** every call uses one of the five canonical TTL constants

#### Scenario: Arbitrary numeric TTL is rejected
- **WHEN** a service writes a cache entry with `cache.Set(ctx, key, val, 3 * time.Second)`
- **THEN** the architecture test fails because `3 * time.Second` is not a canonical TTL constant

### Requirement: Idempotency-via-cache contract
A service that uses the cache for request idempotency SHALL implement the two-phase state pattern: `SetNX(key, "PENDING", TTLShort)` on entry; transition to `"COMPLETED"` atomically via a Lua script (or the platform's `SetNXWithValue`) when the work completes; on terminal failure call `Del(key)` and on retryable failure leave the key to expire. The cache SHALL NOT be the source of truth for idempotency — every cache-backed idempotency key SHALL also be persisted to a PostgreSQL table keyed on the same `(idempotency_key, fingerprint)` so the system survives a cache outage.

#### Scenario: Two-phase state prevents lost duplicate
- **WHEN** two concurrent requests with the same `Idempotency-Key` arrive
- **THEN** exactly one request reaches the application layer; the second request observes `PENDING` and waits

#### Scenario: Cache outage does not lose idempotency state
- **WHEN** the cache is unavailable
- **THEN** the system falls back to the PostgreSQL `idempotency_keys` table and the request still succeeds with the documented cache miss behavior

#### Scenario: Terminal error clears the key
- **WHEN** the application returns a 4xx error
- **THEN** the cache key is deleted so the client can retry with a fresh state

### Requirement: Cache observability
The cache adapter SHALL emit metrics `cache_operations_total{operation, status}`, `cache_operation_duration_seconds{operation}`, `cache_hit_total{cache_purpose}`, `cache_miss_total{cache_purpose}`, `cache_eviction_total{cache_purpose}`, and `cache_outage_duration_seconds` (gauge during an outage). The adapter SHALL emit a structured log on every outage, including the cache purpose, the affected keyspace prefix, the outage start time, and the recovery time. The adapter SHALL NOT log cache keys or cache values.

#### Scenario: Cache hit increments the hit counter
- **WHEN** the adapter returns a value present in the cache
- **THEN** `cache_hit_total{cache_purpose=<purpose>}` is incremented by 1

#### Scenario: Cache outage is logged
- **WHEN** the cache is unreachable for more than 1 second
- **THEN** the structured log records `cache_outage=true cache_purpose=<purpose> affected_prefix=<prefix> started_at=<ts>` without leaking the key or value

### Requirement: Local dev cache image
The platform's local compose overlay SHALL include a `redis` service pinned to `redis:8.8-alpine` (or `valkey/valkey:9.1-alpine`) when a service's architecture tests declare a cache dependency. The cache image SHALL expose a `/metrics` endpoint via `oliver006/redis_exporter` and SHALL be configured with `appendonly yes`, `appendfsync everysec`, and `maxmemory-policy noeviction` (idempotency keys MUST NOT be evicted under memory pressure).

#### Scenario: Local compose brings up the cache image
- **WHEN** a service declares a cache dependency
- **THEN** `docker compose up` brings up the cache container and the cache adapter's `Ping(ctx)` returns no error

#### Scenario: Idempotency keys survive memory pressure
- **WHEN** the cache reaches `maxmemory` and a write would evict an idempotency key
- **THEN** the `noeviction` policy causes the write to fail and the application falls back to the PostgreSQL idempotency table

### Requirement: Cache failure semantics
The cache adapter SHALL distinguish four failure modes: `ErrCacheMiss` (key not present), `ErrCacheOutage` (cannot reach cache), `ErrCacheCorruption` (cached bytes cannot be decoded), `ErrCacheConfiguration` (cache is disabled by configuration). The application SHALL treat `ErrCacheOutage` as a soft failure (fall back to the source of truth and increment the outage metric). The application SHALL treat `ErrCacheCorruption` as a hard failure (log the corrupted key prefix, increment the corruption counter, do not serve the corrupted value).

#### Scenario: Cache outage falls back to the source of truth
- **WHEN** `cache.Get` returns `ErrCacheOutage`
- **THEN** the application queries the source of truth (PostgreSQL) and returns the value; `cache_outage_duration_seconds` increases

#### Scenario: Cache corruption does not serve the corrupted value
- **WHEN** `cache.Get` returns `ErrCacheCorruption`
- **THEN** the application does NOT return the corrupted value, the corruption counter is incremented, and a `SEV-3` log entry is recorded

#### Scenario: Disabled cache is a no-op
- **WHEN** the service configuration sets `CACHE_ENABLED=false`
- **THEN** every cache call returns `ErrCacheConfiguration` and the application treats it as a cache miss without contacting the cache

### Requirement: Multi-key operations and hash tags
When a service requires atomic multi-key operations (e.g., composite rate limit across `(tenant, ip, api_key)`), the service SHALL use the hash-tag pattern `<keyspace>:{<tenant>}:<purpose>:<id>` so the keys share a hash slot in Redis Cluster mode. Single-key operations SHALL use the simple `<service>:<purpose>:<id>` pattern.

#### Scenario: Composite rate limit keys share a hash slot
- **WHEN** the rate-limit Lua script is called with three keys
- **THEN** all three keys carry the same `{<tenant>}` hash tag

#### Scenario: Single-key operations do not introduce hash tags
- **WHEN** a service uses a single-key cache
- **THEN** the key uses the simple `<service>:<purpose>:<id>` pattern

### Requirement: Cache as cache-only — never as a source of truth
The platform SHALL reject any service that uses the cache as the authoritative store for business data (orders, payments, customer profiles). The architecture test SHALL scan every cache-write call site and verify the same write also lands in PostgreSQL in the same transaction or immediately after. The cache MAY be used for read-mostly data (catalog quote, product info) ONLY when the source of truth (PostgreSQL) is also written in the same code path.

#### Scenario: Source-of-truth write accompanies every cache write
- **WHEN** the architecture test scans every cache-write call site
- **THEN** the same code path also writes to PostgreSQL (or the architecture test flags the write for explicit review)

#### Scenario: Sole-source-of-truth cache is rejected
- **WHEN** a service writes business data to the cache without a corresponding PostgreSQL write
- **THEN** the architecture test fails the build

### Requirement: Distributed locks via Postgres advisory locks, not Redis Redlock
The platform SHALL use PostgreSQL advisory locks (`pg_try_advisory_xact_lock(key)`) for any single-writer mutual exclusion. The platform SHALL NOT adopt Redlock or any Redis-based distributed lock for correctness-critical coordination. For K8s-native leader election, the platform SHALL use a `Lease` object via `k8s.io/client-go`. The cache SHALL NOT be used as a lock backend.

#### Scenario: Single-writer uses Postgres advisory lock
- **WHEN** a service requires that exactly one process perform a critical operation
- **THEN** the service uses `pg_try_advisory_xact_lock(key)` and falls back to retry if the lock is contended

#### Scenario: Redlock is not imported
- **WHEN** the architecture test scans the dependency graph
- **THEN** no service imports a Redlock client library

### Requirement: Cross-service cache keyspace documentation
A service that uses the cache SHALL publish its keyspace under `services/<name>/docs/cache-keyspace.md` with every key prefix, every TTL band, every cache purpose, the maximum key size, the eviction policy, and the recovery procedure for a cache outage. The document SHALL be reviewed in the service's `make verify-pr` gate.

#### Scenario: Cache keyspace documentation exists
- **WHEN** a service declares a cache dependency
- **THEN** `services/<name>/docs/cache-keyspace.md` exists and is current

#### Scenario: Cache keyspace is enforced by the architecture test
- **WHEN** a new cache key prefix is introduced
- **THEN** the architecture test fails unless `docs/cache-keyspace.md` lists the new prefix