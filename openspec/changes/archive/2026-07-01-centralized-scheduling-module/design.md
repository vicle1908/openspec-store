## Context

The TDT ecosystem currently has scheduling scattered across **many independent mechanisms**. The original five are the launch targets; a workspace sweep (excluding the iOS/Android repos and the `mcp-router` fork) surfaced more that this change now brings into scope:

| # | System | Mechanism | Statefulness | Crash Recovery | Disposition |
|---|--------|-----------|-------------|----------------|-------------|
| 1 | `webhook-receiver` MR debounce | `ReviewDebouncer` (in-memory, `threading.Lock`) | In-memory only | Lost on restart | Migrate (Phase 4) |
| 2 | `webhook-receiver` freshness debounce | `FreshnessDebouncer` (in-memory, `threading.Lock`) | In-memory only | Lost on restart | Migrate (Phase 4) |
| 3 | `jira-daily-reports` cron | 13 entries in macOS crontab | None | None | Migrate (Phase 5) |
| 4 | `review-coverage` launchd | `com.tdt.review-coverage.plist` `StartInterval=600` | None | launchd restarts | Migrate (Phase 6) |
| 5 | CLV2 observer | Shell `sleep $INTERVAL` loop + PID file | PID file | None (zombie on crash) | Migrate (Phase 7) |
| 6 | `agent-core` durable engine | `DurableEngine` + DBOS (disabled by default) | PostgreSQL | Full DBOS recovery | Source of the extracted engine |
| 7 | `jira-skill` cron suite | 9 entries via `automation/setup-cron.sh` | None | None | Migrate (Phase 8) — **dedup vs #3 first** |
| 8 | `jira-skill` API loops | `asyncio.sleep(30)` health refresh + `asyncio.sleep(3600)` keepalive in `api/main.py` | In-memory | None | Migrate (Phase 8) — low value, in-process |
| 9 | `jira-kanban-from-spreadsheet` | crontab example in OPERATOR_RUNBOOK/README (no coded mechanism) | None | None | Migrate (Phase 8) — register operators' documented cron, replace doc with `tdt-scheduler` |

**Reviewed and excluded (NOT time-based scheduling):** `jira-epic-report/collector.py` (`while True` is JQL pagination), `ops-automation-suite/engine.py` (DAG workflow engine — dependency-driven, same category as the `mcp-router` DAG), `webhook-receiver/actions/merge_request.sh` (event-triggered action). Docker `HEALTHCHECK` and Graphify watch are infrastructure/dev-tool, not application scheduling.

The `agent-core` package already has a working DBOS-backed scheduling engine (`DurableEngine`, `ScheduleRegistry`, `QueueWrapper`, `DebouncerWrapper`) but it's isolated — no other service imports it. This design extracts those primitives into `tdt-core[scheduler]` and migrates **all non-mobile, non-fork** scheduling onto it. This same contract now also covers `android-scan-agent`'s daily technical-debt scan, which runs as a DBOS cron workload in the Docker scheduler service with no LaunchAgent fallback.

**Constraints:**
- All Python services already depend on `tdt-core` — natural home for shared scheduling
- `mcp-router` is a separately-maintained TypeScript/Electron fork — **out of scope** for this change
- iOS/Android mobile apps (`poems-mobile3-ios*`, `poems-mobile3-android*`) are client-side — **permanently out of scope**
- **OVERLAP HAZARD:** `jira-skill`'s 9 cron reports overlap `jira-daily-reports`'s 13 (standup, sprint-health, missing-info, blocked, code-review, velocity, priority, platform appear in BOTH). The finalized `jira-reports-consolidation` change owns which implementation is canonical — migration MUST defer to it and register each report ONCE (Decision 10), never double-schedule.
- **BINDING:** the promoted spec `specs/ai-review-deployment-state` mandates `webhook-receiver` (:8080) and `ai-review` (:8090) as launchd-managed services and prohibits other launch patterns — this change MUST NOT containerize them; their schedules run in-process (Decision 4)
- Ecosystem is evolving Docker-first: `agent-core-docker-local-development` ships a pinned `python:3.14.5-slim-trixie` + `postgres:18.4-trixie` compose, and `workspace-relocation` (Ready) moved the tree to `$HOME/Developer/tdt` specifically because Docker bind-mounts `/Users` — new infra should ride this current
- An always-on PostgreSQL + a live DBOS runtime are required for any cron/observer schedule to fire (Decision 4, Decision 8)
- Passthrough covers only the on-demand primitives (debouncer, queue); it is not a fallback for scheduled workflows (Decision 7)

## Goals / Non-Goals

**Goals:**
- Extract scheduling primitives from `agent-core` into `tdt-core[scheduler]` with no behavior change to the primitives themselves (NOTE: config loading must be re-implemented — `tdt-core` cannot import `agent_core.foundation.settings`, so `SchedulerSettings`/`from_env` is new code, not a verbatim move)
- Migrate **every non-mobile, non-fork scheduling mechanism** onto DBOS-backed equivalents — the 5 launch targets plus `jira-skill`'s cron suite + API loops and `jira-kanban`'s documented cron (see Context inventory + Decision 10)
- Establish a standing policy: all *new* periodic/recurring scheduling in non-mobile Python repos uses `tdt-core[scheduler]` rather than a fresh crontab/launchd/`asyncio.sleep` loop (Decision 10)
- Provide unified `tdt-scheduler` CLI for schedule management across all services
- Provide FastAPI health router for aggregated scheduling observability
- **Target an always-on container as the canonical scheduling host**, on an explicit path to deploy-as-service (local Docker Compose now → always-on host/VM → orchestrated service later). The container, not the laptop session, owns scheduling.
- **Favor DBOS-native primitives** (`scheduled_workflow`, `queue`, `debouncer`, exactly-once, automatic recovery) over any bespoke cron/lock/retry code — see Decision 9
- Remove all legacy scheduling code (debouncers, crontab, launchd plist, PID files)
- Passthrough mode for the *on-demand* primitives (debouncer, queue): when DBOS is unavailable they execute inline. NOTE: passthrough is **not** a fallback for `scheduled_workflow` — see Decision 7.

**Non-Goals (permanent hard exclusions):**
- Touch `mcp-router` in any way (separately-maintained TypeScript/Electron fork — cron support there, if wanted, is a separate proposal against the fork)
- Migrate iOS/Android mobile timers (`poems-mobile3-ios*`, `poems-mobile3-android*` — client-side, fundamentally different)

**Out of scope because reviewed and found NOT to be time-based scheduling:**
- `jira-epic-report/collector.py` `while True` (JQL pagination, not a scheduler)
- `ops-automation-suite/engine.py` (DAG workflow engine — dependency-driven execution, same category as the excluded `mcp-router` DAG)
- Docker `HEALTHCHECK` directives and Graphify watch (infrastructure / dev-tool, not application scheduling)
- Add new scheduling *features* beyond what DBOS provides (no custom cron engine)

## Decisions

### Decision 1: Extract to `tdt-core[scheduler]` (not a new repo)

**Choice:** Add scheduling primitives as an optional dependency group `[scheduler]` in `tdt-core`.

**Rationale:**
- `tdt-core` is already the shared infrastructure package — all Python services depend on it
- Follows the existing pattern: `[jira]`, `[gitlab]` optional groups
- Avoids creating yet another repo with its own CI/CD, venv, and deployment
- `agent-core` already depends on `tdt-core` — no circular dependency

**Alternatives considered:**
- New `tdt-scheduler` repo: More isolation but adds deployment complexity
- Keep in `agent-core`: Perpetuates the isolation problem this change aims to solve

### Decision 2: Rename from "Durable" to "Scheduler" terminology

**Choice:** Rename `DurableEngine` → `SchedulerEngine`, `DurableConfig` → `SchedulerConfig`, etc.

**Rationale:**
- "Durable" is an implementation detail (DBOS exactly-once); "Scheduler" is the user-facing concept
- Cleaner API for consumers who don't care about the underlying durability mechanism
- Consumers are migrated to the new names in this change (no re-export shim — see Decision 10)

### Decision 3: Remove `asyncio.to_thread()` in webhook-receiver

**Choice:** DBOS workflows are natively async and non-blocking — the `asyncio.to_thread()` workaround in `schedule_merge_request()` is no longer needed.

**Rationale:**
- The workaround existed because the old in-memory debouncer ran synchronously
- DBOS `Debouncer.debounce()` returns immediately; the workflow runs in the background
- Simplifies the code and removes a layer of indirection

### Decision 4: An always-on container is the canonical scheduling host (deploy-as-service is the explicit target); native hosting only where a contract or the host filesystem forces it

**Choice:** The committed target is an **always-on Docker container** (`scheduler`, `restart: unless-stopped`) that owns the durable store + every cron/interval workload that *can* move — a real service, not a laptop-session job. This is on an explicit **deploy-as-service** path (local Compose now → always-on host/VM → orchestrated service later; see Deployment Evolution Path below). A workload stays off the container only for one of two explicit reasons — (A) a binding deployment contract, or (B) deep host-filesystem coupling — and each exception is flagged transitional with a documented supersede path.

| Workload | Host | Flavor | Why |
|----------|------|--------|-----|
| **PostgreSQL (durable store)** | **Docker** `postgres` service | Docker | Reuse `agent-core`'s `postgres:18.4-trixie` compose, single shared **server** (per-app logical DB — Decision 8); native Postgres on macOS is strictly worse; relocation tree is Docker-bind-mount-friendly |
| **jira-daily-reports cron (13 reports)** | **Docker** `scheduler` service | Docker | No resident process today, no launchd contract — the cleanest deploy-as-service fit |
| **review-coverage scan** | **Docker** `scheduler` service | Docker | `CoverageScanner.scan()` is **pure data** (rows → gaps; no FS/git/network) and the binding spec pins only :8080/:8090 — NOT the `com.tdt.review-coverage` job. So it moves into the same container as jira cron. Consolidates both unconstrained cron workloads into one Docker host |
| **webhook debouncers** | Native, in-process in `webhook-receiver` (:8080) | Exception A (contract) | Highest-value workload, but invoked synchronously from the HTTP handler so it *cannot* leave the process; binding `ai-review-deployment-state` keeps :8080 on launchd. Point its DSN at the Docker Postgres (`127.0.0.1:<port>`) — durable debouncers with **zero** deployment change |
| **CLV2 observer** | Native, launchd-supervised | Exception B (host-coupled) | Reads Claude session transcripts, project dirs, `.observer-sessions` leases; runs shell scripts against local paths — containerizing means mounting large host FS slices |

**Rationale:**
- **Always-on container leads.** Both workloads that can move (jira reports, coverage) land in a single `scheduler` container, so the deploy-as-service path is that one service: the `scheduler` relocates to an always-on box / VM / k8s as a unit and **attaches to the single ecosystem Postgres** (which relocates on its own agent-core track). Nothing in the container path is macOS-bound.
- **DBOS *wants* an always-on host — the engine and the deployment reinforce each other.** DBOS recovery, cron firing, and queue draining all require a persistent runtime connected to Postgres; a one-shot launchd/crontab invocation is architecturally mismatched with DBOS (the process exits before recovery/scheduling can happen). Choosing DBOS (Decision 9) and choosing the always-on container are the same decision viewed from two angles.
- **Only two, well-justified exceptions.** The debouncers are blocked by a *binding contract* (not preference); the observer by *host coupling*. Both are explicitly transitional — if `ai-review-deployment-state` is superseded, :8080's debouncer logic is already DBOS-backed and could move into the container; if the observer is decoupled from the host FS, it too can containerize.
- launchd is **not the deployment story** — it shrinks to (a) the two binding-spec services, (b) one supervisor entry for the native observer, and (c) keeping Docker Desktop alive at login. The scheduling *infrastructure* lives in the always-on container.
- This rides the ecosystem current (`agent-core-docker-local-development`, `workspace-relocation`) rather than fighting it.

**Alternatives considered:**
- In-process coverage inside the ai-review FastAPI service: rejected — it would tie a contract-free, pure-data workload to the launchd service unnecessarily and keep it off the container path. Moving it to the `scheduler` container is more aligned with the always-on target and removes a launchd job entirely.
- Containerize every service (webhook-receiver, ai-review too): blocked by the binding `ai-review-deployment-state` spec; a separate, larger proposal that supersedes that contract (and the natural next step once this lands).
- Keep crontab/launchd as the *trigger* and use DBOS only for durability/observability: **rejected as the target** — it abandons the always-on/deploy-as-service aim and the DBOS synergy above. Retained ONLY as the per-phase emergency rollback posture (see Rollback Strategy), not as a deployment option.
- One shared scheduler daemon for all services: the `scheduler` container *is* that daemon for the movable workloads; the two exceptions are deliberately excluded to respect their constraints.

### Deployment Evolution Path (target: deploy-as-service)

| Stage | Host | What runs | Trigger to advance |
|-------|------|-----------|--------------------|
| **0 — now** | Local Docker Compose on the dev Mac (`restart: unless-stopped`, Docker Desktop as login item) | `scheduler` service (jira cron + `jira-run-all` + coverage) attached to the ecosystem Postgres; debouncers in-process; observer native | This change |
| **1 — always-on box** | Same Compose file on a dedicated always-on host / small VM | Same stack, unchanged | When laptop-sleep gaps become unacceptable |
| **2 — orchestrated service** | Managed runtime (k8s / managed container service) | `scheduler` as a deployed service + managed Postgres; the two exceptions migrate once their blockers clear | When other services also containerize / `ai-review-deployment-state` is superseded |

The Compose file is the migration unit across all three stages — no rewrite, only relocation.

**Target Compose (illustrative — reuses `agent-core`'s pinned pattern):**
```yaml
name: tdt-scheduler-local
# Scheduler attaches to the SINGLE ecosystem Postgres SERVER (agent-core's
# postgres:18.4-trixie) using its OWN logical DB. It defines NO postgres
# service and NO DB volume — only a second logical database on that server.
services:
  scheduler:                     # owns jira cron + jira-run-all + coverage scan
    image: tdt-scheduler:local
    build: { context: ., args: { PYTHON_IMAGE: python:3.14.5-slim-trixie, UV_VERSION: 0.11.17 } }
    restart: unless-stopped
    env_file: [~/.tdt/.env]      # JIRA_*, SPREADSHEET_ID, GOOGLE_* creds + egress config
    environment:
      SCHEDULER_ENABLED: "true"
      SCHEDULER_SCHEDULING_ENABLED: "true"
      # ONE Postgres SERVER, OWN logical DB: agent-core's instance, database tdt_scheduler
      # (DBOS auto-derives tdt_scheduler_dbos_sys). Per Decision 8.
      DBOS_DATABASE_URL: ${DBOS_DATABASE_URL:?postgresql://…@<ecosystem-pg>/tdt_scheduler}
    command: ["uv", "run", "tdt-scheduler", "serve"]   # long-lived: initialize + apply_schedules + block
    # Reach the ecosystem Postgres EITHER by joining agent-core's compose network
    # (e.g. networks: [agent-core-local_default]) OR via the published 127.0.0.1 port.
    # depends_on: { condition: service_healthy } only works if co-located in agent-core's
    # project; when run as a separate project, `tdt-scheduler serve` performs a
    # wait-for-DB readiness check before launching DBOS.
# no postgres service, no DB volume — the server is agent-core's single instance;
# the scheduler just owns its own logical database on it
```
`tdt-scheduler serve` is a new long-lived CLI command (initialize the engine, register `scheduler_setup` workflows, `apply_schedules()`, then block) — distinct from the existing one-shot `list/pause/...` commands.

### Decision 5: Schedule name prefixing to avoid collisions

**Choice:** Prefix all schedule names with the service identifier: `webhook-mr-debounce`, `jira-standup`, `coverage-scan`, `clv2-observer`.

**Rationale:**
- The scheduler app hosts several workloads (jira reports, `jira-run-all`, coverage) in **one** DBOS app/DB, so their schedule names must be unique *within* that app (intra-app uniqueness — per Decision 8, cross-app isolation comes from the per-app database, not from naming)
- Schedule names must be unique within the app's DBOS registry
- Prefixing is simple and self-documenting

### Decision 6: Keep `CRON_ON_TRANSITION_GRACE_HOURS=48` logic

**Choice:** The dual-path design (webhook real-time + cron safety net) for Jira reminders is preserved exactly.

**Rationale:**
- This is a correctness requirement, not an implementation detail
- The grace period ensures the webhook guard has time to act before cron fires
- Moving from crontab to DBOS doesn't change this logic

### Decision 7: Passthrough is NOT a fallback for scheduled workflows

**Choice:** Be explicit that `SchedulerConfig.enabled=False` (passthrough) only degrades the *on-demand* primitives — `debouncer()` and `queue()` run their wrapped function inline. A `scheduled_workflow` has nothing to fall through to: with no live DBOS runtime there is no clock.

**DBOS capability note (2026):** DBOS Python supports persistent schedule management (create/apply/list/get/pause/resume/delete) and optional **manual** backfill over a date range (`backfill_schedule`). Automatic backfill (`automatic_backfill=True`) is a DBOS-available option that this policy disables by default.

**TDT policy (this change):** Default `automatic_backfill` for all migrated schedules is **OFF**.

- For *notification/report* schedules (jira-daily-reports, coverage scan), backfill is harmful: a long outage would emit a burst of stale reports.
- If we later add *state reconciliation* schedules that can safely replay missed ticks, backfill MAY be enabled **only** as an explicit per-schedule opt-in after reviewing side effects.

**Rationale:**
- “Missed tick is missed” is true under this policy, not because DBOS lacks backfill.
- This prevents surprise bursts after downtime while still allowing each workflow’s *next* run to safely reconcile state (idempotent, time-windowed logic).
- Consumers needing “runs even if DBOS is down” still require an OS-native trigger (Decision 4 alternative).

### Decision 8: One PostgreSQL server (prerequisite + single point of failure), with a separate logical database per app

**Choice:** There is exactly one PostgreSQL **server/instance** for the whole ecosystem — `agent-core`'s pinned `postgres:18.4-trixie` (one container, one volume, one backup surface). On that server, **each DBOS application uses its own logical database** (the DBOS-documented multi-app pattern), NOT one database shared by all apps:
- `agent-core` → `agent_core` (+ auto `agent_core_dbos_sys`)
- the Docker `scheduler` app → `tdt_scheduler` (+ auto `tdt_scheduler_dbos_sys`)
- `webhook-receiver` debouncers (in-process) → its own DB (+ auto `_dbos_sys`)
- CLV2 observer (native, launchd) → its own DB (e.g. `clv2_observer`, + auto `_dbos_sys`)

Creating a logical DB is a one-line `CREATE DATABASE`, so this remains "one Postgres for the whole ecosystem" while following best practice.

**Rationale (verified against `dbos-transact-py`):**
- DBOS stores workflow/queue/scheduler bookkeeping in a **separate system database** derived as `<appdb>_dbos_sys`. The documented pattern for multiple distinct apps on one server is a **database per app** — it isolates system tables and keeps each app's observability (`tdt-scheduler schedules list`, the health API) scoped to that app only.
- Recovery is already scoped by `executor_id`/`application_version`, so sharing a single DB would be *functionally* safe — but separate DBs avoid contention on shared system tables and decouple each app's DBOS-version/schema churn. Schedule-name uniqueness (Decision 5) is therefore an **intra-app** concern (the scheduler app hosts jira + coverage workloads together), not the cross-app isolation mechanism.
- DBOS cannot initialize without a reachable DSN; every cron/observer phase is blocked until the server exists (Phase 0).
- **Single point of failure:** one server is one failure domain — when it is down, **every** migrated schedule stops at once (today the 5 mechanisms fail independently). Accepted deliberately; mitigated by `restart: unless-stopped`, Docker Desktop as a login item, and idempotent catch-up-on-next-run logic. Phase ordering lands the high-value debouncers first.

### Decision 9: Favor DBOS-native primitives over bespoke scheduling code

**Choice:** Every migrated workload is expressed with a **DBOS-native primitive** — `scheduled_workflow` (cron), `queue` (concurrency/rate limits), `debouncer` (coalescing), `workflow`/`step` (exactly-once + automatic retry/recovery). The change adds **no** custom cron parser, in-memory lock, manual retry loop, or PID file. Where a legacy mechanism did one of those things, it is replaced by the equivalent DBOS feature, not reimplemented.

**Rationale:**
- This is *why the always-on container exists* (Decision 4): DBOS recovery, cron firing, and queue draining need a persistent runtime — the engine choice and the deployment choice are the same decision.
- Less code to own: exactly-once, crash recovery, backfill, and schedule listing come from DBOS, not from us. The in-memory debouncer's lost-state bug disappears precisely because DBOS persists state.
- Uniform observability: one `tdt-scheduler` CLI + health API over the DBOS system tables, instead of five bespoke status surfaces.
- DBOS usage is **uniform regardless of host** — the Decision 4 exceptions (in-process debouncers, native observer) still use the *same* DBOS primitives; only their process/host differs. "Flavor DBOS" and "flavor Docker" are independent axes: every workload is DBOS; most workloads are also containerized.

**Consequences / boundaries:**
- Do not add scheduling features beyond what DBOS provides (Non-Goal). If a need can't be expressed as a DBOS primitive, raise it as a separate proposal rather than hand-rolling around the engine.
- The observer's 3-gate shell logic stays (it is business logic, not scheduling) but its outer loop becomes a DBOS `scheduled_workflow`.
- Pin `dbos>=2.22.0,<3` in the `[scheduler]` extra so the primitive contract is stable across hosts.

### Decision 10: Clean cut — complete migration, no backward-compat shims or legacy fallbacks

**Scope audit (research result):** A full workspace sweep (launchd plists, crontab, `threading.Timer`/`sched`/`APScheduler`, shell `sleep` loops, JS timers) confirms the original catalogue of **6 mechanisms is complete**. The only newly surfaced periodic-looking hits are explicitly **not** in scope:
- `com.tdt.agentmemory` launchd job — `RunAtLoad`/`KeepAlive` **persistent daemon**, not an interval/cron schedule; it is service hosting, not scheduling.
- `graphify/watch.py` `while True: sleep(0.5)` — local developer file-watch (already a Non-Goal).
- `cleanup_debouncer_task` `while True: sleep(3600)` — internal cleanup that this change **deletes** (DBOS handles retention).
- Remaining `asyncio.sleep` / `while True` hits — retry/backoff, REPL, pagination, HTTP redirects: control flow, not scheduling.

**Choice:** Because a complete cut is acceptable, this change does **not** retain backward-compat or legacy paths:
- **No `agent-core` re-export shim.** Update every `agent-core` import site to `tdt_core.scheduler` in this change and delete `agent_core/durable_execution/` in the same change. `impact()` confirms a small blast radius: `durable_execution/__init__` → `cli/app.py` → `cli/__init__`.
- **No crontab compatibility.** Delete `generate_crontab`, `install_crontab`, and the `--install`/`--show` crontab paths. The canonical cron definitions move into `scheduler_setup.py` `@scheduled_workflow` decorators; `tdt-scheduler schedules list` is the single "show" surface.
- **No in-memory / PID / legacy fallbacks.** The in-memory debouncers, PID files, and signal handlers are removed outright (not feature-flagged).

**Supersedes:** the "re-exports old names for backward compat during migration" language in Decision 2 and the "Keep `--show` as read-only compat" mitigation in Risks. The migration guide (final phase) documents the cut for humans; there is no code-level compat layer.

**Rationale:**
- The re-export shim and the crontab `--show` view exist only to soften a phased rollout; with a complete change accepted they are pure carrying cost.
- A single source of truth (DBOS + `tdt-core.scheduler`) with no parallel legacy path *is* the "single pane of glass" goal; leaving shims undermines it.
- Smaller surface to test and no "two ways to do it" ambiguity for future contributors.

**Trade-off:** consumers pinned to `agent_core.durable_execution.*` break immediately on upgrade. Accepted — all consumers are in-repo (verified) and updated in the same change.

### Decision 11: Two concepts, two homes — durable execution stays embedded; only cross-cutting cron is centralized

**Choice:** Treat **durable execution** and **scheduling** as distinct concerns with distinct homes:
- **Durable execution** (`workflow`/`step` — exactly-once + crash recovery) is a **library capability** that each service embeds in-process via `tdt-core[scheduler]`. DBOS workflows run in the process where their code lives; they are **not** relocated into a central service. `agent-core` keeps its durable runtime in-process (it wraps agent runs / LLM / tools / memory); `webhook-receiver` runs its debouncers in-process. They centralize only by sharing the one ecosystem PostgreSQL.
- **Scheduling** (cron/interval) is **cross-cutting** and is owned by the dedicated Docker `scheduler` service for every *movable* workload (the 13 jira reports, `jira-run-all`, the coverage scan). The CLV2 observer is the single cron schedule that runs from a **native** host instead (Decision 4 exception B — host-FS-coupled), still using the same DBOS primitive.

**Evidence (research):** The canonical scheduling reference is now `agent-core/scheduler_setup.py` — it imports `jira_daily_reports.scheduler_setup` (14 Jira schedules), registers `coverage-scan` every 10 minutes, and registers `daily-android-scan` daily at 7 AM. All 16 schedules run via the Docker `tdt-scheduler` service using DBOS `scheduled_workflow` decorators. The old demo `examples/scheduled_pipeline.py` has been removed.

**Consequence:** "Centralized scheduling" = **one shared PostgreSQL server + one cron-owning service**, NOT a remote RPC scheduler that other services call. Every service embeds `tdt-core[scheduler]` and points `DBOS_DATABASE_URL` at **its own logical database on the single ecosystem Postgres server** (Decision 8 — not a shared application DB). Do not design an RPC/queue hop to "submit" a workflow to the scheduler container — that is not how DBOS works.

### Decision 12: Verified DBOS API surface — `serve` registers by function; the CLI/API manage by name via `DBOSClient`

**Choice:** Build the CLI, health API, and `serve` host on DBOS's actual public APIs (verified against `dbos-transact-py` v2.x), with a clean split between the two processes:

- **`serve` (in-process, owns the workflow code):** registers schedules with `DBOS.apply_schedules([...])`, where each entry needs `schedule_name`, `workflow_fn`, `schedule` (cron), and optional `context`, `automatic_backfill`, `cron_timezone` (IANA; UTC default), `queue_name`. This is the existing `ScheduleRegistry.to_dbos_inputs()` shape (verified to match).
- **Management & read operations (CLI + health API) are name-based via `DBOSClient`:** `list_schedules(status=…, workflow_name=…, schedule_name_prefix=…)`, `get_schedule(name)` (→ `last_fired_at`), `pause_schedule(name)`, `resume_schedule(name)`, `delete_schedule(name)`, and `trigger_schedule(name)` (immediate enqueue at current time). These need no `workflow_fn`, so they work from **any** process — the standalone `tdt-scheduler` CLI (which has no workflow code at all) AND the health router whether it is mounted inside `serve` or hosted separately. (`DBOSClient.apply_schedules` takes `workflow_name`, not `workflow_fn` — another reason management is name-based.)

**Verified facts (DeepWiki on `dbos-transact-py`):**
- `cron_timezone` is a real per-schedule parameter (IANA name; defaults to UTC) — Decision/timezone requirement is sound.
- `pause_schedule` / `resume_schedule` / `delete_schedule` are real public APIs on both `DBOS` and `DBOSClient` — the CLI commands are NOT inventing capability.
- `list_schedules` / `get_schedule` exist; `get_schedule().last_fired_at` is the last-run time.

**Validated against official DBOS docs + `dbos/_client.py` source (2026-06; DeepWiki + Context7 + docs.dbos.dev):**
1. **No next-run API — confirmed.** `WorkflowSchedule` exposes `status`, `last_fired_at`, `automatic_backfill`, `cron_timezone`, `queue_name`, but **no** next-run field (DBOS computes `next_exec_time` internally via croniter). The CLI/API therefore derive next-run from cron + `last_fired_at`, or omit it — never fabricate it.
2. **`trigger_schedule(name)` IS a real API — corrected.** Both `DBOS.trigger_schedule(name)` and `DBOSClient.trigger_schedule(name)` "immediately enqueue the scheduled workflow at the current time" and return a workflow handle. The health-API/CLI trigger uses this directly. Constraint: `trigger_schedule`, `backfill_schedule`, and `apply_schedules` **cannot be called from within a workflow** (they raise `DBOSException`) — invoke them from the request handler / CLI process, not inside a workflow body.
3. **`Debouncer` confirmed.** `Debouncer.create(workflow, *, debounce_timeout_sec, queue)` (sync) / `create_async` exist; external debouncing uses `DebouncerClient("wf_name", client, debounce_timeout_sec=…).debounce(period_sec, *args)`. `.debounce()` is real — only confirm the exact positional arg order against the pinned `dbos>=2.22.0,<3` when wiring `DebouncerWrapper`.

**Backfill note:** DBOS *does* support catch-up (`automatic_backfill=True` and `DBOS.backfill_schedule(name, start, end)`, idempotent via deterministic `sched-{name}-{time}` workflow IDs). This change deliberately keeps `automatic_backfill=False` (Decision 7) — catch-up is available if a future workload wants it, but the reports/observer rely on idempotent next-run reconciliation instead of a restart burst.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Single PostgreSQL = single point of failure** | If the shared DB is down, ALL migrated schedules stop (today the 5 mechanisms fail independently) | Accept deliberately (Decision 8); run Postgres in Docker with `restart: unless-stopped` + Docker Desktop as a login item; idempotent catch-up-on-next-run report logic; phase migration so the high-value debouncers land first |
| **No clock without a live runtime** | A `scheduled_workflow` tick is missed if the DBOS host is down — passthrough does NOT cover cron (Decision 7) | Reserve passthrough for on-demand primitives only; design every report/observer run to be idempotent and self-correcting on the next successful tick |
| **Always-on host required** | `jira-daily-reports` has no resident process today; cron migration introduces one | Per Decision 4: one Docker `scheduler` service (`restart: unless-stopped`) owns BOTH jira cron and the coverage scan; debouncers stay in-process in webhook-receiver (no new host); the observer stays native under one launchd supervisor entry; Docker Desktop launches at login |
| **Webhook response latency** | GitLab times out if dispatch blocks | DBOS workflows are async/non-blocking; verify with `timeout=2s` test |
| **Crontab removal confusion** | Users expect `crontab -l` to work | Clean cut (Decision 10): crontab paths deleted; `tdt-scheduler schedules list` is the single view; document the cut in the migration guide |
| **launchd plist regenerated by deploy.sh** | Deleting the plist file is not enough — `ai-review/scripts/deploy.sh` recreates it inline on next deploy | Strip the plist-generation heredoc block from `deploy.sh` in the same change (Phase 4) |
| **Shell observer crash recovery** | Observer runs inside DBOS workflow | Test with `kill -9` on the observer process; DBOS restarts within `retry_interval_seconds` |
| **Deployment mirror drift** | `deployments/**` vendored copies can resurrect deleted legacy code | Re-sync deploy trees as part of each phase; add a check to the final integration task |
| **Schedule name collisions** | One schedule overwrites another | Prefixing by service name prevents this |
| **DBOS version compatibility** | `dbos>=2.22.0` may conflict | Pin version in `[scheduler]` extras; test in CI |

## Migration Plan

> **`tasks.md` is the canonical execution sequence.** The milestones below are a higher-level grouping for reasoning about ordering and rollback; the granular, checkable steps live in `tasks.md`. Mapping: design **P1** (extract) → tasks **P1–P3** (extract + CLI + health API); design **P2** (webhook) → tasks **P4**; design **P3** (Docker scheduler + jira cron) → tasks **P5**; design **P4** (coverage) → tasks **P6**; design **P5** (observer) → tasks **P7**. Tasks **P8** is out of scope (mcp-router) and **P9** is cleanup/docs.

### Phase 0: Prerequisites (blocking)
1. Confirm the **single ecosystem PostgreSQL server** (`agent-core`'s pinned `postgres:18.4-trixie`, `restart: unless-stopped`, healthcheck, port on `127.0.0.1`) is running; do NOT stand up a second Postgres server. Create the scheduler's own logical DB `tdt_scheduler` on it (DBOS auto-derives `tdt_scheduler_dbos_sys`) — one server, per-app database (Decision 8)
2. Ensure Docker Desktop launches at login (otherwise the "always-on" store isn't always on)
3. Confirm the deployment topology per workload (Decision 4): in-process for webhook-receiver/ai-review, Docker `scheduler` service for jira cron, native for the observer
4. Add the `scheduler:` section to `~/.tdt/config.yaml` (DSN points at the published Docker Postgres port)
5. Verify `SchedulerEngine.from_env()` connects and `get_status()` reports `dbos_connected=true`

### Phase 1: Extract to `tdt-core[scheduler]`
1. Create `tdt-core/src/tdt_core/scheduler/` package with renamed types
2. Add `[scheduler]` optional dependency group to `tdt-core/pyproject.toml`
3. Rewrite every `agent-core` import site from `agent_core.durable_execution.*` to `tdt_core.scheduler.*` and delete `agent_core/durable_execution/` (no re-export shim — Decision 10); make `agent-core` depend on `tdt-core[scheduler]`
4. Write tests for the extracted module
5. Verify all existing `agent-core` tests pass

### Phase 2: Migrate webhook-receiver debouncers
1. Replace `ReviewDebouncer` with DBOS `DebouncerWrapper` (in-process; DSN → Docker Postgres)
2. Replace `FreshnessDebouncer` with DBOS `DebouncerWrapper`
3. Remove `cleanup_debouncer_task()`
4. Remove `core/debouncer.py` and debounce logic from `report_freshness.py`
5. Verify webhook response time < 500ms AND the service is still launchd-managed (binding `ai-review-deployment-state`)

### Phase 3: Build the Docker `scheduler` stack + migrate jira-daily-reports crontab
1. Add a `Dockerfile` (mirror `agent-core`'s pinned `python:3.14.5-slim-trixie` + `uv==0.11.17`) and a `compose.yaml` with a **single `scheduler` service** (no `postgres` service — it attaches to the ecosystem Postgres via `DBOS_DATABASE_URL`); the `scheduler` runs a long-lived `SchedulerEngine` (`tdt-scheduler serve`) that calls `apply_schedules()` on startup
2. Create `scheduler_setup.py` with 13 `@scheduled_workflow` registrations, plus `jira-run-all` (the full report, now **daily** — supersedes the legacy Saturday-only entry)
3. Register `jira-run-all` on a daily cron at an off-peak hour (e.g. `0 7 * * *`, before the 08:00 individual-report cluster) so the daily full report does not collide with the per-report schedules
4. Change `schedule.py` `--install`/`--uninstall` to register/remove via DBOS (`SchedulerEngine.apply_schedules()`)
5. Delete `generate_crontab`/`install_crontab` and the crontab `--show` path — `tdt-scheduler schedules list` is the only view (Decision 10)
6. Remove crontab installation code

### Phase 4: Move review-coverage into the Docker `scheduler` stack
1. Register the coverage scan as a `@scheduled_workflow(cron="*/10 * * * *")` **in the same Docker `scheduler` container** (NOT in-process in ai-review) — `CoverageScanner.scan()` is pure-data and the binding spec does not pin the `com.tdt.review-coverage` job, so it moves cleanly to Docker and removes a launchd job entirely
2. Remove `deployments/ai-review/launchd/com.tdt.review-coverage.plist`
3. Remove the inline plist-generation heredoc block from `ai-review/scripts/deploy.sh` (otherwise the next deploy recreates it)
4. CAVEAT: coverage is pure-data today; if it later grows local-git/worktree grounding (like the ai-review diff path), re-evaluate placement

### Phase 5: Migrate CLV2 observer
1. Run the observer as a DBOS scheduled workflow from a **native, launchd-supervised** resident host (NOT Docker — it is host-FS-coupled)
2. Remove PID file and signal handling from observer-loop.sh
3. Keep the 3-gate system (time window, cooldown, idle detection) in the shell script

### Rollback Strategy
- Each phase is a single revertible commit; rollback = revert that commit (which re-enables the OS-native trigger that phase replaced). Per Decision 10 there is NO parallel legacy code kept in the tree.
- For the on-demand primitives (Phase 2), passthrough (`enabled=False`) is the emergency fallback. For cron/observer phases there is no inline fallback (Decision 7) — rollback re-enables the crontab/launchd trigger from the reverted commit.

## Resolved Decisions

- **One ecosystem-wide PostgreSQL server, per-app logical DB** (DB-topology decision, verified against `dbos-transact-py`). There is exactly one Postgres **server** for the whole TDT ecosystem — `agent-core`'s pinned `postgres:18.4-trixie` — and this change does NOT stand up a second server. On it, each DBOS app uses its **own logical database** (`agent_core`, `tdt_scheduler`, webhook-receiver's own), each with an auto-derived `_dbos_sys`. That is DBOS's documented multi-app pattern; a logical DB is a one-line `CREATE DATABASE`, so the "one Postgres for the ecosystem" intent holds.
- **`run-all` full report runs daily** — registered as `jira-run-all` on a daily cron, superseding the legacy Saturday-only `0 9 * * 6` entry.
- **crontab `--install` is removed, not kept as a no-op** — clean cut per Decision 10.
- **Always-on container is committed.** The `scheduler` container is the canonical scheduling host on an explicit deploy-as-service path (Decision 4, Deployment Evolution Path). The crontab/launchd-as-trigger option is retained ONLY as a per-phase emergency rollback posture, not as a deployment choice.
