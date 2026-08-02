# Design: Redis Cluster Hardening

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION TOPOLOGY                           │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────────┐     ┌──────────────────────────────────────┐
  │ catalog-api  │────▶│  Redis 8.8 Cluster (6 nodes)         │
  │              │     │  ┌─────────┐ ┌─────────┐ ┌─────────┐│
  │              │     │  │Master   │ │Master   │ │Master   ││
  │              │     │  │ 7001    │ │ 7002    │ │ 7003    ││
  │              │     │  │Slot 0-  │ │Slot 5461│ │Slot10923││
  │              │     │  │  5460   │ │-10922   │ │-16383   ││
  │              │     │  └────┬────┘ └────┬────┘ └────┬────┘│
  │              │     │       │           │           │      │
  │              │     │  ┌────▼────┐ ┌────▼────┐ ┌────▼────┐│
  │              │     │  │Replica  │ │Replica  │ │Replica  ││
  │              │     │  │  7004   │ │  7005   │ │  7006   ││
  │              │     │  └─────────┘ └─────────┘ └─────────┘│
  └──────────────┘     └──────────────────────────────────────┘
                                                       │
                                               ┌───────▼───────┐
                                               │ Redis Exporter│
                                               │    :9121      │
                                               └───────┬───────┘
                                                       │
                                               ┌───────▼───────┐
                                               │  Prometheus   │
                                               │  (via OTel)   │
                                               └───────┬───────┘
                                                       │
                                               ┌───────▼───────┐
                                               │   Grafana     │
                                               │ Dashboard 763 │
                                               └───────────────┘
```

## Technical Design

### 1. Adapter Refactoring (Modern)

**File:** `services/catalog-service/internal/adapters/redis/adapter.go`

**Current:**
```go
type Adapter struct {
    client *redis.Client
    enabled bool
}

func New(ctx context.Context, cfg Config) (*Adapter, error) {
    client := redis.NewClient(&redis.Options{
        Addr:     cfg.Address,
        Password: cfg.Password,
        DB:       cfg.DB,
    })
    // ...
}
```

**Proposed (Greenfield — Cluster-Only):**
```go
type Adapter struct {
    client *redis.ClusterClient
    enabled bool
}

func New(ctx context.Context, cfg Config) (*Adapter, error) {
    client := redis.NewClusterClient(&redis.ClusterOptions{
        Addrs:              cfg.Addrs,
        Username:           cfg.Username,
        Password:           cfg.Password,
        PoolSize:           cfg.PoolSize,
        MaxActiveConns:     cfg.MaxActiveConns,
        MinIdleConns:       cfg.MinIdleConns,
        ConnMaxIdleTime:    cfg.ConnMaxIdleTime,
        ConnMaxLifetime:    cfg.ConnMaxLifetime,
        ReadTimeout:        cfg.ReadTimeout,
        WriteTimeout:       cfg.WriteTimeout,
        DialTimeout:        cfg.DialTimeout,
        MaxRetries:         cfg.MaxRetries,
        MaxRedirects:       3,
        ReadOnly:           true,
        RouteByLatency:     true,
        Protocol:           3,  // RESP3
        TLSConfig:          buildTLSConfig(cfg),
    })

    if err := client.Ping(ctx).Err(); err != nil {
        return nil, fmt.Errorf("redis: ping: %w", err)
    }

    return &Adapter{client: client, enabled: true}, nil
}

// Get uses zero-copy buffer for performance (go-redis v9.21.0)
func (a *Adapter) Get(ctx context.Context, productID string, minuteEpoch int64) (quote.Quote, bool, error) {
    if !a.enabled {
        return quote.Quote{}, false, ports.ErrCacheConfiguration
    }
    key := ports.QuoteCacheKey(productID, minuteEpoch)

    // Zero-copy: read directly into pre-allocated buffer
    buf := make([]byte, 0, 1024)  // pre-allocate
    cmd := a.client.GetToBuffer(ctx, key, buf)
    if cmd.Err() != nil {
        if errors.Is(cmd.Err(), redis.Nil) {
            return quote.Quote{}, false, ports.ErrCacheMiss
        }
        return quote.Quote{}, false, fmt.Errorf("%w: %v", ports.ErrCacheOutage, cmd.Err())
    }

    // Use cmd.Bytes() for zero-copy access
    var q quote.Quote
    if err := json.Unmarshal(cmd.Bytes(), &q); err != nil {
        return quote.Quote{}, false, fmt.Errorf("%w: %v", ports.ErrCacheCorruption, err)
    }
    return q, true, nil
}

// Set uses zero-copy buffer for performance (go-redis v9.21.0)
func (a *Adapter) Set(ctx context.Context, productID string, minuteEpoch int64, q quote.Quote, ttl time.Duration) error {
    if !a.enabled {
        return ports.ErrCacheConfiguration
    }
    raw, err := json.Marshal(q)
    if err != nil {
        return fmt.Errorf("redis: encode: %w", err)
    }
    key := ports.QuoteCacheKey(productID, minuteEpoch)

    // Zero-copy: write directly from byte buffer
    if err := a.client.SetFromBuffer(ctx, key, raw, ttl).Err(); err != nil {
        return fmt.Errorf("%w: %v", ports.ErrCacheOutage, err)
    }
    return nil
}

func buildTLSConfig(cfg Config) *tls.Config {
    if !cfg.TLSEnabled {
        return nil
    }
    cert, err := tls.LoadX509KeyPair(cfg.TLSCertFile, cfg.TLSKeyFile)
    if err != nil {
        return nil
    }
    caCert, err := os.ReadFile(cfg.TLSCAFile)
    if err != nil {
        return nil
    }
    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)
    return &tls.Config{
        MinVersion:   tls.VersionTLS12,
        Certificates: []tls.Certificate{cert},
        RootCAs:      caCertPool,
    }
}
```

### 2. Config Expansion

**File:** `services/catalog-service/internal/config/config.go`

**Add to Config struct:**
```go
type Redis struct {
    Address         string        `mapstructure:"address"`
    Addrs           []string      `mapstructure:"addrs"`
    Username        string        `mapstructure:"username"`
    Password        string        `mapstructure:"password"`
    DB              int           `mapstructure:"db"`
    Enabled         bool          `mapstructure:"enabled"`
    ClusterMode     bool          `mapstructure:"cluster_mode"`
    TLSEnabled      bool          `mapstructure:"tls_enabled"`
    TLSCertFile     string        `mapstructure:"tls_cert_file"`
    TLSKeyFile      string        `mapstructure:"tls_key_file"`
    TLSCAFile       string        `mapstructure:"tls_ca_file"`
    PoolSize        int           `mapstructure:"pool_size"`
    MaxActiveConns  int           `mapstructure:"max_active_conns"`
    MinIdleConns    int           `mapstructure:"min_idle_conns"`
    ConnMaxIdleTime time.Duration `mapstructure:"conn_max_idle_time"`
    ConnMaxLifetime time.Duration `mapstructure:"conn_max_lifetime"`
    ReadTimeout     time.Duration `mapstructure:"read_timeout"`
    WriteTimeout    time.Duration `mapstructure:"write_timeout"`
    DialTimeout     time.Duration `mapstructure:"dial_timeout"`
    MaxRetries      int           `mapstructure:"max_retries"`
    Protocol        int           `mapstructure:"protocol"`
}
```

**Environment Variables:**
```
# Cluster mode
CATALOG_REDIS_CLUSTER_MODE=true
CATALOG_REDIS_ADDRS=redis-7001:6379,redis-7002:6379,redis-7003:6379

# Authentication
CATALOG_REDIS_USERNAME=catalog-svc
CATALOG_REDIS_PASSWORD=${REDIS_PASSWORD}

# TLS
CATALOG_REDIS_TLS_ENABLED=true
CATALOG_REDIS_TLS_CERT_FILE=/certs/redis.crt
CATALOG_REDIS_TLS_KEY_FILE=/certs/redis.key
CATALOG_REDIS_TLS_CA_FILE=/certs/ca.crt

# Connection pool
CATALOG_REDIS_POOL_SIZE=50
CATALOG_REDIS_MAX_ACTIVE_CONNS=100
CATALOG_REDIS_MIN_IDLE_CONNS=10
CATALOG_REDIS_CONN_MAX_IDLE_TIME=5m
CATALOG_REDIS_CONN_MAX_LIFETIME=10m

# Timeouts
CATALOG_REDIS_READ_TIMEOUT=3s
CATALOG_REDIS_WRITE_TIMEOUT=3s
CATALOG_REDIS_DIAL_TIMEOUT=5s
CATALOG_REDIS_MAX_RETRIES=3
CATALOG_REDIS_PROTOCOL=3
```

### 3. Multi-Node SCAN

**File:** `services/catalog-service/internal/adapters/redis/adapter.go`

```go
func (a *Adapter) InvalidateByProduct(ctx context.Context, productID string) error {
    if !a.enabled {
        return ports.ErrCacheConfiguration
    }

    pattern := ports.QuoteCachePattern(productID)

    if a.clusterMode {
        return a.invalidateCluster(ctx, pattern)
    }
    return a.invalidateSingle(ctx, pattern)
}

func (a *Adapter) invalidateCluster(ctx context.Context, pattern string) error {
    clusterClient, ok := a.client.(*redis.ClusterClient)
    if !ok {
        return fmt.Errorf("%w: not a cluster client", ports.ErrCacheOutage)
    }

    // Get all master nodes
    nodes, err := clusterClient.ClusterNodes(ctx).Result()
    if err != nil {
        return fmt.Errorf("%w: %v", ports.ErrCacheOutage, err)
    }

    // SCAN each master
    for _, node := range nodes {
        if node.Flags == "master" {
            if err := a.scanAndDelete(ctx, node.Addr, pattern); err != nil {
                return err
            }
        }
    }
    return nil
}

func (a *Adapter) scanAndDelete(ctx context.Context, addr, pattern string) error {
    // Create a temporary client for this node
    // SCAN and DEL on this specific node
    // ...
}
```

### 4. Docker Compose Cluster

**File:** `deploy/docker-compose.redis-cluster.yaml`

```yaml
services:
  redis-7001:
    image: redis:${REDIS_VERSION}
    ports: ["7001:7001"]
    command: >
      redis-server --port 7001
      --cluster-enabled yes
      --cluster-config-file nodes-7001.conf
      --cluster-node-timeout 5000
      --appendonly yes
      --appendfsync everysec
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
      --requirepass ${REDIS_PASSWORD}
      --aclfile /etc/redis/users.acl
    volumes:
      - redis-7001:/data
      - ./redis/acl:/etc/redis/users.acl:ro
    networks: [redis-cluster]
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 6

  # ... redis-7002 through redis-7006 similar

  redis-init:
    image: redis:${REDIS_VERSION}
    depends_on: [redis-7001, redis-7002, redis-7003, redis-7004, redis-7005, redis-7006]
    entrypoint: >
      sh -c "sleep 3 &&
      redis-cli --cluster create
      redis-7001:7001 redis-7002:7002 redis-7003:7003
      redis-7004:7004 redis-7005:7005 redis-7006:7006
      --cluster-replicas 1
      --cluster-yes
      -a ${REDIS_PASSWORD}"

  redis-exporter:
    image: oliver006/redis_exporter:${REDIS_EXPORTER_VERSION}
    environment:
      REDIS_ADDR: redis://redis-7001:7001
      REDIS_PASSWORD: ${REDIS_PASSWORD}
    ports: ["9121:9121"]
    networks: [redis-cluster]

volumes:
  redis-7001:
  redis-7002:
  redis-7003:
  redis-7004:
  redis-7005:
  redis-7006:

networks:
  redis-cluster:
    driver: bridge
```

### 5. Kubernetes StatefulSet

**File:** `deploy/k8s/base/redis-statefulset.yaml`

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
spec:
  serviceName: redis-cluster
  replicas: 6
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      containers:
        - name: redis
          image: redis:${REDIS_VERSION}
          command:
            - sh
            - -c
            - |
              INDEX=${HOSTNAME##*-}
              if [ $INDEX -lt 3 ]; then
                PORT=$((7001 + INDEX))
              else
                PORT=$((7004 + INDEX - 3))
              fi
              redis-server /conf/redis.conf --port $PORT
          ports:
            - containerPort: 7001
              name: redis
          resources:
            requests:
              memory: "2Gi"
              cpu: "500m"
            limits:
              memory: "4Gi"
              cpu: "1000m"
          volumeMounts:
            - name: data
              mountPath: /data
            - name: conf
              mountPath: /conf
          readinessProbe:
            tcpSocket:
              port: 7001
            initialDelaySeconds: 10
            periodSeconds: 5
          livenessProbe:
            tcpSocket:
              port: 7001
            initialDelaySeconds: 30
            periodSeconds: 10
      volumes:
        - name: conf
          configMap:
            name: redis-cluster-config
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 20Gi
```

### 6. ACL Configuration

**File:** `deploy/redis/acl/users.acl`

```
# Default user disabled
user default off

# Catalog service
user catalog-svc on >catalog-password ~catalog:quote:* +@read +@write +@fast -@dangerous -@admin

# Notification service
user notification-svc on >notification-password ~notification:* ~rate:* +@read +@write +@fast -@dangerous -@admin

# Redis Exporter
user redis-exporter on >exporter-password ~* +@read +@info +@slow -@write -@admin -@dangerous
```

### 7. Rate Limiter Implementation (Modern)

**File:** `services/notification-service/internal/adapters/redis/ratelimiter.go`

```go
package redis

import (
    "context"
    "time"

    "github.com/redis/go-redis/v9"
)

type RateLimiter struct {
    client    *redis.ClusterClient
    namespace string
    limits    map[notification.Channel]ChannelLimit
}

type ChannelLimit struct {
    Limit  int
    Window time.Duration
}

// Allow checks if the request is within rate limit.
// Uses Redis 8.8 INCREX command (no fallback — greenfield).
func (r *RateLimiter) Allow(ctx context.Context, channel notification.Channel, recipientID string) (bool, time.Duration, error) {
    limit := r.limits[channel]
    key := r.namespace + ":" + string(channel) + ":" + recipientID

    // INCREX key BYINT 1 UBOUND <limit> EX <window> ENX
    // Response: [current_value, delta] where delta=0 means rate limited
    result, err := r.client.Do(ctx,
        "INCREX", key,
        "BYINT", 1,
        "UBOUND", limit.Limit,
        "EX", int64(limit.Window.Seconds()),
        "ENX",
    ).Result()

    if err != nil {
        // Fail open on Redis outage
        return true, 0, nil
    }

    // Parse response: [current_value, delta]
    vals, ok := result.([]interface{})
    if !ok || len(vals) != 2 {
        return true, 0, nil
    }

    delta, _ := vals[1].(int64)
    if delta == 0 {
        // Rate limited — get TTL for retryAfter
        ttl, _ := r.client.TTL(ctx, key).Result()
        return false, ttl, nil
    }

    return true, 0, nil
}
```

## Hash Slot Distribution

```
┌─────────────────────────────────────────────────────────────────┐
│              HASH SLOT DISTRIBUTION                              │
└─────────────────────────────────────────────────────────────────┘

  REDIS CLUSTER SHARDING:
  ═══════════════════════
  - 16,384 hash slots distributed across masters
  - Slot = CRC16(key) mod 16384
  - Each master owns a subset of slots
  - Keys automatically routed to correct master

  YOUR KEY PATTERN:
  ═════════════════
  catalog:quote:<productID>:<minuteEpoch>

  Example:
    catalog:quote:prod-123:1721500000
    CRC16("catalog:quote:prod-123:1721500000") mod 16384 = slot X

  DISTRIBUTION:
  ══════════════
  Master 1: slots 0-5460      (~33% of keys)
  Master 2: slots 5461-10922  (~33% of keys)
  Master 3: slots 10923-16383 (~33% of keys)

  VERIFICATION:
  ═════════════
  redis-cli -c -p 7001 CLUSTER KEYSLOT catalog:quote:prod-123:1721500000
  → Returns slot number (0-16383)

  redis-cli -c -p 7001 CLUSTER NODES
  → Shows which master owns each slot range
```

## Hash Tag Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│              HASH TAG STRATEGY                                  │
└─────────────────────────────────────────────────────────────────┘

  CURRENT KEY PATTERN:
  ════════════════════
  catalog:quote:<productID>:<minuteEpoch>
  → No hash tag (each key independent)

  WHEN TO USE HASH TAGS:
  ══════════════════════
  Use hash tags when you need multi-key operations (MGET, transactions)
  on related keys. Example:

  user:{123}:profile  → slot = CRC16("123") mod 16384
  user:{123}:orders   → slot = CRC16("123") mod 16384
  user:{123}:wishlist → slot = CRC16("123") mod 16384

  All three keys land on the same slot → MGET works.

  YOUR USE CASE:
  ══════════════
  catalog:quote:<productID>:<minuteEpoch>
  → Each quote is independent (no multi-key operations needed)
  → No hash tag required
  → Keys distribute evenly across masters

  DECISION: Keep current pattern (no hash tag).
  Keys distribute evenly. Revisit if multi-key operations needed.
```

## SCAN Across Masters

```
┌─────────────────────────────────────────────────────────────────┐
│              SCAN IN CLUSTER MODE                                │
└─────────────────────────────────────────────────────────────────┘

  SCAN IS NODE-LOCAL:
  ════════════════════
  - SCAN only searches keys on the current node
  - Must SCAN each master to find all keys
  - go-redis ClusterClient handles this automatically

  INVALIDATION STRATEGY:
  ══════════════════════
  Current: InvalidateByProduct("prod-123")
  Pattern: catalog:quote:prod-123:*

  In cluster mode:
  1. Get master list from CLUSTER NODES
  2. SCAN each master for pattern
  3. DEL matching keys on each master
```

## Resharding Best Practices

```
┌─────────────────────────────────────────────────────────────────┐
│              RESHARDING BEST PRACTICES                           │
└─────────────────────────────────────────────────────────────────┘

  ADDING A NODE:
  ══════════════
  1. Start new Redis node with cluster-enabled yes
  2. Add to cluster: redis-cli --cluster add-node <new> <existing>
  3. Reshard slots: redis-cli --cluster reshard <existing>
  4. Verify: redis-cli --cluster check <existing>

  REMOVING A NODE:
  ════════════════
  1. Reshard all slots away from the node
  2. Verify node has 0 slots: CLUSTER NODES
  3. Remove: redis-cli --cluster del-node <existing> <node-id>

  REBALANCING:
  ════════════
  redis-cli --cluster rebalance <any-node>
  → Automatically moves slots to balance load

  BEST PRACTICES:
  ═══════════════
  ✅ Reshard during low-traffic periods
  ✅ Monitor replication lag during resharding
  ✅ Verify cluster health after resharding
  ⚠️  Don't reshard too many slots at once
  ⚠️  Don't remove a node that has replicas
```

## Security Considerations

1. **TLS Certificates** — Self-signed for local dev, cert-manager for K8s
2. **Credential Rotation** — Kubernetes Secrets support rolling updates
3. **Network Isolation** — NetworkPolicy restricts Redis access to authorized namespaces
4. **Command Restrictions** — FLUSHALL, DEBUG, CONFIG disabled in production

## Performance Considerations

1. **Connection Pool** — `PoolSize=10×CPU`, `MinIdleConns=10` prevents cold starts
2. **Read Replicas** — `ReadOnly=true`, `RouteByLatency=true` offload reads
3. **Protocol 3** — RESP3 reduces parsing overhead
4. **SCAN Batching** — `COUNT 100` per SCAN iteration prevents blocking

## Migration Strategy

1. **Phase 1** — Local cluster validation (Docker Compose)
2. **Phase 2** — Security hardening (ACLs, TLS)
3. **Phase 3** — Monitoring deployment (Redis Exporter)
4. **Phase 4** — K8s deployment (StatefulSet)
5. **Phase 5** — Rate limiter (notification-service)

## Rollback Strategy

1. Set `ClusterMode=false` and `Address=redis:6379` to revert to single-node
2. Remove Redis Exporter from docker-compose
3. Delete K8s Redis resources
4. Existing cache key pattern unchanged — no data migration needed
