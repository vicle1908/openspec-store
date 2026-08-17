# Design: Upgrade ecosystem container images

## Image-Tag Governance Policy

All stateful services (databases, message brokers, observability backends) SHALL use exact, immutable release tags. Floating tags (`latest`, major-only) are prohibited for stateful services. Exceptions require: documented rationale in Compose comments, pinned digest, verified `linux/amd64` + `linux/arm64`, and a 30-day re-pin review. Local images (`:local-dev`, `:local`) are exempt.

## PostgreSQL Volume Safety

PostgreSQL 18 cannot open a PostgreSQL 16 data directory. No volumes exist locally, so local testing uses fresh initialization. Other deployments may have PG16 volumes.

- Never auto-delete PG16 volumes
- Use PG18 mount layout (`/var/lib/postgresql`)
- Preserve old volumes for rollback
- For retained data: start PG16 against original volume → `pg_dump` → fresh PG18 volume → `pg_restore`
- Test fresh startup and existing-data migration separately
- Disposal strategy: disposable local metadata uses fresh PG18 volume; persistent environments use dump/restore; rollback retains original PG16 volume untouched

## Research Matrix (4-Column: Current → Upstream latest → App-supported baseline → Selected target)

| Service | Current | Upstream latest | Application-supported baseline | Selected target | Source |
|---------|---------|----------------|-------------------------------|-----------------|--------|
| **PostgreSQL** (agent-core) | `18.6-trixie` | 18.6-trixie | >=15 (Langfuse v4) | `18.6-trixie` | Docker Hub ✅ amd64+arm64 |
| **PostgreSQL** (go-micro) | `18.4-alpine` | 18.6-alpine | N/A | `18.6-alpine` | Docker Hub ✅ amd64+arm64 |
| **Langfuse server** | `3.219` | 4.11 | 4.11.0 | `4.11.0` | Docker Hub ✅ amd64+arm64 |
| **Langfuse worker** | `3` (float) | 4.11 | 4.11.0 | `4.11.0` | Docker Hub ✅ amd64+arm64 |
| **ClickHouse** (Langfuse) | standalone | 26.7 | **25.12** (Langfuse baseline) | `25.12.11.4-alpine` | Docker Hub; must be Langfuse-compatible line |
| **Redis** (Langfuse) | standalone | 8.10 | **7** (Langfuse baseline) | `7.4.10-alpine3.21` — Langfuse v4 baseline | Langfuse v4 Compose uses `redis:7` |
| **Redis** (go-micro) | `8.8-alpine` | 8.10.0 | 8.8 | `8.8.1-alpine` | Docker Hub ✅ amd64+arm64 |
| **MinIO server** (Langfuse) | Chainguard | Chainguard | Chainguard (Langfuse v4) | `cgr.dev/chainguard/minio` (latest) | Langfuse v4 Compose baseline |
| **MinIO mc** | `latest` (float) | RELEASE.2025-08-13 | independent | `RELEASE.2025-08-13T08-35-41Z` | Docker Hub ✅ amd64+arm64 |
| **MLflow** | `latest` (float) | v3.15.1 | v3.15.1 | `v3.15.1` | GHCR ✅ amd64+arm64 |
| **ClickHouse** (agent-core) | `latest` (float) | 26.7 | N/A (standalone) | `26.4.5-alpine` | Docker Hub ✅ amd64+arm64 |
| **MinIO server** (agent-core) | `latest` (float) | RELEASE.2025-09-07 | N/A (standalone) | `RELEASE.2025-09-07T16-13-09Z` | Quay.io ✅ amd64+arm64 |
| **OTel Collector** (agent-core) | `0.157.0` | 0.158.0 | 0.158.0 | `0.158.0` | Docker Hub ✅ amd64+arm64 |
| **OTel Collector** (go-micro) | `0.156.0` | 0.158.0 | 0.158.0 | `0.158.0` | Docker Hub ✅ amd64+arm64 |
| **Grafana** (go-micro) | `13.1.1` | 13.1.3 | 13.1.3 | `13.1.3` | GitHub ✅ amd64+arm64 |
| **Mailpit** (go-micro) | `v1.30` | v1.30.7 | v1.30.7 | `v1.30.7` | GitHub ✅ amd64+arm64 |
| **Python** (pgcli base) | `3.13-slim` | 3.14.5 | 3.14.5 | `3.14.5-slim` | Docker Hub ✅ amd64+arm64 |
| **Golang** (build) | `1.26.5-bookworm` | 1.26.5 | 1.26.5 | `1.26.5-bookworm` | Docker Hub ✅ amd64+arm64 |
| **Distroless** | `:nonroot` (mutable) | digest pin | digest pin | record index digest | GCR ✅ amd64+arm64 |
| **Busybox** | `1.37.0-uclibc` | 1.37.0 | 1.37.0 | `1.37.0-uclibc` | Docker Hub ✅ amd64+arm64 |
| **Valkey** | `9.1-alpine` | 9.1 | 9.1 | `9.1-alpine` | Docker Hub ✅ amd64+arm64 |
| **OTel LGTM** | `0.29.0` | 0.29.0 | 0.29.0 | `0.29.0` | Docker Hub ✅ amd64+arm64 |
| **Redis exporter** | `v1.87.0` | v1.87.0 | v1.87.0 | `v1.87.0` | GitHub ✅ amd64+arm64 |
| **kcat** | `8.1.2` | 8.1.2 | 8.1.2 | `8.1.2` | Docker Hub ✅ amd64+arm64 |
| **Kafka UI** | `v1.0.0` | v1.0.0 | v1.0.0 | `v1.0.0` | GHCR ✅ amd64+arm64 |

### Key decisions

1. **ClickHouse (Langfuse)**: Pin to `25.12.11.4-alpine` — NOT 26.x. Langfuse v4.11.0 official Compose uses ClickHouse 25.12 line.
2. **Redis (Langfuse)**: **DEFERRED** — retain Redis 7 patch. Langfuse v4.11.0 official Compose uses `redis:7`. Redis 8 compatibility is not proven and not in Langfuse's official baseline.
3. **MinIO (Langfuse)**: Pin Chainguard MinIO by OCI digest (sha256:6196...04b) — verified amd64+arm64. This is Langfuse v4.11.0 baseline.
4. **MLflow**: `v3.15.1` on GHCR (v2.28.1 does not exist).
5. **PostgreSQL (Langfuse)**: Use 18.6 — Langfuse v4 states `>=15` support. Fresh-start local test required to prove.

## Langfuse v4.11.0 Migration Notes

From the official `v4.11.0` Compose file:
- Service renamed: `langfuse` → `langfuse-web`, `langfuse-worker` (new, separate)
- PostgreSQL: `${POSTGRES_VERSION:-17}` — Langfuse defaults to PG 17 but states `>=15`
- ClickHouse: `clickhouse/clickhouse-server:25.12` — pinned to 25.x line
- Redis: `redis:7` — pinned, uses `--requirepass` and `--maxmemory-policy noeviction`
- MinIO: `cgr.dev/chainguard/minio` — Chainguard hardened variant, NOT upstream MinIO
- New env vars: `SALT`, `ENCRYPTION_KEY`, `LANGFUSE_S3_EVENT_UPLOAD_*`, `LANGFUSE_S3_MEDIA_UPLOAD_*`, `LANGFUSE_S3_BATCH_EXPORT_*`
- S3 storage: uses `http://minio:9000` with `FORCE_PATH_STYLE: true`
- Health check changed: `wget --no-verbose --tries=1 --spider http://localhost:8123/ping`

Environment variable reconciliation required between existing agent-core config and Langfuse v4 official Compose. Differences must be documented.

## Upgrade Slices

| Slice | Scope | Risk | Dependencies |
|-------|-------|------|-------------|
| A | go-microservices patch-level (PG 18.4→18.6, Mailpit, Grafana, OTel, Python) | Low | None |
| B | PostgreSQL volume layout + migration docs | Low | None |
| C | Pin floating tags (ClickHouse agent-core, MLflow, MinIO server, mc) | Medium | None |
| D | Langfuse 3→4 migration (server + worker, ClickHouse 25.12, Redis 7 compat, env/config) | **High** | B, C |
| E | Redis 8 evaluation (only if Langfuse v4 proves compatible) | Medium | D |
| F | Base images / digest alignment (distroless, Go builders) | Low | None |

## Verification Per Slice

1. `docker compose config --quiet`
2. Isolated Compose: `COMPOSE_PROJECT_NAME=image-upgrade-validation`
3. Fresh volumes for destructive/major upgrades
4. Health checks for every service
5. Repo tests, lint, type-check, lock, diff gates
6. OpenSpec strict validation (focused + full-store)
7. `linux/amd64` + `linux/arm64` architecture confirmation
8. GitNexus `detect_changes` for each commit

## Rollback

All changes git-revertible per slice. Old PG16 volumes preserved. Langfuse 4→3: restore PG16 volume, revert tags. Redis 8→7: revert to exact Redis 7 patch.

## Commits

1. `chore(images): update go-microservices patch-level image pins`
2. `fix(compose): use PostgreSQL 18 volume layout and migration-safe volumes`
3. `chore(images): pin observability infrastructure images`
4. `feat(observability): migrate Langfuse stack to v4`
5. `docs(images): document image policy and migration procedures`
