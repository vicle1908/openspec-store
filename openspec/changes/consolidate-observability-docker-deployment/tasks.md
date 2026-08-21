# Tasks: Consolidate Observability Docker Deployment

## 1. Create tdt-observability Docker Foundation

- [ ] 1.1 Create `tdt-observability/deploy/tools.env` with pinned image versions: `POSTGRES_VERSION=18.6-trixie`, `OTEL_LGTM_VERSION=0.29.0`, `LANGFUSE_VERSION=4.11.0`, `MLFLOW_VERSION=v3.15.1`. Verify versions match go-microservices `deploy/tools.env`.
- [ ] 1.2 Create `tdt-observability/deploy/docker-compose.yaml` — base stack: `otel-lgtm` (grafana/otel-lgtm), `postgres` (postgres:18.6-trixie). Network: `tdt-observability` (bridge). LGTM ports: `127.0.0.1:3000:3000` (Grafana), `127.0.0.1:9009:9009` (Prometheus). Postgres port: `127.0.0.1:5432:5432`. LGTM healthcheck: `curl http://localhost:3000/api/health`. Postgres healthcheck: `pg_isready`. Volume: `lgtm-data:/data`, `postgres-data:/var/lib/postgresql`.
- [ ] 1.3 Create `tdt-observability/Dockerfile` — Python 3.14-slim base, install uv, copy `pyproject.toml` + `uv.lock` + `src/`, run `uv sync`, install system deps (curl, ca-certificates). Expose no ports (background services). CMD: configurable via `HEALTH_POLLER_ENABLED` and `LOG_COLLECTOR_ENABLED` env vars.
- [ ] 1.4 Verify base stack: `cd tdt-observability && docker compose -f deploy/docker-compose.yaml up -d` → Grafana accessible at `localhost:3000` (admin/admin), LGTM healthy, Postgres accepts connections.

## 2. Update Grafana Dashboard Provisioning

- [ ] 2.1 Remove `tdt-observability/grafana/provisioning/datasources/datasources.yaml` — LGTM image ships with pre-configured datasources (Prometheus uid: `prometheus`, Tempo uid: `tempo`, Loki uid: `loki`). The current file overrides with `localhost` URLs which don't work in Docker.
- [ ] 2.2 Update `tdt-observability/grafana/provisioning/dashboards/dashboards.yaml` — verify the provider path matches the LGTM image mount point (`/otel-lgtm/grafana/conf/provisioning/dashboards/custom`). Update if needed.
- [ ] 2.3 Update `tdt-observability/grafana/dashboards/tdt-service-health.json` — change datasource UID from `mimir` to `prometheus` (LGTM built-in Prometheus datasource uses uid `prometheus`). The current dashboard has 3 panels: Service Availability, Response Time p95, Error Rate.
- [ ] 2.4 Update `tdt-observability/grafana/dashboards/tdt-distributed-traces.json` — verify Trace Explorer panel uses `tempo` datasource UID. The current dashboard has 1 panel: Trace Explorer with 2 template variables.
- [ ] 2.5 Verify dashboards render: `docker compose -f deploy/docker-compose.yaml up -d` → Grafana → Dashboards → TDT → panels show data (after traces are generated).

## 3. Create tdt-observability Dockerfile for Health Poller + Log Collector

- [ ] 3.1 Create `tdt-observability/Dockerfile` with multi-stage build: builder stage installs dependencies, runtime stage runs health-poller or log-collector. The image should support both via CMD override.
- [ ] 3.2 Add `HEALTH_POLLER_ENABLED=true` env var support — when set, container runs `python -m tdt_observability.health_poller --interval 30`.
- [ ] 3.3 Add `LOG_COLLECTOR_ENABLED=true` env var support — when set, container runs `python -m tdt_observability.log_collector`.
- [ ] 3.4 Mount `~/.tdt/logs` as `/var/log/tdt:ro` for log collector, `~/.tdt/observability` as `/data` for DuckDB storage.
- [ ] 3.5 Verify health-poller container starts and polls services (check stdout for poll cycle output).
- [ ] 3.6 Verify log-collector container starts and watches log files (check stdout for file watch output).

## 4. Create tdt-scheduler Services Overlay

- [ ] 4.1 Create `tdt-observability/deploy/docker-compose.services.yaml` — overlay with: `scheduler` (build from `../tdt-scheduler`, command: `agent-core-scheduler serve`), `agent-core` (build from `../agent-core`, command: `sleep infinity`), `health-poller` (build from `..`, command: health-poller), `log-collector` (build from `..`, command: log-collector). All services join `tdt-observability` network as external.
- [ ] 4.2 Update `tdt-scheduler/compose.yaml` — change network from `agent-core-local_default` to `tdt-observability` (external). Update `OTEL_OTEL_COLLECTOR_ENDPOINT` from `http://otel-collector:4317` to `http://otel-lgtm:4317`.
- [ ] 4.3 Update `tdt-scheduler/tdt-scheduler-verification.override.yaml` — change network reference if needed. Verify the override still works with the new network.
- [ ] 4.4 Verify services stack: `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.services.yaml up -d` → scheduler health endpoint responds, agent-core container running, health-poller polling, log-collector watching.

## 5. Migrate Agent-Core Compose Cleanup

- [ ] 5.1 Remove from `agent-core/compose.yaml`: services `langfuse-clickhouse`, `langfuse-postgres`, `langfuse-redis`, `minio`, `minio-init`, `langfuse-web`, `langfuse-worker`, `mlflow-postgres`, `mlflow-server`, `otel-collector` (10 services). Remove named volumes: `langfuse-clickhouse-data`, `langfuse-postgres-18-data`, `langfuse-redis-data`, `minio-data`, `mlflow-postgres-18-data` (5 volumes). Keep: `postgres`, `app`, `agent-core-postgres-data`.
- [ ] 5.2 Remove `agent-core/otel-collector-config.yaml` — this debug-only config is replaced by tdt-observability's LGTM routing.
- [ ] 5.3 Update `agent-core/config.yaml.example` — change `otel_collector_endpoint` default from `"http://otel-collector:4317"` to `"http://otel-lgtm:4317"`. Add comment noting the old value is deprecated.
- [ ] 5.4 Verify agent-core stack: `cd agent-core && docker compose up -d` → Postgres + app start successfully. No references to removed services remain.
- [ ] 5.5 Run `docker volume prune` to clean up orphaned agent-core observability volumes.

## 6. Create Optional Backend Overlays

- [ ] 6.1 Create `tdt-observability/deploy/docker-compose.langfuse.yaml` — Langfuse overlay with: `langfuse-clickhouse`, `langfuse-postgres`, `langfuse-redis`, `minio`, `minio-init`, `langfuse-web`, `langfuse-worker`. All join `tdt-observability` network. Langfuse web port: `127.0.0.1:3000:3000`. Use `LANGFUSE_VERSION` from `tools.env`.
- [ ] 6.2 Create `tdt-observability/deploy/docker-compose.mlflow.yaml` — MLflow overlay with: `mlflow-postgres`, `mlflow-server`. MLflow server port: `127.0.0.1:5000:5000`. Use `MLFLOW_VERSION` from `tools.env`.
- [ ] 6.3 Create `tdt-observability/deploy/otel-collector-config.yaml` — fan-out collector config: receives OTLP gRPC/HTTP, exports to LGTM (`otlphttp/lgtm`), Langfuse (`otlphttp/langfuse` with Basic Auth + `x-langfuse-ingestion-version: 4`), MLflow (`otlphttp/mlflow` with `x-mlflow-experiment-id` header). Processors: `memory_limiter`, `batch`.
- [ ] 6.4 Verify Langfuse overlay: `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.langfuse.yaml up -d` → Langfuse web accessible at `localhost:3000`, ClickHouse healthy.
- [ ] 6.5 Verify MLflow overlay: `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.mlflow.yaml up -d` → MLflow server accessible at `localhost:5000`, health endpoint responds.

## 7. Remove Legacy Files

- [ ] 7.1 Remove `tdt-observability/deploy/lgtm/run-lgtm.sh` — replaced by `docker compose -f deploy/docker-compose.yaml up -d`.
- [ ] 7.2 Remove `tdt-observability/deploy/launchd/com.tdt.observability-health-poller.plist` — replaced by Docker service in `docker-compose.services.yaml`.
- [ ] 7.3 Remove `tdt-observability/deploy/launchd/com.tdt.observability-log-aggregator.plist` — replaced by Docker service in `docker-compose.services.yaml`.
- [ ] 7.4 Unload launchd agents on macOS: `launchctl unload ~/Library/LaunchAgents/com.tdt.observability-health-poller.plist` and `launchctl unload ~/Library/LaunchAgents/com.tdt.observability-log-aggregator.plist`. Verify they don't restart.
- [ ] 7.5 Update `tdt-observability/README.md` — replace `run-lgtm.sh` usage with `docker compose` commands. Document the overlay pattern and available stacks.

## 8. Integration Verification

- [ ] 8.1 Full stack smoke test: `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.services.yaml up -d` → all services healthy, scheduler responds on `:9100`, Grafana accessible on `:3000`.
- [ ] 8.2 Trace flow verification: trigger an agent-core CLI command (e.g., `agent-core health`) → trace appears in Grafana → Explore → Tempo. Verify span contains `service.name=agent-core`.
- [ ] 8.3 Log flow verification: check Grafana → Explore → Loki → logs from scheduler/agent-core appear with `service` label.
- [ ] 8.4 Metric flow verification: check Grafana → Prometheus datasource → `up{job="tdt-scheduler"}` returns 1.
- [ ] 8.5 Cross-repo compose verification: `cd tdt-scheduler && docker compose up -d` → scheduler joins `tdt-observability` network, connects to `otel-lgtm:4317`, health endpoint responds.
- [ ] 8.6 Verification override compatibility: `docker compose -f ../tdt-observability/deploy/docker-compose.yaml -f ../tdt-observability/deploy/docker-compose.services.yaml -f tdt-scheduler-verification.override.yaml up -d` → verification container starts on `:19100`.
