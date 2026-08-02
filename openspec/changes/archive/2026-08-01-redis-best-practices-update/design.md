# Design: Redis Best Practices Update

## Context

The Redis cluster hardening change (2026-07-21) delivered cluster deployment,
security, monitoring, and rate limiting. This change closes the remaining
best-practice gaps identified during the Redis architecture audit.

## Goals

1. Mandate RESP3 protocol across all Redis clients
2. Configure server-side slowlog for production observability
3. Harden connection pool settings with explicit values
4. Enhance health checks to verify cluster state (not just PING)
5. Document graceful shutdown and rolling restart procedures

## Non-Goals

- Client-side caching (CLIENT TRACKING) — no go-redis v9 native support
- LATENCY MONITOR — documented as future improvement
- Redis 8.8 Array data structure — no current use case
- Streams NACKing — Kafka handles event streaming

---

## Section 1: RESP3 Protocol Mandate

### Current

| Setting | Value | Source |
|---------|-------|--------|
| `Protocol` | 3 | `config.go` default, `adapter.go` passes to ClusterOptions |

The code defaults to RESP3 but the spec (`redis-cluster RC-002`) doesn't
mention it. A new service could connect with RESP2 and lose type-aware
responses.

### Proposed

Add RESP3 as a mandatory requirement in `redis-cluster` spec.

| Requirement | Text |
|-------------|------|
| RC-011 | All Redis clients SHALL use RESP3 protocol (Protocol=3). The `Protocol` option SHALL be set to `3` in all cluster options. |

### Why

RESP3 provides:
- Native type-aware responses (no type-mapping overhead)
- Better error handling (typed error responses)
- More efficient serialization for complex types
- Zero-copy buffer support (`GetToBuffer`)

---

## Section 2: Slowlog Server-Side Configuration

### Current

| Setting | Value | Source |
|---------|-------|--------|
| `slowlog-log-slower-than` | 10000 (10ms) | Redis default |
| `slowlog-max-len` | 128 | Redis default |
| Monitoring | RM-005 exists | Spec only |

The Redis defaults happen to be reasonable (10ms threshold, 128 entries),
but they're not explicitly configured in the compose file. If someone
changes the Redis config, the slowlog could silently disappear.

### Proposed

Add explicit slowlog config to cluster compose and monitoring spec.

| Config | Value | Rationale |
|--------|-------|-----------|
| `--slowlog-log-slower-than` | 10000 | Log commands >10ms (matches RM-005) |
| `--slowlog-max-len` | 128 | Retain 128 entries (bounded memory) |

Add to `redis-monitoring` spec:

| Requirement | Text |
|-------------|------|
| RM-006 | Redis nodes SHALL configure `slowlog-log-slower-than 10000` (10ms) and `slowlog-max-len 128` explicitly. The slowlog configuration SHALL NOT rely on Redis defaults. |

### Why

Explicit configuration prevents silent degradation. If a Redis upgrade
changes defaults, our slowlog continues to work.

---

## Section 3: Connection Pool Hardening

### Current

| Setting | Value | Source |
|---------|-------|--------|
| `PoolSize` | 0 (10 x GOMAXPROCS) | go-redis default |
| `MinIdleConns` | 10 | Config default |
| `ConnMaxIdleTime` | 5m | Config default |
| `ConnMaxLifetime` | 10m | Config default |
| `PoolFIFO` | false (LIFO) | go-redis default |
| `MinRetryBackoff` | 8ms | go-redis default |
| `MaxRetryBackoff` | 512ms | go-redis default |

LIFO pool behavior causes the same connections to be reused while others
idle. Under burst traffic, this creates connection imbalance.

### Proposed

| Setting | Current | Proposed | Why |
|---------|---------|----------|-----|
| `PoolFIFO` | false (LIFO) | true (FIFO) | Even connection distribution; prevents hot-connection exhaustion |
| `MinRetryBackoff` | 8ms (implicit) | 8ms (explicit) | Document the default; prevent surprises on upgrade |
| `MaxRetryBackoff` | 512ms (implicit) | 512ms (explicit) | Document the default; prevent surprises on upgrade |

Add to `redis-verification` spec:

| Requirement | Text |
|-------------|------|
| RV-012 | Redis clients SHALL configure `PoolFIFO: true` for even connection distribution. Retry backoff SHALL be explicitly configured: `MinRetryBackoff: 8ms`, `MaxRetryBackoff: 512ms`. |

### Why

- FIFO pool prevents LIFO's "hot connection" problem where a few connections
  handle most traffic while others idle and get reaped
- Explicit backoff prevents surprise behavior if go-redis changes defaults

---

## Section 4: Enhanced Health Checks

### Current

| Check | Command | What it verifies |
|-------|---------|-----------------|
| Docker Compose | `redis-cli ping` | Port is open, Redis is responding |
| Kubernetes | `tcpSocket` on 6379 | Port is open |

Neither verifies cluster state. A node could be in `fail` state but still
respond to PING.

### Proposed

| Check | Command | What it verifies |
|-------|---------|-----------------|
| Docker Compose | `redis-cli -a $PASS cluster-info \| grep cluster_state:ok` | Cluster is healthy |
| Kubernetes | `tcpSocket` + custom exec probe | Port + cluster state |

Add to `redis-cluster` spec:

| Requirement | Text |
|-------------|------|
| RC-012 | Docker Compose healthchecks SHALL verify `cluster_state:ok` via `CLUSTER INFO`, not just `PING`. Kubernetes probes SHALL use `exec` with `redis-cli CLUSTER INFO` to verify cluster state. |

### Why

PING only confirms the Redis process is alive. A node in `fail` state
or with uncovered slots still responds to PING. Cluster-state verification
catches split-brain and degraded states.

---

## Section 5: Graceful Shutdown

### Current

No documented procedure for Redis graceful shutdown during rolling restarts.

### Proposed

Add to `docs/runbooks/redis.md`:

**Graceful Shutdown Procedure:**

1. **Pre-shutdown**: Verify cluster is healthy (`CLUSTER INFO` shows `cluster_state:ok`)
2. **On replicas**: Stop replica first (`docker stop redis-<replica>`)
3. **On masters**: Before stopping, verify replica is caught up:
   ```
   redis-cli -p <master> INFO replication | grep master_repl_offset
   redis-cli -p <replica> INFO replication | grep slave_repl_offset
   ```
4. **SIGTERM**: Redis handles SIGTERM by:
   - Stopping accepting new connections
   - Completing in-flight commands
   - Writing AOF (if `appendonly yes`)
   - Exiting cleanly
5. **On restart**: Redis reads AOF on startup, rejoins cluster automatically
6. **Verification**: After restart, verify `cluster_state:ok` and replication status

Add to `redis-cluster` spec:

| Requirement | Text |
|-------------|------|
| RC-013 | Redis nodes SHALL handle SIGTERM gracefully: complete in-flight commands, write AOF, and exit cleanly. The operational runbook SHALL document the rolling restart procedure including replica-first ordering and replication offset verification. |

### Why

Without documented procedures, operators may use `SIGKILL` which can
corrupt AOF files or cause unnecessary full resyncs.

---

## Section 6: Documentation Updates

### docs/redis-architecture.md

Update the "Best Practice Alignment" section:

| Area | Before | After |
|------|--------|-------|
| RESP3 protocol | Good (code uses it, spec doesn't mandate) | Excellent (RC-011 mandates) |
| Slowlog config | Good (relies on defaults) | Excellent (RM-006 explicit) |
| Connection pool | Good (LIFO default) | Excellent (FIFO + explicit backoff) |
| Health checks | Good (PING only) | Excellent (CLUSTER INFO) |
| Graceful shutdown | Missing | Excellent (RC-013 + runbook) |

### docs/runbooks/redis.md

Add new sections:
- "Graceful Shutdown" under Maintenance Procedures
- "Rolling Restart" with replica-first ordering
- "Version Upgrade" with SIGTERM handling

---

## Affected Specs

| Spec | Delta Type | Requirements |
|------|-----------|-------------|
| redis-cluster | MODIFIED | RC-002 (add slowlog args), RC-003 (enhanced healthcheck) |
| redis-cluster | ADDED | RC-011 (RESP3 mandate), RC-012 (cluster healthcheck), RC-013 (graceful shutdown) |
| redis-monitoring | MODIFIED | RM-005 (add slowlog config), RM-006 (new: explicit slowlog) |
| redis-verification | MODIFIED | RV-006 (add pool hardening), RV-012 (new: FIFO + backoff) |
| redis-security | UNCHANGED | — |
| redis-rate-limiter | UNCHANGED | — |
