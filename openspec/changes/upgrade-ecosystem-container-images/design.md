# Design: Upgrade ecosystem container images

## Image-Tag Governance Policy

All stateful services (databases, message brokers, observability backends) SHALL use exact, immutable release tags for production. Floating tags (`:latest`, major-only) are prohibited for stateful services. Exceptions require documented rationale. Local build images (`:local-dev`, `:latest`) are exempt.

## PostgreSQL Volume Safety

PostgreSQL 18 cannot open a PostgreSQL 16 data directory. No volumes exist locally, so local testing uses fresh initialization. Other deployments may have PG16 volumes.

- Never auto-delete PG16 volumes
- Use PG18 mount layout (`/var/lib/postgresql`)
- Preserve old volumes for rollback

## Research Matrix (4-Column)

| Service | Current | Latest upstream | Langfuse baseline | **Selected target** | Evidence |
|---------|---------|----------------|-------------------|---------------------|----------|
| **PostgreSQL** | 18.4-alpine / 18.6-trixie | 18.6 | >=15 | **18.6-trixie** | Docker Hub ✅ |
| **Langfuse** | 3.219 | v4.11.0 (2026-08-14) | 4 | **4.11.0** | GitHub Releases ✅ |
| **Langfuse worker** | 3 (float) | v4.11.0 | 4 | **4.11.0** | GitHub Releases ✅ |
| **MLflow** | :latest | v3.15.1 (2026-08-03) | — | **v3.15.1** + derived image | GitHub Releases + PyPI ✅ |
| **ClickHouse** | :latest | **v26.7.3.19** | 25.12 | **26.4.5.143-alpine** | Docker Hub ✅ |
| **Redis** | 7-alpine | **8.10.0** (2026-07-29) | redis:7 | **8.10.0-alpine** | GitHub Releases ✅ |
| **MinIO server** | quay.io/minio:latest | Chainguard 2026-07-17 | Chainguard | **@sha256:6196cdd…** (digest-pinned) | Docker image inspect ✅ |
| **minio/mc** | :latest | RELEASE.2025-08-13 | — | **RELEASE.2025-08-13T08-35-41Z** | GitHub Releases ✅ |
| **OTel Collector** | 0.157.0 | v0.158.0 (2026-08-04) | — | **0.158.0** | GitHub Releases ✅ |

## Compatibility Deviations

### Redis 8.10.0 (Langfuse)

Langfuse v4.11.0 official Compose uses `redis:7`. This project selects **Redis 8.10.0** per explicit user requirement. Redis 8 is not yet in Langfuse's official compatibility baseline.

- Langfuse uses ioredis and BullMQ, which support Redis 8 at the client level.
- `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK` exists in the official Compose as an override flag.
- **Acceptance criterion**: Langfuse web and worker must start, remain healthy, and produce no Redis-related errors or restarts with Redis 8.10.0.
- **Re-evaluation trigger**: Langfuse release notes or documentation explicitly adding Redis 8 support.

### ClickHouse 26.4.5.143 (Langfuse)

Global upstream latest is ClickHouse **v26.7.3.19**. Langfuse v4.11.0 official Compose uses ClickHouse 25.12.

- Known Langfuse issue: ClickHouse 26.5+ triggers `NOT_FOUND_COLUMN_IN_BLOCK` errors due to analyzer behavior changes.
- **Selected target: 26.4.5.143-alpine** — latest ClickHouse 26.x patch before the known 26.5+ incompatibility.
- **Acceptance criterion**: Langfuse ClickHouse migration completes and no `NOT_FOUND_COLUMN_IN_BLOCK` errors appear in logs.
- **Re-evaluation trigger**: Langfuse issue/PR confirming ClickHouse 26.5+ compatibility.

### MLflow Derived Image

Upstream `ghcr.io/mlflow/mlflow:v3.15.1` ships SQLAlchemy 2.0.51 but no PostgreSQL DBAPI driver (`psycopg2`). The derived image adds `psycopg2-binary==2.9.12` (latest stable from PyPI).

```dockerfile
FROM ghcr.io/mlflow/mlflow:v3.15.1
RUN pip install --no-cache-dir psycopg2-binary==2.9.12
```

Local image tag: `mlflow-local-dev:v3.15.1-psycopg2-2.9.12`

## Upgrade Slices

| Slice | Scope | Risk | Evidence |
|-------|-------|------|----------|
| A | go-microservices patch-level (PG 18.6, Mailpit, Grafana, OTel, Python) | Low | 36/36 image checks, `85cee48` on main |
| B | PostgreSQL volume layout + migration docs | Low | 15/15 Docker-local tests, `ce0df18` |
| C | Pin MLflow + OTel collector | Low | 2 regression tests, `8bf1e57` |
| D | Langfuse v3→v4 + Redis 8 + ClickHouse 26.4 + MinIO digest | High | 10 regression tests, `643c80a`–`21b0dec` |
| E | MLflow derived Dockerfile (psycopg2-binary) | Medium | 3 regression tests, MLflow healthy at runtime |

## Runtime Acceptance Criteria

All of the following must pass in an isolated Compose project with fresh volumes:

1. **PostgreSQL 18.6**: starts, healthy, accepts connections
2. **Redis 8.10.0**: starts, `--requirepass` auth works, unauthenticated access rejected, Langfuse web+worker healthy
3. **ClickHouse 26.4.5.143**: starts, Langfuse migration completes, no `NOT_FOUND_COLUMN_IN_BLOCK` errors
4. **MLflow**: derived image starts, PostgreSQL backend connected, `/health` returns 200
5. **Langfuse web**: starts, `/api/public/health` returns OK, all dependencies healthy
6. **Langfuse worker**: starts, remains running, no restarts
7. **MinIO**: starts, S3-compatible API responds

## Commits (agent-core worktree)

1. `ce0df18` — fix(compose): use migration-safe PostgreSQL 18 volumes
2. `8bf1e57` — chore(images): pin MLflow and OTel collector releases
3. `643c80a` — feat(observability): migrate Langfuse stack to v4
4. `964c95e` — chore(images): upgrade Redis to 8.10.0 and ClickHouse to 26.4.5
5. `4db3573` — fix(mlflow): add psycopg2-binary to derived Dockerfile
6. `21b0dec` — fix(mlflow): use exact derived image and strengthen regression coverage

## Commits (go-microservices)

1. `7b5df1c` — chore(images): update platform image pins (PG 18.6, Mailpit, OTel, Grafana, Python)
2. `85cee48` — fix(images): align deployment verification image references
