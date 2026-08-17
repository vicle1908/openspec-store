# Tasks: Upgrade ecosystem container images

## Planning

- [x] Research all image versions against authoritative registries
- [x] Verify multi-architecture support (amd64 + arm64) for all target images
- [x] Reconcile targets against Langfuse v4.11.0 official Compose baseline
- [x] Design 4-column research matrix (current → upstream → app baseline → selected)
- [x] Document PG16→18 volume migration safety requirements
- [x] Validate change with `openspec validate --strict`

## Slice A — go-microservices low-risk patches

- [ ] Update `POSTGRES_VERSION` in `deploy/tools.env` from `18.4-alpine` to `18.6-alpine`
- [ ] Update `MAILPIT_VERSION` from `v1.30` to `v1.30.7`
- [ ] Update `GRAFANA_VERSION` from `13.1.1` to `13.1.3`
- [ ] Update `OTEL_COLLECTOR_VERSION` from `0.156.0` to `0.159.0`
- [ ] Update `PYTHON_IMAGE_VERSION` from `3.13-slim` to `3.14.5-slim`
- [ ] Run `scripts/verify-images.sh --arch arm64` (if exists)
- [ ] Run `docker compose -f deploy/docker-compose.yaml config --quiet`
- [ ] Run Go tests and linters
- [ ] Commit: `chore(images): update go-microservices patch-level image pins`

## Slice B — PostgreSQL volume safety

- [ ] Update `langfuse-postgres` volume mount from `/var/lib/postgresql/data` to `/var/lib/postgresql`
- [ ] Update `mlflow-postgres` volume mount from `/var/lib/postgresql/data` to `/var/lib/postgresql`
- [ ] Validate `docker compose config --quiet`
- [ ] Isolated Compose up with fresh volumes, verify PG18.6 `SHOW server_version`
- [ ] Document migration procedure for existing PG16 deployments
- [ ] Commit: `fix(compose): use PostgreSQL 18 volume layout and migration-safe volumes`

## Slice C — Pin floating tags

- [ ] Pin `ghcr.io/mlflow/mlflow:latest` to `v3.15.1`
- [ ] Pin `clickhouse/clickhouse-server:latest` to `25.12.11.4-alpine` (Langfuse-compatible line)
- [ ] Pin `quay.io/minio/minio:latest` to `RELEASE.2025-09-07T16-13-09Z`
- [ ] Pin `minio/mc:latest` to `RELEASE.2025-08-13T08-35-41Z`
- [ ] Validate `docker compose config --quiet`
- [ ] Commit: `chore(images): pin observability infrastructure images`

## Slice D — Langfuse 3→4 migration

- [ ] Research Langfuse v4.11.0 env vars: `SALT`, `ENCRYPTION_KEY`, S3 config, ClickHouse config
- [ ] Update `langfuse/langfuse` to `4.11.0`
- [ ] Update `langfuse/langfuse-worker` to `4.11.0`
- [ ] Update ClickHouse to `25.12.11.4-alpine`
- [ ] Update MinIO to Chainguard variant `cgr.dev/chainguard/minio`
- [ ] Retain Redis 7 (Langfuse v4.11 baseline)
- [ ] Reconcile environment variables with Langfuse v4 official Compose
- [ ] Isolated Compose up with fresh volumes, verify Langfuse health
- [ ] Commit: `feat(observability): migrate Langfuse stack to v4`

## Slice E — Redis 8 evaluation

- [ ] Confirm Langfuse v4 Redis 7 compatibility status
- [ ] If compatible: update `redis:7-alpine` to `redis:8-alpine`
- [ ] If incompatible: retain `redis:7.4.10-alpine` (exact patch)
- [ ] Commit: `chore(redis): upgrade observability Redis baseline` (or `chore(redis): pin Redis 7.4.10`)

## Slice F — Base images / digest alignment

- [ ] Record distroless multi-arch index digest
- [ ] Verify Go builder and Python base tags
- [ ] Commit: `docs(images): document image policy and migration procedures`

## Closure

- [ ] Cross-repo verification: agent-core, agent-harness, go-microservices, openspec-store
- [ ] Full-store OpenSpec validation
- [ ] Independent final review
- [ ] Archive OpenSpec change
