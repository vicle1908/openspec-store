## Why

The scheduler is cross-repo infrastructure serving 8+ repos, but its Docker deployment lives inside `agent-core/`. Its build context is `context: ..` (workspace root), its bind-mounts reference `../sibling-repos`, and its compose project is named `agent-core-local`. This creates confusing ownership: is the scheduler part of agent-core, or independent?

The `decouple-scheduler-workflows-from-agent-core` change decoupled the scheduler's *code* from agent-core. This change decouples its *deployment*.

## What Changes

- **Create `~/Developer/tdt-scheduler/`** — dedicated directory for the scheduler Docker service containing: Dockerfile, entrypoint.sh, generators/, dispatch_manifest_generation.py, dependency_integrity_gate.py, compose.yaml
- **New `tdt-scheduler/compose.yaml`** — scheduler service with `context: ..` (workspace root, needed because Dockerfile COPY paths reference sibling repos), shared postgres via Docker network
- **Move postgres-backup** — the backup service targets `tdt_scheduler_dbos_sys`, so it moves with the scheduler
- **Remove scheduler from `agent-core/compose.yaml`** — agent-core keeps: app, postgres, langfuse-*, minio, mlflow, otel-collector
- **BREAKING**: `docker compose build scheduler` must now run from `tdt-scheduler/` instead of `agent-core/`
- **BREAKING**: `docker compose up -d scheduler` must now run from `tdt-scheduler/` (or `-f tdt-scheduler/compose.yaml`)
- **Update references**: tdt-core README, verify_scheduler_compose_up.sh (substantial rewrite), generators/__init__.py docstring

## Capabilities

### Modified Capabilities

- `scheduler-docker-deployment`: Dockerfile path changes from `agent-core/deployments/scheduler/Dockerfile` to `tdt-scheduler/Dockerfile`. Compose project separates from agent-core.
- `scheduler-entrypoint`: Entrypoint location changes; no functional change to entrypoint behavior.
- `scheduler-dockerfile-canonicalization`: Canonical Dockerfile path changes.
- `agent-core-docker-local-development`: Scheduler service removed from agent-core's compose.yaml.

### New Capabilities

None — this is a deployment restructuring, not a behavior change.

## Non-Goals

- Changing the scheduler Docker image contents (same Dockerfile, same entrypoint logic)
- Changing the scheduler's runtime behavior (same `tdt-scheduler serve`)
- Changing how YAML manifests are generated or loaded
- Changing the DBOS engine or tdt-core scheduler framework
- Modifying the scheduler's health API or CLI

## Ownership Boundaries

| Component | Current Location | After Change |
|-----------|-----------------|--------------|
| Dockerfile | `agent-core/deployments/scheduler/Dockerfile` | `tdt-scheduler/Dockerfile` |
| entrypoint.sh | `agent-core/deployments/scheduler/entrypoint.sh` | `tdt-scheduler/entrypoint.sh` |
| generators/ | `agent-core/deployments/scheduler/generators/` | `tdt-scheduler/generators/` |
| dispatch_manifest_generation.py | `agent-core/deployments/scheduler/` | `tdt-scheduler/` |
| dependency_integrity_gate.py | `agent-core/deployments/scheduler/` | `tdt-scheduler/` |
| compose.yaml (scheduler) | `agent-core/compose.yaml` (shared) | `tdt-scheduler/compose.yaml` (own) |
| postgres-backup | `agent-core/compose.yaml` | `tdt-scheduler/compose.yaml` |
| postgres | `agent-core/compose.yaml` (unchanged) | `agent-core/compose.yaml` (unchanged) |

## Impact

- **Code repos touched**: agent-core (compose cleanup, script updates), tdt-core (README update)
- **New directory**: `~/Developer/tdt-scheduler/` (standalone, not a git repo — deployment files only)
- **Docker network**: scheduler and agent-core postgres must share a network (via `external: true` or `docker network connect`)
- **Scripts affected**: `agent-core/scripts/verify_scheduler_compose_up.sh` (substantial rewrite needed — `docker compose down -v` must be scoped to scheduler only, not agent-core stack)
- **Risk**: LOW — deployment restructuring only; no runtime behavior changes. Rollback: move files back and restore compose.yaml
