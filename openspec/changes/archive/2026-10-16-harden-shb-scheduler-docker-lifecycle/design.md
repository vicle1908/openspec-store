# Design

## Context

`shb-schedule` is the canonical durable scheduling engine for Saigon - Hanoi Bank (SHB), powered by DBOS v3.2.0, FastAPI/Starlette health endpoints on port `9110`, and PostgreSQL 18.6 schema isolation (`shb_scheduler`).

Operational probes confirmed that while the containerized stack starts cleanly and reports healthy status (`is_leader: true`), shutdown and log management require alignment with workstation Docker best practices.

## Technical Architecture & Invariants

```
┌─────────────────────────────────────────────────────────────┐
│                       macOS Host                            │
│  - Docker Desktop Login Item (auto-start on boot)           │
│  - LaunchAgent: com.developer.workstation-daily-update      │
│  - docker-service.sh: Unified COMPOSE_STACKS orchestrator   │
└──────────────────────────────┬──────────────────────────────┘
                               │ docker compose
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Docker Compose (shb-schedule)               │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  service: db (postgres:18.6-alpine)                 │   │
│   │  - restart: unless-stopped                          │   │
│   │  - volume: shb-scheduler-pgdata                     │   │
│   │  - logging: max-size 10m, max-file 3                │   │
│   └──────────────────────────┬──────────────────────────┘   │
│                              │ healthy                      │
│   ┌──────────────────────────▼──────────────────────────┐   │
│   │  service: scheduler (shb-scheduler:latest)          │   │
│   │  - restart: unless-stopped                          │   │
│   │  - stop_grace_period: 60s (DBOS clean drain)        │   │
│   │  - logging: max-size 10m, max-file 3                │   │
│   │  - mount: ~/.shb/schedules -> /etc/shb/schedules:ro │   │
│   │  - single-owner advisory lock on postgres           │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 1. Graceful Shutdown & Step Draining (`stop_grace_period: 60s`)
When Docker issues `SIGTERM` during container stop, restart, or system reboot, the ASGI web server and DBOS background worker threads initiate graceful shutdown:
- ASGI lifespan context manager begins server teardown.
- DBOS completes currently executing `@DBOS.step` functions or reaches safe checkpoint boundaries.
- PostgreSQL session advisory locks are automatically released upon connection close.
A `stop_grace_period: 60s` (increased from Docker's default 10s) guarantees adequate time for transactions to commit without triggering abrupt SIGKILL corruption.

### 2. Log Rotation Configuration
Both `db` and `scheduler` undergo health checks every 5 seconds. To prevent disk bloat:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```
Caps total log footprint per service to 30 MiB.

### 3. Unified Workstation Management (`docker-service.sh`)
Adding `/Users/androidteam/Developer/shb/shb-schedule` to `COMPOSE_STACKS` in `~/Developer/scripts/docker-service.sh` ensures that commands like `./docker-service.sh stop`, `./docker-service.sh restart`, or `./docker-service.sh drain` iterate through all production workstation stacks uniformly.

### 4. Workload Execution Partitioning
- **Containerized Schedulers**: Headless banking workflows (`docs_sync`, `recon`, `compliance_scan`) have zero host-GUI or Darwin-binary dependencies and execute inside the Alpine/Debian containers against PostgreSQL.
- **Host Toolchain Updates**: `workstation_update` requires host macOS binaries (`/opt/homebrew/bin/brew`, `/opt/homebrew/bin/mas`, `pmset`, `/Users/androidteam/.npm-global/bin`). It executes natively on the host via launchd at 08:00 HCM or manual CLI trigger (`uv run shb-schedule run-now workstation-daily-update`). Inside Docker, it detects absent binaries and returns `SKIPPED` without error.
