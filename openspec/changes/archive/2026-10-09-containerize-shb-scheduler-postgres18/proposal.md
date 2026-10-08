# Proposal: Containerize SHB Scheduler with Docker Compose and PostgreSQL 18.6

## Why

The SHB `shb-schedule` daemon currently relies on host-specific process managers (`launchd` on macOS, manual systemd on Linux) and a local SQLite WAL database, creating platform fragmentation, concurrency limits, and operational uncertainty for team servers, CI, and cloud deployments. Standardizing on a containerized architecture using DBOS Transact, Docker Compose, and PostgreSQL 18.6 (`postgres:18.6-alpine`) provides uniform scheduling across all environments while preserving existing CLI workflows for development.

## What Changes

- **New Capability**: `specs/shb-schedule-engine/spec.md` (delta to existing capability) — adds Docker Compose orchestration for the scheduler with PostgreSQL 18.6-alpine backend, eliminating host-dependent service installers.
- **Modified Capability**: `shb-agent-skills/skills/scheduler-skill/SKILL.md` — update documentation to reference containerized deployment patterns (`docker compose up`, `docker compose exec`, health checks).
- **Removed Artifact**: `src/shb_schedule/service/launchd.py` — removed from implementation; replaced by `compose.yaml` + `compose.override.yaml`.
- **New Artifacts**:
  - `shb-schedule/Dockerfile` (multi-stage build, `python:3.14-slim` base, `ghcr.io/astral-sh/uv:0.12.23` pinned, `uv sync --frozen --no-dev --no-editable`, entrypoint `shb-schedule serve --host 0.0.0.0 --port 9110`).
  - `shb-schedule/Dockerfile.dockerignore` (positioned for `context: ..`, excluding `.venv/`, `.gitnexus/`, `graphify-out/`, `__pycache__/`, `.git/`).
  - `shb-schedule/compose.yaml` (base production profile: `postgres:18.6-alpine` with explicit `pg_isready` healthcheck, `shb-scheduler` image, named volume `shb-scheduler-pgdata`).
  - `shb-schedule/compose.override.yaml` (local dev: host port `127.0.0.1:9110:9110`, optional workspace bind-mount).
  - `~/.shb/schedules/*.yaml` manifests are mounted read-only; no source code repositories are mounted in base production mode.
- **Fail-Closed Workflow Contracts**: Workflows fail closed on absent inputs in manifest-only containers: `eod-settlement-recon` removes sample transaction fallbacks to report `ACTION_REQUIRED` instead of faking `BALANCED`; `daily-shb-docs-sync` and `nightly-compliance-scan` report `PARTIAL` rather than `SUCCESS` when all target repositories are unmounted.

**Non-Breaking**: The CLI commands (`shb-schedule validate`, `list`, `run-now`, `reload`) remain available via `docker compose exec`. Local SQLite mode remains opt-in via environment variable overrides (`SHB_SCHEDULER_BACKEND=sqlite`).

**Breaking**: Removal of `shb-schedule service install` as a host-launcher command; users manage the scheduler lifecycle through Docker Compose or explicit environment overrides.

## Capabilities

### New Capabilities

| ID | Name | Purpose |
|---|---|---|
| specs/shb-schedule-engine/spec.md | SHB Schedule Engine (Containerized Variant) | Adds standardized Docker Compose orchestration, PostgreSQL 18.6 schema isolation, and health-probeable daemon lifecycle. |

### Modified Capabilities

| ID | Name | Change Summary |
|---|---|---|
| shb-schedule-engine/spec.md | (existing delta capability) | Extend existing schedule manifest registry to be deployable via Docker Compose only. |
| shb-agent-skills (all skills) | (skill catalog) | Update `scheduler-skill` guidance to reference containerized workflow triggers. |

## Non-Goals

- Do not migrate TDT scheduling workloads; keep them separate (they have their own Compose stack).
- Do not implement multi-repo source-code mounting in base production mode; audits will run with minimal mounts (manifests only).
- Do not introduce custom orchestration frameworks (e.g., Kubernetes CRDs); stay within Docker Compose boundaries.
- Do not modify `shb-tools` logic; it remains pure Python callable from in-container workflows.

## Impact

- **Operational Simplicity**: One command (`docker compose up`) brings up scheduler with PostgreSQL, health probes, and logs. No host dependencies beyond Docker daemon.
- **Concurrent Execution**: PostgreSQL MVCC row-level locking (`SKIP LOCKED`) enables concurrent queue workers and on-demand CLI triggers (`run-now`) without SQLite lock contention, while daemon leader election remains single-owner across container boundaries via PostgreSQL session advisory locking (with local SQLite mode retaining `fcntl.flock`).
- **Platform Independence**: Identical behavior on macOS (Docker Desktop), Linux (systemd + dockerd), CI runners, and cloud VMs.
- **Audit Readiness**: All execution history persisted to Postgres, queryable via SQL or via OpenSpec store audit tools.

## Affected Repositories

- `shb/shb-schedule`: Add Dockerfile, compose files, remove launchd service installer, export CLI entrypoints to containers.
- `platform/openspec-store`: Create delta spec `shb-schedule-engine/spec.md` and artifact tracking change.
- `shb/shb-agent-skills`: Update `scheduler-skill/SKILL.md` documentation (no code changes).
