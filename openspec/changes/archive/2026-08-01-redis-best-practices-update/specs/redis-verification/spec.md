# redis-verification (delta)

## Purpose

Enhanced Redis verification with connection pool hardening requirements.

## MODIFIED Requirements

### Requirement: RV-006: Performance Verification

Performance SHALL be verified under load:
- Cache hit rate > 90% for repeated queries
- p99 latency < 50ms for cache operations
- Connection pool handles concurrent requests
- No connection leaks under sustained load
- Connection pool SHALL use FIFO mode (`PoolFIFO: true`) for even distribution
- Retry backoff SHALL be explicitly configured: `MinRetryBackoff: 8ms`, `MaxRetryBackoff: 512ms`

#### Scenario: Cache Hit Rate

Given a warm cache with 1000 product quotes
When 10000 random quote requests are executed
Then cache hit rate shall be > 90%
And `redis_keyspace_hits_total / (hits + misses)` shall be > 0.9

#### Scenario: Latency Under Load

Given Redis cluster with 50 concurrent connections
When 1000 SET/GET operations are executed
Then p99 latency shall be < 50ms
And no timeouts shall occur

#### Scenario: Connection Pool Stability

Given the adapter with `PoolSize=50`, `MinIdleConns=10`, `PoolFIFO=true`
When 100 concurrent requests are executed
Then the pool shall not exhaust connections
And `redis_connected_clients` shall remain stable
And connections shall be distributed evenly (FIFO, not LIFO)

#### Scenario: Retry Backoff Configuration

Given the adapter with explicit retry backoff
When a transient connection error occurs
Then the first retry shall wait ~8ms
And subsequent retries shall exponentially backoff up to 512ms
And the retry behavior shall be consistent across restarts

## ADDED Requirements

### Requirement: RV-012: Connection Pool Hardening

Redis clients SHALL configure `PoolFIFO: true` for even connection distribution. Retry backoff SHALL be explicitly configured: `MinRetryBackoff: 8ms`, `MaxRetryBackoff: 512ms`. These settings SHALL be documented in the adapter configuration and verified in integration tests.

#### Scenario: FIFO Pool Behavior

Given a Redis client with `PoolFIFO: true`
When 50 concurrent connections are requested
Then connections shall be served in FIFO order (oldest idle first)
And no single connection shall handle disproportionate traffic

#### Scenario: Explicit Backoff Values

Given a Redis client with explicit retry backoff
When the client configuration is inspected
Then `MinRetryBackoff` shall be `8ms`
And `MaxRetryBackoff` shall be `512ms`
And these values shall be documented in the config struct
