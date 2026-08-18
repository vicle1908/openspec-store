## 1. Create tdt-scheduler/ directory structure

- [x] 1.1 Create `~/Developer/tdt-scheduler/` directory
- [x] 1.2 Copy `agent-core/deployments/scheduler/Dockerfile` → `tdt-scheduler/Dockerfile` (verbatim — same content, new location)
- [x] 1.3 Copy `agent-core/deployments/scheduler/entrypoint.sh` → `tdt-scheduler/entrypoint.sh`
- [x] 1.4 Copy `agent-core/deployments/scheduler/generators/` → `tdt-scheduler/generators/` (all .py files)
- [x] 1.5 Copy `agent-core/deployments/scheduler/dispatch_manifest_generation.py` → `tdt-scheduler/`
- [x] 1.6 Copy `agent-core/deployments/scheduler/dependency_integrity_gate.py` → `tdt-scheduler/`
- [x] 1.7 Remove `__pycache__/` directories from copied files

## 2. Create tdt-scheduler/compose.yaml

- [x] 2.1 Create `tdt-scheduler/compose.yaml` with project name `tdt-scheduler`
- [x] 2.2 Define scheduler service: `build: { context: .., dockerfile: tdt-scheduler/Dockerfile }`, `image: tdt-scheduler:local`, `restart: unless-stopped`
- [x] 2.3 Set explicit `container_name: tdt-scheduler` for predictable naming
- [x] 2.4 Add shared postgres network: `networks: { default: { external: true, name: agent-core-local_default } }`
- [x] 2.5 Add postgres-backup service with `container_name: tdt-scheduler-backup`
- [x] 2.6 Copy volume mounts from agent-core compose (paths remain `../sibling-repo` relative to workspace root — same as current)
- [x] 2.7 Keep `working_dir: /workspace/agent-core/src` (scheduler imports agent_core)
- [x] 2.8 Add env_file reference to `.env.docker`
- [x] 2.9 Copy environment block from agent-core compose (TDT_HOME, SCHEDULER_POSTGRES_DSN, TDT_SCHEDULER_SETUP_MODULE, etc.)
- [x] 2.10 Verify compose config: `cd tdt-scheduler && docker compose config`

## 3. Create tdt-scheduler/.env.docker

- [x] 3.1 Create `tdt-scheduler/.env.docker`
- [x] 3.2 Set `SCHEDULER_POSTGRES_DSN=postgresql://agent_core:agent_core_dev@postgres:5432/tdt_scheduler` (Docker-internal hostname)
- [x] 3.3 Add host-side override comment: `SCHEDULER_POSTGRES_DSN=postgresql://agent_core:agent_core_dev@127.0.0.1:54329/tdt_scheduler` (for host-side access)

## 4. Remove scheduler from agent-core/compose.yaml

- [x] 4.1 Remove `scheduler` service block from `agent-core/compose.yaml`
- [x] 4.2 Remove `postgres-backup` service block from `agent-core/compose.yaml`
- [x] 4.3 Remove scheduler-related comments referencing `agent-core/deployments/scheduler/`
- [x] 4.4 Verify agent-core compose still works: `cd agent-core && docker compose config`

## 5. Rewrite verify_scheduler_compose_up.sh

- [x] 5.1 Rewrite `agent-core/scripts/verify_scheduler_compose_up.sh`:
  - Change `COMPOSE_FILE` to `tdt-scheduler/compose.yaml` (or use `-f` flag)
  - Remove `docker compose down -v` (it would tear down ALL agent-core services) — replace with scoped scheduler-only teardown
  - Add postgres-running precondition check (agent-core postgres must be up)
  - Add Docker network existence check (`docker network inspect agent-core-local_default`)
  - Update all `docker compose` commands to use `-f tdt-scheduler/compose.yaml`
  - Update container name references from `agent-core-local-scheduler-1` to `tdt-scheduler`
- [x] 5.2 Run verify script to confirm it passes (requires agent-core postgres running)

## 6. Update docs

- [x] 6.1 Update `tdt-core/src/tdt_core/scheduler/README.md` — change `agent-core/compose.yaml` reference to `tdt-scheduler/compose.yaml`
- [x] 6.2 Update `agent-core/docs/deployment-governance.md` if it references scheduler compose
- [x] 6.3 Update `generators/__init__.py` line 15 docstring: change `agent-core/compose.yaml` to `tdt-scheduler/compose.yaml`
- [x] 6.4 Update container name references from `agent-core-local-scheduler-1` to `tdt-scheduler`

## 7. Build and verify

- [x] 7.1 Ensure Docker network exists: `docker network inspect agent-core-local_default` (if not, run `cd agent-core && docker compose up -d postgres` first)
- [x] 7.2 Build scheduler image: `cd tdt-scheduler && docker compose build scheduler`
- [x] 7.3 Start scheduler: `cd tdt-scheduler && TDT_HOME=~/.tdt docker compose up -d scheduler`
- [x] 7.4 Wait for health: `curl http://127.0.0.1:9100/scheduler/health`
- [x] 7.5 Verify schedules: `curl http://127.0.0.1:9100/scheduler/schedules | jq '.[].name'`
- [x] 7.6 Verify stale_workflow_cleaner is registered and ACTIVE
- [x] 7.7 Stop scheduler: `cd tdt-scheduler && docker compose stop scheduler`

## 8. Clean up old files

- [x] 8.1 Remove `agent-core/deployments/scheduler/Dockerfile`
- [x] 8.2 Remove `agent-core/deployments/scheduler/entrypoint.sh`
- [x] 8.3 Remove `agent-core/deployments/scheduler/generators/`
- [x] 8.4 Remove `agent-core/deployments/scheduler/dispatch_manifest_generation.py`
- [x] 8.5 Remove `agent-core/deployments/scheduler/dependency_integrity_gate.py`
- [x] 8.6 Remove `agent-core/deployments/scheduler/__pycache__/` if present
- [x] 8.7 Verify agent-core tests still pass

## 9. Commit

- [x] 9.1 Commit tdt-scheduler/ changes (new directory with compose + deployment files)
- [x] 9.2 Commit agent-core changes (compose cleanup, script rewrite, file removals)
- [x] 9.3 Commit tdt-core README update
- [x] 9.4 Commit openspec-store change (proposal, specs, design, tasks)
