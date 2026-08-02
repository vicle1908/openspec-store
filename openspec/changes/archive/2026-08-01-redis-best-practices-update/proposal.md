# Redis Best Practices Update

## Why

The Redis cluster hardening change (2026-07-21) delivered the foundational
cluster deployment, security, monitoring, and rate limiting. However, the
current implementation lacks several Redis 8.8 best practices that improve
reliability, observability, and performance:

1. **No RESP3 protocol mandate** — Code uses `Protocol: 3` but the spec
   doesn't enforce it. New services may default to RESP2, losing type-aware
   responses and zero-copy buffer benefits.

2. **No slowlog server-side config** — RM-005 monitors slowlog but the
   Redis nodes don't configure `slowlog-log-slower-than` or
   `slowlog-max-len`. Without server-side config, the slowlog is empty
   regardless of command duration.

3. **Incomplete connection pool hardening** — RV-006 mentions pool settings
   but doesn't mandate `PoolFIFO`, `MinRetryBackoff`, `MaxRetryBackoff`,
   or `ConnMaxIdleTime`. Default LIFO pool behavior causes uneven
   connection distribution.

4. **Basic health checks** — RC-003 uses `redis-cli ping` which only
   verifies the port is up. Should also verify `cluster_state:ok` to
   detect split-brain or degraded cluster state.

5. **No graceful shutdown procedure** — Rolling restarts and version
   upgrades lack documented Redis-specific steps (SIGTERM handling,
   AOF rewrite prevention, replica promotion order).

## What Changes

- **Spec updates**: Add RESP3 mandate to redis-cluster, slowlog config to
  redis-monitoring, connection pool hardening to redis-verification,
  enhanced health checks to redis-cluster
- **Code updates**: Add `PoolFIFO: true`, explicit retry backoff to
  catalog-service adapter
- **Deploy updates**: Add `--slowlog-log-slower-than 10000` and
  `--slowlog-max-len 128` to cluster compose command args
- **Doc updates**: Add graceful shutdown procedure to Redis runbook

## Capabilities

### Modified Capabilities

- `redis-cluster`: Enhanced health checks (CLUSTER INFO verification),
  RESP3 protocol mandate, graceful shutdown documentation
- `redis-monitoring`: Slowlog server-side configuration
- `redis-verification`: Connection pool hardening requirements,
  enhanced health check verification

### Non-Goals

- Client-side caching (CLIENT TRACKING) — go-redis v9 doesn't natively
  support this; defer to when a long-TTL cache use case arises
- LATENCY MONITOR — useful for deep debugging but not critical for
  current workloads; document as future improvement
- Redis 8.8 Array data structure — no current use case; document as
  future capability
- Streams NACKing — Kafka handles event streaming; not needed

## Impact

### Affected Code
- `services/catalog-service/internal/adapters/redis/adapter.go` — PoolFIFO, retry backoff
- `services/catalog-service/internal/config/config.go` — new pool config fields

### Affected Infrastructure
- `deploy/docker-compose.redis-cluster.yaml` — slowlog config args

### Affected Docs
- `docs/redis-architecture.md` — update best practice alignment
- `docs/runbooks/redis.md` — add graceful shutdown procedure

### Compatibility
- **Non-breaking** — all changes are additive config/code enhancements
- Existing behavior preserved; new settings improve reliability
