## ADDED Requirements

### Requirement: Langfuse v3 Docker Compose stack
The system SHALL provide a Docker Compose configuration for Langfuse v3 (server version 3.219) with the following 7 services:
1. `langfuse-web` — `langfuse/langfuse:3.219` (UI + API, port 3000)
2. `langfuse-worker` — `langfuse/langfuse:3.219` (async event processing)
3. `langfuse-clickhouse` — `clickhouse/clickhouse-server:latest` (trace storage, ports 8123/9000)
4. `langfuse-postgres` — `postgres:16` (metadata storage)
5. `langfuse-redis` — `redis:7-alpine` (queuing + caching)
6. `minio` — `quay.io/minio/minio:latest` (S3-compatible blob storage, ports 9000/9001 — shared with MLflow)

All storage is local. No cloud credentials required. MinIO uses default credentials (`minio`/`miniosecret`) for local development.

Minimum resource requirements per Langfuse docs: Web 2 CPU/4GB, Worker 2 CPU/4GB, ClickHouse 2 CPU/4GB.

#### Scenario: All services start successfully
- **WHEN** `docker compose up -d` is run with the Langfuse services
- **THEN** all containers are healthy and Langfuse UI is accessible at `http://localhost:3000`

#### Scenario: Services survive restart
- **WHEN** `docker compose restart` is run
- **THEN** all services restart and resume processing within 30 seconds (ClickHouse may take up to 60s on first boot due to schema migrations)

### Requirement: Langfuse required environment variables (local Docker Compose)
The system SHALL configure Langfuse services via environment variables in `.env.docker`. Required variables SHALL include:
- `LANGFUSE_SECRET_KEY` — encryption key (256 bits, 64 hex chars)
- `LANGFUSE_NEXT_AUTH_SECRET` — NextAuth secret for session management
- `ENCRYPTION_KEY` — 256-bit hex key for encrypting sensitive data
- `SALT` — salt for hashing
- `DATABASE_URL` — PostgreSQL connection string (e.g., `postgresql://langfuse:langfuse@langfuse-postgres:5432/langfuse`)
- `CLICKHOUSE_URL` — ClickHouse HTTP endpoint (e.g., `http://langfuse-clickhouse:8123`)
- `CLICKHOUSE_MIGRATION_URL` — ClickHouse native endpoint (e.g., `langfuse-clickhouse:9000`)
- `REDIS_CONNECTION_STRING` — Redis connection (e.g., `redis://langfuse-redis:6379`)
- `LANGFUSE_S3_EVENT_UPLOAD_BUCKET` — MinIO bucket name (default: `langfuse`)
- `LANGFUSE_S3_EVENT_UPLOAD_REGION` — MinIO region (default: `us-east-1`)
- `LANGFUSE_S3_EVENT_UPLOAD_ACCESS_KEY_ID` — MinIO access key (default: `minio`)
- `LANGFUSE_S3_EVENT_UPLOAD_SECRET_ACCESS_KEY` — MinIO secret key (default: `miniosecret`)
- `LANGFUSE_S3_EVENT_UPLOAD_ENDPOINT` — MinIO endpoint (default: `http://minio:9000`)
- `LANGFUSE_S3_EVENT_UPLOAD_FORCE_PATH_STYLE` — Required for MinIO (default: `true`)
- `LANGFUSE_S3_EVENT_UPLOAD_PREFIX` — Event prefix (default: `events/`)

All S3 variables default to local MinIO values. No cloud credentials required.

#### Scenario: Missing required env vars prevent startup
- **WHEN** `ENCRYPTION_KEY` is not set
- **THEN** Langfuse web container logs an error and does not start

#### Scenario: All env vars configured with MinIO defaults
- **WHEN** all required environment variables are set in `.env.docker` with MinIO defaults
- **THEN** `docker compose up -d` starts all Langfuse services successfully and Langfuse connects to local MinIO

### Requirement: ClickHouse persistence
The system SHALL persist ClickHouse data via Docker named volume (`langfuse-clickhouse-data`). Trace data SHALL survive container restarts and rebuilds.

#### Scenario: Data persists across restart
- **WHEN** traces are ingested, then `docker compose restart langfuse-clickhouse` is run
- **THEN** all previously ingested traces are still queryable

### Requirement: MinIO bucket initialization
The system SHALL create required S3 buckets (`langfuse` for Langfuse events, `mlflow` for MLflow artifacts) on first MinIO startup. This SHALL be done via a MinIO client (`mc`) init container that waits for MinIO to be healthy, then runs `mc alias set local http://minio:9000 minio miniosecret && mc mb local/langfuse && mc mb local/mlflow`. Buckets SHALL persist across container restarts via Docker named volume (`minio-data`).

#### Scenario: Buckets created on first start
- **WHEN** `docker compose up -d` is run for the first time
- **THEN** MinIO has buckets `langfuse` and `mlflow` ready for use

#### Scenario: Buckets persist across restarts
- **WHEN** `docker compose restart minio` is run
- **THEN** existing buckets and their data are preserved

### Requirement: Langfuse health check endpoint
The system SHALL expose a health check endpoint at `http://localhost:3000/api/public/health` that returns 200 when all Langfuse services are operational.

#### Scenario: Health check returns OK
- **WHEN** all Langfuse services are running
- **THEN** `curl http://localhost:3000/api/public/health` returns HTTP 200

### Requirement: Resource limits
The Docker Compose configuration SHALL set memory limits: ClickHouse 4GB, Langfuse Web 4GB, Langfuse Worker 4GB, MinIO 1GB, Redis 512MB. CPU limits SHALL be set where possible.

#### Scenario: Containers respect memory limits
- **WHEN** Docker stats is checked for Langfuse containers
- **THEN** no container exceeds its configured memory limit

### Requirement: Integration with existing compose.yaml
The Langfuse services SHALL be added to the existing `compose.yaml` (which currently contains `postgres`, `app`, and `scheduler` services at the agent-core root). New services SHALL use the same Docker network and respect existing volume naming conventions (`agent-core-*` prefix).

#### Scenario: Combined stack starts
- **WHEN** `docker compose up -d` is run from agent-core root
- **THEN** all existing services (postgres, app, scheduler) AND new Langfuse services start together

#### Scenario: Existing services unaffected
- **WHEN** Langfuse services are added to compose.yaml
- **THEN** `docker compose up -d postgres app scheduler` starts only the original services (backward compatible)
