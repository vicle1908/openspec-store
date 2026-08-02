# redis-monitoring

## Purpose

Observability for Redis cluster: metrics collection, Prometheus integration, Grafana dashboards, and alert rules.

## Current State

- Redis Exporter v1.86.0 pinned in `deploy/tools.env` but NOT deployed
- Latest available: v1.87.0 (released July 15, 2026)
- Prometheus already configured in `deploy/prometheus.yml` (scrapes OTel Collector and services)
- Grafana available via LGTM stack (`deploy/docker-compose.lgtm.yaml`)
- No Redis-specific metrics, dashboards, or alerts configured

## Dependencies

- Redis Exporter v1.87.0 (upgrade from v1.86.0, supports Valkey 9.x + Redis 8.x)
- Prometheus (already in LGTM stack)
- Grafana (already in LGTM stack)

## Requirements

### Requirement: RM-001: Redis Exporter Deployment

Redis Exporter v1.87.0 SHALL be deployed alongside the Redis cluster. It SHALL scrape metrics from Redis nodes and expose them on port 9121.

#### Scenario: Docker Compose Exporter
Given the Docker Compose topology
When `docker compose -f deploy/docker-compose.redis-cluster.yaml up -d` is executed
Then the `redis-exporter` container shall start with image `oliver006/redis_exporter:v1.87.0`
And it shall connect to `redis://redis-7001:6379`
And it shall expose `/metrics` on port 9121

#### Scenario: Single-Node Exporter
Given the current single-node Redis in `deploy/docker-compose.catalog-service.yaml`
When the exporter is added
Then it shall connect to `redis://redis:6379`
And it shall expose `/metrics` on port 9121

#### Scenario: Multi-Node Scraping
Given a 6-node Redis cluster
When the exporter starts
Then it shall scrape metrics from at least one master node
And it shall report cluster-level metrics (memory, connections, hit rate)

### Requirement: RM-002: Prometheus Integration

Redis metrics SHALL be scraped by Prometheus. The scrape configuration SHALL be added to `deploy/prometheus.yml`.

#### Scenario: Prometheus Scrape Config
Given the Prometheus configuration in `deploy/prometheus.yml`
When the `redis-exporter` job is added
Then it shall scrape `redis-exporter:9121/metrics`
And metrics shall be stored with 15-second resolution
And labels shall include `service: redis`

#### Scenario: Metrics Available
Given Prometheus scraping Redis Exporter
When querying `redis_memory_used_bytes`
Then the metric shall be available
And it shall report current memory usage per node

### Requirement: RM-003: Grafana Dashboard

A Redis dashboard SHALL be available in Grafana. The dashboard SHALL display: memory usage, connected clients, cache hit rate, operations per second, replication lag, and cluster state.

#### Scenario: Dashboard Import
Given the Grafana instance (via LGTM stack)
When the Redis dashboard is imported (ID 763 or custom)
Then it shall display real-time Redis metrics
And panels shall auto-refresh every 15 seconds

#### Scenario: Dashboard Panels
Given the Redis dashboard
When viewing the panels
Then memory usage shall show `used_memory_human` and `maxmemory_human`
And hit rate shall show `keyspace_hits / (hits + misses)`
And replication lag shall show `master_repl_offset - slave_offset`

### Requirement: RM-004: Alert Rules

Prometheus alert rules SHALL be configured for: RedisHighMemory (used/max > 85% for 5m), RedisReplicationLag (lag > 10MB for 5m), RedisLowHitRate (hit_rate < 90% for 10m), RedisClusterStateNotOk (cluster_state != 1 for 1m), RedisSlowCommands (slowlog_length > 0 for 5m).

#### Scenario: High Memory Alert
Given Redis memory usage at 90%
When the metric is reported for 5 minutes
Then the `RedisHighMemory` alert shall fire
And the alert shall be visible in Grafana

#### Scenario: Cluster State Alert
Given a Redis cluster with a failed master
When `cluster_state` becomes `fail`
Then the `RedisClusterStateNotOk` alert shall fire within 1 minute

### Requirement: RM-005: Slowlog Integration

Redis SLOWLOG SHALL be monitored. Slow commands (> 10ms) SHALL be logged and available for debugging. The exporter shall expose `redis_commands_duration_seconds` metrics.

#### Scenario: Slow Command Detection
Given a Redis node with slowlog enabled
When a command takes > 10ms
Then it shall be recorded in SLOWLOG
And the exporter shall expose the duration metric
