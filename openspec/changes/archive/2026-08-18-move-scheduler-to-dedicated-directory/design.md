## Context

The scheduler's Docker deployment currently lives inside `agent-core/`:
- Dockerfile + entrypoint + generators at `agent-core/deployments/scheduler/`
- Scheduler service defined in `agent-core/compose.yaml` alongside 13 other services
- Build context is `context: ..` (workspace root) — reaches outside agent-core
- Bind-mounts reference `../sibling-repos` (8 repos)

The `decouple-scheduler-workflows-from-agent-core` change decoupled the scheduler's *code* (workflow functions moved to individual repos). This change decouples its *deployment*.

## Goals / Non-Goals

**Goals:**
- Scheduler gets its own directory (`tdt-scheduler/`) with `context: .` (no more `..` hack)
- Scheduler has its own `compose.yaml` — clean ownership boundary
- Postgres remains shared (no second DB instance)
- All existing behavior preserved (same Dockerfile, same entrypoint, same runtime, `uv run` for all Python execution)

**Non-Goals:**
- Changing the Docker image contents or runtime behavior
- Moving the scheduler framework (tdt-core/scheduler/) — that's a library, not deployment
- Creating a git repo for `tdt-scheduler/` — it's deployment files, not application code
- Changing how YAML manifests are generated or loaded
- Modifying the DBOS engine or tdt-core scheduler framework

## Decisions

### D1: Dedicated `tdt-scheduler/` directory at workspace root

**Decision:** Create `~/Developer/tdt-scheduler/` containing the Dockerfile, entrypoint.sh, generators/, dispatch_manifest_generation.py, dependency_integrity_gate.py, and a new compose.yaml. The build context remains `..` (workspace root) because the Dockerfile COPY paths reference sibling repos (`../tdt-core`, `../jira-daily-reports`, etc.) that are only reachable from the workspace root.

**Rationale:** The scheduler serves the entire workspace, not agent-core. A dedicated directory makes ownership explicit. The `context: ..` pattern is correct for a cross-repo service — the issue was ownership, not the context direction. This completes the decoupling story started by `decouple-scheduler-workflows-from-agent-core`.

**Why `context: .` is infeasible:** The Dockerfile at lines 42-68 COPYs from `agent-core/`, `tdt-core/`, `jira-daily-reports/`, `code-daily-scan/`, `jira-epic-report/`, `jira-skill/`, `webhook-receiver/`, `tdt-sheets/`, `tdt-observability/`, and `ai-review/`. These are all siblings at the workspace root. Docker restricts COPY to the build-context tree, so `context: .` (tdt-scheduler/) cannot reach them. `context: ..` (workspace root) is the only viable option without restructuring the Dockerfile to eliminate sibling COPYs (a much larger change).

**Alternative considered:** Keep in agent-core but split compose files → rejected because it still conflates ownership.

### D2: Postgres shared via Docker network (not co-located)

**Decision:** The scheduler's compose.yaml connects to agent-core's postgres via a shared Docker network. The postgres service stays in `agent-core/compose.yaml`. The scheduler uses `external: true` network referencing agent-core's default network.

**Rationale:** Postgres is shared infrastructure. Duplicating it wastes resources. The scheduler already uses its own logical database (`tdt_scheduler`) on the shared server.

**Network setup:** Agent-core's compose defines `agent-core-local_default` network. The scheduler's compose references it as external:
```yaml
networks:
  default:
    external: true
    name: agent-core-local_default
```

**Alternative considered:** Co-locate postgres in both compose files → rejected because it creates two postgres instances fighting for the same port and data directory.

### D3: postgres-backup moves with the scheduler

**Decision:** The `postgres-backup` service (which backs up `tdt_scheduler_dbos_sys`) moves to `tdt-scheduler/compose.yaml`.

**Rationale:** The backup targets the scheduler's system database. It logically belongs with the scheduler. It connects to the same shared postgres via the Docker network.

**Alternative considered:** Keep in agent-core → rejected because the backup is scheduler-specific (backs up `tdt_scheduler_dbos_sys`, not `agent_core`).

### D4: verify_scheduler_compose_up.sh rewritten, not just path-updated

**Decision:** Rewrite `agent-core/scripts/verify_scheduler_compose_up.sh` to work with the new `tdt-scheduler/compose.yaml`. The current script does `docker compose down -v` which would tear down ALL agent-core services including postgres data. The rewrite must:
- Scope `down -v` to only the scheduler's compose project
- Add a postgres-running precondition check
- Use `-f tdt-scheduler/compose.yaml` or `cd tdt-scheduler` for scheduler commands
- Restructure the verification flow

**Rationale:** The script is in agent-core's git repo and is critical for post-deploy validation. A simple path update is insufficient — the `down -v` semantics change fundamentally when postgres is in a different compose project.

**Alternative considered:** Move script to tdt-scheduler/ → rejected because it's part of agent-core's development workflow.

**Note:** `agent-core/scripts/docker-dev.sh` does NOT reference the scheduler and needs no changes.

### D5: Container naming with explicit service names

**Decision:** Set explicit `container_name` in tdt-scheduler/compose.yaml to maintain predictable container names for log references and health checks.

**Rationale:** Docker Compose generates container names from `<project>-<service>-<index>`. Moving from `agent-core-local` to `tdt-scheduler` project changes the scheduler container name. Setting explicit names avoids surprises.

**Implementation:**
```yaml
services:
  scheduler:
    container_name: tdt-scheduler
  postgres-backup:
    container_name: tdt-scheduler-backup
```

### D6: .env.docker for scheduler-specific overrides

**Decision:** Create `tdt-scheduler/.env.docker` with scheduler-specific environment overrides (SCHEDULER_POSTGRES_DSN, etc.). The compose.yaml references it via `env_file`.

**Rationale:** The scheduler needs its own env overrides (e.g., DSN pointing to shared postgres via Docker network hostname). Separating this from agent-core's .env.docker keeps concerns clean.

## Risks / Trade-offs

- **[Docker network discovery]** → When scheduler and postgres are in different compose projects, they need a shared network. Mitigation: use `external: true` network referencing agent-core's default network. The scheduler's compose.yaml defines the network as external.

- **[postgres startup ordering]** → Scheduler depends on postgres being healthy, but postgres is in a different compose project. Mitigation: agent-core's postgres must be running before the scheduler starts. The `restart: unless-stopped` policy on both ensures eventual consistency. For explicit ordering, the operator starts agent-core first.

- **[Script references]** → Agent-core scripts reference `docker compose build scheduler` and `docker compose up -d scheduler`. These need updating to `-f tdt-scheduler/compose.yaml`. Mitigation: update scripts and verify.

- **[Container naming]** → Container names change from `agent-core-local-scheduler-1` to `tdt-scheduler`. This affects log references and health checks. Mitigation: set explicit `container_name` in compose.yaml.

## Migration Plan

1. Create `tdt-scheduler/` directory with Dockerfile, entrypoint.sh, generators/, dispatch_manifest_generation.py, dependency_integrity_gate.py
2. Ensure Docker network exists: `docker network inspect agent-core-local_default` — if not, start agent-core postgres first (`cd agent-core && docker compose up -d postgres`)
3. Create `tdt-scheduler/compose.yaml` with scheduler + postgres-backup services, shared postgres network (external: true). **Critical**: volume mount for agent-core must be `../agent-core:/workspace/agent-core` (not `..:/workspace/agent-core`) so pyproject.toml is at `/workspace/agent-core/pyproject.toml` for `uv run` project discovery.
4. Create `tdt-scheduler/.env.docker` with scheduler-specific env overrides
5. Update Dockerfile COPY paths from `agent-core/deployments/scheduler/` to `tdt-scheduler/`
6. Remove scheduler and postgres-backup from `agent-core/compose.yaml`
7. Rewrite `agent-core/scripts/verify_scheduler_compose_up.sh` for new location (scope down -v, add postgres precondition)
8. Update `tdt-core/src/tdt_core/scheduler/README.md` reference to compose location
9. Update `generators/__init__.py` docstring reference from `agent-core/compose.yaml` to `tdt-scheduler/compose.yaml`
10. Verify agent-core compose still works: `cd agent-core && docker compose config`
11. Build and verify: `cd tdt-scheduler && docker compose build scheduler && TDT_HOME=~/.tdt docker compose up -d scheduler`
12. Verify health: `curl http://127.0.0.1:9100/scheduler/health`
13. Verify schedules: `curl http://127.0.0.1:9100/scheduler/schedules`
14. Clean up old files from agent-core/deployments/scheduler/

**Rollback:** Move files back to `agent-core/deployments/scheduler/`, restore scheduler service in `agent-core/compose.yaml`, revert script changes, delete `tdt-scheduler/`.

## Open Questions

- Should `tdt-scheduler/` be a git repository or just a directory of deployment files? Currently leaning toward "just a directory" since the files are simple and don't change often. But if it grows, a repo might be warranted.
