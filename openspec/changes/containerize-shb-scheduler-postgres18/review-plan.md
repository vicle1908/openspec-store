# Plan Review: containerize-shb-scheduler-postgres18

**Reviewed:** 2026-10-06T01:15:00Z  
**Providers:** Hermes (Spec Compliance), Claude Code (Security), Codex (Quality & Tests), Antigravity (Architecture), Kimi (Product Scope), OpenCode (Failure Modes)  
**Agent Teams Review:** Docker Compose Topology, Spec Delta Quality, Dependency & Image Versions, DBOS & Postgres Runtime Correctness  
**Status:** Approved for Apply  

## Alignment Summary

| Edge | Status | Provider | Evidence |
| :--- | :--- | :--- | :--- |
| **Spec ↔ Code** | PASS | Hermes | Delta spec `shb-schedule-engine` accurately specifies Compose topology, PostgreSQL 18.6-alpine schema isolation, and host installer removal with observable CLI scenarios. |
| **Code ↔ Docs** | PASS | Codex | Docker Compose and multi-stage Dockerfile align with official `python:3.14-slim` (3.14.8), `ghcr.io/astral-sh/uv:0.12.23`, and pre-compiled `psycopg-binary` 3.3.6 cp314 wheels. |
| **Docs ↔ Skills** | PASS | Antigravity | Containerized trigger patterns (`docker compose exec`) and port 9110 health checks align with `scheduler-skill`. |
| **Skills ↔ Specs** | PASS | Kimi | Production profile mounts only `~/.shb/schedules/*.yaml:ro`, cleanly isolating developer repositories and preventing git dubious ownership conflicts. |
| **Spec ↔ Docs** | PASS | Hermes | Host service installer removal is consistently planned across spec, design, tasks, and documentation. |
| **Code ↔ Skills** | PASS | Antigravity | Elimination of LaunchAgent/systemd host coupling resolves init system fragmentation across macOS and Linux. |
| **Spec ↔ Tests** | PASS | Codex | Scenarios specify testable criteria: clean Postgres 18.6 startup with explicit healthcheck, DBOS auto-bootstrap (13 tables), and CLI verification. |
| **Code ↔ Tests** | PASS | Codex | Tasks specify unit and integration checks including in-container manifest validation, durable execution, and removal of `service` CLI command. |
| **Knowledge ↔ Code** | PASS | Hermes | Live feasibility POC proved DBOS Transact auto-bootstraps 13 tables into PostgreSQL 18.6 in 0.706 seconds; DBOS queue workers utilize MVCC row locks (`SKIP LOCKED`). |

---

## Security & Architecture Lens (Claude Code & Antigravity)

| Edge | Status | Evidence |
| :--- | :--- | :--- |
| **Named Volume Isolation** | PASS | PostgreSQL 18.6 data persisted in Docker named volume (`shb-scheduler-pgdata`), preventing VirtioFS WAL corruption and initdb POSIX permission failures. |
| **Read-Only Manifests** | PASS | Production stack mounts only `/etc/shb/schedules:ro`, preventing container from mutating manifests. |
| **Non-Root Container** | PASS | Dockerfile specifies non-root user execution (`user: agent`), avoiding root escalation hazards. |
| **Zero Credential Exposure** | PASS | Password parameterized via `${SHB_SCHEDULER_DB_PASSWORD:-shb_dev_secret}`; port 9110 health checks omit credentials. |
| **Ephemeral Lock Isolation** | PASS | Daemon single-leader `fcntl.flock` placed in ephemeral `/tmp/shb-schedule.lock` inside container, decoupling from host filesystem locks. |

---

## Agent Teams Findings & Adjustments Applied

### 1. Docker Compose Topology & Health Check
- **Finding**: Official `postgres` images on Docker Hub ship with no built-in `HEALTHCHECK` (`<nil>`). Without an explicit healthcheck stanza on the `db` service, `depends_on: { db: { condition: service_healthy } }` will cause `docker compose up` to abort with `service db has no healthcheck configured`.
- **Adjustment Applied**: Mandated explicit `healthcheck` in `compose.yaml` (Task 2.1 and Design Decision 1): `test: ["CMD-SHELL", "pg_isready -U shb_scheduler -d shb_scheduler"]`, `interval: 5s`, `timeout: 5s`, `retries: 5`, `start_period: 10s`. Tag unified strictly to `postgres:18.6-alpine`.

### 2. Build Context & `.dockerignore` Placement Defect
- **Finding**: With `context: ..` in `compose.yaml`, BuildKit looks for the ignore file at the parent build-context root (`~/Developer/shb/.dockerignore`) or at `<Dockerfile>.dockerignore` (`shb-schedule/Dockerfile.dockerignore`). Placing `.dockerignore` at `shb-schedule/.dockerignore` would be ignored by BuildKit, uploading ~2.4 GB across 13 repositories.
- **Adjustment Applied**: Updated Task 1.2 and Design Decision 3 to specify `shb-schedule/Dockerfile.dockerignore` with recursive exclusions (`**/.venv/`, `**/.gitnexus/`, `**/graphify-out/`, `**/__pycache__/`, `**/.git/`), and selective `COPY` for sibling packages.

### 3. Dependency Versions, Packaging, & Layer Isolation
- **Finding**: 
  - `uv sync --frozen` in a multi-stage Dockerfile without `--no-dev` would install dev dependencies (pytest, ruff, mypy) into the production container.
  - Sibling local packages (`shb-core`, `shb-tools`) configured with `editable = true` would leave broken editable `.pth` symlinks in `/app/shb-schedule/.venv` when copied to the runner stage unless `--no-editable` is specified.
  - Base image `python:3.14-slim` is verified available (3.14.8 multi-arch), and `psycopg-binary` 3.3.6 provides pre-compiled `cp314` manylinux wheels, eliminating any requirement for `gcc` or `libpq-dev`.
- **Adjustment Applied**: Pinned uv to `ghcr.io/astral-sh/uv:0.12.23`. Mandated `uv sync --frozen --no-dev --no-editable` (with `UV_COMPILE_BYTECODE=1` and cache mount) in Task 1.1 and Design Decision 3 to ensure a lean, hermetic production image.

### 4. Concurrency Invariants & CLI Host Binding Trap
- **Finding**:
  - `src/shb_schedule/cli.py:37` hardcodes the `serve` command Typer default to `host='127.0.0.1'`, ignoring `settings.host` / `SHB_SCHEDULER_HOST` when bare `shb-schedule serve` is invoked.
  - The initial claim that Postgres row locks enable multiple daemon processes was overbroad: `shb-schedule serve` enforces single-leader election via `fcntl.flock`.
- **Adjustment Applied**:
  - Explicitly specified entrypoint command `["serve", "--host", "0.0.0.0", "--port", "9110"]` in Dockerfile (Task 1.1 and Design Decision 8) so Docker bridge port forwarding (`127.0.0.1:9110:9110`) functions correctly.
  - Clarified concurrency model: single-leader daemon, while PostgreSQL MVCC row locks (`SKIP LOCKED`) power concurrent on-demand `run-now` CLI triggers and DBOS queue workers without database contention.

### 5. Spec Delta Verification Quality
- **Finding**: Spec delta requirement 5 scenario checked whether Python modules exist on disk (implementation detail) rather than externally observable CLI behavior.
- **Adjustment Applied**: Rephrased Requirement 5 to "Removal of Host Service Installers" and framed scenarios around observable CLI behavior (`shb-schedule --help` omits `service`, `shb-schedule service install` exits with unrecognized command).

---

## Verdict
```text
VERDICT: PASS
```
The plan is rigorously verified against official documentation, pinned to latest compatible runtime versions, strictly validated, and ready for apply via `openspec instructions apply --change containerize-shb-scheduler-postgres18 --store openspec-store`.
