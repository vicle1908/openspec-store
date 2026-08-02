# platform-cache (modified)

## Purpose

Update the catalog-service Redis adapter to use modern Redis 8.8 and go-redis v9.21.0 features: cluster mode, zero-copy buffers, RESP3 protocol, connection pooling, and TLS configuration. This is a greenfield implementation — no backward compatibility with legacy patterns.

## Current State

The adapter (`services/catalog-service/internal/adapters/redis/adapter.go`) currently:
- Uses `redis.NewClient` (single-node only)
- Client type: `*redis.Client`
- Config struct has: `Address`, `Password`, `DB`, `Enabled`, `Timeout`
- No cluster support, no TLS, no connection pool tuning
- Key pattern: `catalog:quote:<productID>:<minuteEpoch>`
- Invalidation uses `SCAN MATCH` (node-local)

The `QuoteCache` interface (`services/catalog-service/internal/ports/cache.go`) has:
- `Get(ctx, productID, minuteEpoch) (Quote, bool, error)`
- `Set(ctx, productID, minuteEpoch, Quote, ttl) error`
- `InvalidateByProduct(ctx, productID) error`
- `Ping(ctx) error`

## Dependencies

- go-redis v9.21.0 (latest, with zero-copy buffer support)
- Redis 8.8-alpine (pinned in `deploy/tools.env`)
- No fallback to single-node or older Redis versions — this is greenfield

## MODIFIED Requirements

### Requirement: PC-001: Cluster-Only Mode

The adapter SHALL use `redis.NewClusterClient` exclusively. Single-node mode is not supported in this greenfield implementation. The `ClusterMode` flag is removed — cluster is always enabled.

#### Scenario: Cluster Client Creation
Given the adapter configuration with `Addrs=["redis-7001:6379", "redis-7002:6379", "redis-7003:6379"]`
When the adapter initializes
Then it shall create a `redis.NewClusterClient` with `ClusterOptions`
And commands shall be automatically routed to the correct node
And the adapter shall handle `MOVED` and `ASK` redirections transparently

### Requirement: PC-002: Modern Config Structure

The `Config` struct SHALL be designed for modern Redis 8.8 and go-redis v9.21.0 features. No legacy fields.

New fields:
- `Addrs []string` (cluster node addresses, required)
- `Username string` (ACL username)
- `Password string` (ACL password)
- `TLSEnabled bool` (default: false)
- `TLSCertFile string` (client certificate path)
- `TLSKeyFile string` (client key path)
- `TLSCAFile string` (CA certificate path)
- `PoolSize int` (default: 10 × runtime.GOMAXPROCS(0))
- `MaxActiveConns int` (default: 0, unlimited)
- `MinIdleConns int` (default: 10)
- `ConnMaxIdleTime time.Duration` (default: 5m)
- `ConnMaxLifetime time.Duration` (default: 10m)
- `ReadTimeout time.Duration` (default: 3s)
- `WriteTimeout time.Duration` (default: 3s)
- `DialTimeout time.Duration` (default: 5s)
- `MaxRetries int` (default: 3)
- `Protocol int` (default: 3, RESP3)

#### Scenario: Modern Config
Given a Config with cluster addresses and pool settings
When the adapter initializes
Then it shall create a cluster client with all modern settings
And `Protocol` shall be `3` (RESP3)

### Requirement: PC-003: Zero-Copy Buffer Operations

The adapter SHALL use go-redis v9.21.0 zero-copy buffer operations for Get/Set to minimize GC pressure.

#### Scenario: Zero-Copy Get
Given a cached quote stored in Redis
When `Get(ctx, productID, minuteEpoch)` is called
Then it shall use `client.GetToBuffer(ctx, key, buf)` to read directly into a pre-allocated buffer
And it shall avoid intermediate string allocation
And performance shall be optimized for high-throughput scenarios

#### Scenario: Zero-Copy Set
Given a quote to cache
When `Set(ctx, productID, minuteEpoch, quote, ttl)` is called
Then it shall use `client.SetFromBuffer(ctx, key, buf)` to write directly from a byte buffer
And it shall avoid intermediate string conversion
And performance shall be optimized for high-throughput scenarios

### Requirement: PC-004: Connection Pool Tuning

The adapter SHALL use modern connection pool settings via ClusterOptions.

#### Scenario: Default Pool Settings
Given the adapter with default configuration
When the adapter initializes
Then `PoolSize` shall be 10 × runtime.GOMAXPROCS(0)
And `MinIdleConns` shall be 10
And `ReadTimeout` shall be 3 seconds
And `WriteTimeout` shall be 3 seconds
And connections shall be recycled after 10 minutes lifetime

#### Scenario: Custom Pool Settings
Given `PoolSize=50`, `MinIdleConns=20`, `MaxActiveConns=100`
When the adapter initializes
Then the pool shall maintain up to 50 base connections
And at least 20 connections shall be kept warm
And no more than 100 connections shall be active at once

### Requirement: PC-005: TLS Support

The adapter SHALL support TLS connections when `TLSEnabled=true`. The implementation SHALL load client certificate, CA certificate, and use TLS 1.2 minimum.

#### Scenario: TLS Enabled
Given `TLSEnabled=true` and valid certificate paths
When the adapter initializes
Then it shall call `tls.LoadX509KeyPair(TLSCertFile, TLSKeyFile)`
And it shall call `x509.NewCertPool()` and append CA certificate
And it shall set `TLSConfig = &tls.Config{MinVersion: tls.VersionTLS12, Certificates: []tls.Certificate{cert}, RootCAs: caCertPool}`
And connections shall use TLS 1.2 or higher

#### Scenario: TLS Disabled
Given `TLSEnabled=false` (default)
When the adapter initializes
Then `TLSConfig` shall be nil
And connections shall be unencrypted

### Requirement: PC-006: Multi-Node SCAN

The `InvalidateByProduct` method SHALL work correctly in cluster mode. The implementation SHALL get all master nodes via `CLUSTER NODES`, then SCAN each master for matching keys.

#### Scenario: SCAN in Cluster Mode
Given a cluster with 3 masters
When `InvalidateByProduct("prod-123")` is called
Then the adapter shall call `clusterClient.ClusterNodes(ctx)` to get master list
And for each master, it shall SCAN with pattern `catalog:quote:prod-123:*`
And it shall DEL all matching keys on each master
And SCAN shall use `COUNT 100` per iteration

### Requirement: PC-007: Cluster-Aware Healthcheck

The `Ping` method SHALL work correctly in cluster mode. The implementation SHALL ping a random node in the cluster.

#### Scenario: Ping in Cluster Mode
Given a cluster with 3 masters
When `Ping(ctx)` is called
Then the adapter shall call `clusterClient.Ping(ctx)`
And it shall return `nil` if any node responds
And it shall return `ErrCacheOutage` if all nodes fail

### Requirement: PC-008: RESP3 Protocol

The adapter SHALL use RESP3 protocol (Redis 6+ serialization protocol) for improved performance and type support.

#### Scenario: RESP3 Enabled
Given the adapter with default configuration
When the adapter initializes
Then `ClusterOptions.Protocol` shall be `3`
And communication shall use RESP3 serialization
And performance shall be improved over RESP2

### Requirement: PC-009: ClusterOptions Fields

The `redis.ClusterOptions` struct SHALL be configured with the following fields:
- `Addrs: cfg.Addrs`
- `Username: cfg.Username`
- `Password: cfg.Password`
- `PoolSize: cfg.PoolSize`
- `MaxActiveConns: cfg.MaxActiveConns`
- `MinIdleConns: cfg.MinIdleConns`
- `ConnMaxIdleTime: cfg.ConnMaxIdleTime`
- `ConnMaxLifetime: cfg.ConnMaxLifetime`
- `ReadTimeout: cfg.ReadTimeout`
- `WriteTimeout: cfg.WriteTimeout`
- `DialTimeout: cfg.DialTimeout`
- `MaxRetries: cfg.MaxRetries`
- `MaxRedirects: 3`
- `ReadOnly: true`
- `RouteByLatency: true`
- `Protocol: 3`
- `TLSConfig: tlsConfig` (if TLSEnabled)

#### Scenario: ClusterOptions Applied
Given a Config with cluster settings
When the adapter creates a ClusterClient
Then `ClusterOptions.Addrs` shall be `cfg.Addrs`
And `ClusterOptions.ReadOnly` shall be `true`
And `ClusterOptions.RouteByLatency` shall be `true`
And `ClusterOptions.MaxRedirects` shall be `3`
And `ClusterOptions.Protocol` shall be `3`
