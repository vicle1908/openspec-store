# Consolidate Observability Docker Deployment

## Why

The TDT ecosystem's observability deployment is fragmented across three repos with overlapping concerns:

1. **agent-core/compose.yaml** owns the full observability stack (Langfuse 4.11, MLflow 3.15, MinIO, OTel Collector, ClickHouse, Redis, Postgres) — but agent-core is an agent framework, not an operations platform. The OTel Collector only exports to `debug` (traces go nowhere). Langfuse and MLflow are deployed but not connected to the scheduler's OTel pipeline.

2. **tdt-scheduler/compose.yaml** joins `agent-core-local_default` network and points `OTEL_OTEL_COLLECTOR_ENDPOINT` at `http://otel-collector:4317` — but that collector only emits to debug.

3. **tdt-observability** has launchd plists for health-poller and log-aggregator, a standalone `run-lgtm.sh` script (v0.28.0), Grafana dashboards with localhost datasources, and no Dockerfile or compose.yaml. It has no Docker deployment story.

4. **No single `docker compose up`** brings up the full observability stack. The LGTM stack (Grafana + Loki + Tempo + Prometheus) is never actually running — the `run-lgtm.sh` script exists but nothing sends data to it.

5. **Image versions are misaligned**: tdt-observability uses LGTM v0.28.0, go-microservices uses v0.29.0.

The result: operators must check multiple sources (Docker containers, launchd processes, DuckDB files) to understand system health. Traces are collected by the scheduler but discarded by the collector. The Grafana dashboards exist but have no data.

## What Changes

### Ownership Transfer

Move observability stack ownership from agent-core to tdt-observability:

| Component | Current Owner | New Owner |
|-----------|--------------|-----------|
| LGTM stack (Grafana, Loki, Tempo, Prometheus) | tdt-observability (script only) | tdt-observability (Docker Compose) |
| OTel Collector | agent-core (debug-only) | tdt-observability (routes to LGTM) |
| Langfuse stack | agent-core | tdt-observability (overlay) |
| MLflow stack | agent-core | tdt-observability (overlay) |
| MinIO | agent-core | tdt-observability (overlay) |
| Health poller | tdt-observability (launchd) | tdt-observability (Docker) |
| Log aggregator | tdt-observability (launchd) | tdt-observability (Docker) |
| Grafana dashboards | tdt-observability | tdt-observability (updated provisioning) |
| PostgreSQL (shared) | agent-core | tdt-observability (base) |
| agent-core app | agent-core | agent-core (unchanged) |
| tdt-scheduler | tdt-scheduler | tdt-scheduler (network updated) |

### File Changes by Repo

**tdt-observability (primary):**
- Create `deploy/docker-compose.yaml` — base: LGTM + Postgres
- Create `deploy/docker-compose.services.yaml` — TDT services overlay (scheduler, agent-core, health-poller, log-collector)
- Create `deploy/docker-compose.langfuse.yaml` — Langfuse overlay
- Create `deploy/docker-compose.mlflow.yaml` — MLflow overlay
- Create `deploy/tools.env` — pinned image versions (LGTM v0.29.0, Langfuse 4.11.0, MLflow v3.15.1)
- Create `deploy/otel-collector-config.yaml` — fan-out collector (for Langfuse/MLflow routing)
- Create `Dockerfile` — tdt-observability image (health-poller + log-collector)
- Update `grafana/provisioning/datasources/datasources.yaml` — remove (use LGTM built-in)
- Update `grafana/dashboards/tdt-service-health.json` — change datasource UID from `mimir` to `prometheus` (LGTM built-in)
- Remove `deploy/lgtm/run-lgtm.sh` — replaced by Docker Compose
- Remove `deploy/launchd/*.plist` — replaced by Docker services

**agent-core:**
- Remove from `compose.yaml`: langfuse-clickhouse, langfuse-postgres, langfuse-redis, minio, minio-init, langfuse-web, langfuse-worker, mlflow-postgres, mlflow-server, otel-collector (10 services + 5 volumes)
- Remove `otel-collector-config.yaml` — moved to tdt-observability
- Update `config.yaml.example` — change `otel_collector_endpoint` default from `http://otel-collector:4317` to `http://otel-lgtm:4317`

**tdt-scheduler:**
- Update `compose.yaml` — change network from `agent-core-local_default` to `tdt-observability` (external)
- Update `compose.yaml` — change `OTEL_OTEL_COLLECTOR_ENDPOINT` from `http://otel-collector:4317` to `http://otel-lgtm:4317`

### Non-Goals

- Modifying agent-core application source code (only compose/config changes)
- Modifying tdt-scheduler application source code (only compose/env changes)
- Implementing new observability features (traces, metrics, logs are existing)
- Kubernetes or cloud deployment (Docker Compose only for now)
- Changing the tdt-observability Python source code
- Modifying the agent-observability-contract spec (already archived)

## Capabilities

### New Capabilities

None. This is a deployment restructuring, not a feature change.

### Modified Capabilities

None. The `skip_specs: true` flag is set — no OpenSpec capability specifications are modified.

## Impact

### Repos Touched

| Repo | Change Type | Risk |
|------|------------|------|
| tdt-observability | New Docker files, remove legacy | LOW — additive, old files replaced |
| agent-core | Remove 10 services from compose | MEDIUM — compose structure changes |
| tdt-scheduler | Update network + env vars | LOW — two-line change |

### Breaking Changes

- `agent-core-local_default` network no longer contains Langfuse/MLflow/OTel — services must use `tdt-observability` network
- `http://otel-collector:4317` no longer resolves — must use `http://otel-lgtm:4317`
- LaunchAgents for health-poller and log-aggregator must be unloaded before Docker services start
- `run-lgtm.sh` is removed — use `docker compose -f deploy/docker-compose.yaml up -d` instead

### Backward Compatibility

- agent-core `config.yaml` users must update `otel_collector_endpoint` (old value deprecated, not removed)
- tdt-scheduler compose must be started with the tdt-observability stack running first
- The `tdt-scheduler-verification.override.yaml` must be updated to use the new network

### Data Migration

- DuckDB files (`health.duckdb`, `events.duckdb`) remain in `~/.tdt/observability/` — Docker volumes mount them
- Langfuse data moves from agent-core volumes to tdt-observability volumes — fresh start recommended (no production data in local dev)
- MLflow data moves similarly — fresh start recommended

## Relationship to Existing Changes

This change is **complementary** to the active `local-compose-observability-deployment` change:
- That change documents verification procedures and warning classification
- This change restructures the actual deployment files
- The verification procedures from that change apply to the new deployment structure
- No conflict — different scope (documentation vs implementation)

## Deployment Verification

After implementation:
1. `docker compose -f deploy/docker-compose.yaml up -d` — LGTM + Postgres start
2. `curl http://localhost:3000/api/health` — Grafana healthy
3. `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.services.yaml up -d` — services join
4. `curl http://localhost:9100/scheduler/health` — scheduler healthy
5. Traces visible in Grafana → Explore → Tempo
6. Logs visible in Grafana → Explore → Loki
7. Metrics visible in Grafana → Prometheus datasource
