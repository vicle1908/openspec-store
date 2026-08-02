## Why

The catalog service's Redis deployment is a single instance with no authentication, no TLS, no clustering, and no monitoring. This is acceptable for local development but creates three critical gaps:

1. **No high availability** — a single Redis failure breaks all quote lookups, forcing fallthrough to PostgreSQL (320ms p99 vs 5ms cached)
2. **No security** — Redis is exposed on port 6379 with no password, no ACLs, no encryption. Over 50,000 Redis instances were found exposed on the internet in 2025.
3. **No observability** — Redis Exporter is pinned in `tools.env` but never deployed; there are no metrics, no dashboards, no alerts for cache hit rate, memory usage, or replication lag.

Redis 8.8 (May 2026) introduces `INCREX` for native rate limiting, which the notification-service needs for per-recipient rate limiting without Lua scripts.

## What Changes

- **Redis 8.8 cluster deployment** — 6-node cluster (3 masters + 3 replicas) for local Docker Compose and Kubernetes StatefulSet
- **Security hardening** — ACL users per service (`catalog-svc`, `notification-svc`), TLS for cross-node and client communication, command restrictions (`FLUSHALL`, `DEBUG`, `CONFIG` disabled)
- **Adapter refactoring** — `catalog-service/internal/adapters/redis/adapter.go` refactored to support cluster mode (`redis.NewClusterClient`), connection pool tuning, and TLS configuration
- **Monitoring stack** — Redis Exporter v1.87.0 deployed, Prometheus scrape configured, Grafana dashboard imported, alert rules for memory/replication/hit-rate
- **Kubernetes manifests** — StatefulSet, Headless Service, ConfigMap, Secret, PVC, NetworkPolicy for production Redis deployment
- **Rate limiter** — notification-service gets Redis-backed rate limiting using Redis 8.8 `INCREX` command (with sorted-set fallback for Redis < 8.8)

## Capabilities

### New Capabilities

- `redis-cluster`: Redis 8.8 cluster deployment (6 nodes, 3M+3R) for local Docker Compose and Kubernetes StatefulSet with healthchecks, persistence, and cluster bootstrap
- `redis-security`: ACL-based authentication per service, TLS encryption for client and inter-node communication, command restrictions, network isolation
- `redis-monitoring`: Redis Exporter metrics collection, Prometheus scrape configuration, Grafana dashboard, alert rules for memory/replication/hit-rate/slow-commands
- `redis-rate-limiter`: Distributed rate limiting for notification-service using Redis 8.8 `INCREX` command with per-recipient sliding window
- `redis-verification`: Pre-deployment validation, post-deployment verification, failover testing, operational scripts, bug investigation procedures, rollback procedures

### Modified Capabilities

- `platform-cache`: Adapter refactored to support cluster mode (`redis.NewClusterClient`), connection pool tuning (`PoolSize`, `MinIdleConns`), TLS configuration, and multi-node SCAN for invalidation

## Impact

### Affected Code
- `services/catalog-service/internal/adapters/redis/adapter.go` — cluster client, TLS, pool tuning
- `services/catalog-service/internal/config/config.go` — new config fields (ClusterMode, Addrs, TLS, PoolSize)
- `services/notification-service/internal/ports/rate_limiter.go` — Redis-backed implementation
- `services/notification-service/internal/adapters/redis/` — new adapter directory

### Affected Infrastructure
- `deploy/docker-compose.redis-cluster.yaml` — new file, 6-node cluster
- `deploy/docker-compose.catalog-service.yaml` — updated Redis env vars
- `deploy/k8s/base/redis-statefulset.yaml` — new file
- `deploy/k8s/base/redis-service.yaml` — new file
- `deploy/k8s/base/redis-configmap.yaml` — new file
- `deploy/k8s/base/redis-secret.yaml` — new file
- `deploy/docker-compose.yaml` — Redis Exporter service added

### Dependencies
- Redis 8.8-alpine (already pinned in `deploy/tools.env`)
- go-redis/v9 (already in `services/catalog-service/go.mod`)
- Redis Exporter v1.87.0 (already pinned in `deploy/tools.env`)

### Compatibility
- **Non-breaking** — existing single-node mode continues to work via `ClusterMode=false` config flag
- Cache key pattern (`catalog:quote:<productID>:<minuteEpoch>`) unchanged
- `ports.QuoteCache` interface unchanged

### Rollout
1. Local cluster validation (Docker Compose)
2. Security hardening (ACLs, TLS)
3. Monitoring deployment (Redis Exporter)
4. Kubernetes deployment (StatefulSet)
5. Rate limiter (notification-service)

### Rollback
- Set `ClusterMode=false` and `Address=redis:6379` to revert to single-node
- Remove Redis Exporter from docker-compose
- Delete K8s Redis resources
