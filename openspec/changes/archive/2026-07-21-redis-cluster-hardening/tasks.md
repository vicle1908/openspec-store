# Tasks: Redis Cluster Hardening

## Phase 1: Local Cluster + Adapter Refactoring

### 1.1 Docker Compose Cluster
- [x] Create `deploy/docker-compose.redis-cluster.yaml`
  - 6 Redis 8.8-alpine nodes (3M + 3R)
  - Cluster init container
  - Healthchecks per node
  - Named volumes for persistence
- [x] Test cluster startup and slot distribution
- [x] Verify `cluster_state:ok` after init

### 1.2 Adapter Refactoring
- [x] Update `services/catalog-service/internal/config/config.go`
  - Add `ClusterMode bool` (default: false)
  - Add `Addrs []string` (cluster node addresses)
  - Add `Username string` (ACL username)
  - Add TLS fields: `TLSEnabled`, `TLSCertFile`, `TLSKeyFile`, `TLSCAFile`
  - Add pool fields: `PoolSize`, `MinIdleConns`, `ConnMaxIdleTime`, `ConnMaxLifetime`
  - Keep existing fields: `Address`, `Password`, `DB`, `Enabled`, `Timeout`
- [x] Update `services/catalog-service/internal/adapters/redis/adapter.go`
  - Change `client *redis.Client` to `client *redis.ClusterClient`
  - Add cluster client creation: `redis.NewClusterClient`
  - Add TLS config builder function
  - Add connection pool tuning
  - Update `InvalidateByProduct` for multi-node SCAN
  - Update `Ping` for cluster-aware healthcheck
- [x] Update `services/catalog-service/cmd/catalog-service/main.go`
  - Wire new config fields to adapter

### 1.3 Environment Configuration
- [x] Update `deploy/docker-compose.catalog-service.yaml`
  - Add `CATALOG_REDIS_CLUSTER_MODE=false` (default, backward compatible)
  - Keep existing `CATALOG_REDIS_ADDRESS=redis:6379`
- [x] Create `deploy/docker-compose.redis-cluster.env`
  - `CATALOG_REDIS_CLUSTER_MODE=true`
  - `CATALOG_REDIS_ADDRS=redis-7001:6379,redis-7002:6379,redis-7003:6379`
  - `CATALOG_REDIS_PASSWORD=${REDIS_PASSWORD}`

### 1.4 Validation
- [x] Test catalog-service against single-node (existing behavior)
- [x] Test catalog-service against cluster
- [x] Verify quote cache GET/SET across slots
- [x] Test SCAN invalidation across masters
- [x] Test failover: kill master, verify service continues

## Phase 2: Security Hardening

### 2.1 ACL Configuration
- [x] Create `deploy/redis/acl/users.acl`
  - `user default off`
  - `user catalog-svc on >password ~catalog:quote:* +@read +@write +@fast -@dangerous`
  - `user notification-svc on >password ~notification:* ~rate:* +@read +@write +@fast -@dangerous`
  - `user redis-exporter on >password ~* +@read +@info +@slow -@write -@admin`
- [x] Update docker-compose to mount ACL file
- [x] Add `--aclfile /etc/redis/users.acl` to Redis command
- [x] Test ACL enforcement

### 2.2 TLS Configuration
- [x] Generate self-signed certificates for local dev
  - Create `deploy/certs/redis/` directory
  - Generate CA, server, and client certs
- [x] Update docker-compose to mount certificates
- [x] Add TLS directives to Redis command
- [x] Update adapter with TLS config
- [x] Test TLS connection from adapter

### 2.3 Command Restrictions
- [x] Add `rename-command FLUSHALL ""` to Redis command
- [x] Add `rename-command DEBUG ""` to Redis command
- [x] Add `rename-command CONFIG ""` to Redis command
- [x] Test command restrictions

### 2.4 Network Isolation
- [x] Verify Docker Compose network isolation
- [x] Test external access is blocked

## Phase 3: Monitoring Stack

### 3.0 Version Upgrade
- [x] Update `deploy/tools.env`
  - Change `REDIS_EXPORTER_VERSION=v1.86.0` to `REDIS_EXPORTER_VERSION=v1.87.0`
  - (v1.87.0 released July 15, 2026, supports Valkey 9.x + Redis 8.x)

### 3.1 Redis Exporter
- [x] Add `redis-exporter` service to `deploy/docker-compose.redis-cluster.yaml`
  - Image: `oliver006/redis_exporter:v1.87.0`
  - Environment: `REDIS_ADDR`, `REDIS_PASSWORD`
  - Port: `9121:9121`
- [x] Test exporter metrics endpoint at `/metrics`
- [x] Verify metrics for cluster

### 3.2 Prometheus Integration
- [x] Add scrape config to `deploy/prometheus.yml`
  ```yaml
  - job_name: redis-exporter
    static_configs:
      - targets: ["redis-exporter:9121"]
        labels:
          service: redis
  ```
- [x] Verify metrics in Prometheus
- [x] Test metric queries

### 3.3 Grafana Dashboard
- [x] Import dashboard ID 763 (Redis Dashboard)
- [x] Verify panels display data
- [x] Configure auto-refresh (15s)

### 3.4 Alert Rules
- [x] Create `deploy/prometheus/redis-alerts.yml`
  - `RedisHighMemory`: `used/max > 85%` for 5m
  - `RedisReplicationLag`: `lag > 10MB` for 5m
  - `RedisLowHitRate`: `hit_rate < 90%` for 10m
  - `RedisClusterStateNotOk`: `cluster_state != 1` for 1m
  - `RedisSlowCommands`: `slowlog_length > 0` for 5m
- [x] Add alert rules to Prometheus config
- [x] Test alert firing

## Phase 4: Kubernetes Deployment

### 4.1 StatefulSet
- [x] Create `deploy/k8s/base/redis-statefulset.yaml`
  - 6 replicas
  - Image: `redis:${REDIS_VERSION}`
  - VolumeClaimTemplates: 20Gi per node
  - Init container for cluster bootstrap
  - Readiness/TCP probes

### 4.2 Services
- [x] Create `deploy/k8s/base/redis-service.yaml` (Headless)
  - `clusterIP: None`
  - DNS: `redis-cluster-{0..5}.redis-cluster.microservices`

### 4.3 ConfigMap
- [x] Create `deploy/k8s/base/redis-configmap.yaml`
  - `redis.conf` with cluster settings
  - ACL file

### 4.4 Secrets
- [x] Create `deploy/k8s/base/redis-secret.yaml`
  - ACL passwords
  - TLS certificates (if using cert-manager)

### 4.5 NetworkPolicy
- [x] Create `deploy/k8s/base/redis-networkpolicy.yaml`
  - Allow ingress from `microservices` namespace
  - Deny all other traffic

### 4.6 Integration
- [x] Add redis resources to `deploy/k8s/base/kustomization.yaml`
- [x] Add to overlays (local, staging, production)
- [x] Test K8s deployment

## Phase 5: Rate Limiter

### 5.1 Interface Update
- [x] Update `services/notification-service/internal/ports/rate_limiter.go`
  - Add `recipientID string` parameter to `Allow`
  - Update signature: `Allow(ctx, channel, recipientID) (bool, time.Duration, error)`

### 5.2 Adapter
- [x] Create `services/notification-service/internal/adapters/redis/ratelimiter.go`
  - Implement INCREX-based rate limiting (Redis 8.8)
  - Add graceful degradation on Redis outage (fail open)

### 5.3 Configuration
- [x] Add rate limiter config to notification-service
  - `RATE_LIMIT_WINDOW=60s`
  - `RATE_LIMIT_EMAIL=100`
  - `RATE_LIMIT_SMS=10`
  - `RATE_LIMIT_PUSH=50`

### 5.4 Integration
- [x] Wire rate limiter in `services/notification-service/internal/runtime/fx.go`
- [x] Update dispatcher to pass recipientID
- [x] Update tests to use new interface

### 5.5 Validation
- [x] Test within rate limit
- [x] Test rate limit exceeded
- [x] Test Redis outage (fail open)
- [x] Test per-channel configuration
- [x] Verify `TestDispatch_RateLimited` passes
- [x] Verify `TestDispatch_LimiterError` passes

## Phase 6: Documentation & Testing

### 6.1 Documentation
- [x] Update `services/catalog-service/docs/architecture.md`
  - Document cluster mode
  - Document security configuration
- [x] Update `services/catalog-service/docs/runbooks/catalog.md`
  - Add Redis cluster runbook
  - Add TLS certificate rotation
  - Add ACL user management
  - Add failover investigation procedures
  - Add rollback procedures

### 6.2 Testing
- [x] Update `services/catalog-service/test/architecture/layering_test.go`
  - Ensure cluster client import doesn't violate layering
- [x] Add cluster integration tests
- [x] Add TLS integration tests
- [x] Add ACL integration tests

### 6.3 Architecture Tests
- [x] Verify cache admission test still passes
- [x] Add cluster mode validation to test suite

## Phase 7: Verification & Operational Scripts

### 7.1 Verification Scripts
- [x] Create `scripts/redis-cluster-healthcheck.sh`
  - Check all 6 nodes
  - Verify `cluster_state:ok`
  - Report memory usage per node
  - Exit code 0 on success
- [x] Create `scripts/redis-cluster-failover-test.sh`
  - Identify a master node
  - Execute `DEBUG SEGFAULT`
  - Wait for failover
  - Verify cluster recovery
  - Report failover duration
- [x] Create `scripts/redis-cache-purge.sh`
  - SCAN all masters for pattern
  - DEL matching keys
  - Report number of keys deleted

### 7.2 Post-Deployment Verification
- [x] Verify application connectivity to cluster
- [x] Verify cache operations (GET/SET/DELETE)
- [x] Verify invalidation across masters
- [x] Verify monitoring metrics are available
- [x] Verify alerts are configured and firing

### 7.3 Failover Testing
- [x] Test master crash failover (`DEBUG SEGFAULT`)
- [x] Test master debug sleep (`DEBUG sleep 30`)
- [x] Verify application resilience during failover
- [x] Document failover duration and behavior

### 7.4 Security Verification
- [x] Test ACL authentication for catalog-svc
- [x] Test ACL unauthorized access denial
- [x] Test dangerous commands are blocked
- [x] Test TLS connections work

### 7.5 Performance Verification
- [x] Test cache hit rate > 90%
- [x] Test p99 latency < 50ms
- [x] Test connection pool stability
- [x] Test no connection leaks under load

### 7.6 Monitoring Verification
- [x] Verify Redis Exporter metrics are scraped
- [x] Verify Grafana dashboard displays data
- [x] Verify alert rules fire correctly
- [x] Verify alert routing works

### 7.7 Bug Investigation Procedures
- [x] Document `CLUSTER INFO` investigation
- [x] Document `CLUSTER NODES` investigation
- [x] Document `SLOWLOG` investigation
- [x] Document memory investigation
- [x] Document connection investigation

### 7.8 Rollback Procedures
- [x] Document rollback to single-node (`ClusterMode=false`)
- [x] Document rollback deployment (`docker compose down -v`)
- [x] Document restore from AOF backup

### 7.9 Real Operation Triggers
- [x] Configure cache hit rate alert (< 90% for 10m)
- [x] Configure memory alert (> 85% for 5m)
- [x] Configure replication lag alert (> 10MB for 5m)
- [x] Configure cluster state alert (!= ok for 1m)
- [x] Document investigation procedures for each trigger
