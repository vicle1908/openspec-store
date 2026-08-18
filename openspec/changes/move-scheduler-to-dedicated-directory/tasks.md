## 1. Create tdt-scheduler/ directory structure

- [ ] 1.1 Create `~/Developer/tdt-scheduler/` directory
- [ ] 1.2 Copy `agent-core/deployments/scheduler/Dockerfile` → `tdt-scheduler/Dockerfile`
- [ ] 1.3 Copy `agent-core/deployments/scheduler/entrypoint.sh` → `tdt-scheduler/entrypoint.sh`
- [ ] 1.4 Copy `agent-core/deployments/scheduler/generators/` → `tdt-scheduler/generators/` (all .py files)
- [ ] 1.5 Copy `agent-core/deployments/scheduler/dispatch_manifest_generation.py` → `tdt-scheduler/`
- [ ] 1.6 Copy `agent-core/deployments/scheduler/dependency_integrity_gate.py` → `tdt-scheduler/`
- [ ] 1.7 Remove `__pycache__/` directories from copied files

## 2. Create tdt-scheduler/compose.yaml

- [ ] 2.1 Create `tdt-scheduler/compose.yaml` with project name `tdt-scheduler`
- [ ] 2.2 Define scheduler service: `build: context: .., dockerfile: tdt-scheduler/Dockerfile`, `image: tdt-scheduler:local`, `restart: unless-stopped`
- [ ] 2.3 Set explicit `container_name: tdt-scheduler` for predictable naming
- [ ] 2.4 Add shared postgres network: `networks: { default: { external: true, name: agent-core-local_default } }`
- [ ] 2.5 Add postgres-backup service with `container_name: tdt-scheduler-backup`
- [ ] 2.6 Copy volume mounts from agent-core compose (paths remain `../sibling-repo` relative to workspace root)
- [ ] 2.7 Keep `working_dir: /workspace/agent-core/src` (scheduler imports agent_core)
- [ ] 2.8 Add env_file reference to `.env.docker`
- [ ] 2.9 Copy environment block from agent-core compose (TDT_HOME, SCHEDULER_POSTGRES_DSN, etc.)
- [ ] 2.10 Verify compose config: `cd tdt-scheduler && docker compose config`

## 3. Create tdt-scheduler/.env.docker

- [ ] 3.1 Create `tdt-scheduler/.env.docker` with SCHEDULER_POSTGRES_DSN pointing to shared postgres via Docker network hostname
- [ ] 3.2 Set `SCHEDULER_POSTGRES_DSN=postgresql://agent_core:agent_core_dev@postgres:5432/tdt_scheduler`
- [ ] 3.3 Add other scheduler-specific env overrides if needed

## 4. Remove scheduler from agent-core/compose.yaml

- [ ] 4.1 Remove `scheduler` service block from `agent-core/compose.yaml`
- [ ] 4.2 Remove `postgres-backup` service block from `agent-core/compose.yaml`
- [ ] 4.3 Remove scheduler-related comments referencing `agent-core/deployments/scheduler/`
- [ ] 4.4 Verify agent-core compose still works: `cd agent-core && docker compose config`

## 5. Update scripts

- [ ] 5.1 Update `agent-core/scripts/verify_scheduler_compose_up.sh`: change `cd "$PROJECT_ROOT"` to `cd "${PROJECT_ROOT}/../tdt-scheduler"` for scheduler commands, update `COMPOSE_FILE` path
- [ ] 5.2 Update `agent-core/scripts/docker-dev.sh` if it references scheduler
- [ ] 5.3 Run verify script to confirm it passes (requires agent-core postgres running)

## 6. Update docs

- [ ] 6.1 Update `tdt-core/src/tdt_core/scheduler/README.md` — change `agent-core/compose.yaml` reference to `tdt-scheduler/compose.yaml`
- [ ] 6.2 Update `agent-core/docs/deployment-governance.md` if it references scheduler compose
- [ ] 6.3 Update `agent-core/AGENTS.md` if it references scheduler compose
- [ ] 6.4 Update container name references from `agent-core-local-scheduler-1` to `tdt-scheduler`

## 7. Build and verify

- [ ] 7.1 Ensure agent-core postgres is running: `cd agent-core && docker compose up -d postgres`
- [ ] 7.2 Build scheduler image: `cd tdt-scheduler && docker compose build scheduler`
- [ ] 7.3 Start scheduler: `cd tdt-scheduler && TDT_HOME=~/.tdt docker compose up -d scheduler`
- [ ] 7.4 Wait for health: `curl http://127.0.0.1:9100/scheduler/health`
- [ ] 7.5 Verify schedules: `curl http://127.0.0.1:9100/scheduler/schedules | jq '.[].name'`
- [ ] 7.6 Verify stale_workflow_cleaner is registered and ACTIVE
- [ ] 7.7 Stop scheduler: `cd tdt-scheduler && docker compose stop scheduler`

## 8. Clean up old files

- [ ] 8.1 Remove `agent-core/deployments/scheduler/Dockerfile`
- [ ] 8.2 Remove `agent-core/deployments/scheduler/entrypoint.sh`
- [ ] 8.3 Remove `agent-core/deployments/scheduler/generators/`
- [ ] 8.4 Remove `agent-core/deployments/scheduler/dispatch_manifest_generation.py`
- [ ] 8.5 Remove `agent-core/deployments/scheduler/dependency_integrity_gate.py`
- [ ] 8.6 Verify agent-core tests still pass

## 9. Commit

- [ ] 9.1 Commit tdt-scheduler/ changes (new directory with compose + deployment files)
- [ ] 9.2 Commit agent-core changes (compose cleanup, script updates, file removals)
- [ ] 9.3 Commit tdt-core README update
- [ ] 9.4 Commit openspec-store change (proposal, specs, design, tasks)
