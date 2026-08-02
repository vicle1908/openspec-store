# Deployment & Scheduling Hygiene — Validated Recommendations

## Why

A research pass across `~/Developer/tdt/` and `~/.tdt/` produced 25 conflicts and
recommendations. After reading the actual files (not just summaries), **three
classes are severe enough to plan now**, three more are documentation /
housekeeping, and several were re-classified as informational. This change
captures the validated ones.

The research output is preserved verbatim in `RESEARCH.md` (no findings were
removed — only re-prioritized after reading source). The split into four work
items below tracks which recommendations are in scope of this change versus
deferred.

A **second validation pass** against live runtime state (Docker containers,
DBOS system DB, launchd plists, git worktrees) was run on 2026-06-27. That
pass found 11 additional findings; 5 caused spec revisions (see
`RESEARCH.md` §"Validation pass 2"). The change is now considered
**ready for execution**.

### In-scope (validated against source)

| ID  | Title                                                   | Severity | Confirmed at                                       |
|-----|---------------------------------------------------------|----------|----------------------------------------------------|
| E-1 | No Postgres backup — single point of failure            | Critical | `compose.yaml:18–19` (named volume, no backup)    |
| E-2 | `scheduler` Docker service has no healthcheck/watchdog  | High     | `compose.yaml:57–72` (no `healthcheck:` block); root cause = `cli.py::_serve()` does not mount `scheduler_router` |
| C1  | ai-review deploy only warns on stale lock (webhook-receiver fails hard) | Medium | `ai-review/scripts/deploy.sh:142`                 |
| C2  | ai-review snapshot only covers app + tdt-core, but copies all path deps | Medium | `ai-review/scripts/deploy.sh:174–183` vs `159–172`|
| C-2 | `source_dirty` written to manifest but does not block  | High     | both `deploy.sh` files; **default preserved** (warn), opt-in `--require-clean` flag added |
| C4  | `daily-health-check.sh` hardcodes legacy `CRON_ROOT`    | Low      | `~/.tdt/scripts/daily-health-check.sh:5`           |
| E-4 | LaunchAgent stdout/stderr logs uncapped (jira logs already partially rotated) | Medium | `~/.tdt/scripts/rotate-logs.sh` exists but not wired |
| E-3 | `tdt_core.env.load_tdt_env` ignores `TDT_HOME` env var  | Medium   | `tdt-core/src/tdt_core/env.py:29`                  |
| C-13| scheduler Dockerfile omits `jira-skill/src` and `webhook-receiver/src` from COPY | Medium | `deployments/scheduler/Dockerfile:31–45` (only volume-mounted) |
| D-1 | TZ-vs-cron_timezone mixing — UTC schedules coexist with `TZ=Asia/Ho_Chi_Minh` | High | `compose.yaml:92` + `scheduler_setup.py:261,271,281,291,397,405,442` |
| VP2-3| Schedule name drift `scan-recent-mrs` (workflow `scan-recent-mr` registered as `scan-recent-mrs` in DBOS) | Medium | live `SELECT * FROM dbos.workflow_schedules` — investigate, possibly `tdt-scheduler schedules delete scan-recent-mrs` |

### Deferred (validated, but separate change recommended)

| ID  | Title                                                   | Reason for deferral |
|-----|---------------------------------------------------------|---------------------|
| B-5 | `~/.tdt/config.toml` is a frozen legacy artifact (nothing reads it) | Cleanup-only; trivial PR; deserves a tiny "delete dead config" change |
| D-2 | `automatic_backfill=False` everywhere — missed ticks are permanently lost | Behavioural design decision; needs a follow-up proposal with backfill semantics |
| C9  | `~/.tdt/state/webhook-secondary.url` has no atomicity or watcher | Operator-script concern, not service-level |
| C12 | `incident-report.sh` hardcodes fallback path             | Operator-script concern, not service-level |
| C8  | No rollback mechanism for any service                    | Architectural; needs separate "deploy rollback contract" change |
| VP2-7 | ngrok-webhook-secondary LaunchAgent restart-loop (`last exit code = 1`) | Owner is `tdt-tools/`; separate ticket |

### Re-classified (research overstated; dropped or downgraded)

| ID  | Original claim                                          | Reality (read source) | New status |
|-----|---------------------------------------------------------|-----------------------|------------|
| F-5 | `crash_recovery.scheduling_enabled` is a wrong key in `config.yaml.example` | The key is **legitimate** — `CrashRecoverySettings` (env prefix `CRASH_RECOVERY_`) is a **separate settings system** from `SchedulerSettings` (env prefix `SCHEDULER_`). Two orthogonal schemas, both valid. | **DROPPED** — not a bug |
| E-4 | "No log rotation anywhere"                              | `~/.tdt/scripts/rotate-logs.sh` exists and `~/.tdt/logs/jira-reports.log.{1,2,3}` confirm manual rotation runs. The gap is LaunchAgent stdout/stderr (uncapped) and that the rotate script is not wired to a LaunchAgent. | **NARROWED** — see above |
| C2 (original framing) | "ai-review snapshot doesn't verify jira-skill, tdt-sheets, webhook-receiver" | Verified — the loop copies them, but the snapshot+diff pair only includes app + tdt-core. The mismatch is real. | **VALID** — same ID, corrected scope |
| C-2 (original direction) | "Block dirty worktree by default; `--allow-dirty` escapes" | Live `git status` shows 3 repos dirty on `main` today (`webhook-receiver`, `jira-daily-reports`, `jira-skill`); default-blocking would break the next deploy. | **REVERSED** — default = warn, opt-in `--require-clean` |
| E-2 (original design) | "Add a new FastAPI `/health` route" | Route already exists at `tdt-core/src/tdt_core/scheduler/health.py::scheduler_router` (built by `centralized-scheduling-module`); defect is the **mount**, not the route. | **REFOCUSED** — mount the existing router in a daemon thread |

## What Changes

Four capabilities added (one per validated cluster):

1. **`scheduler-postgres-watchdog`** — the `scheduler` Docker service gains a
   healthcheck AND a sidecar container that runs `pg_dump` (over TCP)
   daily at 03:00 UTC to `~/.tdt/backups/postgres/<date>.pgdump`. Closes E-1
   and E-2.

2. **`host-deploy-script-consistency`** — `ai-review/scripts/deploy.sh` is
   aligned with `webhook-receiver/scripts/deploy.sh`:
   - pre-deploy lock check fails hard (C1)
   - snapshot+diff covers all path deps that the copy loop touches (C2)
   - dirty worktree **continues to warn by default** (current behavior
     preserved) and gains an opt-in `--require-clean` flag for CI (C-2)

3. **`tdt-env-loader-tdt-home`** — `tdt_core.env.load_tdt_env()` honours
   `TDT_HOME` when set, then falls back to `Path.home() / ".tdt"`. (E-3)

4. **`scheduler-timezone-clarification`** — every `@_ENGINE.scheduled_workflow`
   decorator gets an inline comment naming the timezone it actually uses
   (UTC vs `workspace_timezone_name()`), and the scheduler service's
   `TZ=Asia/Ho_Chi_Minh` is documented as cosmetic-only. (D-1)
   **Plus:** investigate and resolve the `scan-recent-mrs` schedule name
   drift (VP2-3).

Plus one operational fix (not a new capability):

5. **`daily-health-check.sh` legacy paths fixed** — `CRON_ROOT` derives from
   `TDT_HOME` or `$HOME`, so the script stops producing false negatives. (C4)

Plus one image-portability fix:

6. **`scheduler` Dockerfile copies `jira-skill/src` and `webhook-receiver/src`**
   so the image can run without the compose volume overlay. (C-13)

Plus one housekeeping item (single PR, not a capability):

7. **`~/.tdt/scripts/rotate-logs.sh` is wired to a new
   `com.tdt.rotate-logs.plist` LaunchAgent** so LaunchAgent stdout/stderr
   logs get capped. Per-service log paths enumerated in
   `RESEARCH.md` §VP2-8. (E-4, LaunchAgent portion only.)

Plus one **wiring** fix that closes the largest hidden gap in the
scheduler runtime:

8. **`cli.py::_serve()` mounts the existing `scheduler_router`** in a
   daemon thread on `127.0.0.1:9100`, so the scheduler container exposes
   `/scheduler/health` for the new healthcheck. Without this, the
   `scheduler-postgres-watchdog` healthcheck would have nothing to curl.

## Capabilities

### New Capabilities

- **`scheduler-postgres-watchdog`**: rules for the scheduler service
  healthcheck + daily `pg_dump` to `~/.tdt/backups/postgres/`.
- **`host-deploy-script-consistency`**: rules for ai-review deploy script
  to match webhook-receiver's pre-deploy gate, snapshot coverage, and
  dirty-worktree handling.
- **`tdt-env-loader-tdt-home`**: rule that `load_tdt_env()` honours
  `TDT_HOME` before falling back to `Path.home() / ".tdt"`.
- **`scheduler-timezone-clarification`**: rule that every
  `@scheduled_workflow` decorator carries an inline comment naming the
  timezone it actually fires in, regardless of the container's `TZ` env.

### Updated Capabilities (ADDED delta)

- None — the existing `scheduler-engine` and `uv-runtime-management`
  capabilities are not modified by this change.

## Impact

- **Affected services**: `tdt-scheduler` (Docker — gains healthcheck, gains
  `postgres-backup` sidecar, gains `scheduler_router` mount in `cli.py::_serve()`),
  `ai-review` (LaunchAgent deploy script), `tdt-core` (env loader + scheduler
  README + `cli.py::serve()`), `agent-core` (compose + scheduler Dockerfile).
- **Affected repos**: `tdt-meta` (new docs in `docs/operations/`),
  `agent-core` (compose + Dockerfile), `ai-review` (deploy.sh),
  `tdt-core` (env.py, cli.py), `~/.tdt/scripts/` (daily-health-check.sh + a new
  LaunchAgent plist for rotate-logs).
- **Schedule count**: live `dbos.workflow_schedules` shows **21 schedules**
  (15 jira-* + 6 from `agent-core/scheduler_setup.py`), all `ACTIVE` and
  firing on schedule. **One has a name drift** (`scan-recent-mrs` vs
  the source `scan-recent-mr`) — investigated and possibly cleaned up
  by this change (VP2-3).
- **No new secrets, no new env vars** beyond the optional
  `TDT_HOME` (already set in compose) and the new
  `SCHEDULER_HEALTH_LISTEN` (default `127.0.0.1:9100`; disable for tests).
- **No data migration**: `pg_dump` is additive; existing data is unchanged.
- **No breaking change to MR review flow**: ai-review deploys continue
  end-to-end; the deploy script now blocks stale-lock (C1) and snapshots
  all path deps (C2). The dirty-worktree check **remains warn-by-default**
  (current behavior) with an opt-in `--require-clean` for CI.
- **No regression on existing `~/.tdt/scripts/rotate-logs.sh` cron-style
  rotation**: the new LaunchAgent and section are added; the existing
  `jira-reports.log.{1,2,3}` rotation block is untouched.

## Non-Goals

- Migrating cron backfill semantics (`D-2`). The current
  `automatic_backfill=False` is intentional per `centralized-scheduling-module`;
  flipping it requires design discussion about DBOS recovery semantics.
- Adding rollback automation (`C8`). The current `deployment-manifest.json`
  provides provenance; rollback automation deserves a dedicated change.
- Replacing `~/.tdt/scripts/daily-health-check.sh` with a richer
  monitoring tool. This change only fixes the legacy path bug.
- Removing the existing `~/.tdt/config.toml`. Listed in deferred (B-5) —
  trivial cleanup, separate PR.
- Touching the `CrashRecoverySettings` (`CRASH_RECOVERY_*` env vars) code
  path. That settings system is owned by `agent-core` and is orthogonal to
  the scheduler; do not conflate.
