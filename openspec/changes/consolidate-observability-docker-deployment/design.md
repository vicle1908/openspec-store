# Design: Consolidate Observability Docker Deployment

## Context

The TDT ecosystem has three Docker Compose configurations that overlap:

- **agent-core/compose.yaml** (309 lines): 12 services — Postgres, app, Langfuse stack (6), MLflow stack (2), MinIO, OTel Collector. The OTel Collector config exports only to `debug`. No networks section (uses default `agent-core-local_default`).

- **tdt-scheduler/compose.yaml** (86 lines): 2 services — scheduler, postgres-backup. Joins `agent-core-local_default` as external network. Points `OTEL_OTEL_COLLECTOR_ENDPOINT=http://otel-collector:4317`.

- **tdt-observability**: No compose.yaml, no Dockerfile. Has launchd plists (macOS-only), `run-lgtm.sh` (v0.28.0), Grafana dashboards with localhost datasources.

The go-microservices repo has a proven pattern: `deploy/docker-compose.yaml` (base) + `deploy/docker-compose.lgtm.yaml` (overlay) + `deploy/tools.env` (pinned versions). The LGTM image (v0.29.0) bundles Grafana + Loki + Tempo + Prometheus + OTel Collector with pre-configured datasources and cross-linking.

## Goals / Non-Goals

**Goals:**
- Single `docker compose up` brings up the full observability stack
- tdt-observability owns all observability deployment files
- LGTM image replaces standalone OTel Collector (uses built-in collector)
- Langfuse/MLflow move to tdt-observability overlays (activated via `-f` flag)
- LaunchAgents replaced by Docker services
- Image versions aligned with go-microservices (LGTM v0.29.0)
- Grafana datasources use LGTM built-in provisioning (remove custom override)

**Non-Goals:**
- Modifying agent-core or tdt-scheduler application source code
- Kubernetes or cloud deployment (Docker Compose only)
- New observability features
- Modifying the agent-observability-contract spec

## Decisions

### Decision 1: LGTM Built-In vs Separate OTel Collector

**Choice**: Use LGTM's built-in OTel Collector for LGTM-only setup. Add a separate collector only when Langfuse/MLflow overlays are activated.

**Rationale**: The LGTM image bundles an OTel Collector that routes traces→Tempo, metrics→Prometheus, logs→Loki. Running a separate collector adds complexity with no benefit for the LGTM-only case. When Langfuse/MLflow are needed, a separate collector fans out to all backends.

**Divergence from go-microservices**: go-microservices runs its own separate collector (v0.158.0) on top of LGTM's built-in collector (v0.156.0). This is intentional for their production topology (agent→gateway). For TDT's local dev use case, the built-in collector is sufficient. The Langfuse/MLflow overlays add a separate collector only when fan-out is needed.

**Alternatives considered**:
- Always use separate collector: Simpler mental model, but adds a container and config for no benefit in the common case
- Use LGTM's built-in collector with custom config: Possible via volume mount, but the built-in config is correct and well-tested

**Architecture**:
```
LGTM-only (base):
  Services → LGTM :4317 (built-in collector) → Tempo/Loki/Prometheus

With Langfuse/MLflow overlay:
  Services → Separate Collector :4317 → LGTM :4318
                               → Langfuse (otlphttp)
                               → MLflow (otlphttp)
```

### Decision 2: Overlay Pattern vs Monolithic Compose

**Choice**: Layered overlays activated via `-f` flag, matching go-microservices pattern.

**Rationale**: Each overlay is independently activatable. Base stack (LGTM + Postgres) is always needed. Services overlay adds TDT services. Langfuse/MLflow are optional. This matches the proven go-microservices pattern.

**Alternatives considered**:
- Docker Compose profiles: Would require `--profile langfuse` syntax, less explicit than `-f` overlays
- Single monolithic compose: Simpler but can't selectively activate Langfuse/MLflow
- Docker Compose `include`: Requires Compose 2.20+, less portable

### Decision 3: Network Naming

**Choice**: External named network `tdt-observability` (not `agent-core-local_default`).

**Rationale**: Observability is the network owner. Services join it as external. The old `agent-core-local_default` network name couples tdt-scheduler to agent-core's project name.

**Migration**: tdt-scheduler changes `external: true, name: agent-core-local_default` → `external: true, name: tdt-observability`.

### Decision 4: Grafana Datasource Provisioning

**Choice**: Remove custom `datasources.yaml` override. Use LGTM built-in datasources.

**Rationale**: The LGTM image ships with pre-configured datasources (Prometheus, Tempo, Loki, Pyroscope) that are cross-linked (metrics→traces, traces→logs). The current `tdt-observability/grafana/provisioning/datasources/datasources.yaml` overrides these with localhost URLs — wrong for Docker.

**What changes**: Remove `grafana/provisioning/datasources/datasources.yaml`. Keep `grafana/provisioning/dashboards/dashboards.yaml` (points to custom dashboard JSON files). Update dashboard JSON datasource UIDs: `mimir` → `prometheus` (LGTM built-in Prometheus datasource uses uid `prometheus`). The `tempo` and `loki` UIDs already match.

### Decision 5: Health Poller and Log Collector as Docker Services

**Choice**: Package as Docker services in the services overlay, not standalone containers.

**Rationale**: They're part of the TDT observability stack. Running as Docker services means `docker compose up` brings everything up. The Dockerfile installs the tdt-observability package and runs the health-poller or log-collector as the command.

**Trade-off**: Launchd had `KeepAlive` and PID management. Docker Compose has `restart: unless-stopped` which provides equivalent behavior. The PID file management in the Python code becomes a no-op (process is always PID 1 in container).

**Health poller URL migration**: The default service URLs in `health_poller/__init__.py` use `http://localhost:8080/health` etc. Inside a Docker container, `localhost` refers to the container itself. Two options:
1. Volume-mount a config file at `~/.tdt/observability/config/config.yaml` with Docker-network URLs (e.g., `http://webhook-receiver:8080/health`)
2. Keep the health-poller on the host (via launchd) and only containerize the log-collector

**Chosen approach**: Option 1 — the health-poller config file (`~/.tdt/observability/config/config.yaml`) is mounted into the container. If the file doesn't exist, the health-poller falls back to defaults (which won't work in Docker). The task includes creating this config file with Docker-network service URLs.

### Decision 6: LGTM Version Alignment

**Choice**: Pin to v0.29.0 (matching go-microservices), not v0.28.0 (current tdt-observability).

**Rationale**: go-microservices has verified v0.29.0 for `linux/arm64`. Using the same version avoids divergence.

## Risks / Trade-offs

**[Risk] Launchd → Docker migration breaks health-poller/log-collector on macOS dev**
→ Mitigation: Docker Desktop runs on macOS. The health-poller and log-collector work identically in containers. The `~/.tdt/logs/` and `~/.tdt/observability/` directories are mounted as volumes.

**[Risk] Langfuse data loss during migration**
→ Mitigation: Local dev only — no production data. Fresh `docker compose up` creates new volumes. Old agent-core volumes can be pruned with explicit `docker volume rm` commands.

**[Risk] Port conflict: Grafana :3000 vs Langfuse :3000**
→ Mitigation: Langfuse web binds to `127.0.0.1:3001:3000` (host port 3001) when the Langfuse overlay is activated. Grafana remains on `:3000`. The LGTM base and Langfuse overlay can coexist.

**[Risk] tdt-scheduler fails to connect if tdt-observability stack isn't running**
→ Mitigation: Document dependency. The scheduler's `depends_on` can reference LGTM healthcheck. The scheduler already has graceful degradation when OTEL endpoint is unavailable.

**[Risk] Dashboard queries break after datasource UID change**
→ Mitigation: The current dashboards use `mimir` uid for the Prometheus datasource. The LGTM built-in uses `prometheus` uid. Task 2.3 updates the dashboard JSON to match. Verify panel queries after migration.

**[Risk] DuckDB lock contention between Docker health-poller and host processes**
→ Mitigation: If health-poller runs in Docker, it uses the same `~/.tdt/observability/health.duckdb` via volume mount. The existing retry/backoff logic in the retention module handles this.

## Migration Plan

### Phase 1: Foundation (tdt-observability only)
1. Create `deploy/docker-compose.yaml` (LGTM + Postgres)
2. Create `deploy/tools.env` (pinned versions)
3. Create `Dockerfile` (health-poller + log-collector image)
4. Remove `deploy/lgtm/run-lgtm.sh`
5. Remove `deploy/launchd/*.plist`
6. Verify: `docker compose up` → Grafana accessible, LGTM healthy

### Phase 2: Network Migration
1. Update `tdt-scheduler/compose.yaml` network to `tdt-observability`
2. Update `tdt-scheduler/compose.yaml` OTEL endpoint to `http://otel-lgtm:4317`
3. Create `deploy/docker-compose.services.yaml` (scheduler + agent-core + health-poller + log-collector)
4. Remove `tdt-scheduler/tdt-scheduler-verification.override.yaml` (update to new network)
5. Verify: scheduler starts, health endpoint responds, traces visible in Grafana

### Phase 3: Agent-Core Cleanup
1. Remove 10 services from `agent-core/compose.yaml` (Langfuse, MLflow, MinIO, OTel Collector)
2. Remove 5 named volumes from `agent-core/compose.yaml`
3. Remove `agent-core/otel-collector-config.yaml`
4. Update `agent-core/config.yaml.example` — change `otel_collector_endpoint` default
5. Verify: `agent-core/compose.yaml` starts with just Postgres + app

### Phase 4: Optional Backends
1. Create `deploy/docker-compose.langfuse.yaml` (Langfuse overlay) with `otel-collector` service
2. Create `deploy/docker-compose.mlflow.yaml` (MLflow overlay)
3. Create `deploy/otel-collector-config.yaml` (fan-out collector config)
4. Verify: `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.langfuse.yaml up` → Langfuse receives traces

### Rollback
Each phase is independently reversible:
- Phase 1: Remove tdt-observability deploy files, restore launchd plists
- Phase 2: Revert tdt-scheduler network to `agent-core-local_default`
- Phase 3: Restore agent-core/compose.yaml from git history
- Phase 4: Remove overlay files

## Open Questions

1. Should the tdt-scheduler `compose.yaml` keep its own `postgres-backup` service, or should backup be handled by the tdt-observability stack? (Currently scheduler has its own backup container.)
2. Should the verification override (`tdt-scheduler-verification.override.yaml`) be updated in this change or deferred to the `local-compose-observability-deployment` change?
