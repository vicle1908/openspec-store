# Tasks: Upgrade ecosystem container images

## Slice A — go-microservices patch-level (DONE)
- [x] PG 18.4→18.6, Mailpit v1.30→v1.30.7, OTel 0.156→0.158, Grafana 13.1.1→13.1.3, Python 3.13→3.14.5
- [x] 36/36 image architecture checks pass (amd64+arm64)
- [x] All Go tests pass, stale ref sweep clean
- [x] Cherry-picked to `go-microservices/main` at `85cee48`
- [x] Deployment verification references aligned at `85cee48`

## Slice B — PostgreSQL volume layout (DONE)
- [x] langfuse-postgres: versioned volume `langfuse-postgres-18-data:/var/lib/postgresql`
- [x] mlflow-postgres: versioned volume `mlflow-postgres-18-data:/var/lib/postgresql`
- [x] Old `langfuse-postgres-data` / `mlflow-postgres-data` volumes removed
- [x] PG16→18 migration docs added to `docs/observability.md`
- [x] 15/15 Docker-local tests pass, `docker compose config` valid
- [x] Committed as `ce0df18`

## Slice C — Pin MLflow + OTel (DONE)
- [x] MLflow: `ghcr.io/mlflow/mlflow:latest` → `v3.15.1`
- [x] OTel: `0.157.0` → `0.158.0`
- [x] 2 regression tests added
- [x] Committed as `8bf1e57`

## Slice D — Langfuse v3→v4 + Redis 8 + ClickHouse 26.4 + MinIO (DONE)
- [x] Langfuse: `3.219` → `4.11.0`, worker: `3` → `4.11.0`
- [x] ClickHouse: `:latest` → `26.4.5.143-alpine` (latest 26.x before known 26.5+ bug)
- [x] Redis: `7-alpine` → `8.10.0-alpine` (user-requested, ioredis/BullMQ client-compatible)
- [x] MinIO: `quay.io/minio/minio:latest` → Chainguard `@sha256:6196cdd…` (digest-pinned)
- [x] minio/mc: `:latest` → `RELEASE.2025-08-13T08-35-41Z` (exact release)
- [x] REDIS_CONNECTION_STRING → REDIS_HOST/PORT/AUTH (v4 pattern)
- [x] Redis command + healthcheck with `--requirepass`
- [x] 10 regression tests added
- [x] Committed as `643c80a` + `964c95e`

## Slice E — MLflow derived Dockerfile (DONE)
- [x] Dockerfile.mlflow: `FROM ghcr.io/mlflow/mlflow:v3.15.1` + `psycopg2-binary==2.9.12`
- [x] compose.yaml: build context + exact local image tag `mlflow-local-dev:v3.15.1-psycopg2-2.9.12`
- [x] Derived image built and verified: psycopg2 2.9.12 importable
- [x] MLflow server starts, connects to PostgreSQL, `/health` returns 200
- [x] 3 strengthened regression tests (build directive, exact tag, Dockerfile pins)
- [x] Committed as `4db3573` + `21b0dec`

## Phase 2 — Runtime Validation (IN PROGRESS)
- [x] Redis 8.10.0: version, auth, Langfuse web+worker healthy, no BullMQ errors
- [x] ClickHouse 26.4.5.143: version, Langfuse migration, no NOT_FOUND_COLUMN_IN_BLOCK
- [x] Langfuse web: health endpoint, all dependencies
- [x] Langfuse worker: remains running, no restarts
- [x] Full stack: all 10 services start with fresh volumes

## Phase 3 — Integration + Promotion
- [x] Cherry-pick 6 commits onto current `agent-core/main` (`7a89372`)
- [x] Full test suite (pytest, ruff, mypy, lock, compose)
- [x] Fast-forward `agent-core/main` to verified commit

## Phase 4 — OpenSpec Archive
- [x] Task checkboxes updated with evidence
- [x] Strict validation passes
- [x] Archived to `openspec/changes/archive/2026-08-17-upgrade-ecosystem-container-images/`
