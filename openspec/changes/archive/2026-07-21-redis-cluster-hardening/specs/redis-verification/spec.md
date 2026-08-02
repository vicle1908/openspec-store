# redis-verification

## Purpose

Verification strategies for Redis cluster implementation: pre-deployment validation, post-deployment verification, failover testing, sharding verification, and operational procedures.

## ADDED Requirements

### Requirement: RV-001: Pre-Deployment Verification

Before deploying Redis cluster, the following checks SHALL be performed:
- Cluster configuration validated (all 6 nodes start)
- Healthchecks pass for all nodes
- Cluster bootstrap completes successfully
- `cluster_state:ok` reported
- All 16,384 slots covered

#### Scenario: Local Cluster Validation
Given `deploy/docker-compose.redis-cluster.yaml`
When `docker compose -f deploy/docker-compose.redis-cluster.yaml up -d` is executed
Then all 6 containers shall start
And `redis-cli --cluster check redis-7001:6379` shall report no errors
And `cluster_state:ok` shall be returned by `CLUSTER INFO`

#### Scenario: Slot Coverage
Given a running Redis cluster
When `redis-cli --cluster check redis-7001:6379` is executed
Then all 16384 slots shall be assigned
And all slots shall be in `ok` state
And no slots shall be in `fail` or `pfail` state

### Requirement: RV-002: Post-Deployment Verification

After deploying Redis cluster, the following SHALL be verified:
- Application can connect to cluster
- Cache operations work (GET/SET/DELETE)
- Invalidation works across masters
- Monitoring metrics are available
- Alerts are configured

#### Scenario: Application Connectivity
Given the catalog-service configured with `ClusterMode=true`
When the service starts
Then `Ping(ctx)` shall return `nil`
And `Get(ctx, productID, minuteEpoch)` shall return `ErrCacheMiss` for new keys
And `Set(ctx, productID, minuteEpoch, quote, ttl)` shall succeed

#### Scenario: Cache Operations
Given a running Redis cluster
When `SET catalog:quote:prod-123:1721500000 <value>` is executed
Then the key shall be stored on the correct slot
And `GET catalog:quote:prod-123:1721500000` shall return the value
And `DEL catalog:quote:prod-123:1721500000` shall delete the key

#### Scenario: Invalidation Across Masters
Given cached quotes for product `prod-123` on multiple masters
When `InvalidateByProduct("prod-123")` is called
Then all matching keys shall be deleted from all masters
And subsequent `Get` calls shall return `ErrCacheMiss`

#### Scenario: Monitoring Metrics
Given Redis Exporter deployed
When `curl http://localhost:9121/metrics` is executed
Then `redis_memory_used_bytes` shall be available
And `redis_connected_clients` shall be available
And `redis_keyspace_hits_total` shall be available

### Requirement: RV-003: Failover Testing

Failover SHALL be tested by simulating master failure. The following scenarios SHALL be validated:
- Master crash triggers automatic failover
- Replica promoted to master within `cluster-node-timeout` (5s)
- Application continues serving requests
- No data loss for acknowledged writes

#### Scenario: Master Crash Failover
Given a running Redis cluster with 3 masters
When `redis-cli -p 7001 DEBUG SEGFAULT` is executed (simulates crash)
Then the master on port 7001 shall become unavailable
And within 5-15 seconds, its replica shall be promoted
And `cluster_state:ok` shall be restored
And the application shall continue serving requests

#### Scenario: Master Debug Sleep
Given a running Redis cluster
When `redis-cli -p 7001 DEBUG sleep 30` is executed (simulates unavailability)
Then the master shall be unreachable for 30 seconds
And the replica shall be promoted after `cluster-node-timeout`
And after DEBUG sleep ends, the old master shall rejoin as replica

#### Scenario: Application Resilience During Failover
Given the catalog-service connected to Redis cluster
When a master node crashes
Then the adapter shall handle `MOVED` redirections
And cache operations shall continue (possibly with increased latency)
And no `ErrCacheOutage` shall be returned to the application

### Requirement: RV-004: Sharding Verification

Sharding SHALL be verified to ensure proper key distribution:
- Keys are distributed across all masters
- No single master holds disproportionate load
- Hash tags work correctly for multi-key operations
- Resharding works without downtime

#### Scenario: Key Distribution Verification
Given 1000 product quotes stored in cluster
When `CLUSTER KEYSLOT` is checked for each key
Then keys shall be distributed across all 3 masters
And no master shall hold > 50% of keys
And the distribution shall be roughly equal (~33% each)

#### Scenario: Hash Slot Assignment
Given a key `catalog:quote:prod-123:1721500000`
When `CLUSTER KEYSLOT catalog:quote:prod-123:1721500000` is executed
Then a slot number (0-16383) shall be returned
And `CLUSTER NODES` shall show which master owns that slot

#### Scenario: Hash Tag Colocation
Given keys `user:{123}:profile` and `user:{123}:orders`
When `CLUSTER KEYSLOT` is checked for both keys
Then both keys shall return the same slot number
And MGET across both keys shall succeed (no CROSSSLOT error)

#### Scenario: CROSSSLOT Error Detection
Given keys on different slots
When MGET is executed across both keys
Then `CROSSSLOT keys in request don't hash to the same slot` shall be returned
And the application shall handle this error gracefully

#### Scenario: Resharding Without Downtime
Given a running 6-node cluster
When slots are moved from master 7001 to new master 7007
Then the cluster shall remain available during resharding
And `MOVED` redirections shall be sent to clients
And clients shall update their slot maps automatically

#### Scenario: Slot Rebalancing
Given a cluster with uneven slot distribution
When `redis-cli --cluster rebalance 7001:7001` is executed
Then slots shall be redistributed evenly across masters
And the cluster shall remain available during rebalancing

### Requirement: RV-005: Security Verification

Security configuration SHALL be verified:
- ACL users can authenticate
- Unauthorized access is denied
- TLS connections work
- Dangerous commands are blocked

#### Scenario: ACL Authentication
Given the `catalog-svc` ACL user configured
When the catalog-service authenticates with username/password
Then the connection shall succeed
And the service shall only access `catalog:quote:*` keys

#### Scenario: ACL Unauthorized Access
Given the `catalog-svc` ACL user
When attempting to access `notification:*` keys
Then the access shall be denied
And `ERR authorization denied` shall be returned

#### Scenario: Dangerous Commands Blocked
Given Redis with `rename-command FLUSHALL ""`
When `FLUSHALL` is executed
Then `ERR unknown command 'FLUSHALL'` shall be returned
And no data shall be deleted

### Requirement: RV-006: Performance Verification

Performance SHALL be verified under load:
- Cache hit rate > 90% for repeated queries
- p99 latency < 50ms for cache operations
- Connection pool handles concurrent requests
- No connection leaks under sustained load

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
Given the adapter with `PoolSize=50`, `MinIdleConns=10`
When 100 concurrent requests are executed
Then the pool shall not exhaust connections
And `redis_connected_clients` shall remain stable

### Requirement: RV-007: Operational Scripts

Operational scripts SHALL be provided for common tasks:
- `scripts/redis-cluster-healthcheck.sh` — check cluster health
- `scripts/redis-cluster-failover-test.sh` — test failover
- `scripts/redis-cache-purge.sh` — purge cache keys
- `scripts/redis-audit.sh` — audit ACL configuration

#### Scenario: Healthcheck Script
Given the `scripts/redis-cluster-healthcheck.sh` script
When executed against a running cluster
Then it shall check all 6 nodes
And it shall report `cluster_state:ok`
And it shall report memory usage per node
And it shall exit with code 0 on success

#### Scenario: Failover Test Script
Given the `scripts/redis-cluster-failover-test.sh` script
When executed against a running cluster
Then it shall identify a master node
And it shall execute `DEBUG SEGFAULT` on that master
And it shall wait for failover to complete
And it shall verify `cluster_state:ok` is restored
And it shall report failover duration

#### Scenario: Cache Purge Script
Given the `scripts/redis-cache-purge.sh` script
When executed with `--pattern 'catalog:quote:*'`
Then it shall SCAN all masters for matching keys
And it shall DEL all matching keys
And it shall report number of keys deleted

### Requirement: RV-008: Monitoring Verification

Monitoring SHALL be verified:
- Redis Exporter metrics are scraped
- Grafana dashboard displays data
- Alert rules fire correctly
- Alert routing works

#### Scenario: Metrics Scraping
Given Prometheus scraping `redis-exporter:9121/metrics`
When querying `redis_memory_used_bytes`
Then the metric shall be available
And it shall report non-zero value

#### Scenario: Grafana Dashboard
Given Grafana with Redis dashboard imported
When viewing the dashboard
Then memory panel shall display current usage
And hit rate panel shall display ratio
And connections panel shall display count

#### Scenario: Alert Firing
Given `RedisHighMemory` alert configured
When memory usage exceeds 85% for 5 minutes
Then the alert shall fire
And it shall be visible in Grafana Alerting

### Requirement: RV-009: Bug Investigation Procedures

When issues are detected, the following investigation SHALL be performed:
- Check Redis cluster state (`CLUSTER INFO`, `CLUSTER NODES`)
- Check SLOWLOG for slow commands
- Check memory usage and fragmentation
- Check connection count and pool status
- Check replication lag

#### Scenario: Slow Command Investigation
Given reports of slow cache operations
When `redis-cli SLOWLOG GET 10` is executed
Then slow commands shall be listed
And each entry shall show command, duration, timestamp

#### Scenario: Memory Investigation
Given reports of high memory usage
When `redis-cli INFO memory` is executed
Then `used_memory_human` shall be reported
And `mem_fragmentation_ratio` shall be checked
And `maxmemory_human` shall be compared to usage

#### Scenario: Connection Investigation
Given reports of connection issues
When `redis-cli INFO clients` is executed
Then `connected_clients` shall be reported
And `blocked_clients` shall be checked
And `client_longest_output_list` shall be checked

### Requirement: RV-010: Rollback Procedures

If issues occur, the following rollback SHALL be possible:
- Revert to single-node Redis (set `ClusterMode=false`)
- Remove cluster deployment
- Restore from AOF backup

#### Scenario: Rollback to Single-Node
Given issues with Redis cluster
When `CATALOG_REDIS_CLUSTER_MODE=false` is set
And `CATALOG_REDIS_ADDRESS=redis:6379` is set
Then the catalog-service shall connect to single-node Redis
And behavior shall be identical to pre-cluster implementation

#### Scenario: Rollback Deployment
Given issues with cluster deployment
When `docker compose -f deploy/docker-compose.redis-cluster.yaml down -v` is executed
Then all cluster containers shall be removed
And the original single-node Redis in `docker-compose.catalog-service.yaml` shall be used

### Requirement: RV-011: Real Operation Triggers

Real operations SHALL be triggered by specific conditions:
- Cache hit rate < 90% for 10 minutes → investigate cache invalidation
- Memory usage > 85% for 5 minutes → scale or evict
- Replication lag > 10MB for 5 minutes → investigate network
- Cluster state != ok for 1 minute → critical incident

#### Scenario: Cache Hit Rate Trigger
Given monitoring metrics
When cache hit rate drops below 90% for 10 minutes
Then an alert shall fire
And the on-call engineer shall investigate
And the investigation SHALL check: invalidation frequency, TTL settings, key distribution

#### Scenario: Memory Trigger
Given monitoring metrics
When memory usage exceeds 85% for 5 minutes
Then an alert shall fire
And the on-call engineer shall investigate
And the investigation SHALL check: key count, value sizes, eviction rate

#### Scenario: Cluster State Trigger
Given monitoring metrics
When `cluster_state` is not `ok` for 1 minute
Then a critical alert shall fire
And the on-call engineer shall investigate immediately
And the investigation SHALL check: node status, slot coverage, network connectivity
