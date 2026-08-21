# Tasks: Consolidate Observability Docker Deployment

## 0. Pre-flight Checks

- [ ] 0.1 Verify Docker Compose version: `docker compose version` must be 2.20+.
- [ ] 0.2 Stop all running containers: `cd ~/Developer/agent-core && docker compose down; cd ~/Developer/tdt-scheduler && docker compose down`.
- [ ] 0.3 Unload launchd agents: `launchctl unload ~/Library/LaunchAgents/com.tdt.observability-health-poller.plist` and `launchctl unload ~/Library/LaunchAgents/com.tdt.observability-log-aggregator.plist`. Verify they don't restart.
- [ ] 0.4 Verify no active DBOS workflows: check scheduler logs for in-flight jobs.

## 1. Create tdt-observability Docker Foundation

- [ ] 1.1 Create `tdt-observability/deploy/tools.env` with pinned image versions: `POSTGRES_VERSION=18.6-alpine` (matching go-microservices), `OTEL_LGTM_VERSION=0.29.0`, `LANGFUSE_VERSION=4.11.0`, `MLFLOW_VERSION=v3.15.1`. Add documentation header explaining each pin and how to update.
- [ ] 1.2 Create `tdt-observability/deploy/docker-compose.yaml` — base stack: `otel-lgtm` (grafana/otel-lgtm), `postgres` (postgres:18.6-alpine). Network: `tdt-observability` (bridge, created with `docker network create tdt-observability` as prerequisite). LGTM ports: `127.0.0.1:3000:3000` (Grafana), `127.0.0.1:9009:9009` (Prometheus). Postgres port: `127.0.0.1:5432:5432`. All ports bound to `127.0.0.1` (not `0.0.0.0`). LGTM healthcheck: `curl http://localhost:3000/api/health`. Postgres healthcheck: `pg_isready`. Volume: `lgtm-data:/data`, `postgres-data:/var/lib/postgresql`.
- [ ] 1.3 Create `tdt-observability/Dockerfile` — build context is workspace root (`context: ..` in compose), dockerfile is `tdt-observability/Dockerfile`. Python 3.14-slim base, install uv, copy `pyproject.toml` + `uv.lock` + `src/`, run `uv sync`, install system deps (curl, ca-certificates). Expose no ports (background services). Support both health-poller and log-collector via CMD override. Add startup identity log: `"Starting health-poller (HEALTH_POLLER_ENABLED=true)"` or `"Starting log-collector (LOG_COLLECTOR_ENABLED=true)"`.
- [ ] 1.4 Create `tdt-observability/deploy/health-poller-config.yaml` — Docker-network service URLs: `webhook-receiver:8080`, `ai-review:8090`, `tdt-scheduler:9100`. Mount into health-poller container at `~/.tdt/observability/config/config.yaml`.
- [ ] 1.5 Remove `tdt-observability/deploy/lgtm/run-lgtm.sh` — replaced by `docker compose -f deploy/docker-compose.yaml up -d`.
- [ ] 1.6 Remove `tdt-observability/deploy/launchd/com.tdt.observability-health-poller.plist` and `com.tdt.observability-log-aggregator.plist` — replaced by Docker services.
- [ ] 1.7 Verify base stack: `cd ~/Developer/tdt-observability && docker compose -f deploy/docker-compose.yaml up -d` → Grafana accessible at `localhost:3000` (admin/admin), LGTM healthy, Postgres accepts connections.

## 2. Update Grafana Dashboard Provisioning

- [ ] 2.1 Remove `tdt-observability/grafana/provisioning/datasources/datasources.yaml` — LGTM image ships with pre-configured datasources (Prometheus uid: `prometheus`, Tempo uid: `tempo`, Loki uid: `loki`, Pyroscope uid: `pyroscope`). The current file overrides with `localhost` URLs which don't work in Docker.
- [ ] 2.2 Update `tdt-observability/grafana/provisioning/dashboards/dashboards.yaml` — verify the provider path matches the LGTM image mount point (`/otel-lgtm/grafana/conf/provisioning/dashboards/custom`). Update if needed.
- [ ] 2.3 Update `tdt-observability/grafana/dashboards/tdt-service-health.json` — change all `"uid": "mimir"` references to `"uid": "prometheus"` to match LGTM built-in Prometheus datasource. The current dashboard has 3 panels: Service Availability, Response Time p95, Error Rate. All panels reference the Mimir uid which won't exist after removing the override.
- [ ] 2.4 Verify `tdt-observability/grafana/dashboards/tdt-distributed-traces.json` — confirm it already uses `"uid": "tempo"` (no change needed). The current dashboard has 1 panel: Trace Explorer with 2 template variables.
- [ ] 2.5 Verify dashboards render: `docker compose -f deploy/docker-compose.yaml up -d` → Grafana → Dashboards → TDT → panels show data (after traces are generated).

## 3. Create tdt-observability Dockerfile for Health Poller + Log Collector

- [ ] 3.1 Add `HEALTH_POLLER_ENABLED=true` env var support to Dockerfile entrypoint — when set, container runs `python -m tdt_observability.health_poller --interval 30`. Add startup log: `"Starting health-poller"`.
- [ ] 3.2 Add `LOG_COLLECTOR_ENABLED=true` env var support to Dockerfile entrypoint — when set, container runs `python -m tdt_observability.log_collector`. Add startup log: `"Starting log-collector"`.
- [ ] 3.3 Mount volumes: `~/.tdt/logs` as `/var/log/tdt:ro` for log collector, `~/.tdt/observability` as `/data` for DuckDB storage, `deploy/health-poller-config.yaml` as config mount.
- [ ] 3.4 Add Docker HEALTHCHECK for health-poller container: `python -c "import urllib.request; urllib.request.urlopen('http://localhost:9100/scheduler/health')"` or similar.
- [ ] 3.5 Verify health-poller container starts and polls services (check stdout for poll cycle output).
- [ ] 3.6 Verify log-collector container starts and watches log files (check stdout for file watch output).

## 4. Create tdt-scheduler Services Overlay

- [ ] 4.1 Create `tdt-observability/deploy/docker-compose.services.yaml` — overlay with: `scheduler` (build from `../tdt-scheduler`, command: `agent-core-scheduler serve`, `depends_on: otel-lgtm: condition: service_healthy`), `agent-core` (build from `../agent-core`, command: `sleep infinity`), `health-poller` (build from `..`, command: health-poller), `log-collector` (build from `..`, command: log-collector). All services join `tdt-observability` network as external.
- [ ] 4.2 Update `tdt-scheduler/compose.yaml` — change network from `agent-core-local_default` to `tdt-observability` (external). Update `OTEL_OTEL_COLLECTOR_ENDPOINT` from `http://otel-collector:4317` to `http://otel-lgtm:4317`. Add `depends_on: otel-lgtm: condition: service_healthy`.
- [ ] 4.3 Update `tdt-scheduler/tdt-scheduler-verification.override.yaml` — inherits network from base compose (now `tdt-observability`). Verify the override works with the new network. No explicit network change needed in override.
- [ ] 4.4 Verify services stack: `cd ~/Developer/tdt-observability && docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.services.yaml up -d` → scheduler health endpoint responds at `:9100`, agent-core container running, health-poller polling, log-collector watching.

## 5. Migrate Agent-Core Compose Cleanup

- [ ] 5.1 Remove from `agent-core/compose.yaml`: services `langfuse-clickhouse`, `langfuse-postgres`, `langfuse-redis`, `minio`, `minio-init`, `langfuse-web`, `langfuse-worker`, `mlflow-postgres`, `mlflow-server`, `otel-collector` (10 services). Remove named volumes: `langfuse-clickhouse-data`, `langfuse-postgres-18-data`, `langfuse-redis-data`, `minio-data`, `mlflow-postgres-18-data` (5 volumes). Keep: `postgres`, `app`, `agent-core-postgres-data`.
- [ ] 5.2 Remove `agent-core/otel-collector-config.yaml` — this debug-only config is replaced by tdt-observability's LGTM routing.
- [ ] 5.3 Update `agent-core/config.yaml.example` — change `otel_collector_endpoint` default from `"http://otel-collector:4317"` to `"http://otel-lgtm:4317"`. Change `langfuse.host` from `"http://127.0.0.1:3000"` to `"http://127.0.0.1:3001"` (Langfuse moves to port 3001 in overlay). Add comments noting old values are deprecated.
- [ ] 5.4 Verify agent-core stack: `cd ~/Developer/agent-core && docker compose up -d` → Postgres + app start successfully. No references to removed services remain.

## 6. Create Optional Backend Overlays

- [ ] 6.1 Create `tdt-observability/deploy/docker-compose.langfuse.yaml` — Langfuse overlay with: `langfuse-clickhouse`, `langfuse-postgres`, `langfuse-redis`, `minio`, `minio-init` (use `${MINIO_ROOT_USER}` and `${MINIO_ROOT_PASSWORD}` env vars in init command, not hardcoded), `langfuse-web`, `langfuse-worker`, `otel-collector` (fan-out). All join `tdt-observability` network. Langfuse web port: `127.0.0.1:3001:3000` (host 3001 to avoid conflict with Grafana on 3000). OTel Collector ports: `127.0.0.1:4317:4317` (gRPC), `127.0.0.1:4318:4318` (HTTP). OTel Collector `depends_on: langfuse-web: condition: service_started` (NOT `service_healthy` — to avoid blocking LGTM tracing during Langfuse startup). Use `LANGFUSE_VERSION` from `tools.env`.
- [ ] 6.2 Create `tdt-observability/deploy/docker-compose.mlflow.yaml` — MLflow overlay with: `mlflow-postgres`, `mlflow-server`. MLflow server port: `127.0.0.1:5000:5000`. Use `MLFLOW_VERSION` from `tools.env`.
- [ ] 6.3 Create `tdt-observability/deploy/otel-collector-config.yaml` — fan-out collector config: receives OTLP gRPC/HTTP, exports to LGTM (`otlphttp/lgtm`), Langfuse (`otlphttp/langfuse` with Basic Auth + `x-langfuse-ingestion-version: 4`), MLflow (`otlphttp/mlflow` with `x-mlflow-experiment-id` header). Processors: `memory_limiter`, `batch`.
- [ ] 6.4 Create `tdt-observability/deploy/.env.example` — document all secrets and their defaults with a header warning that defaults must not be used in production. Include: `LANGFUSE_AUTH`, `MINIO_ROOT_PASSWORD`, `LANGFUSE_SECRET_KEY`, `NEXTAUTH_SECRET`, `ENCRYPTION_KEY`, `POSTGRES_PASSWORD`.
- [ ] 6.5 Verify Langfuse overlay: `cd ~/Developer/tdt-observability && docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.langfuse.yaml up -d` → Langfuse web accessible at `localhost:3001`, ClickHouse healthy, OTel Collector receiving traces.
- [ ] 6.6 Verify MLflow overlay: `cd ~/Developer/tdt-observability && docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.mlflow.yaml up -d` → MLflow server accessible at `localhost:5000`, health endpoint responds.

## 7. Remove Legacy Files

- [ ] 7.1 Remove `tdt-observability/deploy/lgtm/run-lgtm.sh` — replaced by `docker compose -f deploy/docker-compose.yaml up -d`.
- [ ] 7.2 Remove `tdt-observability/deploy/launchd/com.tdt.observability-health-poller.plist` — replaced by Docker service in `docker-compose.services.yaml`.
- [ ] 7.3 Remove `tdt-observability/deploy/launchd/com.tdt.observability-log-aggregator.plist` — replaced by Docker service in `docker-compose.services.yaml`.
- [ ] 7.4 Update `tdt-observability/README.md` — replace `run-lgtm.sh` usage with `docker compose` commands. Document the overlay pattern, port map, and available stacks. Add Grafana credentials (admin/admin). Add preflight check: `docker info >/dev/null 2>&1 || echo "Docker Desktop is not running"`.
- [ ] 7.5 Add port map table to README:

```
| Service       | Port  | Protocol | Binding       |
|---------------|-------|----------|---------------|
| Grafana       | 3000  | HTTP     | 127.0.0.1     |
| Prometheus    | 9009  | HTTP     | 127.0.0.1     |
| Postgres      | 5432  | TCP      | 127.0.0.1     |
| Langfuse      | 3001  | HTTP     | 127.0.0.1     |
| MLflow        | 5000  | HTTP     | 127.0.0.1     |
| OTel Collector| 4317  | gRPC     | 127.0.0.1     |
| OTel Collector| 4318  | HTTP     | 127.0.0.1     |
| Scheduler     | 9100  | HTTP     | 127.0.0.1     |
| Verification  | 19100 | HTTP     | 127.0.0.1     |
```

- [ ] 7.6 Add overlay quick reference to README:

```bash
# Base stack only (LGTM + Postgres)
docker compose -f deploy/docker-compose.yaml up -d

# With TDT services
docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.services.yaml up -d

# With Langfuse
docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.langfuse.yaml up -d

# Full stack (everything)
docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.services.yaml -f deploy/docker-compose.langfuse.yaml -f deploy/docker-compose.mlflow.yaml up -d
```

## 8. Cleanup

- [ ] 8.1 Remove orphaned agent-core volumes: `docker volume rm langfuse-clickhouse-data langfuse-postgres-18-data langfuse-redis-data minio-data mlflow-postgres-18-data` (explicit removal, not `docker volume prune`).
- [ ] 8.2 Remove orphaned network: `docker network rm agent-core-local_default` (if exists).
- [ ] 8.3 Remove old LGTM image: `docker rmi grafana/otel-lgtm:v0.28.0` (if exists).
- [ ] 8.4 Remove old bind-mount directory: `rm -rf ~/.tdt/observability/lgtm-data` (old run-lgtm.sh data).

## 9. Integration Verification

- [ ] 9.1 Full stack smoke test: `cd ~/Developer/tdt-observability && docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.services.yaml up -d` → all services healthy, scheduler responds on `:9100`, Grafana accessible on `:3000`.
- [ ] 9.2 Trace flow verification: trigger an agent-core CLI command (e.g., `agent-core health`) → trace appears in Grafana → Explore → Tempo. Verify span contains `service.name=agent-core`.
- [ ] 9.3 Log flow verification: check Grafana → Explore → Loki → logs from scheduler/agent-core appear with `service` label.
- [ ] 9.4 Metric flow verification: check Grafana → Prometheus datasource → `up{job="tdt-scheduler"}` returns 1.
- [ ] 9.5 Cross-repo compose verification: `cd ~/Developer/tdt-scheduler && docker compose up -d` → scheduler joins `tdt-observability` network, connects to `otel-lgtm:4317`, health endpoint responds.
- [ ] 9.6 Verification override compatibility: `cd ~/Developer/tdt-observability && docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.services.yaml -f ../tdt-scheduler/tdt-scheduler-verification.override.yaml up -d` → verification container starts on `:19100`.
- [ ] 9.7 Health-poller Docker mode: verify health-poller container polls services using Docker-network URLs (not localhost). Check stdout for successful poll responses.
- [ ] 9.8 Langfuse overlay trace flow: `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.langfuse.yaml up -d` → trigger agent run → traces appear in both Grafana Tempo AND Langfuse UI at `localhost:3001`.
