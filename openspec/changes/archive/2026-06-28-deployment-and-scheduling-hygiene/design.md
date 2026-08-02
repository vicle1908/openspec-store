# Design Notes — Deployment & Scheduling Hygiene

## 1. `scheduler-postgres-watchdog` (E-1 + E-2)

### E-1 Postgres backup

**State today.** `agent-core/compose.yaml:18–19`:

```yaml
volumes:
  - agent-core-postgres-data:/var/lib/postgresql
  - ./docker-entrypoint-initdb.d:/docker-entrypoint-initdb.d:ro
```

The named volume `agent-core-postgres-data` is the **only** storage. If it
corrupts or the host disk dies, all DBOS schedule metadata, debouncer queue
state, and `agentmemory` data is lost.

**Why no backup today.** `~/.tdt/backups/` contains jira.db (57 KB),
crontab backups, and a Jira filter backup — but **no Postgres dump**
(verified 2026-06-27, `ls ~/.tdt/backups/`). The `agentmemory`
LaunchAgent has no backup hook either.

**Design (revised 2026-06-27).**

- Add a new container `postgres-backup` to `agent-core/compose.yaml` that
  runs `pg_dump --format=custom --compress=9` once a day at 03:00 (off-peak,
  matches the `dlq-reaper` cadence). Output to a bind-mounted
  `~/.tdt/backups/postgres/YYYY-MM-DD.pgdump`.
- **Connection method:** `pg_dump` runs **inside the sidecar container**
  against the live `postgres` service over TCP, **not** against a shared
  data volume. The original design (`:ro` mount of
  `agent-core-postgres-data`) was rejected because:
  1. The PG18 internal layout is `/var/lib/postgresql/18/docker/` (not
     `/var/lib/postgresql/18/main/` as in PG14) — the sidecar would need
     `PGDATA=/var/lib/postgresql/18/docker` to read it correctly.
  2. Any future major version bump (PG19, PG20) breaks the sidecar in
     ways the operator does not notice until backup time.
  3. `pg_dump` is already in the `postgres:18.4-trixie` image (verified
     `docker exec … which pg_dump`), so no extra apt install is needed.
- **Loop pattern:** the sidecar sleeps until 03:00 UTC of the next day
  (`date -u -d 'tomorrow 03:00 UTC' +%s`), runs `pg_dump`, then sleeps
  again. It does **not** `depends_on` postgres at startup — it tolerates
  Postgres being down (logs to `/backups/pg_dump.err.log`, exits cleanly,
  the next loop iteration retries).
- Retention: keep 30 days (`find /backups -name '*.pgdump' -mtime +30 -delete`).
- Restore procedure is operator-driven: `docker compose stop scheduler app &&
  pg_restore -d agent_core <snapshot>.pgdump && docker compose start scheduler app`.
  Documented in `docs/operations/postgres-restore.md`.

**Alternatives considered.**

- Host LaunchAgent running `pg_dump` against the host-exposed port (54329).
  Rejected because the Postgres container may not be running, and the
  LaunchAgent does not know when the stack is healthy. A sidecar container
  with `depends_on: postgres: condition: service_healthy` is more robust.
  (We still use the sidecar, just not for `depends_on`; the loop
  tolerates Postgres being down.)
- Shared `:ro` volume mount. Rejected (see "Connection method" above).
- WAL archiving to S3. Out of scope — local backup closes the immediate
  SPOF. A follow-up change can add off-host.

### E-2 Scheduler healthcheck

**State today.** `agent-core/compose.yaml:57–72`:

```yaml
scheduler:
  image: tdt-scheduler:local
  ...
  restart: unless-stopped
  command: ["uv", "run", "tdt-scheduler", "serve"]
  # no healthcheck: block
```

A scheduler hang (DBOS queue worker deadlock, Python hang on a long
subprocess) keeps the container "running" but stops firing cron.

**Design (revised 2026-06-27).** The proposal originally described
adding a brand-new `/health` FastAPI route. **That route already exists.**
The defect is **mounting**, not defining.

- `tdt-core/src/tdt_core/scheduler/health.py` defines `scheduler_router`
  with 4 endpoints: `/scheduler/health`, `/scheduler/schedules`,
  `/scheduler/schedules/{name}`, `/scheduler/schedules/{name}/trigger`.
  Built by `centralized-scheduling-module` task 3.1–3.5 (all `[x]`).
- `cli.py::_serve()` (lines 622–639) currently calls:
  ```python
  _cancel_stale_pending_workflows(engine)
  _cancel_stale_enqueued_workflows(engine)
  engine.initialize()
  engine.apply_schedules()
  stop_event.wait()
  ```
  No uvicorn, no `scheduler_router` import, no HTTP listener.
- **Fix:** add a daemon thread in `_serve()` that imports
  `scheduler_router` from `.health`, mounts it under prefix `/scheduler`,
  and runs `uvicorn` on `127.0.0.1:9100`. The thread is non-blocking
  (`uvicorn.Server` with `install_signal_handlers=False`); the main
  thread still owns SIGTERM via `stop_event`.
- **Configurable:** `SCHEDULER_HEALTH_LISTEN` (default `127.0.0.1:9100`;
  `""` or `0` to disable for unit tests that don't need the port).
- **Healthcheck:** `curl -fsS http://127.0.0.1:9100/scheduler/health`,
  interval 60 s, timeout 10 s, retries 3, start_period 120 s.

## 2. `host-deploy-script-consistency` (C1 + C2 + C-2)

### C1 — lock check failure mode

`ai-review/scripts/deploy.sh:134–145`:

```bash
for src_dir in "$SRC" "$TDT_ROOT"/*/; do
  ...
  if ! ( cd "$src_dir" && uv lock --check 2>/dev/null ); then
    echo "WARNING: $src_dir/uv.lock may be stale (continuing anyway)"
  fi
done
```

`webhook-receiver/scripts/deploy.sh:158–164` fails hard on the same
condition. The ai-review loop is structurally identical but uses
`2>/dev/null` and prints WARNING instead of failing. This is a clear
asymmetry.

**Design.** Mirror webhook-receiver's logic exactly: drop `2>/dev/null`,
print `ERROR: ...` with the same remediation text, `exit 1`. Same for both
deploy scripts.

### C2 — snapshot coverage

`ai-review/scripts/deploy.sh:159–172` copies **all** repos with
`pyproject.toml` into `$DEPLOYMENT_ROOT/deps/`:

```bash
for src_dir in "$TDT_ROOT"/*/; do
  ...
  if [ -f "$src_dir/pyproject.toml" ] && grep -q "^\[project\]" ...; then
    mkdir -p "$DEPS_DIR/$repo_name"
    echo "  copying $repo_name"
    cp -R "$src_dir/src" "$src_dir/pyproject.toml" "$DEPS_DIR/$repo_name/" 2>/dev/null || true
    [ -f "$src_dir/README.md" ] && cp "$src_dir/README.md" "$DEPS_DIR/$repo_name/" || ...
  fi
done
```

But `ai-review/scripts/deploy.sh:174–183` only snapshots + diffs app + tdt-core:

```bash
SOURCE_APP_SNAPSHOT_PATH="$STATE_DIR/source-app.sha256"
RUNTIME_APP_SNAPSHOT_PATH="$STATE_DIR/runtime-app.sha256"
SOURCE_TDT_CORE_SNAPSHOT_PATH="$STATE_DIR/source-tdt-core.sha256"
RUNTIME_TDT_CORE_SNAPSHOT_PATH="$STATE_DIR/runtime-tdt-core.sha256"
```

So if a developer edits `jira-skill/src/foo.py` and runs the ai-review
deploy, the deploy copies the new jira-skill into `$DEPLOYMENT_ROOT/deps/jira-skill/`
but **does not verify** that the runtime copy matches source. The runtime
drifts silently.

**Design.** Generate snapshot paths from the same loop that copies deps.
Build a list of `(repo, source_root, runtime_root, target_paths)` triples
in the copy loop; iterate that list to snapshot and diff.

webhook-receiver's approach (separate variables per dep) is brittle — the
new code uses an explicit list to keep them in lock-step.

### C-2 — dirty worktree

Both deploy scripts write `source_dirty` to the manifest but do not block:

```python
if git -C "$SRC" diff --quiet --ignore-submodules HEAD --; then
  source_dirty="False"
else
  source_dirty="True"
fi
```

**Design (revised 2026-06-27).** Live `git status` shows
`webhook-receiver`, `jira-daily-reports`, and `jira-skill` are **already
dirty on `main` today** (uncommitted files). A default-block gate would
break the next deploy on those three repos. Therefore:

- **Default:** warn loudly (current behavior — the manifest records
  `source_dirty=True/False` and stderr prints the dirty files).
- **Opt-in:** `--require-clean` flag hard-fails before any source copy
  with `ERROR: $src_dir has uncommitted changes: <list>` and `exit 1`.
- The manifest always records `gate_require_clean: true|false` (new
  field), making audits easier.
- This **preserves** the observed current behavior (warn-and-record)
  and **adds** a CI / production deploy mode (block-by-explicit-opt-in)
  for teams that want it.

This is the inverse of the original "block-by-default, escape via
`--allow-dirty`" design — and is the **right** direction given the
current dirty state of production worktrees.

## 3. `tdt-env-loader-tdt-home` (E-3)

`tdt-core/src/tdt_core/env.py:29`:

```python
tdt_env = Path.home() / ".tdt" / ".env"
```

`Path.home()` reads `$HOME`. In Docker, `HOME=/home/agent` so the path
resolves correctly to `/home/agent/.tdt/.env` which is the bind-mounted
host path. In launchd plists, `HOME=$HOME` (host). So it works.

But: a future launch configuration that sets a nonstandard `HOME` (e.g.,
running ai-review under a sandboxed profile) would silently lose
credentials. `TDT_HOME` is already set in compose `environment:` but is
not consulted by `load_tdt_env`.

**Design.** Precedence: `TDT_HOME` env var (if set and non-empty) >
`Path.home() / ".tdt"` > empty (current error path).

```python
tdt_root = Path(os.environ.get("TDT_HOME", "")).expanduser() or (Path.home() / ".tdt")
tdt_env = tdt_root / ".env"
```

5-line change. Backwards-compatible: callers that did not set `TDT_HOME`
get the same path as today.

`agent_core/foundation/settings.py:32` already does this correctly
(`TDT_HOME = Path(os.environ.get("TDT_HOME", Path.home() / ".tdt"))`).
This change makes `tdt_core/env.py` consistent with it.

## 4. `scheduler-timezone-clarification` (D-1)

### State today

`compose.yaml:92`:

```yaml
TZ: Asia/Ho_Chi_Minh
```

`agent-core/scheduler_setup.py` decorators:

| Decorator | cron_timezone | Fires at |
|---|---|---|
| `webhook_selftest` (line 261) | `"UTC"` | every 5 min UTC |
| `dlq_reaper` (line 271) | `"UTC"` | 03:00 UTC |
| `coverage_scan` (line 281) | `workspace_timezone_name()` | 07:00 / 10:00 / etc. Asia |
| `jira_ticket_intelligence_hourly` (line 291) | `workspace_timezone_name()` | top of hour Asia |
| `daily_android_scan` (line 397) | `_android_config.timezone` | 07:00 Asia (from yaml) |
| `daily_ios_scan` (line 405) | `_ios_config.timezone` | 07:00 Asia (from yaml) |
| `scan_recent_mr` (line 442) | `"UTC"` | every 15 min UTC |

The container's `TZ` env var is ignored by DBOS — `cron_timezone` is
explicit per-schedule. Firing times are correct, but the `TZ=Asia/Ho_Chi_Minh`
in compose is misleading to anyone who later edits a cron expression.

### Design

- Add an inline comment to every `@_ENGINE.scheduled_workflow` decorator:
  `# cron_timezone=UTC — DBOS interprets this independently of the container's TZ env var`.
- Move the timezone explanation to a module-level docstring at the top of
  `scheduler_setup.py`, citing both compose.yaml line 92 and the cron_timezone
  behavior.
- Document in `tdt-core/src/tdt_core/scheduler/README.md` "Timezones" section.
- No code change in `compose.yaml` — `TZ=Asia/Ho_Chi_Minh` is still useful
  for Python `datetime.now()` calls inside the workflow bodies (e.g.,
  log timestamps); only the cron firing is timezone-explicit.

## 5. `daily-health-check.sh` legacy paths (C4)

`~/.tdt/scripts/daily-health-check.sh:5`:

```bash
CRON_ROOT="/Users/lekhanhvinh/tdt"
REPORT_DIR="$CRON_ROOT/tools/agents/skills/jira-daily-reports"
```

**Design.** Replace with:

```bash
TDT_HOME="${TDT_HOME:-$HOME/.tdt}"
CRON_ROOT="${TDT_WORKSPACE_ROOT:-$HOME/Developer/tdt}"
REPORT_DIR="$CRON_ROOT/jira-daily-reports"
```

The new path matches the canonical workspace. Drop the `run_report.sh`
existence check (it does not exist in the canonical layout) and the
`crontab -l` block (cron is DBOS-driven now). Keep the pytest checks —
those still apply.

## 6. Scheduler Dockerfile COPY (C-13)

`deployments/scheduler/Dockerfile:31–45`:

```dockerfile
COPY --chown=agent:agent agent-core/pyproject.toml agent-core/README.md ./agent-core/
COPY --chown=agent:agent agent-core/scheduler_setup.py ./agent-core/scheduler_setup.py
COPY --chown=agent:agent agent-core/src ./agent-core/src

COPY --chown=agent:agent jira-daily-reports/src ./jira-daily-reports/src
COPY --chown=agent:agent ai-review/src ./ai-review/src
COPY --chown=agent:agent code-daily-scan/src ./code-daily-scan/src
COPY --chown=agent:agent code-daily-scan/config ./code-daily-scan/config
COPY --chown=agent:agent code-daily-scan/pyproject.toml ./code-daily-scan/

COPY --chown=agent:agent tdt-core/pyproject.toml tdt-core/README.md ./tdt-core/
COPY --chown=agent:agent tdt-core/src ./tdt-core/src

COPY --chown=agent:agent tdt-sheets/pyproject.toml tdt-sheets/README.md ./tdt-sheets/
COPY --chown=agent:agent tdt-sheets/src ./tdt-sheets/src
```

Missing: `jira-skill/src`, `webhook-receiver/src`, plus
`jira-daily-reports/pyproject.toml` (needed by `uv sync`).

The compose `volumes:` block mounts these at runtime, but a `docker run`
without compose would fail.

**Design.** Add the missing COPYs:

```dockerfile
COPY --chown=agent:agent jira-daily-reports/pyproject.toml jira-daily-reports/README.md ./jira-daily-reports/
COPY --chown=agent:agent jira-skill/pyproject.toml jira-skill/README.md ./jira-skill/
COPY --chown=agent:agent jira-skill/src ./jira-skill/src
COPY --chown=agent:agent webhook-receiver/pyproject.toml webhook-receiver/README.md ./webhook-receiver/
COPY --chown=agent:agent webhook-receiver/src ./webhook-receiver/src
```

The compose volume mounts remain — they take precedence over the COPY
because mounts win in Docker. The COPY makes the image self-contained
for ad-hoc runs.

## 7. LaunchAgent log rotation (E-4)

### State today

Live `cat ~/Library/LaunchAgents/*.plist` (2026-06-27) — log paths
**vary by service**:

| Service | Log path |
|---------|----------|
| webhook-receiver | `~/Developer/tdt/deployments/webhook-receiver/logs/webhook-receiver.{stdout,stderr}.log` |
| ai-review | `~/Developer/tdt/deployments/ai-review/logs/ai-review.{stdout,stderr}.log` |
| agentmemory | `~/.agentmemory/launchd-{stdout,stderr}.log` |
| qi-bridge-proxy | `~/.qi-bridge/launchd-{stdout,stderr}.log` |
| ngrok-webhook-secondary | not verified (out of scope) |

No rotation. Files grow unbounded.

`~/.tdt/scripts/rotate-logs.sh` exists and handles `~/.tdt/logs/jira-daily-reports/`
and `~/.tdt/logs/webhook-receiver/` (legacy `/var/log`-style path),
but is not wired to any LaunchAgent.

### Design (revised 2026-06-27)

- Extend `rotate-logs.sh` with a per-service log path table (Bash
  associative array) covering all 4 LaunchAgents above + ngrok-secondary
  as a no-op. Cap at 50 MB per file, keep 5 rotations (`.1` through `.5`).
- Use **in-place truncate** (`: > "$log"`) after rotation to preserve
  the inode — `tail -F` and `lsof`-style followers do not need to
  re-open the file after rotation.
- Add a new `com.tdt.rotate-logs.plist` LaunchAgent:
  `StartCalendarInterval: Hour=4, Minute=0` (off-peak). Single command:
  `/bin/zsh ~/.tdt/scripts/rotate-logs.sh`.
- The existing manual-rotation scope (jira logs) stays; the LaunchAgent
  just adds the previously-missing LaunchAgent stdout/stderr files.

## Risks

- **Backup container restart.** `postgres-backup` is `restart: unless-stopped`
  but does **not** `depends_on: postgres: condition: service_healthy`
  at startup (a backup that waits for the DB to be healthy at boot
  would miss the very outage it's meant to cover if Postgres is down).
  Instead: try `pg_dump`, log on failure, sleep until tomorrow 03:00
  UTC, retry. The loop tolerates Postgres being down for days.
- **Healthcheck during DBOS cold start.** `start_period: 120s` is calibrated
  to DBOS + workflow recovery (~45s on cold start). If startup is consistently
  longer, increase `start_period` rather than `retries`.
- **`TDT_HOME` env var.** Already set in compose (`HOME: /home/agent`,
  `TDT_HOME: /home/agent/.tdt`). Setting it on the host (for launchd
  services) is **not** required by this change — `Path.home()` fallback
  works there. Operators that explicitly set `TDT_HOME` for testing
  get the new path resolution.
- **ai-review `--require-clean`.** A developer who has set up an explicit
  short-lived hot-fix flow on `main` must pass `--require-clean` consciously
  if they want CI to enforce cleanliness. The flag is recorded in the
  deployment-manifest (`gate_require_clean: true|false`) so audits
  remain visible. **Default behavior is unchanged** (warn-and-record,
  not block).
- **rotate-logs.sh extension.** Renaming the existing file (or splitting
  it into per-target sub-scripts) is out of scope; in-place extension with
  a clear comment block.
- **Schedule name drift `scan-recent-mrs`.** This change does not rename
  the workflow function (would break queue dedup across deploys). It only
  investigates, and if confirmed stale, deletes the schedule row from DBOS.
  Any future rename of the workflow function must come with a coordinated
  `tdt-scheduler schedules delete <old>` + `apply` cycle.
- **`scheduler/health.py` reuse.** The existing FastAPI router already
  returns the correct schema; this change only wires it. If the router's
  contract changes (e.g., adding a `next_run_time` field to
  `/scheduler/health`), the healthcheck in `compose.yaml` does not break
  — it only asserts `200` from the endpoint.
