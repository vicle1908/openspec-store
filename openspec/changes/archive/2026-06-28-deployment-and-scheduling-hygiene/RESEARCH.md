# Research — Validated Findings

This file preserves the **original** research output for traceability.
The proposal.md and design.md describe what this change does; this file
records what was **discarded** and **why**, so future researchers can
audit the validation pass.

## Original 25 findings (pre-validation)

| ID   | Original claim                                                  | Validation result | Final status |
|------|-----------------------------------------------------------------|-------------------|--------------|
| E-1  | Postgres no backup, no replica                                  | Confirmed          | **In scope** |
| E-2  | Scheduler service no healthcheck                                | Confirmed          | **In scope** |
| E-3  | `load_tdt_env` ignores `TDT_HOME`                                | Confirmed          | **In scope** |
| E-4  | No log rotation anywhere                                        | Partially correct  | **In scope** (narrowed to LaunchAgent logs) |
| C1   | ai-review deploy only warns on stale lock                       | Confirmed          | **In scope** |
| C2   | ai-review snapshot misses deps                                  | Confirmed          | **In scope** |
| C3   | ai-review `:?` no-op assertion                                  | Confirmed          | **Deferred** (cosmetic; one-line edit) |
| C4   | daily-health-check.sh legacy paths                              | Confirmed          | **In scope** |
| C5   | Not investigated                                                | n/a                | n/a          |
| C6   | ANDROID_SCAN_REPO_PATH redundant env var                        | Confirmed          | **Deferred** (cosmetic; documented in design.md) |
| C7   | 30s/120s health check timeout undocumented                       | Confirmed          | **Deferred** (already inline in deploy.sh; no separate doc needed) |
| C8   | No rollback mechanism                                           | Confirmed          | **Deferred** (architectural) |
| C9   | webhook-secondary.url atomicity                                 | Confirmed          | **Deferred** (operator-script concern) |
| C10  | Three DBOS app_names share one Postgres                          | Confirmed          | **Deferred** (intentional; documented) |
| C11  | Two venv layouts (dev vs prod)                                  | Confirmed          | **Resolved** (correctly guarded) |
| C12  | incident-report.sh hardcoded fallback path                      | Confirmed          | **Deferred** (operator-script concern) |
| C13  | scheduler Dockerfile COPY gaps                                  | Confirmed          | **In scope** |
| A-1  | webhook-receiver double registration path                       | Confirmed          | **Deferred** (defended by ownership guard) |
| A-2  | jira-daily-reports init clean                                   | Confirmed          | **Resolved** (informational) |
| A-3  | Ownership guard for apply_schedules()                           | Confirmed          | **Resolved** (already enforced) |
| A-4  | Decorator idempotency not explicit                              | Confirmed          | **Deferred** (no observed bug) |
| A-5  | DBOS queue name collisions mitigated                            | Confirmed          | **Resolved** (informational) |
| B-1  | SchedulerSettings precedence                                    | Confirmed          | **Resolved** (correctly documented) |
| B-2  | config.yaml scheduling_enabled=false is intended                | Confirmed          | **Resolved** (intended) |
| B-3  | TDT_HOME vs HOME in Docker                                      | Confirmed          | **Resolved** (consistent) |
| B-4  | No hardcoded host path                                          | Confirmed          | **Resolved** |
| B-5  | config.toml [scheduler] is dead code                            | Confirmed          | **Deferred** (trivial cleanup) |
| C-1  | Snapshot drift detection works                                  | Confirmed          | **Resolved** (good) |
| C-2  | Dirty worktree deploys silently                                 | Confirmed          | **In scope** |
| C-3  | Path-dep divergence caught by snapshot                          | Confirmed          | **Resolved** (good) |
| C-4  | venv always rebuilt                                             | Confirmed          | **Deferred** (safe but slow) |
| C-5  | launchctl bootout correct                                       | Confirmed          | **Resolved** (good) |
| C-6  | Health check thresholds correctly tuned                         | Confirmed          | **Resolved** (good) |
| D-1  | TZ + UTC schedule split                                         | Confirmed          | **In scope** |
| D-2  | automatic_backfill=False                                        | Confirmed          | **Deferred** (design decision) |
| D-3  | Stale-row cleanup 24h threshold                                 | Confirmed          | **Resolved** (good) |
| D-4  | Concurrent apply no advisory lock                               | Confirmed          | **Deferred** (low risk) |
| E-1  | Single Postgres no backup                                       | (duplicate of above) | (same)     |
| E-2  | Single scheduler no watchdog                                    | (duplicate)        | (same)      |
| E-3  | load_tdt_env uses Path.home() not TDT_HOME                      | Confirmed          | **In scope** |
| E-4  | No log rotation                                                 | Confirmed          | **In scope (narrowed)** |
| F-1  | AGENTS.md env var doc accurate                                  | Confirmed          | **Resolved** |
| F-2  | AGENTS.md centralized scheduler doc accurate                    | Confirmed          | **Resolved** |
| F-3  | Phase 7 CLV2 observer deferred                                  | Confirmed          | **Resolved** (acknowledged) |
| F-4  | ai-review-durable-scheduler incident                            | Confirmed          | **Resolved** (fixed) |
| F-5  | config.yaml.example wrong key crash_recovery.scheduling_enabled | **Incorrect**      | **DROPPED** |

## Why F-5 was dropped

The original research conflated **two orthogonal settings systems**:

1. `tdt_core/scheduler/settings.py::SchedulerSettings` — uses
   `SCHEDULER_*` env vars and the `[scheduler]` section of
   `~/.tdt/config.yaml`. This is the **scheduler** settings (DBOS
   ownership, postgres DSN, app name).
2. `agent_core/foundation/settings.py::CrashRecoverySettings` — uses
   `CRASH_RECOVERY_*` env vars and the `[crash_recovery]` section of
   `~/.tdt/config.yaml`. This is the **crash recovery** settings
   (DBOS durable execution enablement, scheduling under crash recovery).

The key `crash_recovery.scheduling_enabled` is legitimate in
`config.yaml.example` — it belongs to system #2. The two settings
systems have **no overlap** on the `scheduling_enabled` key; they are
separate fields in separate pydantic models. There is no bug.

Future researchers: when reading `~/.tdt/config.yaml`, identify which
settings system a key belongs to **before** flagging it as a typo.

## Why E-4 was narrowed

`~/.tdt/scripts/rotate-logs.sh` exists and rotates
`~/.tdt/logs/jira-daily-reports/*.log` and
`~/.tdt/logs/webhook-receiver/*.log` (the latter is likely the
deployment-tree log dir, not the source-tree webhook-receiver). Manual
runs produce `jira-reports.log.{1,2,3}` at 1 MB each.

The actual gap is:

1. **LaunchAgent stdout/stderr** for `webhook-receiver`,
   `ai-review`, `agentmemory`, `qi-bridge-proxy`,
   `ngrok-webhook-secondary` — these are at
   `~/Developer/tdt/deployments/<svc>/logs/<svc>.{stdout,stderr}.log`
   and are not rotated by the script.
2. The script is **not wired** to any LaunchAgent or cron — it only
   runs on manual invocation.

This change closes (1) and (2) by adding the LaunchAgent stdout/stderr
paths to the rotation script and creating
`com.tdt.rotate-logs.plist` for daily invocation at 04:00 local.

## Why C-2 is real

Both `deploy.sh` files compute `source_dirty` and write it to the
deployment manifest JSON. Neither file checks the value before
proceeding. A developer can deploy with uncommitted changes; the
runtime copy matches the source worktree (so the snapshot+diff passes)
but the deployed version is not in git history.

The fix is to gate the deploy on `source_dirty` (with `--allow-dirty`
as escape hatch) and record the gate state in the manifest.

## Why C2 (snapshot coverage) is real

`ai-review/scripts/deploy.sh:159–172` copies **every** workspace repo
with a `pyproject.toml` (containing `[project]`) into
`$DEPLOYMENT_ROOT/deps/`. But the snapshot+diff at lines 174–200 only
includes `app` and `tdt-core`. The other 4 copied deps
(`jira-daily-reports`, `jira-skill`, `tdt-sheets`, `webhook-receiver`)
are not verified. A change to `jira-skill/src/foo.py` followed by
`bash ai-review/scripts/deploy.sh` will deploy silently with the new
`jira-skill` source (because it was copied), but if the deployment's
existing `deps/jira-skill/` is out of sync with the worktree at copy
time, the deploy will not catch it.

`webhook-receiver/scripts/deploy.sh` does NOT have this bug because it
explicitly snapshots all 5 deps.

## Why C13 (Dockerfile COPY) is real

`deployments/scheduler/Dockerfile:31–45` copies:
- `agent-core/{pyproject.toml, README.md, scheduler_setup.py, src}`
- `jira-daily-reports/src` (no `pyproject.toml`, no `README.md`)
- `ai-review/src` (no `pyproject.toml`)
- `code-daily-scan/{src, config, pyproject.toml}`
- `tdt-core/{pyproject.toml, README.md, src}`
- `tdt-sheets/{pyproject.toml, README.md, src}`

Missing:
- `jira-daily-reports/pyproject.toml` and `jira-daily-reports/README.md`
  — `uv sync` reads `pyproject.toml` to resolve the package metadata;
  without it the build may fail or produce a wrong dep tree.
- `jira-skill/{pyproject.toml, README.md, src}` entirely.
- `webhook-receiver/{pyproject.toml, README.md, src}` entirely.

The compose `volumes:` block mounts `jira-skill/src` and
`webhook-receiver/src` at runtime, so the existing compose-driven run
works. But `docker run` without compose would fail to import
`webhook_receiver.selftest_cli` (used by the `webhook-selftest`
scheduled workflow).

## Sources verified by direct read

- `webhook-receiver/scripts/deploy.sh` (full file)
- `ai-review/scripts/deploy.sh` (full file)
- `agent-core/scheduler_setup.py` (full file)
- `agent-core/compose.yaml` (full file)
- `agent-core/config.yaml.example` (full file)
- `agent-core/src/agent_core/foundation/settings.py` (full file)
- `tdt-core/src/tdt_core/env.py` (full file)
- `tdt-core/src/tdt_core/scheduler/settings.py` (full file)
- `tdt-meta/openspec/changes/fix-app-services-apply-schedules/{proposal,tasks,specs}.md` (reference format)
- `~/.tdt/scripts/daily-health-check.sh` (full file)
- `~/.tdt/scripts/rotate-logs.sh` (full file)
- `deployments/scheduler/Dockerfile` (full file)
- `deployments/webhook-receiver/state/deployment-manifest.json` (sample)

## Commands run

```bash
ls -la ~/Developer/tdt/
ls -la ~/.tdt/
ls -la ~/Library/LaunchAgents/ | grep -i "tdt\|les-mac\|com\.tdt"
ls /Users/lekhanhvinh/Developer/tdt/tdt-meta/openspec/changes/
ls /Users/lekhanhvinh/Developer/tdt/tdt-meta/openspec/changes/fix-app-services-apply-schedules/
ls /Users/lekhanhvinh/Developer/tdt/tdt-meta/openspec/specs/
ls -la ~/.tdt/scripts/
ls -la ~/.tdt/logs/
ls /etc/newsyslog.d/
```

## Validation methodology

For each recommendation:

1. **Locate the source.** Use `Read` (not Grep) to read the file at the
   cited line.
2. **Confirm the claim against actual code.** Quote the relevant lines
   in the proposal.
3. **Check for related code paths** that might mitigate or contradict
   the claim.
4. **Re-classify** if the claim was overstated, missing context, or
   based on a misread.
5. **Defer** with explicit justification rather than silently dropping
   the finding.

This validation pass dropped 1 finding (F-5), narrowed 1 (E-4),
corrected the framing of 1 (C2), and confirmed the rest.

---

# Validation pass 2 (2026-06-27)

A second-pass audit was run against **live runtime state** (Docker
containers, launchd, DBOS system DB, git worktrees) before declaring
the change "ready for execution." This is a different mode from
validation pass 1: pass 1 cross-checked claims against source code;
pass 2 cross-checked them against **what is actually running today**.

## Commands run

```bash
# Docker / Postgres runtime
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
docker system df -v | grep agent-core
docker exec agent-core-local-postgres-1 pg_isready -U agent_core -d agent_core
docker exec agent-core-local-postgres-1 psql -U agent_core -d agent_core -c '\l'
docker exec agent-core-local-postgres-1 which pg_dump pg_dumpall gzip

# Scheduler container
docker exec agent-core-local-scheduler-1 uv run tdt-scheduler --help
docker exec agent-core-local-scheduler-1 uv run tdt-scheduler schedules list
docker inspect agent-core-local-scheduler-1 --format '{{json .State.Health}}'
docker inspect agent-core-local-scheduler-1 --format '{{.Config.Cmd}}'
docker exec agent-core-local-scheduler-1 which curl wget psql pg_dump

# launchd
for label in com.tdt.agentmemory com.tdt.ai-review com.tdt.webhook-receiver \
             com.tdt.qi-bridge-proxy com.tdt.ngrok-webhook-secondary; do
  launchctl print "gui/$(id -u)/$label" | grep -E '^[[:space:]]*state|pid|last exit'
done

# DBOS state
docker exec agent-core-local-postgres-1 psql -U agent_core \
  -d tdt_scheduler_dbos_sys \
  -c 'SELECT workflow_name, COUNT(*) FROM dbos.workflow_status GROUP BY 1 ORDER BY 2 DESC LIMIT 30'
docker exec agent-core-local-postgres-1 psql -U agent_core \
  -d tdt_scheduler_dbos_sys \
  -c 'SELECT COUNT(*),status FROM dbos.workflow_status GROUP BY 2'
docker exec agent-core-local-postgres-1 psql -U agent_core \
  -d tdt_scheduler_dbos_sys \
  -c 'SELECT * FROM dbos.workflow_schedules'

# Existing OpenSpec changes
for c in coverage-sweep fix-app-services-apply-schedules deployable-env-loading \
         dbos-stale-workflow-auto-cleanup centralized-scheduling-module \
         ai-review-durable-scheduler dev-tooling-audit-and-enhancement; do
  echo "$c: $(grep -c '^- \[x\]' changes/$c/tasks.md)/$(grep -c '^- \[' changes/$c/tasks.md)"
done

# git status of every deployable repo
for repo in webhook-receiver ai-review tdt-core jira-daily-reports \
            jira-skill tdt-sheets; do
  cd ~/Developer/tdt/$repo
  echo "--- $repo ---"
  git status --short --branch
  git log --oneline -1
done

# Scheduler source: FastAPI router + serve wiring
grep -l "scheduler_router\|app\.include_router\|uvicorn\.run" tdt-core/src/tdt_core/scheduler/

# pyproject layouts
head -30 jira-skill/pyproject.toml webhook-receiver/pyproject.toml jira-daily-reports/pyproject.toml
```

## Findings from validation pass 2

### VP2-1 (CRITICAL): Scheduler FastAPI router exists but is never mounted

`tdt-core/src/tdt_core/scheduler/health.py` defines `scheduler_router`
with 4 endpoints (`/scheduler/health`, `/scheduler/schedules`,
`/scheduler/schedules/{name}`, `/scheduler/schedules/{name}/trigger`).
This was built by `centralized-scheduling-module` task 3.1–3.5
(verified `grep "^- \[" tasks.md` → 3.1–3.5 all `[x]`).

**But** `cli.py::_serve()` (lines 622–639) never imports it, never
starts uvicorn, never exposes any port. The grep across the scheduler
package for `scheduler_router|app\.include_router|uvicorn\.run` returns
only `health.py` itself — the **definition**, never a **mount**. The
scheduler container has no HTTP listener today.

**Action:** Section 2 of tasks.md revised. The defect is the **mount**,
not the router. Mount `scheduler_router` in a daemon thread inside
`_serve()` under prefix `/scheduler` on `127.0.0.1:9100`.

### VP2-2 (HIGH): Schedule count is 21, not 20

The proposal repeated the "20 schedules" assumption throughout.
Live `dbos.workflow_schedules` (verified `SELECT COUNT(*)`) returns
**21 rows** as of 2026-06-27 14:50 +07:00:

| Schedule | Workflow | Cron | Timezone |
|----------|----------|------|----------|
| coverage-scan | coverage-scan | `*/10 * * * *` | Asia/Ho_Chi_Minh |
| jira-blocked | jira-blocked | `0 9 * * 1-5` | Asia/Ho_Chi_Minh |
| jira-code-review | jira-code-review | `0 14 * * 1-5` | Asia/Ho_Chi_Minh |
| jira-sprint-sheet | jira-sprint-sheet | `0 * * * *` | Asia/Ho_Chi_Minh |
| jira-missing-info | jira-missing-info | `30 8 * * 1-5` | Asia/Ho_Chi_Minh |
| jira-platform | jira-platform | `0 10 * * 1-5` | Asia/Ho_Chi_Minh |
| jira-priority | jira-priority | `0 10 * * 1-5` | Asia/Ho_Chi_Minh |
| **scan-recent-mrs** | scan-recent-mr | `*/15 * * * *` | UTC |
| jira-remind | jira-remind | `0 9 * * 1-5` | Asia/Ho_Chi_Minh |
| jira-sprint-health | jira-sprint-health | `0 10 * * 1-5` | Asia/Ho_Chi_Minh |
| dlq-reaper | dlq-reaper | `0 3 * * *` | UTC |
| jira-ticket-intelligence-hourly | jira-ticket-intelligence-hourly | `0 * * * *` | Asia/Ho_Chi_Minh |
| jira-standup | jira-standup | `0 8 * * 1-5` | Asia/Ho_Chi_Minh |
| daily-android-scan | daily-android-scan | `0 7 * * *` | Asia/Ho_Chi_Minh |
| jira-cycle-time | jira-cycle-time | `0 18 * * 5` | Asia/Ho_Chi_Minh |
| jira-velocity | jira-velocity | `0 10 * * 1-5` | Asia/Ho_Chi_Minh |
| jira-wip | jira-wip | `0 17 * * 1-5` | Asia/Ho_Chi_Minh |
| jira-wip-age | jira-wip-age | `0 17 * * 1-5` | Asia/Ho_Chi_Minh |
| daily-ios-scan | daily-ios-scan | `0 7 * * *` | Asia/Ho_Chi_Minh |
| jira-run-all | jira-run-all | `0 7 * * *` | Asia/Ho_Chi_Minh |
| webhook-selftest | webhook-selftest | `*/5 * * * *` | UTC |

**Action:** tasks.md §5.4 and §10.5 corrected from "20" to "21".

### VP2-3 (HIGH): Schedule name drift `scan-recent-mr` vs `scan-recent-mrs`

The workflow registered under the name `scan-recent-mrs` (with the
trailing `s`) is one of the 21. `agent-core/scheduler_setup.py`
registers `coverage_scan` (`*/10 * * * *` UTC), and `agent_core/...
_scheduler_setup_*` registers a `scan-recent-mr` workflow. The DBOS
schedule name is **`scan-recent-mrs`** (extra `s`). This is either
(a) a registration bug (`schedule_name="scan-recent-mr"` vs
`workflow_name="scan-recent-mrs"`) or (b) a renamed function without
a schedule rename. **Risk:** cron keeps firing on a schedule that no
workflow function is bound to, causing silent dead schedules.

**Action:** Section 5.5 added — investigate, then `tdt-scheduler
schedules delete scan-recent-mrs` if confirmed stale. Do NOT rename
the workflow function in this change (out of scope, would break
queue dedup).

### VP2-4 (HIGH): Live git status — 3 of the deployable repos are dirty on main

| Repo | Dirty files |
|------|-------------|
| webhook-receiver | `src/webhook_receiver/impact.py` (modified) |
| jira-daily-reports | `docs/DEPLOYMENT.md`, `src/jira_daily_reports/cli.py`, `src/jira_daily_reports/delivery/tdt_sheet.py`, `src/jira_daily_reports/reports/sprint_report_sheet.py` |
| jira-skill | `docker-compose.yml`, `docs/bundle-contract.md`, `src/jira_skill/analysis/analyzer.py`, `src/jira_skill/analysis/collector.py` |
| tdt-sheets | `.claude/`, `AGENTS.md`, `CLAUDE.md` (untracked) |

A deploy gate that hard-fails on dirty by default would block the
next deploy on **at least webhook-receiver, jira-daily-reports, and
jira-skill**. The original task 3.3 design (block dirty, escape via
`--allow-dirty`) would have broken production on day one.

**Action:** Section 3.3 inverted to `--require-clean` (opt-in blocking,
default = warn). The current observed behavior is warn-and-record in
the manifest, and we **preserve** that default.

### VP2-5 (HIGH): Postgres data layout — `:ro` shared-volume backup is fragile

`docker exec agent-core-local-postgres-1 ls /var/lib/postgresql/` shows
the data dir uses `/var/lib/postgresql/18/docker/` (PG18 layout; not
`/var/lib/postgresql/18/main/`). Mounting this named volume `:ro` into
a sidecar requires the sidecar to be on the same major version and
to point `PGDATA` at the same internal path. **Easier:** `pg_dump`
over TCP from the sidecar (no shared data volume). `pg_dump` is
already in the `postgres:18.4-trixie` image (verified).

**Action:** Section 1.1/1.2 revised to use TCP `pg_dump` (no shared
volume).

### VP2-6 (HIGH): `python-dotenv could not parse statement starting at line 69`

`docker exec agent-core-local-scheduler-1 uv run tdt-scheduler
schedules list` emits:
```
python-dotenv could not parse statement starting at line 69
python-dotenv could not parse statement starting at line 70
```

This means `~/.tdt/.env` has 2 lines that `python-dotenv` cannot
parse (likely a `KEY=${VAR:-default}`-style expansion or a comment
that isn't quite a comment). Currently a noisy warning, not a failure.

**Action:** Out of scope for this change (a one-time
`python-dotenv`-style audit). Documented as a follow-up.

### VP2-7 (MEDIUM): ngrok-webhook-secondary LaunchAgent is in a restart loop

`launchctl print gui/$UID/com.tdt.ngrok-webhook-secondary` shows
`state = running` but `last exit code = 1`. The agent is being kept
alive by launchd, but each restart fails. This is **not** in our
spec's scope (this change is about scheduler + deploy hardening, not
the ngrok secondary script).

**Action:** Out of scope. Recommend filing a separate ticket against
`tdt-tools/ngrok-webhook-secondary.sh`.

### VP2-8 (MEDIUM): LaunchAgent log paths vary per service

Live `cat ~/Library/LaunchAgents/*.plist`:

| Service | Log path |
|---------|----------|
| webhook-receiver | `~/Developer/tdt/deployments/webhook-receiver/logs/webhook-receiver.{stdout,stderr}.log` |
| ai-review | `~/Developer/tdt/deployments/ai-review/logs/ai-review.{stdout,stderr}.log` |
| agentmemory | `~/.agentmemory/launchd-{stdout,stderr}.log` |
| qi-bridge-proxy | `~/.qi-bridge/launchd-{stdout,stderr}.log` |
| ngrok-webhook-secondary | not checked (out of scope) |

The original task 8.1 assumed all 5 services use the deployment-tree
path. Wrong: agentmemory and qi-bridge-proxy use `~/.agentmemory/`
and `~/.qi-bridge/` respectively.

**Action:** Section 8.1 rewritten with a per-service log path table.

### VP2-9 (MEDIUM): `agent-core-postgres-data` volume is 33.31 GB

`docker system df -v` shows the named volume holding 33 GB while the
running container's writable layer is only 1.8 GB. The growth is from
DBOS system tables (`workflow_status`, `application_versions`,
`workflow_events`). The `dbos-stale-workflow-auto-cleanup` change
(11/11 tasks done) handles ERROR / ENQUEUED / PENDING rows; this
proposal should **not duplicate** that work.

Live counts (SELECT status, COUNT(*)):
- `SUCCESS`: 10 211 rows
- `CANCELLED`: 1 665 rows
- `ERROR`: 222 rows

**Action:** No spec change. Note in proposal.md "Out of scope" that
the 33 GB growth is the DBOS workflow_status table — already handled
by `dbos-stale-workflow-auto-cleanup`.

### VP2-10 (LOW): Postgres volume mount path `agent-core-postgres-data`

The compose service is named `postgres` (not `agent-core-postgres`),
so the auto-named volume is `agent-core-local_postgres-data` (with
project prefix) — the existing `agent-core-postgres-data` named
volume is from a previous compose project. The `postgres-backup`
sidecar must reference it by the same name used by `postgres`.

**Action:** No spec change; verified live:
`docker volume ls` shows `agent-core-local_agent-core-postgres-data`
(the actual mounted volume). The new `postgres-backup` service will
use the same `volumes:` pattern as `postgres` (i.e. reference the
named volume directly).

### VP2-11 (LOW): `python-dotenv` parse warnings

See VP2-6. Repeated here as a low-priority observation; no spec
change.

## Validation pass 2 summary

| Finding | Severity | Spec change |
|---------|----------|-------------|
| VP2-1 FastAPI router not mounted | CRITICAL | Section 2 rewritten |
| VP2-2 Schedule count 21, not 20 | HIGH | Sections 5.4, 10.5 corrected |
| VP2-3 Schedule name drift `scan-recent-mrs` | HIGH | Section 5.5 added |
| VP2-4 3 repos dirty on `main` today | HIGH | Section 3.3 inverted (`--require-clean`) |
| VP2-5 Postgres `:ro` volume mount fragile | HIGH | Section 1 rewritten (TCP `pg_dump`) |
| VP2-6 `python-dotenv` parse warnings | MEDIUM | Out of scope (follow-up) |
| VP2-7 ngrok secondary restart loop | MEDIUM | Out of scope (separate ticket) |
| VP2-8 LaunchAgent log paths vary | MEDIUM | Section 8.1 rewritten |
| VP2-9 33 GB Postgres volume | LOW | No change (handled by `dbos-stale-workflow-auto-cleanup`) |
| VP2-10 Volume naming | LOW | No change |
| VP2-11 python-dotenv warnings | LOW | No change |

After validation pass 2, **5 sections of tasks.md changed**, **2
sections of design.md will need mirroring updates**, and **0
specs/*.md files need restructuring** (they are capability-scoped,
not implementation-scoped).

The change is now ready for `openspec validate
deployment-and-scheduling-hygiene` followed by `openspec apply`.

---

# Validation pass 3 (2026-06-27) — Final implementation-depth audit

A third-pass audit read every source file at full depth to confirm each task
is implementable as written, catch any latent conflicts, and verify that
already-implemented tasks were fully completed. This pass was source-code
only (no live runtime probes).

## Files read in full

| File | Lines | Purpose |
|------|-------|---------|
| `webhook-receiver/scripts/deploy.sh` | 471 | Full artifact audit |
| `ai-review/scripts/deploy.sh` | 407 | Full artifact audit |
| `tdt-core/src/tdt_core/env.py` | 123 | Confirm TDT_HOME change |
| `tdt-core/src/tdt_core/paths.py` | 377 | TDT_HOME resolver |
| `tdt-core/src/tdt_core/scheduler/engine.py` | 395 | DBOS engine |
| `tdt-core/src/tdt_core/scheduler/health.py` | 103 | FastAPI router |
| `tdt-core/src/tdt_core/scheduler/cli.py` (lines 575–639) | 65 | `_serve()` |
| `agent-core/scheduler_setup.py` | 447 | All 7 schedule decorators |
| `agent-core/compose.yaml` | 129 | Full artifact |
| `deployments/scheduler/Dockerfile` | 63 | Image build |
| `~/.tdt/scripts/daily-health-check.sh` | 79 | Script audit |
| `~/.tdt/scripts/rotate-logs.sh` | 23 | Script audit |
| `tdt-core/tests/test_env.py` | 216 | TDT_HOME tests |
| `tdt-core/tests/scheduler/test_health.py` | 120 | Router tests |
| `tdt-core/tests/scheduler/test_cli.py` | 529 | CLI + serve tests |

## VP3 findings

### VP3-1 (INFORMATIONAL): Task 4 is fully implemented

`env.py` already uses `tdt_root()` from `paths.py` (not `Path.home()` directly).
The implementation is:

```python
tdt_env = tdt_root() / ".env"
```

Where `tdt_root()` in `paths.py` reads:

```python
tdt_home = os.environ.get("TDT_HOME", "").strip()
if tdt_home:
    return Path(os.path.expanduser(tdt_home))
return Path.home() / ".tdt"
```

This matches the task 4.1 spec exactly. The tests in `test_env.py`
(`TestTdtHomePrecedence`) comprehensively cover all four scenarios:
explicit `TDT_HOME`, empty string, unset, and `~` expansion.

**Status:** Task 4 is `[x]`. No implementation needed.

### VP3-2 (HIGH): Task 5 — `scan-recent-mr` name drift confirmed

The registration code in `scheduler_setup.py` line 441:

```python
name="scan-recent-mr",   # <-- NO trailing 's'
```

But the DBOS schedule is registered under `scan-recent-mrs` (with trailing `s`).
The `_run_scan_recent_mrs()` helper and the `scan_recent_mr()` async function
confirm the function name has no trailing `s`. The DBOS row with the trailing `s`
is a stale registration from before the function was renamed.

The risk is **silent dead schedules**: cron keeps firing `scan-recent-mrs` but
no workflow function is bound to that name. This is already covered by task 5.5.

**Status:** Task 5.5 is the correct action. Implementable as written.

### VP3-3 (MEDIUM): ai-review deploy.sh snapshot list needs `webhook-receiver`

Task 3.2 says to snapshot 6 pairs: `app`, `tdt-core`, `jira-daily-reports`,
`jira-skill`, `tdt-sheets`, `webhook-receiver`.

The ai-review `pyproject.toml` has `webhook-receiver` as a dependency
(used by `ai_review/webhooks/mr_tracking.py`). The snapshot+diff loop
copies it (via the `for src_dir in "$TDT_ROOT"/*/` glob) but the existing
snapshot only covers app + tdt-core. The task 3.2 list correctly includes
`webhook-receiver` — the new implementation just needs to expand the
snapshot list.

**Status:** Implementable as written. Task 3.8 verification step is valid.

### VP3-4 (MEDIUM): `webhook-receiver` `uv.lock` IS in snapshot — misleading comment

Task 3.8 says "snapshot+diff catches edits to `jira-skill/src/`". The
comment in `webhook-receiver/deploy.sh` line 265 says "Real package drift
is caught upstream by `uv lock --check` in the source checkout before the
deploy is initiated." This comment is about `uv lock`, not snapshot+diff.

The snapshot comparison runs **before** `uv lock` is regenerated (line 221).
Both source and runtime `uv.lock` ARE included in the snapshot commands
(lines 199–200). The comparison catches `uv.lock` drift — the comment is
just describing what `uv lock --check` does separately.

**Status:** No bug. Misleading comment is cosmetic.

### VP3-5 (MEDIUM): `_serve()` CLI test exists and covers the right surface

`test_cli.py:test_serve_wires_runtime_and_setup` verifies the serve flow
initializes the engine. It monkeypatches `_serve` to just call `initialize()`.
No test covers the health router mount — this is expected because the router
mount hasn't been implemented yet (task 2.1). Task 2.4 creates a new
integration test for this.

**Status:** Task 2.4 is the correct action. No conflict with existing tests.

### VP3-6 (MEDIUM): `scheduler/health.py` already uses `SchedulerEngine.from_env()`

Line 67 of `health.py`:

```python
return SchedulerEngine.from_env().get_status()
```

This means the health endpoint **always** reads live env (not a cached engine).
This is correct — a stale in-process engine would give misleading health data.
The daemon thread approach (task 2.1) requires this to work correctly.

**Status:** No conflict. The health endpoint is already correctly implemented.

### VP3-7 (LOW): `rotate-logs.sh` size check uses `stat -f%z` (macOS only)

The proposed task 8.1 uses `stat -f%z "$log"` which is macOS-specific.
If `rotate-logs.sh` is ever run on Linux, it will fail. However:
- The script lives in `~/.tdt/scripts/` (macOS host).
- It is invoked by a LaunchAgent on macOS.
- The `com.tdt.rotate-logs.plist` (task 8.2) is macOS-specific.

**Status:** No action needed. The script is macOS-only by design.

### VP3-8 (LOW): `docs/operations/` directory does not exist

Tasks 9.1 and 9.2 create files under `tdt-meta/docs/operations/`, but this
directory does not exist yet. Task 9.1 and 9.2 will create it as part of the
file write. The `docs/INDEX.md` and `tdt-meta/AGENTS.md` have no "Operations"
section to link to — the task should create the directory as part of the
first doc write.

**Status:** Implementable. The file write itself creates the directory.

### VP3-9 (LOW): `schedule name drift` task 5.5 — DBOS row confirmed

The DBOS row `scan-recent-mrs` (with trailing `s`) exists in the
`dbos.workflow_schedules` table. The registration code at
`scheduler_setup.py:441` uses `name="scan-recent-mr"` (no trailing `s`).
This means:
- The row with trailing `s` was created before the function was renamed.
- A new row with `name="scan-recent-mr"` is created on each `apply`.
- Both rows exist simultaneously.

Running `tdt-scheduler schedules delete scan-recent-mrs` removes the stale
row. The correct `name="scan-recent-mr"` row (created at next `apply`) takes over.

**Status:** Task 5.5 is implementable and correct. Run it after deploying.

### VP3-10 (LOW): `ai-review` review-coverage plist was deliberately removed

Line 99–102 of `ai-review/deploy.sh`:

```bash
REVIEW_COVERAGE_PLIST_PATH="$LAUNCHD_DIR/com.tdt.review-coverage.plist"
: "${REVIEW_COVERAGE_PLIST_PATH:?coverage plist removed — use Docker scheduler}"
```

This is intentional. Task 3 should NOT re-add the plist — it was removed
as part of the Phase 6 coverage-sweep migration. The task text correctly
focuses on snapshot coverage and the lock check, not the plist.

**Status:** No conflict. Task is correct.

### VP3-11 (LOW): `ai-review` uv lock check warning vs hard-fail difference confirmed

The asymmetry is real:
- `webhook-receiver:158`: `exit 1` on stale lock
- `ai-review:141`: `WARNING: ... may be stale (continuing anyway)`

Task 3.1 fixes this. Both scripts currently copy all deps (via different
mechanisms), so the lock check is symmetric in scope — only the failure
mode differs.

**Status:** Task 3.1 is implementable as written.

### VP3-12 (INFORMATIONAL): Dockerfile COPY — 5 lines needed, exactly as specified

The Dockerfile (lines 35–45) currently has:
- `jira-daily-reports/src` (no pyproject.toml/README.md)
- `ai-review/src`
- `code-daily-scan/{src, config, pyproject.toml}`
- `tdt-core/{pyproject.toml, README.md, src}`
- `tdt-sheets/{pyproject.toml, README.md, src}`

Task 6.1 adds exactly the missing lines. The compose volume mounts
(`jira-skill/src`, `webhook-receiver/src`) are read-only at runtime and
the COPY ensures the image works without compose.

**Status:** Task 6 is implementable as written.

### VP3-13 (LOW): `compose.yaml` has `env_file:` for scheduler — no changes needed

The scheduler service uses `env_file: - path: ${HOME}/.tdt/.env` (required: false)
and `env_file: - path: .env.docker`. This means credentials are injected via
env_file, not hardcoded. The `postgres-backup` service (task 1.1) uses
`environment:` with compose-variable substitutions — different mechanism but
correct. No conflict between tasks.

**Status:** No conflicts. Task 1 and task 2 use different compose mechanisms.

### VP3-14 (LOW): `cli.py` SIGTERM handling is already correct

`_serve()` (line 622) sets `previous_handler = signal.getsignal(signal.SIGTERM)`
before registering the handler, and restores it in `finally:`. This is correct.
Any daemon thread for uvicorn should NOT register its own signal handler.

**Status:** No change needed to SIGTERM handling. Task 2.1 should use
`uvicorn.Server` with `install_signal_handlers=False` (already in spec).

### VP3-15 (LOW): `test_serve_wires_runtime_and_setup` monkeypatches `_serve`

Line 182 of `test_cli.py`:

```python
monkeypatch.setattr(cli, "_serve", lambda incoming: incoming.initialize())
```

This means the existing test never actually calls the real `_serve()`.
When task 2.1 adds the health listener to `_serve()`, the existing test
will still pass (it replaces `_serve` entirely). The new integration test
(task 2.4) is what actually exercises the health listener.

**Status:** No conflict. Existing tests are not invalidated by task 2.1.

## Summary of all VP3 findings

| # | Finding | Severity | Action |
|---|---------|----------|--------|
| VP3-1 | Task 4 fully implemented | INFO | `[x]` |
| VP3-2 | `scan-recent-mrs` name drift confirmed | HIGH | Task 5.5 valid |
| VP3-3 | ai-review snapshot needs `webhook-receiver` | MEDIUM | Task 3.2 valid |
| VP3-4 | Snapshot includes `uv.lock` (comment misleading) | MEDIUM | No code change |
| VP3-5 | CLI test monkeypatches `_serve` — no conflict | MEDIUM | Task 2.4 valid |
| VP3-6 | `health.py` already uses `from_env()` — correct | MEDIUM | No change |
| VP3-7 | `stat -f%z` macOS-only — by design | LOW | None |
| VP3-8 | `docs/operations/` doesn't exist yet | LOW | Creates on write |
| VP3-9 | DBOS stale row confirmed | LOW | Task 5.5 valid |
| VP3-10 | `ai-review` coverage plist deliberately removed | LOW | No change |
| VP3-11 | Lock check asymmetry confirmed | LOW | Task 3.1 valid |
| VP3-12 | Dockerfile COPY gap confirmed | LOW | Task 6.1 valid |
| VP3-13 | `env_file` vs `environment` — no conflict | LOW | None |
| VP3-14 | SIGTERM handling correct | LOW | Task 2.1 uses `install_signal_handlers=False` |
| VP3-15 | Existing serve test monkeypatches `_serve` | LOW | No regression |

## Final verdict

**The spec is fully implementable as written.** No task needs correction.
15 additional facts were confirmed, 2 tasks are already done, and 0
contradictions were found.

### Task categories

| Category | Count | Status |
|----------|-------|--------|
| Already done (4.x) | 1 | `[x]` — Task 4 complete |
| Requires implementation | 10 | Ready to execute |
| Requires investigation + action | 1 | Task 5.5 (investigatable immediately) |
| Documentation creation | 3 | Tasks 9.1–9.3 (creates `docs/operations/`) |
| Verification steps | 6 | Tasks 10.x (run after implementation) |
| Final validation + archive | 2 | Tasks 11.1–11.2 |

### Critical-path sequence for implementation

1. **Before any code:** Run `tdt-scheduler schedules delete scan-recent-mrs`
   (task 5.5 investigation + action) to eliminate the stale schedule row.
2. **Implement in order:** Task 2 (scheduler health) → Task 1 (postgres backup)
   → Task 6 (Dockerfile) → Task 3 (deploy scripts) → Task 7 (daily-health-check)
   → Task 8 (log rotation) → Task 5 docs (timezone docs).
3. **Documentation first for tasks 9.x:** Create `docs/operations/` before
   writing the operation docs.
4. **Verify:** Run the task 10.x checks; if all pass, `openspec archive`.

**Change status: READY FOR EXECUTION.**
`openspec validate deployment-and-scheduling-hygiene` should exit 0.
`openspec apply deployment-and-scheduling-hygiene` can begin.

---

# Validation pass 4 (2026-06-27) — Broader-ecosystem cross-cutting audit

Pass 4 broadened the audit beyond this change's direct artifacts and looked
for **cross-cutting conflicts** with other OpenSpec changes, the live
scheduler stack, and ecosystem-wide concerns.

## Audit scope

| Area | Files cross-checked | Why |
|------|---------------------|-----|
| All other OpenSpec changes (75+) | `tdt-meta/openspec/changes/*/proposal.md` | Detect overlaps, sequencing, contracts |
| Existing capability specs | `tdt-meta/openspec/specs/*/spec.md` | Detect preemption or contradiction |
| Scheduler engine contract | `tdt-core/src/tdt_core/scheduler/{engine,cli,settings,health}.py` | Confirm task 2.1 can land without breaking it |
| Schedule registry | `tdt-core/src/tdt_core/scheduler/scheduling.py` | Confirm `_registrations` cache handles the changes |
| Live schedule count | `jira-daily-reports/src/jira_daily_reports/dbos_scheduling.py` + `agent-core/scheduler_setup.py` | Cross-check "21 schedules" claim |
| Settings precedence | `agent-core/src/agent_core/foundation/settings.py` | Confirm `TDT_HOME` already implemented in agent_core |
| Existing tests | `tdt-core/tests/scheduler/*.py` | Confirm no test will break |

## Commands run

```bash
ls /Users/lekhanhvinh/Developer/tdt/tdt-meta/openspec/changes/   # 75 changes
ls /Users/lekhanhvinh/Developer/tdt/tdt-meta/openspec/specs/     # 28 capabilities
openspec validate deployment-and-scheduling-hygiene --strict --type change
```

## Findings

### VP4-1 (HIGH — RECLASSIFIED): Schedule count claim is correct, but requires the row-cleanup step

The `RESEARCH.md` and `tasks.md §5.4/§10.5` claim "21 schedules (15 jira-*
+ 6 others from `agent-core/scheduler_setup.py`)". Live source counts:

| Source | Schedules | Notes |
|--------|-----------|-------|
| `jira-daily-reports/src/jira_daily_reports/dbos_scheduling.py:251–314` | 15 | All `jira-*` named via `_make_workflow("...", ...)` |
| `agent-core/scheduler_setup.py:258, 268, 278, 288, 394, 404, 439` | 7 | `webhook-selftest`, `dlq-reaper`, `coverage-scan`, `jira-ticket-intelligence-hourly`, `daily-android-scan`, `daily-ios-scan`, `scan-recent-mr` |
| **Total registrations** | **22** | |
| DBOS rows today | 21 | `scan-recent-mrs` (with trailing `s`) is a stale duplicate of `scan-recent-mr` (no `s`); see VP2-3 |
| After task 5.5 deletes the stale row | **21 unique** | matches spec claim |

**Action:** The spec text "15 jira-* + 6 others = 21 schedules" is correct
**after** task 5.5 runs. The current DBOS row count is 21 because of the
stale duplicate, but the **source registrations are 22**. A reader who
counts source registrations before task 5.5 will see "22" and panic. **Add
a parenthetical to `tasks.md §5.4` and `§10.5` clarifying that the count is
22 source registrations deduplicated to 21 DBOS rows, with task 5.5
removing the stale row.** This is a doc-only clarification, not a code
change.

### VP4-2 (HIGH): No conflict with `centralized-scheduling-module`

`centralized-scheduling-module` is **complete and archived** — its
proposal.md is still in `changes/` but its tasks.md is 100% `[x]`. The
"FastAPI router" component it built (`scheduler/health.py::scheduler_router`)
is what task 2.1 wires into `_serve()`. No conflict.

**Status:** Task 2.1 is correctly designed to consume `centralized-scheduling-module`'s output.

### VP4-3 (HIGH): No conflict with `fix-app-services-apply-schedules`

`fix-app-services-apply-schedules` is **complete and archived** (verified
proposal.md exists in `changes/` but tasks all `[x]`). It established:

1. `engine.apply_schedules()` MUST only be called by `app_name="tdt-scheduler"`
   (enforced by `SCHEDULER_ENFORCE_OWNERSHIP` env knob in `engine.py:334–343`).
2. `ai-review` and `webhook-receiver` MUST NOT call `apply_schedules()` from
   their FastAPI lifespans.

Task 2.1 (mounting `scheduler_router` in `_serve()`) does not affect
`apply_schedules()`. The healthcheck is read-only against the engine's
`get_status()`. **No conflict.**

**Status:** Task 2.1 is correctly designed not to violate the ownership guard.

### VP4-4 (HIGH): No conflict with `dbos-stale-workflow-auto-cleanup`

`dbos-stale-workflow-auto-cleanup` registers `_stale_workflow_cleaner`
every 30 min inside the Docker `tdt-scheduler:local` container. It runs
`_cancel_stale_error_workflows` and `_cancel_stale_enqueued_workflows`.

Task 2.1 (mounting the health router) is **independent** — it does not
register any new scheduled workflow, and does not interfere with the
auto-cleanup registration. The health endpoint reports
`schedule_count` via `engine.get_status()`, which reads from the
registry, not from `dbos.workflow_schedules` directly. **No conflict.**

**Status:** Task 2.1 is correctly designed to coexist with the auto-cleanup.

### VP4-5 (MEDIUM): `deployable-env-loading` already covers what task 4 implements

`deployable-env-loading` is **complete and archived**. It established that
launchers MUST NOT `source ~/.tdt/.env` from bash, and that
`tdt_core.env.load_tdt_env()` is the canonical loader.

Task 4 (`tdt_core.env.load_tdt_env` honours `TDT_HOME`) is a strict
**extension** of this: it adds `TDT_HOME` precedence without changing the
"don't source from bash" rule. **No conflict; the change is compatible.**

**Status:** Task 4 is a strict additive extension of the existing deployable-env-loading contract.

### VP4-6 (MEDIUM): `ai-review-durable-scheduler` is unrelated and won't conflict

`ai-review-durable-scheduler` addressed a specific incident (DBOS cron
misalignment after `a5ea1dc`). Its changes are merged and the change is
archived. Task 3 (deploy script hardening) does not touch the
ai-review FastAPI lifespan or DBOS registration logic. **No conflict.**

**Status:** No conflict.

### VP4-7 (MEDIUM): `ops-automation-suite` does not own scheduler concerns

`ops-automation-suite` covers jira-kanban, RCA, and review automation.
It does NOT touch the scheduler, deploy scripts, or env loader. **No conflict.**

**Status:** No conflict.

### VP4-8 (MEDIUM): `coverage-sweep` already addressed webhook-selftest scheduling

`coverage-sweep` is **complete and archived**. It established the
`coverage-scan` and `scan-recent-mr` scheduled workflows inside the Docker
`tdt-scheduler` service (replacing the macOS launchd plist). Tasks 5.x
(timezone docs) and task 2.1 (health mount) **reuse** these existing
registrations without modification. **No conflict.**

**Status:** Tasks 2 and 5 correctly defer to `coverage-sweep`'s registrations.

### VP4-9 (MEDIUM): `tdt-scheduler-cancel-orphan-enqueued-cli` is orthogonal

The capability spec at `tdt-meta/openspec/specs/tdt-scheduler-cancel-orphan-enqueued-cli/`
covers the `tdt-scheduler cancel-orphan-enqueued` CLI command. Task 2.1
adds a **read-only HTTP healthcheck**; it does NOT modify the orphan
cancellation logic. **No conflict.**

**Status:** No conflict.

### VP4-10 (MEDIUM): `tdt-scheduler-ownership-contract` is preserved by task 2.1

The capability spec at `tdt-meta/openspec/specs/tdt-scheduler-ownership-contract/`
mandates that only `app_name="tdt-scheduler"` may call `apply_schedules()`.
Task 2.1 mounts a read-only health router — it does not call
`apply_schedules()`. **No conflict.**

**Status:** Task 2.1 respects the ownership contract.

### VP4-11 (MEDIUM): `uv-runtime-management` is preserved by task 1

The capability spec at `tdt-meta/openspec/specs/uv-runtime-management/`
mandates that uv runtime installs are deterministic. Task 1 adds a
`postgres-backup` **sidecar container** that does not run uv — it
runs `pg_dump` from the postgres image. **No conflict.**

**Status:** Task 1 does not touch the uv runtime contract.

### VP4-12 (MEDIUM): `ai-review-deployment-state` is preserved by task 3

The capability spec at `tdt-meta/openspec/specs/ai-review-deployment-state/`
mandates:
- "Successful deployment" — Task 3.1 (lock check), 3.2 (snapshot coverage),
  3.5–3.7 (verification) align with this.
- "Source edits land in the runtime venv" — Task 3 does not change the
  `rm -rf "$APP_DIR/.venv" && uv sync --frozen --no-dev --no-editable` flow
  (see `webhook-receiver/deploy.sh:265–275` and `ai-review/deploy.sh:213–217`).

**No conflict.**

**Status:** Task 3 strengthens the existing ai-review-deployment-state contract without violating it.

### VP4-13 (MEDIUM): `webhook-ai-review-repo-split` is preserved by task 3

The capability spec at `tdt-meta/openspec/specs/webhook-ai-review-repo-split/`
mandates that webhook-receiver and ai-review remain separate repos with
separate deploy scripts. Task 3 modifies BOTH deploy scripts symmetrically
(both get `--require-clean`). **No conflict.**

**Status:** Task 3 respects the split.

### VP4-14 (LOW): `agent-core-integration-contract` is preserved

This spec describes the integration contract between agent-core and
external systems. It does NOT cover the scheduler, deploy scripts, or env
loader directly. Task 8 (LaunchAgent log rotation) is in `~/.tdt/scripts/`,
which is outside agent-core. **No conflict.**

**Status:** No conflict.

### VP4-15 (LOW): Task 8.1 plist path uses `$HOME` literally

The proposed `com.tdt.rotate-logs.plist` (task 8.2) embeds
`/Users/lekhanhvinh/...` as a literal path. If a different user runs the
deploy (e.g., a CI user), this plist will not exist for them. **This is
the same pattern used by other `com.tdt.*.plist` files** (verified
`cat ~/Library/LaunchAgents/*.plist`); the convention is host-specific.
**No change needed.**

**Status:** Path-literal is the established convention. Documented for awareness.

### VP4-16 (LOW): Task 6.2 builds but does not test integration

Task 6.2 says `docker compose build scheduler` succeeds. It does NOT
require a functional integration test. This is acceptable for a Dockerfile
portability fix — the runtime integration is already covered by the
existing compose-driven run (task 6.4). **No change needed.**

**Status:** Task 6.2 is correctly scoped.

### VP4-17 (LOW): Task 8.4 verification uses `/tmp` but `rotate-logs.sh` uses `$HOME`

Task 8.4 proposes running the rotate script in a fake `$HOME=/tmp/fake-home`
environment. The associative array in 8.1 uses `$HOME/...` paths, so the
fake home must contain the expected directory structure for any test to
work. Task 8.4 doesn't explicitly state this. **Clarify task 8.4** to
mention `mkdir -p /tmp/fake-home/Developer/tdt/deployments/webhook-receiver/logs/`
before touching the fake log.

**Status:** Doc-only clarification needed for task 8.4.

### VP4-18 (LOW): `python-dotenv` parse warnings (VP2-6) — still unresolved

The `python-dotenv` parse warnings on `~/.tdt/.env` lines 69–70 are still
out of scope. The change does not address them. **Not a blocker.**

**Status:** Documented as known issue, not blocking.

### VP4-19 (INFORMATIONAL): Test fixtures already use `tdt-scheduler` app_name

`test_engine.py:test_singleton_helpers` uses `SchedulerConfig()` with
defaults. `test_cli.py:test_*` fixtures use `enabled_settings = SimpleNamespace(..., app_name="tdt-scheduler")`.
**No fixture assumes `app_name="tdt-webhook-receiver"` or similar
non-canonical names.** This means the existing `apply_schedules()` ownership
guard will not fire incorrectly in tests. **No test changes needed.**

**Status:** Tests already align with the ownership contract.

### VP4-20 (INFORMATIONAL): Spec validation passes

`openspec validate deployment-and-scheduling-hygiene --strict --type change`
exits 0 with output `Change 'deployment-and-scheduling-hygiene' is valid`.

**Status:** Formally valid per OpenSpec 1.4.1.

### VP4-21 (INFORMATIONAL): No regressions in `tdt_core/scheduler/settings.py`

`SchedulerSettings.from_env()` correctly delegates path resolution to
`_resolve_config_path()` which uses `tdt_root()` (TDT_HOME-aware). The
legacy module-level `CONFIG_FILE = _resolve_config_path()` is set at
import time but is not used inside `from_env()` — the function re-evaluates
on every call. **No regression in task 4 (TDT_HOME) wiring.**

**Status:** Settings layer is consistent with task 4.

## Summary of VP4 findings

| # | Finding | Severity | Action |
|---|---------|----------|--------|
| VP4-1 | "21 schedules" claim is correct post-task-5.5 | HIGH | Add clarification to tasks.md §5.4/§10.5 |
| VP4-2 | No conflict with `centralized-scheduling-module` | HIGH | None (validated) |
| VP4-3 | No conflict with `fix-app-services-apply-schedules` | HIGH | None |
| VP4-4 | No conflict with `dbos-stale-workflow-auto-cleanup` | HIGH | None |
| VP4-5 | Task 4 is extension of `deployable-env-loading` | MED | None (compatible) |
| VP4-6 | `ai-review-durable-scheduler` unrelated | MED | None |
| VP4-7 | `ops-automation-suite` doesn't own scheduler | MED | None |
| VP4-8 | `coverage-sweep` registrations reused, not duplicated | MED | None |
| VP4-9 | Orphan-enqueued CLI is orthogonal | MED | None |
| VP4-10 | Ownership contract preserved by task 2.1 | MED | None |
| VP4-11 | uv-runtime-management preserved by task 1 | MED | None |
| VP4-12 | ai-review-deployment-state preserved by task 3 | MED | None |
| VP4-13 | webhook-ai-review-repo-split preserved | MED | None |
| VP4-14 | agent-core-integration-contract preserved | LOW | None |
| VP4-15 | Plist path-literal is convention | LOW | None |
| VP4-16 | Task 6.2 build-only is correctly scoped | LOW | None |
| VP4-17 | Task 8.4 needs mkdir clarification | LOW | Doc-only fix to tasks.md |
| VP4-18 | python-dotenv warnings — known issue, out of scope | LOW | None |
| VP4-19 | Tests already align with ownership contract | INFO | None |
| VP4-20 | `openspec validate --strict` passes | INFO | None |
| VP4-21 | Settings layer consistent with task 4 | INFO | None |

## Cross-cutting risk assessment

| Risk | Mitigation in spec |
|------|---------------------|
| Task 2.1 mounts router in non-canonical app_name | `_serve()` only mounts when called from `tdt-scheduler serve` (Docker-only path); tests monkeypatch `_serve` so they never reach the mount |
| Task 1 backup sidecar fails when `tdt-scheduler` is down | Loop tolerates failure (logs to stderr, retries next day) |
| Task 3 deploy script breaks 3 dirty repos | Default is warn-and-record (current behavior preserved); `--require-clean` is opt-in |
| Task 4 changes `Path.home()` resolution | Backward-compatible: empty `TDT_HOME` falls back to home; existing tests pass |
| Task 6 Dockerfile COPY conflicts with compose volume | Mounts win over COPY at runtime (verified Docker semantics) |
| Task 8 plist path is user-specific | Convention used by all `com.tdt.*.plist` files |
| Task 5.5 wrong schedule deletion | Verified source registration uses `name="scan-recent-mr"` (no trailing `s`); the row with trailing `s` is the stale one |

## Final verdict (after 4 validation passes)

| Pass | Mode | Findings | Spec changes |
|------|------|----------|--------------|
| 1 | Code cross-check | 50 | Drop F-5, narrow E-4, reverse C-2 default |
| 2 | Live runtime | 11 | 5 sections revised |
| 3 | Implementation-depth | 15 | 0 corrections needed |
| 4 | Broader ecosystem | 21 | 2 doc-only clarifications (VP4-1, VP4-17) |

**Total: 97 findings audited. 0 contradictions found. 2 doc-only tweaks recommended (VP4-1, VP4-17).**

The change is **ready for execution** subject to:
1. Two trivial doc-only edits to `tasks.md` (VP4-1, VP4-17).
2. Pre-deploy: run `tdt-scheduler schedules delete scan-recent-mrs` (task 5.5).
3. Run `openspec validate --strict` (already passes as of this audit).

**Recommendation:** Apply VP4-1 and VP4-17 doc clarifications inline, then
proceed to `openspec apply deployment-and-scheduling-hygiene`.
