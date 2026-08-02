# redis-cluster

## Purpose

Redis 8.8 cluster deployment providing high availability, automatic failover, and horizontal scaling for the microservices platform.

## Current State

- Single Redis 8.8-alpine instance in `deploy/docker-compose.catalog-service.yaml`
- Container: `catalog-redis`, hostname: `redis`, port: `6379`
- Config: `--maxmemory 128mb`, `--maxmemory-policy allkeys-lru`, `--appendonly no`
- Healthcheck: `redis-cli ping`
- No cluster, no auth, no TLS, no persistence

## Dependencies

- Redis 8.8-alpine (pinned in `deploy/tools.env`)
- redis-exporter v1.86.0 (pinned, upgrade to v1.87.0 recommended)

## ADDED Requirements

### Requirement: RC-001: Cluster Topology

The Redis cluster SHALL consist of 6 nodes: 3 masters and 3 replicas. Each master SHALL own a subset of the 16,384 hash slots. Each replica SHALL be paired with exactly one master.

#### Scenario: Local Development Cluster
Given the Docker Compose topology
When `docker compose -f deploy/docker-compose.redis-cluster.yaml up -d` is executed
Then 6 Redis 8.8-alpine containers shall start
And the cluster shall be initialized with `redis-cli --cluster create`
And `cluster_state:ok` shall be reported

#### Scenario: Slot Distribution
Given a 6-node cluster with 3 masters
When the cluster is initialized
Then Master 1 shall own slots 0-5460
And Master 2 shall own slots 5461-10922
And Master 3 shall own slots 10923-16383

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

#### Scenario: Cluster Config Applied
Given a Redis node with the cluster configuration
When the node starts
Then `cluster-enabled` shall be `yes`
And `cluster-node-timeout` shall be `5000`
And `cluster-slave-validity-factor` shall be `0`
And `appendonly` shall be `yes`

### Requirement: RC-003: Cluster Healthchecks

Each Redis node SHALL expose a healthcheck endpoint. Docker Compose healthchecks SHALL use `redis-cli ping`. Kubernetes probes SHALL use `tcpSocket` on the Redis port.

#### Scenario: Docker Compose Healthcheck
Given a Redis node in the cluster
When the healthcheck runs
Then `redis-cli ping` shall return `PONG`
And the container status shall be `healthy`

#### Scenario: Kubernetes Readiness Probe
Given a Redis pod in the StatefulSet
When the readiness probe runs
Then `tcpSocket` on port 6379 shall succeed
And the pod shall be marked as `Ready`

### Requirement: RC-004: Cluster Bootstrap

The cluster SHALL be bootstrapped automatically. For Docker Compose, an init container shall run `redis-cli --cluster create`. For Kubernetes, an init container shall wait for all pods to be ready before creating the cluster.

#### Scenario: Docker Compose Bootstrap
Given 6 Redis containers are running
When the `redis-init` container starts
Then it shall wait 3 seconds for nodes to stabilize
And it shall run `redis-cli --cluster create` with `--cluster-replicas 1`
And it shall exit with code 0

#### Scenario: Kubernetes Bootstrap
Given 6 Redis pods are running
When the init container starts
Then it shall wait for all pods to be ready
And it shall run `redis-cli --cluster create` with `--cluster-replicas 1`
And it shall be idempotent (skip if cluster already exists)

### Requirement: RC-005: Persistence

Redis data SHALL be persisted using AOF with `appendfsync everysec`. For Kubernetes, each node SHALL have a PersistentVolumeClaim (20Gi) for data storage.

#### Scenario: AOF Persistence
Given a Redis node with AOF enabled
When a write operation completes
Then the write shall be logged to the AOF file
And the AOF shall be fsynced within 1 second

#### Scenario: Kubernetes PVC
Given a Redis pod in the StatefulSet
When the pod starts
Then it shall mount a PVC named `data-<pod-index>`
And the PVC shall have 20Gi of storage

### Requirement: RC-006: Hash Slot Distribution

Keys SHALL be distributed across slots using `CRC16(key) mod 16384`. The key pattern `catalog:quote:<productID>:<minuteEpoch>` SHALL be automatically distributed. The `CLUSTER KEYSLOT` command SHALL be used to verify slot assignment.

#### Scenario: Slot Assignment
Given a key `catalog:quote:prod-123:1721500000`
When `CLUSTER KEYSLOT catalog:quote:prod-123:1721500000` is executed
Then a slot number (0-16383) shall be returned
And the key shall be stored on the master owning that slot

#### Scenario: Key Distribution
Given 1000 product quotes
When all keys are stored
Then keys shall be distributed across all 3 masters
And no single master shall hold > 50% of keys (ideal: ~33% each)

### Requirement: RC-007: Hash Tag Strategy

Hash tags SHALL be used to force related keys to the same slot. The pattern `{<entity>:<id>}` SHALL be used for multi-key operations. Current key `catalog:quote:<productID>:<minuteEpoch>` does NOT use hash tags (each key is independent).

#### Scenario: Hash Tag Colocation
Given keys `user:{123}:profile` and `user:{123}:orders`
When both keys are stored
Then both shall land on the same slot (slot = CRC16("123") mod 16384)
And MGET/transactions shall work across both keys

#### Scenario: Current Key Pattern (No Hash Tag)
Given key `catalog:quote:prod-123:1721500000`
When stored in cluster
Then the slot is determined by CRC16 of the full key
And each quote is independent (no hash tag needed)

### Requirement: RC-008: SCAN Across Masters

SCAN-based invalidation SHALL query all master nodes. The adapter SHALL get master list via `CLUSTER NODES`, then SCAN each master.

#### Scenario: SCAN Across Masters
Given cached quotes for product `prod-123` spread across multiple masters
When `InvalidateByProduct("prod-123")` is called
Then the adapter shall get master list from `CLUSTER NODES`
And it shall SCAN each master for `catalog:quote:prod-123:*`
And it shall DEL all matching keys on each master

#### Scenario: SCAN with COUNT
Given a SCAN operation
When scanning a master node
Then it shall use `COUNT 100` per iteration
And it shall continue until cursor returns 0

### Requirement: RC-009: Resharding Support

The cluster SHALL support online resharding without downtime. Hash slots SHALL be movable between masters using `redis-cli --cluster reshard`.

#### Scenario: Add Node and Reshard
Given a running 6-node cluster
When a new master node (7007) is added
Then `redis-cli --cluster add-node 7007:7007 7001:7001` shall succeed
And slots can be moved from existing masters to the new node
And the cluster shall remain available during resharding

#### Scenario: Remove Node
Given a running 6-node cluster
When a master node is removed
Then all its slots must be resharded to other masters first
And `redis-cli --cluster del-node <node-id>` shall succeed
And the cluster shall remain available

### Requirement: RC-010: Backward Compatibility

The existing single-node deployment in `deploy/docker-compose.catalog-service.yaml` SHALL continue to work. The cluster deployment SHALL be in a separate file. Services SHALL use environment variables to select between single-node and cluster modes.

#### Scenario: Single-Node Mode
Given `CATALOG_REDIS_CLUSTER_MODE=false` and `CATALOG_REDIS_ADDRESS=redis:6379`
When the catalog-service starts
Then it shall connect to the single Redis node
And behavior shall be identical to the current implementation

#### Scenario: Cluster Mode
Given `CATALOG_REDIS_CLUSTER_MODE=true` and `CATALOG_REDIS_ADDRS=redis-7001:6379,...`
When the catalog-service starts
Then it shall connect to the Redis cluster
And commands shall be automatically routed
