# redis-cluster (delta)

## Purpose

Enhanced Redis 8.8 cluster with RESP3 protocol mandate, cluster-state health checks, and graceful shutdown documentation.

## MODIFIED Requirements

### Requirement: RC-002: Cluster Configuration

Each Redis node SHALL be configured with the following settings per Redis cluster specification:
- `cluster-enabled yes` — activates cluster mode
- `cluster-config-file nodes-<port>.conf` — auto-managed cluster state file
- `cluster-node-timeout 5000` — 5 seconds before node considered failed
- `cluster-slave-validity-factor 0` — replicas always attempt failover
- `cluster-require-full-coverage yes` — cluster stops writes if slots uncovered
- `cluster-allow-reads-when-down no` — no reads when cluster is down
- `appendonly yes` — AOF persistence
- `appendfsync everysec` — fsync every second
- `maxmemory 256mb` — increased from 128mb for cluster overhead
- `maxmemory-policy allkeys-lru` — LRU eviction
- `slowlog-log-slower-than 10000` — log commands exceeding 10ms
- `slowlog-max-len 128` — retain 128 slowlog entries

#### Scenario: Cluster Config Applied

Given a Redis node with the cluster configuration
When the node starts
Then `cluster-enabled` shall be `yes`
And `cluster-node-timeout` shall be `5000`
And `cluster-slave-validity-factor` shall be `0`
And `appendonly` shall be `yes`
And `slowlog-log-slower-than` shall be `10000`
And `slowlog-max-len` shall be `128`

### Requirement: RC-003: Cluster Healthchecks

Each Redis node SHALL expose a healthcheck endpoint. Docker Compose healthchecks SHALL verify `cluster_state:ok` via `CLUSTER INFO`. Kubernetes probes SHALL use `exec` with `redis-cli CLUSTER INFO` to verify cluster state.

#### Scenario: Docker Compose Healthcheck

Given a Redis node in the cluster
When the healthcheck runs
Then `redis-cli -a $PASS cluster-info` shall report `cluster_state:ok`
And the container status shall be `healthy`

#### Scenario: Kubernetes Readiness Probe

Given a Redis pod in the StatefulSet
When the readiness probe runs
Then `exec redis-cli CLUSTER INFO` shall report `cluster_state:ok`
And the pod shall be marked as `Ready`

## ADDED Requirements

### Requirement: RC-011: RESP3 Protocol

All Redis clients SHALL use RESP3 protocol. The `Protocol` option SHALL be set to `3` in all cluster client options. RESP3 provides native type-aware responses, better error handling, and zero-copy buffer support.

#### Scenario: Client Uses RESP3

Given a Redis client with `Protocol: 3` configured
When connecting to the Redis cluster
Then the connection shall use RESP3 protocol
And responses shall use RESP3 type framing
And zero-copy buffer operations (`GetToBuffer`) shall work correctly

#### Scenario: RESP3 Default Enforced

Given the catalog-service Redis adapter
When the adapter constructs cluster options
Then `Protocol` shall be set to `3`
And the value shall be configurable via `CATALOG_REDIS_PROTOCOL` env var

### Requirement: RC-012: Cluster-State Health Checks

Docker Compose healthchecks SHALL verify `cluster_state:ok` via `CLUSTER INFO`, not just `PING`. Kubernetes probes SHALL use `exec` with `redis-cli CLUSTER INFO` to verify cluster state. Basic PING-only health checks are insufficient because a node in `fail` state still responds to PING.

#### Scenario: Cluster Degraded Detection

Given a Redis cluster with a failed master
When the healthcheck runs on a remaining node
Then `CLUSTER INFO` shall report `cluster_state:fail`
And the container shall be marked as `unhealthy`

#### Scenario: Split-Brain Detection

Given a Redis cluster with a network partition
When the healthcheck runs on an isolated node
Then `CLUSTER INFO` shall report `cluster_state:fail`
And the container shall be marked as `unhealthy`

### Requirement: RC-013: Graceful Shutdown

Redis nodes SHALL handle SIGTERM gracefully: complete in-flight commands, write AOF if enabled, and exit cleanly. The operational runbook SHALL document the rolling restart procedure including replica-first ordering and replication offset verification.

#### Scenario: SIGTERM Handling

Given a Redis node with AOF enabled
When SIGTERM is received
Then the node shall stop accepting new connections
And it shall complete in-flight commands
And it shall write the AOF file
And it shall exit with code 0

#### Scenario: Rolling Restart

Given a 6-node Redis cluster
When performing a rolling restart
Then replicas shall be restarted first (7004, 7005, 7006)
And each replica shall be verified as `master_link_status:up` before proceeding
Then masters shall be restarted with `CLUSTER FAILOVER` before each stop
And the cluster shall remain available throughout the procedure

#### Scenario: Post-Restart Verification

Given a Redis node that has been restarted
When the node rejoins the cluster
Then `CLUSTER INFO` shall report `cluster_state:ok`
And replication shall be `master_link_status:up`
And the operational runbook shall document this verification step
