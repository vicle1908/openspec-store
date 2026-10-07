# Design: Containerize SHB Scheduler with Docker Compose and PostgreSQL 18.6

## Context

See proposal.md for motivation. The current `shb-schedule` package already supports a `postgres` backend via `SchedulerSettings.backend` and `DBOSRuntime`, which sets `dbos_system_schema` from `postgres_schema` (default `shb_scheduler`). The existing config resolves all paths from `Path.home()`, and the current service lifecycle is provided by `shb_schedule/service/launchd.py` (macOS LaunchAgent + Linux systemd text generation). The package depends on editable sibling sources `shb-core` and `shb-tools` declared via `[tool.uv.sources]` with local paths.

A live feasibility POC confirmed that DBOS Transact 3.2.0 initializes against a clean `postgres:18.6-alpine` (18.6) instance in 0.706s, creating all 13 system tables under the `shb_scheduler` schema with zero custom migrations, and successfully executed and persisted a triggered scheduled workflow.

Verified toolchain facts (used below): official Python image `python:3.14-slim` (3.14.8) exists multi-arch; `postgres:18.6-alpine` is a valid published tag identical to current `18-alpine`; `uv` latest stable is `0.12.23` (pin via `ghcr.io/astral-sh/uv:0.12.23`); `shb-schedule/uv.lock` resolves `psycopg-binary` 3.3.6 which ships pre-built `cp314` manylinux wheels, so `uv sync` needs no `gcc`/`libpq-dev`.

## Goals / Non-Goals

**Goals:**
- Provide a portable Compose stack (`compose.yaml`) that runs the scheduler and PostgreSQL 18.6 with a single command on any Docker host.
- Ship a multi-stage `Dockerfile` that installs the scheduler plus sibling `shb-core`/`shb-tools` sources without host binary dependencies and without dev-tool or editable-symlink leakage into the runtime image.
- Preserve existing CLI verbs (`validate`, `list`, `run-now`, `reload`) and HTTP endpoints on port 9110.
- Keep the base production profile lean: manifests-only read-only mount.

**Non-Goals:**
- No Kubernetes/Helm manifests or cloud-specific orchestration.
- No multi-tenant or multi-database sharing; a single dedicated `shb_scheduler` schema.
- No automated migration of legacy SQLite history into PostgreSQL (clean-start only).
- No source-repository mounting in base production mode.

## Decisions

### 1. Compose service topology (db + scheduler)
Two services: `db` (`postgres:18.6-alpine`) and `scheduler` (built image). Use `depends_on` with `condition: service_healthy` gated by `pg_isready`. Rationale: guarantees DB readiness before DBOS launch, avoiding startup races observed in ad-hoc ordering. Alternative considered: a single container bundling Postgres — rejected (anti-pattern, poor data durability).

**Health-check requirement (verified pitfall):** The official `postgres` image on Docker Hub ships **no** built-in `HEALTHCHECK` (verified `<nil>`). `docker compose up` aborts with `service db has no healthcheck configured` unless `compose.yaml` explicitly defines a `healthcheck:` block on the `db` service, e.g. `test: ["CMD-SHELL", "pg_isready -U shb_scheduler -d shb_scheduler"]`, `interval: 5s`, `timeout: 5s`, `retries: 5`, `start_period: 10s`. This is mandated in Task 2.1.

### 2. Database provenance: fresh, named volume
PostgreSQL data lives in a Docker **named volume** (not a bind mount) to avoid crash-unsafe behavior on macOS Docker Desktop VirtioFS bind mounts. Rationale: (a) PostgreSQL `initdb` enforces strict POSIX modes (`0700`/`0750`) and fails when the container `postgres` UID/GID cannot `chmod` files on a macOS-owned VirtioFS path; (b) VirtioFS `fsync` latency risks WAL torn-page corruption; (c) the OmniRoute project already documents that VirtioFS bind mounts corrupt SQLite WAL DBs. A named volume resides on the Linux VM ext4 block device (`Docker.raw`), giving correct POSIX permissions, fast `fsync`, and crash-safe WAL. Alternative considered: host bind mount — rejected for the corruption risk and permission drift on Linux.

**PostgreSQL 18 Volume Layout:** In official `postgres:18+` images, `PGDATA` defaults to `/var/lib/postgresql/18/docker`. When mounting the named volume `shb-scheduler-pgdata` to `/var/lib/postgresql/data`, the `db` container environment MUST explicitly set `PGDATA=/var/lib/postgresql/data/pgdata` (or mount the volume at `/var/lib/postgresql`). This prevents PostgreSQL 18 from writing outside the volume into ephemeral container storage.
### 3. Image build context and sibling dependencies
Build with `context: ..` (the `~/Developer/shb` parent) so the Dockerfile can `COPY` `shb-core`, `shb-tools`, and `shb-schedule` into the image and run `uv sync --frozen`. Rationale: the package declares editable local-path sibling dependencies, so the image must contain those sources. Alternative considered: Buildx `additional_contexts` — viable but requires newer Compose/Buildx; `context: ..` is universally supported.

**`.dockerignore` placement (critical defect if missed):** With `context: ..`, BuildKit looks for the ignore file at the **build-context root** (`~/Developer/shb/.dockerignore`) or at `<Dockerfile-path>.dockerignore` (`shb-schedule/Dockerfile.dockerignore`). A file placed at `shb-schedule/.dockerignore` is **completely ignored**, sending the entire 2.4 GB / 13-repo parent tree (including `.venv/` and `.gitnexus/`) into the build context. Mandate `shb-schedule/Dockerfile.dockerignore` using recursive globs: `**/.venv/`, `**/.gitnexus/`, `**/graphify-out/`, `**/__pycache__/`, `**/.git/`. The Dockerfile MUST use selective `COPY` (`COPY shb-core /app/shb-core`, `COPY shb-tools /app/shb-tools`, `COPY shb-schedule /app/shb-schedule`) preserving the sibling layout `pyproject.toml` expects (`../shb-core`, `../shb-tools`); never `COPY . /app`.

**uv and psycopg wiring:** Copy the pinned uv binary from the official image (`COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /uvx /bin/`). No C toolchain is required because `psycopg-binary` 3.3.6 ships pre-compiled Python 3.14 manylinux wheels. Run `uv sync --frozen --no-dev --no-editable` (or set `UV_NO_DEV=1`, `UV_NO_EDITABLE=1`) so (a) the dev group (pytest, ruff, mypy) is excluded from the image, and (b) `shb-core`/`shb-tools`/`shb-schedule` are compiled into site-packages as real wheels — without `--no-editable`, the editable `.pth` symlinks break when only `.venv` is copied to the runner stage. Use `ENV UV_COMPILE_BYTECODE=1` and a `--mount=type=cache,target=/root/.cache/uv` cache mount.

### 4. Backend selection and schema isolation
Select PostgreSQL by setting `SHB_SCHEDULER_BACKEND=postgres`, `SHB_SCHEDULER_DATABASE_URL=postgresql://...@db:5432/shb_scheduler`, and `SHB_SCHEDULER_POSTGRES_SCHEMA=shb_scheduler`. Rationale: reuses the existing `SchedulerSettings` contract with no code shape change. The DBOS runtime already applies `dbos_system_schema` when backend is postgres (verified in `src/shb_schedule/engine/dbos_runtime.py`).

### 5. Manifest-only mount policy
Mount `${HOME}/.shb/schedules:/etc/shb/schedules:ro` and set `SHB_SCHEDULER_SCHEDULES_DIR=/etc/shb/schedules`. Rationale: the scheduler only needs declarative manifests to reconcile; code repositories are irrelevant to orchestration and would introduce UID/git-ownership hazards. A dev-only `compose.override.yaml` MAY add a read-only workspace mount for local audit workloads.

### 6. Removal of host service installers
Delete `src/shb_schedule/service/launchd.py`, the `service` Typer sub-app, and the `service install` command in `cli.py`. Rationale: eliminates the platform-fragmented, unused-in-container path and respects the "no host process dependency" goal. Alternative considered: keep as a legacy fallback — rejected to reduce surface and avoid dual maintenance.

### 7. Transaction boundaries & concurrency model
- DBOS system-schema creation and migrations execute inside `DBOS.launch()`, within the `shb_scheduler` schema; Compose startup ordering is gated by the DB health check.
- Each scheduled workflow execution is a durable DBOS transaction with step-level retries; no cross-schema writes. DBOS queue workers use `SELECT ... FOR UPDATE SKIP LOCKED` (PostgreSQL MVCC row locks), so concurrent `run-now` triggers and queue workers do not hit SQLite-style "database is locked" errors.
- **Single-owner leader election:** `shb-schedule serve` takes an `fcntl.flock` on a lock file. Only one daemon process may be the active leader at a time; PostgreSQL concurrency benefits concurrent *queue workers and CLI triggers*, not multiple concurrent daemon leaders. (See Decision 8 for lock placement in-container.)

### 8. Container network binding and lock isolation
- In the container environment, the daemon MUST listen on `0.0.0.0` so Docker's port bridge (`127.0.0.1:9110:9110`) correctly routes inbound host requests. **Subtle trap (verified in `cli.py`):** the `serve` command hardcodes its Typer default `host='127.0.0.1'` (from `constants.DEFAULT_HEALTH_HOST`) and ignores `settings.host`/`SHB_SCHEDULER_HOST` when bare `shb-schedule serve` is invoked. Therefore the container **entrypoint MUST explicitly pass `--host 0.0.0.0`** (or `cli.py` must be patched to default host to `settings.host`). Outside Docker, the local CLI default remains `127.0.0.1` for developer safety.
- The single-owner leader lock file resides inside the container's private ephemeral filesystem (`/tmp/shb-schedule.lock`), isolating daemon `flock` semantics from host mount latencies or network filesystem locking restrictions.

## Risks / Trade-offs

- **[Worktown bind-mount UID mismatch on Linux]** → Base profile avoids repository mounts entirely; the optional dev override documents `git config --global --add safe.directory` and read-only mounts to prevent writes.
- **[Sibling source drift in image]** → `uv sync --frozen --no-editable` with committed `uv.lock`; rebuild on lock changes; CI should fail if lock is stale.
- **[Docker daemon not running on developer laptops]** → Document that Colima/Docker Desktop/OrbStack must be running; local SQLite mode remains an explicit opt-in fallback via env override.
- **[Clean-start loses prior SQLite history]** → Acceptable per non-goals; document that history is not migrated and Postgres starts empty.
- **[Postgres major-version tag drift]** → Pin the image to `postgres:18.6-alpine` (exact minor, Alpine) and document the expectation in README; `18-alpine` floats with future minor releases.

## Migration Plan

1. Add `Dockerfile`, `compose.yaml`, `compose.override.yaml`, and `shb-schedule/Dockerfile.dockerignore` (see Decision 3 for placement).
2. Remove `service/launchd.py` and the `service install` CLI path.
3. Update `README.md` and `scheduler-skill/SKILL.md` to containerized operation.
4. Deploy: `docker compose up -d`; verify `http://127.0.0.1:9110/scheduler/health` and `docker compose exec scheduler shb-schedule validate /etc/shb/schedules`.
5. Rollback: `docker compose down` and re-run locally via `uv run shb-schedule serve` with `SHB_SCHEDULER_BACKEND=sqlite` if needed.

## Open Questions

- Whether CI should build and smoke-test the image on every PR, or only on release tags (deferrable; does not change specs or approach).
