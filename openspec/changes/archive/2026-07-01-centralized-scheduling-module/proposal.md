## Why

The TDT ecosystem has **5 independent scheduling mechanisms** spread across the ecosystem — in-memory debouncers, macOS crontab, launchd intervals, shell sleep loops, and an isolated DBOS engine — all doing the same thing differently. This fragmentation means no crash recovery, no observability, no shared state, and duplicated code. By extracting the DBOS-backed scheduling primitives from `agent-core` into `tdt-core[scheduler]` and migrating all Python services onto it, we get exactly-once execution, unified CLI management, crash recovery, and a single pane of glass for all scheduled work.

The deployment aim is an **always-on container** that owns scheduling as a real service (not a laptop-session job), on an explicit **deploy-as-service** path (local Docker Compose now → always-on host/VM → orchestrated service later). The two favored pillars are **Docker** (where work runs) and **DBOS** (how work runs durably); they reinforce each other — DBOS recovery, cron, and queue draining all need the persistent runtime an always-on container provides.

> **Scope note (mcp-router):** `mcp-router` is a separately-maintained TypeScript/Electron fork. It is **out of scope** for this change — no `schedule` field, no Python bridge, no edits. If cron-triggered DAG execution is wanted there, it will be proposed separately against the fork.

## What Changes

- **Extract** scheduling primitives from `agent-core/durable_execution/` into `tdt-core/src/tdt_core/scheduler/` as a new `[scheduler]` optional dependency group
- **Deploy** an always-on Docker `scheduler` container (`restart: unless-stopped`) as the canonical scheduling host, on a deploy-as-service path (local Compose → always-on host/VM → orchestrated service); all movable cron lives here
- **Replace** `webhook-receiver`'s in-memory `ReviewDebouncer` and `FreshnessDebouncer` with DBOS-backed debouncers
- **Replace** `jira-daily-reports`'s 13-entry macOS crontab with DBOS scheduled workflows, hosted by a new dedicated **Docker `scheduler` service**
- **Replace** the `com.tdt.review-coverage` launchd plist (`StartInterval=600`) with a DBOS scheduled workflow hosted in the **same Docker `scheduler` service** (the coverage scan is pure-data and not contract-bound to launchd)
- **Replace** the `android-scan-agent` daily scan with a DBOS scheduled workflow hosted in the Docker `scheduler` service; no host-local timer or LaunchAgent fallback remains
- **Replace** the CLV2 observer shell `sleep` loop with a DBOS scheduled workflow (native, launchd-supervised — host-FS-coupled)
- **Remove** all legacy scheduling code: `ReviewDebouncer`, `FreshnessDebouncer`, crontab entries, launchd plist (including the inline generation block in `ai-review/scripts/deploy.sh`), PID-file management
- **Add** `tdt-scheduler` CLI for unified schedule management (`serve` for the long-lived Docker host; `list`, `pause`, `resume`, `trigger`, `delete` for management)
- **Add** FastAPI health router for aggregated scheduling status
- **BREAKING (clean cut, Decision 10)**: `agent-core`'s `DurableEngine` moves to `tdt-core` with **no re-export shim** — every in-repo import site is updated to `tdt_core.scheduler` and `agent_core/durable_execution/` is deleted in this same change
- **Non-goal for this change**: `mcp-router` cron support is out of scope and will be proposed separately against the TypeScript/Electron fork

## Capabilities

### New Capabilities
- `scheduler-engine`: Core `SchedulerEngine` class wrapping DBOS lifecycle — `initialize()`, `shutdown()`, `workflow()`, `step()`, `scheduled_workflow()`, `queue()`, `debouncer()`, `apply_schedules()`, `get_status()`. Passthrough mode when DBOS is unavailable.
- `scheduler-cli`: Unified CLI (`tdt-scheduler`) for listing, pausing, resuming, triggering, and deleting schedules across all services.
- `scheduler-health-api`: FastAPI router (`/scheduler/health`, `/scheduler/schedules`) for aggregated scheduling observability.
- `scheduler-webhook-migration`: Replace `webhook-receiver` in-memory debouncers with DBOS `DebouncerWrapper`.
- `scheduler-cron-migration`: Replace `jira-daily-reports` crontab and `review-coverage` launchd with DBOS `@scheduled_workflow`.
- `scheduler-observer-migration`: Replace CLV2 observer shell loop with DBOS scheduled workflow.
- `scheduler-docker-deployment`: Docker `scheduler` service (no own Postgres — it attaches to the single ecosystem Postgres) that hosts the long-lived `tdt-scheduler serve` process and owns the movable cron workloads (13 jira reports + daily `jira-run-all` + coverage scan); `restart: unless-stopped` supervision, wait-for-DB before launch, schedule recovery on restart, and the contract-bound/host-coupled exclusions.

### Modified Capabilities
*(None — no existing specs cover scheduling)*

## Impact

- **`tdt-core`**: New `[scheduler]` optional dependency group requiring `dbos>=2.22.0`, `psycopg[binary,pool]`, `pydantic-settings`, `typer`, `structlog`
- **`agent-core`**: all `durable_execution/*` import sites are rewritten to `tdt_core.scheduler` and the `durable_execution/` package is **deleted in this change** (clean cut, Decision 10 — no re-export shim)
- **`webhook-receiver`**: Remove `core/debouncer.py`, `report_freshness.py` debounce logic; add `tdt-core[scheduler]` dependency; debouncers run **in-process** (service stays launchd-managed per the binding `ai-review-deployment-state` spec) with its DSN pointed at the Docker PostgreSQL
- **`jira-daily-reports`**: `schedule.py` changes from crontab generation to DBOS registration; the 13 reports are hosted by a new dedicated **Docker `scheduler` compose service** (the one workload with no resident process today and no launchd contract) — this service also hosts the coverage scan
- **`ai-review`**: Remove the `com.tdt.review-coverage` launchd plist **and** the inline plist-generation block in `ai-review/scripts/deploy.sh` (otherwise the next deploy recreates it); the coverage scan runs as a DBOS `@scheduled_workflow` **inside the Docker `scheduler` service** (its `CoverageScanner.scan()` is pure-data and not contract-bound to launchd — moving it removes a launchd job rather than adding an in-process one). The :8090 FastAPI service is untouched and stays launchd-managed per the binding spec
- **`android-scan-agent`**: its daily technical-debt scan runs as a DBOS `@scheduled_workflow` in the Docker `scheduler` service; the old host-local timer / LaunchAgent path is removed
- **`.claude/skills/continuous-learning-v2/`**: Observer runs as a DBOS scheduled workflow from a **native, launchd-supervised** host (NOT containerized — it is host-FS-coupled); PID file and signal handling removed
- **Deployment mirror copies**: `deployments/webhook-receiver/app/src/...` and `deployments/ai-review/deps/tdt-core/...` are vendored copies of the source repos. Whatever migrates in the source must be re-synced into these deploy trees or they will drift / resurrect deleted code.
- **Infrastructure (prerequisite, not optional)**: An always-on **Docker** PostgreSQL **server** (reusing `agent-core`'s `postgres:18.4-trixie` compose, `restart: unless-stopped`, Docker Desktop as a login item) is **required** before any cron/observer phase can land — DBOS cron triggers need a live runtime + DB. Per Decision 8 each DBOS app uses its **own logical database** on that one server (`tdt_scheduler` for the scheduler app, `agent_core` for agent-core, etc. — DBOS auto-derives each `_dbos_sys`), not a shared application DB. The one server is still a **single point of failure**: if it is down, every migrated schedule is down (today the 5 mechanisms fail independently). `~/.tdt/config.yaml` gains a `scheduler:` section.
- **Binding contract honored**: the promoted `ai-review-deployment-state` spec keeps `webhook-receiver` (:8080) and `ai-review` (:8090) on launchd; this change does NOT containerize them. Containerizing those services would be a separate proposal that supersedes that contract.
- **Out of scope**: `mcp-router` (separately-maintained TypeScript/Electron fork). No impact on: iOS/Android mobile apps, Graphify watch, Docker health checks, qi-bridge proxy, ops-automation-suite, jira-kanban-from-spreadsheet, jira-epic-report
