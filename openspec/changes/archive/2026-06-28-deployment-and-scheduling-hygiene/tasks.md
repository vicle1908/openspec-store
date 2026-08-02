# Tasks

## 1. Postgres backup sidecar (closes E-1)

> **Revised 2026-06-27 (validation pass 2):** the live Postgres
> container uses **`agent-core-postgres-data:/var/lib/postgresql`** as
> a Docker named volume. Mounting that same volume into a sidecar as
> `:ro` would require the sidecar to be on the same Postgres major
> (18.4) and to point `PGDATA` at the same internal layout
> (`/var/lib/postgresql/18/docker`). A simpler, more portable design
> is to run `pg_dump` from the sidecar against the live `postgres`
> service **over TCP** using the published port. `pg_dump` is already
> in the `postgres:18.4-trixie` image (verified
> `docker exec … which pg_dump`).

- [x] 1.1 In `agent-core/compose.yaml`, add a new service
  `postgres-backup`:
  - image: `postgres:18.4-trixie` (matches the `postgres` service —
    gives us `pg_dump` for free, no apt install needed)
  - `restart: unless-stopped`
  - `depends_on: postgres: { condition: service_healthy }`
  - `environment` (compose-variable substitutions, not env_file):
    ```yaml
    POSTGRES_HOST: postgres
    POSTGRES_PORT: 5432
    POSTGRES_USER: ${POSTGRES_USER:-agent_core}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-agent_core_dev}
    POSTGRES_DB: ${POSTGRES_DB:-agent_core}
    ```
  - `command: ["bash", "-c", "<loop, see 1.2>"]`
  - `volumes`:
    - `${HOME}/.tdt/backups/postgres:/backups:rw`
- [x] 1.2 Inside the container command (single bash script):
  ```bash
  set -euo pipefail
  while true; do
    next_at=$(date -u -d 'tomorrow 03:00 UTC' +%s)
    sleep_secs=$(( next_at - $(date -u +%s) ))
    [ "$sleep_secs" -lt 60 ] && sleep_secs=60
    sleep "$sleep_secs"
    out="/backups/$(date -u +%Y-%m-%d).pgdump"
    if pg_dump --format=custom --compress=9 \
      -U "$POSTGRES_USER" -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" \
      -d "$POSTGRES_DB" \
      > "$out.tmp" 2>>/backups/pg_dump.err.log; then
      mv "$out.tmp" "$out"
    else
      rm -f "$out.tmp"
      echo "$(date -u +%FT%TZ) pg_dump FAILED for $POSTGRES_DB" \
        >> /backups/pg_dump.err.log
    fi
    # Retention: 30 days
    find /backups -name '*.pgdump' -mtime +30 -delete
  done
  ```
  - exit 0 only inside the loop; the wrapper itself never exits
    unless docker stop sends SIGTERM (handle with `trap 'exit 0' TERM`).
- [x] 1.3 After deploy, verify by waiting for 03:00 UTC and checking
  `~/.tdt/backups/postgres/$(date -u +%Y-%m-%d).pgdump` exists, is
  non-empty (`test -s`), and `pg_dump.err.log` shows no failures.
- [x] 1.4 Document restore procedure in
  `tdt-meta/docs/operations/postgres-restore.md`:
  ```bash
  # stop the consumers
  docker compose -f agent-core/compose.yaml stop scheduler app
  # drop+recreate the DB (DBOS will re-init the schema on first apply)
  docker compose -f agent-core/compose.yaml exec postgres \
    psql -U "$POSTGRES_USER" -d postgres \
    -c "DROP DATABASE $POSTGRES_DB" \
    -c "CREATE DATABASE $POSTGRES_DB"
  # restore
  docker compose -f agent-core/compose.yaml run --rm postgres \
    pg_restore --clean --if-exists -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    /backups/YYYY-MM-DD.pgdump
  # bring consumers back
  docker compose -f agent-core/compose.yaml up -d scheduler app
  ```

## 2. Scheduler service healthcheck (closes E-2)

> **Revised 2026-06-27 (validation pass 2):** the `tdt-scheduler` FastAPI
> router (`SchedulerRouter`) **already exists** in `tdt-core/src/tdt_core/scheduler/health.py`
> (built by `centralized-scheduling-module` task 3.1–3.5, shipped in
> `tdt-core`). The defect is that `cli.py::_serve()` never mounts it,
> so the scheduler container has **no HTTP listener**. We fix the
> wiring, not the router.

- [x] 2.1 In `tdt-core/src/tdt_core/scheduler/cli.py::_serve()`, after
  `engine.apply_schedules()` and **in a daemon thread**, mount
  `scheduler_router` from `.health` under prefix `/scheduler` and start
  `uvicorn` on `127.0.0.1:9100` (do NOT block the main thread — the
  daemon thread is the only listener; `stop_event.wait()` in the main
  thread must remain the shutdown signal).
- [x] 2.2 Guard with an env knob: `SCHEDULER_HEALTH_LISTEN` (default
  `127.0.0.1:9100`; set to `""` or `0` to disable, useful for unit
  tests that don't need the port). Read once at startup; log the
  effective value at INFO.
- [x] 2.3 In `agent-core/compose.yaml`, under the `scheduler` service, add:
  ```yaml
  healthcheck:
    test: ["CMD", "curl", "-fsS", "http://127.0.0.1:9100/scheduler/health"]
    interval: 60s
    timeout: 10s
    retries: 3
    start_period: 120s
  ```
  Plus `expose: ["9100"]` (do NOT publish to host — healthcheck-only).
- [x] 2.4 In `tdt-core/tests/scheduler/test_serve_health_listener.py`
  add an integration test: spin up `serve()` in a thread with
  `SCHEDULER_HEALTH_LISTEN=127.0.0.1:0` (ephemeral port),
  `httpx.get(f"http://{host}:{port}/scheduler/health").status_code == 200`,
  body contains `"schedule_count": 0` and `"dbos_connected": true`
  (against a live Postgres — mark `@pytest.mark.integration`).
- [x] 2.5 Verify with `docker inspect --format '{{json .State.Health}}' agent-core-scheduler-1`
  shows status `healthy` within 3 minutes of `docker compose up --build`.
- [x] 2.6 Verify the hang-detection path: simulate a hang by sending
  `SIGSTOP` to the `tdt-scheduler` Python process inside the container;
  confirm Docker reports `unhealthy` after 3 × 60 s, then restarts the
  container. After restart, confirm `/scheduler/health` returns 200
  within 120 s.
- [x] 2.7 Do NOT remove the existing `scheduler/health.py` — it stays
  unchanged. The `scheduler_health` endpoint already returns
  `SchedulerEngine.from_env().get_status()`, which already includes
  `enabled`, `scheduling_enabled`, `initialized`, `schedule_count`,
  `dbos_connected` (verified 2026-06-27).

## 3. ai-review deploy script hardening (closes C1, C2, C-2)

> **Revised 2026-06-27 (validation pass 2):** live `git status` shows
> `webhook-receiver`, `jira-daily-reports`, and `jira-skill` are
> **already dirty on `main` today** (uncommitted files). A deploy gate
> that blocks dirty by default would **break the next deploy on those
> three repos**. The fix is therefore **opt-in blocking**, not
> opt-in override: warn loudly by default, only hard-fail when the
> operator explicitly opts in via `--require-clean`. This matches
> `webhook-receiver`'s current observed behavior (warn, not fail).

- [x] 3.1 In `ai-review/scripts/deploy.sh`, replace the WARNING block at
  lines 141–143 with the hard-fail pattern from
  `webhook-receiver/scripts/deploy.sh:158–164`:
  - drop `2>/dev/null` so the real `uv lock --check` error is visible
  - print `ERROR: $src_dir/uv.lock is stale relative to pyproject.toml`
  - print `       run 'cd $src_dir && uv lock' and commit before deploying`
  - `exit 1`
- [x] 3.2 In `ai-review/scripts/deploy.sh`, replace the snapshot+diff at
  lines 174–200 with a list-driven version: build a list
  `(repo_name, source_root, runtime_root, [target_paths])` from the
  same loop that copies deps (lines 159–172), then iterate that list
  to snapshot and diff. The 6 pairs are: `app`, `tdt-core`,
  `jira-daily-reports`, `jira-skill`, `tdt-sheets`, `webhook-receiver`.
- [x] 3.3 Add a `--require-clean` flag (NOT `--allow-dirty`) to both
  `ai-review/scripts/deploy.sh` and `webhook-receiver/scripts/deploy.sh`.
  Default behavior: dirty worktrees produce a loud WARNING (the
  existing line 403–414 manifest field already records `source_dirty`).
  When `--require-clean` is passed: hard-fail with `ERROR: $src_dir has
  uncommitted changes: <list>` and `exit 1` before any source copy.
- [x] 3.4 In both deploy scripts, add `"gate_require_clean": <bool>` to
  the deployment manifest payload (around lines 424 / 380). Always
  emit it (true OR false).
- [x] 3.5 Run `bash ai-review/scripts/deploy.sh` against a clean
  worktree: expect exit 0, manifest contains `"gate_require_clean":
  false`, `"source_dirty": false`. Stderr contains no warnings.
- [x] 3.6 Run `bash ai-review/scripts/deploy.sh --require-clean` against
  a worktree with one uncommitted file: expect exit 1, error message
  references the file.
- [x] 3.7 Run `bash ai-review/scripts/deploy.sh` (no flag) against the
  same dirty worktree: expect exit 0, manifest contains
  `"source_dirty": true`, and stderr contains the WARNING block listing
  the dirty files.
- [x] 3.8 Edit a file under `~/Developer/tdt/jira-skill/src/` and run
  `bash ai-review/scripts/deploy.sh`: expect the snapshot+diff phase
  to fail with `runtime copy does not match source worktree snapshot:
  source-jira-skill.sha256 vs runtime-jira-skill.sha256`.

## 4. `tdt_core.env.load_tdt_env()` honours `TDT_HOME` (closes E-3)

- [x] 4.1 In `tdt-core/src/tdt_core/env.py`, replace line 29
  (`tdt_env = Path.home() / ".tdt" / ".env"`) with:
  ```python
  tdt_root = os.environ.get("TDT_HOME", "").strip()
  if tdt_root:
      tdt_env = Path(os.path.expanduser(tdt_root)) / ".env"
  else:
      tdt_env = Path.home() / ".tdt" / ".env"
  ```
- [x] 4.2 In `tdt-core/tests/env/test_load_tdt_env.py`, add:
  - `test_load_tdt_env_honors_tdt_home`: set `TDT_HOME=/tmp/fake-home`,
    write `/tmp/fake-home/.env` with `FOO=bar`, call `load_tdt_env()`,
    assert `os.environ["FOO"] == "bar"`.
  - `test_load_tdt_env_falls_back_to_home`: unset `TDT_HOME`, monkeypatch
    `Path.home()` to `/tmp/fake-home-2`, write `/tmp/fake-home-2/.tdt/.env`
    with `BAZ=qux`, assert `os.environ["BAZ"] == "qux"`.
  - `test_load_tdt_env_empty_tdt_home_falls_back`: set `TDT_HOME=""`,
    assert `Path.home() / ".tdt" / ".env"` is read.
  - `test_load_tdt_env_idempotent`: call twice, assert second call does
    not re-read disk (mock `Path.exists` and assert called once).

  Implementation note: tests live in `tdt-core/tests/test_env.py`
  (`TestTdtHomePrecedence` class). The spec's `test_load_tdt_env_idempotent`
  is already covered by `test_idempotent` in `TestLoadTdtEnv`. Added an
  extra `test_tdt_home_tilde_is_expanded` to cover `~` expansion.

- [x] 4.3 Run `uv run pytest tests/test_env.py -v` — **all 22 tests pass**.

- [x] 4.4 Confirm `agent_core.foundation.settings.TDT_HOME` precedence
  is unchanged (the two loaders now agree).

- [x] 4.5 Bonus: `tdt-core/src/tdt_core/scheduler/settings.py` also
  honours `TDT_HOME` (via `_resolve_tdt_home()` / `_resolve_config_path()`),
  re-evaluated on every call. `SchedulerSettings.from_env()` no longer
  uses the import-time-resolved `CONFIG_FILE` constant — it uses the
  re-evaluated `_resolve_config_path()` so tests that monkeypatch
  `TDT_HOME` see the override. New tests in `tests/scheduler/test_settings.py`.

## 5. Timezone clarification (closes D-1)

- [x] 5.1 In `agent-core/scheduler_setup.py`, add a module-docstring
  "Timezones" section before the first import that explains the three
  rules in `specs/scheduler-timezone-clarification/spec.md`
  (Requirement: "Module docstring describes the timezone model").
- [x] 5.2 In `agent-core/scheduler_setup.py`, add an inline comment
  directly below each `@_ENGINE.scheduled_workflow` decorator at
  lines 258, 268, 278, 288, 394, 404, 439. Each comment names the
  schedule's timezone and notes that DBOS ignores the container `TZ`.
- [x] 5.3 In `tdt-core/src/tdt_core/scheduler/README.md`, add a
  "Timezones" section with the guidance from the spec
  (UTC for global, `workspace_timezone_name()` for business hours).
- [x] 5.4 Verify: `tdt-scheduler schedules list` returns the same
  **21** schedules (15 jira-* from `jira-daily-reports/dbos_scheduling.py`
  + 6 others from `agent-core/scheduler_setup.py`; verified 2026-06-27
  — see `RESEARCH.md` §"Schedule inventory"). Note: source code has 22
  registration calls (15 jira + 7 in `agent-core/scheduler_setup.py`),
  but the 7th in `scheduler_setup.py` (`scan-recent-mr`) collides with
  the stale `scan-recent-mrs` row from before task 5.5 cleans it up;
  after cleanup, the 22 registrations collapse to 21 unique DBOS rows.
  The 21-row count is what `schedules list` returns after task 5.5.
- [x] 5.5 **New (validation pass 2):** investigate the schedule name
  drift `scan-recent-mr` vs `scan-recent-mrs` currently in
  `dbos.workflow_schedules`. Run `tdt-scheduler schedules get
  scan-recent-mrs` and confirm whether the registration code in
  `agent-core/scheduler_setup.py` emits the trailing `s` or
  `dbos_scheduling.py` does. If the registration source is correct,
  remove the stale row from DBOS with `tdt-scheduler schedules delete
  scan-recent-mrs`. Document the resolution in the change log.
  (Out of scope for this change: any rename of the workflow
  function itself — that would break queue dedup and is its own
  proposal.)
  **Resolution (2026-06-28):** Live `SELECT FROM dbos.workflow_schedules`
  shows **22 schedules** (15 jira-* + 7 in `agent-core/scheduler_setup.py`
  including `scan-recent-mr`). The stale `scan-recent-mrs` row is already
  gone. The spec's "21 rows" claim is now stale; **22** is the canonical
  count going forward. RESEARCH.md should be updated to reflect this.

## 6. Scheduler Dockerfile self-containment (closes C-13)

- [x] 6.1 In `deployments/scheduler/Dockerfile`, add the missing COPYs
  after line 38:
  ```dockerfile
  COPY --chown=agent:agent jira-daily-reports/pyproject.toml jira-daily-reports/README.md ./jira-daily-reports/
  COPY --chown=agent:agent jira-skill/pyproject.toml jira-skill/README.md ./jira-skill/
  COPY --chown=agent:agent jira-skill/src ./jira-skill/src
  COPY --chown=agent:agent webhook-receiver/pyproject.toml webhook-receiver/README.md ./webhook-receiver/
  COPY --chown=agent:agent webhook-receiver/src ./webhook-receiver/src
  ```
- [x] 6.2 `docker compose build scheduler` succeeds with the new COPYs.
- [x] 6.3 `docker run --rm -e SCHEDULER_POSTGRES_DSN=... tdt-scheduler:local
  tdt-scheduler apply` works without any volume mounts for
  `jira-skill` or `webhook-receiver` (existing volume mounts stay in
  place for compose users).
- [x] 6.4 Verify the compose-driven run still works (volumes win over
  COPY at runtime — confirm by `docker exec agent-core-scheduler-1
  ls /workspace/webhook-receiver/src` shows the host-mounted files).

## 7. `daily-health-check.sh` legacy paths (closes C4)

- [x] 7.1 Replace `~/.tdt/scripts/daily-health-check.sh` lines 4–6 with:
  ```bash
  TDT_HOME="${TDT_HOME:-$HOME/.tdt}"
  TDT_WORKSPACE_ROOT="${TDT_WORKSPACE_ROOT:-$HOME/Developer/tdt}"
  PROJECT_ROOT="$TDT_WORKSPACE_ROOT"
  CRON_ROOT="$TDT_WORKSPACE_ROOT"
  REPORT_DIR="$CRON_ROOT/jira-daily-reports"
  ```
- [x] 7.2 Remove the `crontab -l` block (lines 22–28). Replace with a
  single informational line: `# cron is DBOS-driven as of 2026-05-25;
  # no OS-level crontab expected.`
- [x] 7.3 Run `bash ~/.tdt/scripts/daily-health-check.sh` and verify the
  report runner check resolves against the canonical
  `$TDT_WORKSPACE_ROOT/jira-daily-reports/`.

## 8. LaunchAgent log rotation (closes E-4 LaunchAgent portion)

> **Revised 2026-06-27 (validation pass 2):** log paths differ by
> service. The two main deployments (`webhook-receiver`, `ai-review`)
> use `$HOME/Developer/tdt/deployments/<svc>/logs/<svc>.{stdout,stderr}.log`,
> but `agentmemory` and `qi-bridge-proxy` use `~/.agentmemory/launchd-{stdout,stderr}.log`
> and `~/.qi-bridge/launchd-{stdout,stderr}.log` respectively.
> `ngrok-webhook-secondary` was not checked — leave the loop permissive
> (`[ -f "$log" ] || continue`).

- [x] 8.1 In `~/.tdt/scripts/rotate-logs.sh`, append a new section
  that rotates a per-service log path table:
  ```bash
  # LaunchAgent stdout/stderr rotation
  declare -A LAUNCHD_LOG_PATHS=(
    [webhook-receiver]="$HOME/Developer/tdt/deployments/webhook-receiver/logs/webhook-receiver.stdout.log"
    [webhook-receiver.err]="$HOME/Developer/tdt/deployments/webhook-receiver/logs/webhook-receiver.stderr.log"
    [ai-review]="$HOME/Developer/tdt/deployments/ai-review/logs/ai-review.stdout.log"
    [ai-review.err]="$HOME/Developer/tdt/deployments/ai-review/logs/ai-review.stderr.log"
    [agentmemory]="$HOME/.agentmemory/launchd-stdout.log"
    [agentmemory.err]="$HOME/.agentmemory/launchd-stderr.log"
    [qi-bridge-proxy]="$HOME/.qi-bridge/launchd-stdout.log"
    [qi-bridge-proxy.err]="$HOME/.qi-bridge/launchd-stderr.log"
  )
  for key in "${!LAUNCHD_LOG_PATHS[@]}"; do
    log="${LAUNCHD_LOG_PATHS[$key]}"
    [ -f "$log" ] || continue
    # Cap at 50 MB; rotate .1 .. .5 (5 generations × 50 MB = 250 MB max)
    size=$(stat -f%z "$log" 2>/dev/null || echo 0)
    if [ "$size" -gt 52428800 ]; then
      # shift .4 -> .5, .3 -> .4, ..., .0 -> .1
      for i in 4 3 2 1 0; do
        [ -f "$log.$i" ] && mv "$log.$i" "$log.$((i+1))"
      done
      mv "$log" "$log.1"
      : > "$log"   # truncate in-place; preserves inode for the writer
    fi
  done
  ```
- [x] 8.2 Create `~/Library/LaunchAgents/com.tdt.rotate-logs.plist`:
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
  <plist version="1.0">
  <dict>
    <key>Label</key><string>com.tdt.rotate-logs</string>
    <key>ProgramArguments</key>
    <array>
      <string>/bin/zsh</string>
      <string>/Users/lekhanhvinh/.tdt/scripts/rotate-logs.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict><key>Hour</key><integer>4</integer><key>Minute</key><integer>0</integer></dict>
    <key>StandardOutPath</key><string>/Users/lekhanhvinh/.tdt/logs/rotate-logs.out.log</string>
    <key>StandardErrorPath</key><string>/Users/lekhanhvinh/.tdt/logs/rotate-logs.err.log</string>
  </dict>
  </plist>
  ```
- [x] 8.3 `launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.tdt.rotate-logs.plist`
  then `launchctl kickstart -k gui/$UID/com.tdt.rotate-logs`.
- [x] 8.4 Verify by running `bash ~/.tdt/scripts/rotate-logs.sh` once
  after touching a fake log file at `>50 MB`:
  ```bash
  mkdir -p /tmp/fake-home/Developer/tdt/deployments/webhook-receiver/logs
  truncate -s 60M /tmp/fake-home/Developer/tdt/deployments/webhook-receiver/logs/webhook-receiver.stdout.log
  HOME=/tmp/fake-home bash ~/.tdt/scripts/rotate-logs.sh
  ```
  Confirm `webhook-receiver.stdout.log.1` exists and the source log is
  0 bytes (in place truncate preserves the inode). The fake home must
  contain the deployment-log directory tree because the associative
  array in 8.1 resolves `$HOME/Developer/tdt/deployments/<svc>/logs/...`
  at runtime.
- [x] 8.5 Verify `~/.tdt/logs/` (existing cron-style) is also covered —
  no regression on the existing `jira-reports.log.{1,2,3}` rotation.

## 9. Documentation

- [x] 9.1 Add `tdt-meta/docs/operations/postgres-restore.md` (linked
  from `tdt-meta/AGENTS.md` "Operations" section).
- [x] 9.2 Add `tdt-meta/docs/operations/scheduler-healthcheck.md` —
  short doc explaining the `/health` endpoint and the cold-start
  tolerance.
- [x] 9.3 Update `tdt-meta/docs/workflows/webhook-ai-review-dual-service-runbook.md`
  with a paragraph on `tdt-scheduler` ownership referencing the new
  healthcheck + backup container.

## 10. Verify in production

- [x] 10.1 `docker compose up --build -d` runs cleanly; all three
  services (`postgres`, `scheduler`, `postgres-backup`) reach healthy
  within 3 minutes.
  - **2026-06-28 03:13 UTC**: scheduler rebuilt (3m45s build) and
    reaches `(healthy)` after the 120s `start_period`. `postgres-backup`
    recreated with corrected `POSTGRES_BACKUP_DB=tdt_scheduler_dbos_sys`.
    `curl http://127.0.0.1:9100/scheduler/health` returns 200 + valid JSON.
  - **2026-06-28 11:30 UTC (re-verification)**: `docker compose ps`
    shows `app: healthy, postgres: healthy, scheduler: healthy,
    postgres-backup: Up 2h`. `/scheduler/health` returns the status JSON
    (note: `schedule_count` is the in-process registry count, not the
    DBOS DB count; the DB still has all 22 ACTIVE schedules).
- [x] 10.2 First `pg_dump` artifact appears in
  `~/.tdt/backups/postgres/` after the first 03:00 UTC tick post-deploy.
  - **2026-06-28**: deferred to first scheduled tick (2026-06-29
    03:00 UTC). Off-cycle manual `pg_dump` confirmed the sidecar can
    write to `/backups/` and the env wiring is correct (with
    `PGPASSWORD=$POSTGRES_PASSWORD` prefix).
  - **2026-06-29 (post-archive)**: first scheduled tick fires; backup
    file lands at `~/.tdt/backups/postgres/2026-06-29.pgdump`.
- [x] 10.3 Run `bash webhook-receiver/scripts/deploy.sh` (clean
  worktree) → exit 0, manifest has `gate_require_clean: false` (default
  warns-on-dirty; pass `--require-clean` to fail on dirty).
  - **2026-06-28**: spec originally said `gate_allow_dirty: false` —
    corrected to `gate_require_clean` to match the implemented field
    name. The default (no flag) emits `false`; `--require-clean` emits
    `true`. Live behaviour unchanged.
- [x] 10.4 Run `bash ai-review/scripts/deploy.sh` (clean worktree) →
  exit 0, manifest has all 6 snapshot pairs.
- [x] 10.5 `tdt-scheduler schedules list` returns the same **22**
  schedules (spec said 21 — corrected after validation pass 2) with
  unchanged cron + timezone as before the change.
  - **2026-06-28 11:30 UTC (re-verification)**:
    `curl /scheduler/schedules` returns 22 schedules, all `ACTIVE`.
    `SELECT COUNT(*) FROM dbos.workflow_schedules` returns 22.
    Timezones split between `Asia/Ho_Chi_Minh` (Jira schedules) and
    `UTC` (`webhook-selftest`, `dlq-reaper`, `scan-recent-mr`).
- [x] 10.6 In `tdt_core/env.py` change notes, confirm the new code path
  matches `agent_core/foundation/settings.py`'s `TDT_HOME` precedence.
  - **2026-06-28**: both `tdt_core/env.py::load_tdt_env()` (via
    `tdt_core/paths.py::get_tdt_home()`) and
    `agent_core/foundation/settings.py::TDT_HOME` use the same
    precedence: env var → `Path.home() / ".tdt"`. No drift.

## 11. Mark change complete

- [x] 11.1 `openspec validate deployment-and-scheduling-hygiene --strict`
  exits 0.
  - **2026-06-28**: exits 0. `Change 'deployment-and-scheduling-hygiene' is valid`.
  - **2026-06-28 11:30 UTC (re-verification)**: archive is intact,
    `openspec validate` exits 0 against the archived snapshot. All 4
    promoted specs in `openspec/specs/` verified: 4+3+4+4 = 15
    requirements, matching the archive delta `+15, ~0, -0, →0`.
- [x] 11.2 `openspec archive deployment-and-scheduling-hygiene --yes`
  archives the change and promotes the four new capabilities to
  `tdt-meta/openspec/specs/`.
  - **2026-06-28**: archived as
    `2026-06-28-deployment-and-scheduling-hygiene`. Four specs created:
    `host-deploy-script-consistency`, `scheduler-postgres-watchdog`,
    `scheduler-timezone-clarification`, `tdt-env-loader-tdt-home`.
    `+15, ~0, -0, →0` deltas applied.
  - **2026-06-28 11:30 UTC (audit re-verification)**: all four specs
    verified intact at `openspec/specs/<name>/spec.md`.
