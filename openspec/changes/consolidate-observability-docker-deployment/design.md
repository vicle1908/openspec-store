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

**Critical constraint**: When the Langfuse overlay is activated, the separate OTel Collector MUST NOT block LGTM tracing. The collector uses `depends_on: langfuse-web: condition: service_started` (not `service_healthy`) so it can buffer while Langfuse initializes. LGTM traces continue via the base stack's built-in collector until the separate collector is ready.

**Alternatives considered**:
- Always use separate collector: Simpler mental model, but adds a container and config for no benefit in the common case
- Use LGTM's built-in collector with custom config: Possible via volume mount, but the built-in config is correct and well-tested

**Architecture**:
```
LGTM-only (base):
  Services → LGTM :4317 (built-in collector, internal to Docker network) → Tempo/Loki/Prometheus
  Note: 4317/4318 are NOT published to host — only accessible from Docker network

With Langfuse/MLflow overlay:
  Services → LGTM :4317 (built-in) → LGTM backends (always works)
             Separate Collector :4317 (published to host 127.0.0.1) → LGTM :4318 + Langfuse + MLflow
             (separate collector starts async via service_started, doesn't block base)
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

**Network creation**: The `tdt-observability` network must be created before any service starts. Task 1.2 includes `docker network create tdt-observability` as a prerequisite.

### Decision 4: Grafana Datasource Provisioning

**Choice**: Remove custom `datasources.yaml` override. Use LGTM built-in datasources.

**Rationale**: The LGTM image ships with pre-configured datasources (Prometheus uid: `prometheus`, Tempo uid: `tempo`, Loki uid: `loki`, Pyroscope uid: `pyroscope`) that are cross-linked (metrics→traces, traces→logs). The current `tdt-observability/grafana/provisioning/datasources/datasources.yaml` overrides these with localhost URLs — wrong for Docker.

**What changes**: Remove `grafana/provisioning/datasources/datasources.yaml`. Keep `grafana/provisioning/dashboards/dashboards.yaml` (points to custom dashboard JSON files). Update dashboard JSON datasource UIDs: `mimir` → `prometheus` (LGTM built-in Prometheus datasource uses uid `prometheus`). The `tempo` and `loki` UIDs already match.

### Decision 5: Health Poller and Log Collector as Docker Services

**Choice**: Package as Docker services in the services overlay, not standalone containers.

**Rationale**: They're part of the TDT observability stack. Running as Docker services means `docker compose up` brings everything up. The Dockerfile installs the tdt-observability package and runs the health-poller or log-collector as the command.

**Trade-off**: Launchd had `KeepAlive` and PID management. Docker Compose has `restart: unless-stopped` which provides equivalent behavior. The PID file management in the Python code becomes a no-op (process is always PID 1 in container).

**Health poller URL migration**: The default service URLs in `health_poller/__init__.py` use `http://localhost:8080/health` etc. Inside a Docker container, `localhost` refers to the container itself. Two options:
1. Volume-mount a config file at `~/.tdt/observability/config/config.yaml` with Docker-network URLs (e.g., `http://webhook-receiver:8080/health`)
2. Keep the health-poller on the host (via launchd) and only containerize the log-collector

**Chosen approach**: Option 1 — the health-poller config file (`~/.tdt/observability/config/config.yaml`) is mounted into the container. If the file doesn't exist, the health-poller falls back to defaults (which won't work in Docker). The task includes creating this config file with Docker-network service URLs. A startup log warning is added if the config file is missing.

**Dockerfile build context**: The tdt-observability Dockerfile needs `tdt-core` as a dependency (`tdt-core = { path = "../tdt-core", editable = true }` in pyproject.toml). The build context MUST be the workspace root (`~/Developer/`), not `tdt-observability/`. The compose file uses `context: ..` and `dockerfile: tdt-observability/Dockerfile` to include sibling repos.

### Decision 6: LGTM Version Alignment

**Choice**: Pin to v0.29.0 (matching go-microservices), not v0.28.0 (current tdt-observability).

**Rationale**: go-microservices has verified v0.29.0 for `linux/arm64`. Using the same version avoids divergence.

### Decision 7: Migration Atomicity

**Choice**: Execute all 4 phases atomically in a single PR. Phases are NOT independently reversible.

**Rationale**: Phase 2 changes the scheduler's network, which breaks if Phase 1 hasn't created the new network. Phase 3 removes services that Phase 2's scheduler may still reference. The migration must be atomic: stop old stack → apply all changes → start new stack.

**Migration sequence**:
1. Stop all running containers: `cd agent-core && docker compose down; cd ../tdt-scheduler && docker compose down`
2. Unload launchd agents (task 7.4)
3. Apply all file changes (Phases 1-4)
4. Start new stack: `cd tdt-observability && docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.services.yaml up -d`
5. Verify

### Decision 8: postgres-backup Service Handling

**Choice**: Keep `postgres-backup` in `tdt-scheduler/compose.yaml` but add `depends_on` for the LGTM stack.

**Rationale**: The backup service references `postgres` hostname, which resolves via the `tdt-observability` external network. The scheduler compose must be started AFTER the base stack (which defines `postgres`). The `depends_on` ensures correct startup order.

**Alternative considered**: Moving `postgres-backup` to `tdt-observability` — rejected because it's scheduler-specific functionality.

### Decision 9: OTel Collector Port Binding

**Choice**: Bind OTel Collector ports to `127.0.0.1` (not `0.0.0.0`) in all compose files.

**Rationale**: All other services (Postgres, Grafana, Langfuse, MLflow) bind to `127.0.0.1`. The OTel Collector should follow the same pattern for consistency and security. Services on the Docker network resolve `otel-lgtm:4317` via Docker DNS — no need to expose to the host.

**Exception**: The LGTM base stack's built-in collector is internal to the container and not published to the host. The separate OTel Collector (Langfuse overlay) binds `127.0.0.1:4317:4317` for host-side debugging.

## Risks / Trade-offs

**[Risk] Launchd → Docker migration breaks health-poller/log-collector on macOS dev**
→ Mitigation: Docker Desktop runs on macOS. The health-poller and log-collector work identically in containers. The `~/.tdt/logs/` and `~/.tdt/observability/` directories are mounted as volumes. Known limitation: Docker Desktop must be running for the full observability stack.

**[Risk] Langfuse data loss during migration**
→ Mitigation: Local dev only — no production data. Fresh `docker compose up` creates new volumes. Old agent-core volumes can be pruned with explicit `docker volume rm` commands.

**[Risk] Port conflict: Grafana :3000 vs Langfuse :3000**
→ Mitigation: Langfuse web binds to `127.0.0.1:3001:3000` (host port 3001) when the Langfuse overlay is activated. Grafana remains on `:3000`. The LGTM base and Langfuse overlay can coexist.

**[Risk] tdt-scheduler fails to connect if tdt-observability stack isn't running**
→ Mitigation: Add `depends_on: otel-lgtm: condition: service_healthy` to scheduler in services overlay. The scheduler already has graceful degradation when OTEL endpoint is unavailable.

**[Risk] Dashboard queries break after datasource UID change**
→ Mitigation: The current dashboards use `mimir` uid for the Prometheus datasource. The LGTM built-in uses `prometheus` uid. Task 2.3 updates the dashboard JSON to match. Verify panel queries after migration.

**[Risk] DuckDB lock contention between Docker health-poller and host processes**
→ Mitigation: Task 7.4 (unload launchd) MUST complete before task 3.4 (verify health-poller container). The existing retry/backoff logic in the retention module handles any remaining contention.

**[Risk] Langfuse overlay breaks LGTM tracing during startup**
→ Mitigation: The separate OTel Collector uses `depends_on: langfuse-web: condition: service_started` (not `service_healthy`). The base stack's built-in collector continues serving LGTM traces until the separate collector is ready. LGTM tracing is never interrupted.

**[Risk] Health-poller silent fallback to wrong URLs**
→ Mitigation: Task 1.4 creates the config file with Docker-network URLs. Task 3.3 mounts it. A startup log warning is emitted if the config file is missing. The health-poller container has a Docker HEALTHCHECK to detect silent failures.

## Migration Plan

### Phase 0: Pre-flight
1. Verify Docker Compose 2.20+ is installed: `docker compose version`
2. Stop all running containers: `docker compose -f agent-core/compose.yaml down; docker compose -f tdt-scheduler/compose.yaml down`
3. Unload launchd agents: `launchctl unload ~/Library/LaunchAgents/com.tdt.observability-*.plist`
4. Verify no active DBOS workflows in scheduler

### Phase 1: Foundation (tdt-observability only)
1. Create `deploy/docker-compose.yaml` (LGTM + Postgres)
2. Create `deploy/tools.env` (pinned versions)
3. Create `Dockerfile` (build context: workspace root `..`, dockerfile: `tdt-observability/Dockerfile`)
4. Create `deploy/health-poller-config.yaml` (Docker-network service URLs)
5. Remove `deploy/lgtm/run-lgtm.sh`
6. Remove `deploy/launchd/*.plist`
7. Verify: `docker compose up` → Grafana accessible, LGTM healthy

### Phase 2: Network Migration
1. Update `tdt-scheduler/compose.yaml` network to `tdt-observability` (external)
2. Update `tdt-scheduler/compose.yaml` OTEL endpoint to `http://otel-lgtm:4317`
3. Add `depends_on: otel-lgtm: condition: service_healthy` to scheduler service
4. Create `deploy/docker-compose.services.yaml` (scheduler + agent-core + health-poller + log-collector)
5. Verify: scheduler starts, health endpoint responds, traces visible in Grafana

### Phase 3: Agent-Core Cleanup
1. Remove 10 services from `agent-core/compose.yaml` (Langfuse, MLflow, MinIO, OTel Collector)
2. Remove 5 named volumes from `agent-core/compose.yaml`
3. Remove `agent-core/otel-collector-config.yaml`
4. Update `agent-core/config.yaml.example` — change `otel_collector_endpoint` and `langfuse.host` (port 3000→3001)
5. Verify: `agent-core/compose.yaml` starts with just Postgres + app

### Phase 4: Optional Backends
1. Create `deploy/docker-compose.langfuse.yaml` (Langfuse overlay) with `otel-collector` service
2. Create `deploy/docker-compose.mlflow.yaml` (MLflow overlay)
3. Create `deploy/otel-collector-config.yaml` (fan-out collector config)
4. Verify: `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.langfuse.yaml up` → Langfuse receives traces

### Phase 5: Cleanup
1. Remove orphaned Docker volumes: `docker volume rm langfuse-clickhouse-data langfuse-postgres-18-data langfuse-redis-data minio-data mlflow-postgres-18-data`
2. Remove orphaned network: `docker network rm agent-core-local_default` (if exists)
3. Remove old LGTM image: `docker rmi grafana/otel-lgtm:v0.28.0` (if exists)
4. Remove old bind-mount directory: `rm -rf ~/.tdt/observability/lgtm-data` (old run-lgtm.sh data)

### Rollback
The migration is atomic — all phases execute in one PR. Rollback:
- `git checkout <commit-before-migration> -- agent-core/compose.yaml tdt-scheduler/compose.yaml`
- `docker compose -f agent-core/compose.yaml up -d` (restores old stack)
- Re-load launchd agents if needed

## Open Questions

1. Should the tdt-scheduler `compose.yaml` keep its own `postgres-backup` service, or should backup be handled by the tdt-observability stack? (Currently scheduler has its own backup container.) **Recommendation:** Keep in scheduler — it's scheduler-specific.
2. Should the verification override (`tdt-scheduler-verification.override.yaml`) be updated in this change or deferred? **Recommendation:** Update in this change — it's a simple network inheritance fix.
