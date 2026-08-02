# Spec Deltas

This change proposes **four new capabilities** and **zero** updated
capabilities. Each capability is described by its own `spec.md` in a
sibling directory.

## ADDED Deltas

### `scheduler-postgres-watchdog`

See `specs/scheduler-postgres-watchdog/spec.md`. Adds a Postgres backup
sidecar container and a `healthcheck:` block on the scheduler service.
Closes E-1 (Postgres SPOF) and E-2 (scheduler hang no-watchdog).

### `host-deploy-script-consistency`

See `specs/host-deploy-script-consistency/spec.md`. Aligns the
`ai-review` deploy script with `webhook-receiver` on three points: hard
fail on stale uv lock (C1), snapshot+diff over **all** copied path deps
(C2), and block deploys on dirty worktrees unless `--allow-dirty` (C-2).

### `tdt-env-loader-tdt-home`

See `specs/tdt-env-loader-tdt-home/spec.md`. Makes
`tdt_core.env.load_tdt_env()` honour `TDT_HOME` when set, falling back
to `Path.home() / ".tdt"` otherwise. Aligns with the precedence already
used by `agent_core.foundation.settings.TDT_HOME` (E-3).

### `scheduler-timezone-clarification`

See `specs/scheduler-timezone-clarification/spec.md`. Adds inline
timezone comments to every `@scheduled_workflow` decorator in
`agent-core/scheduler_setup.py` and a top-of-file docstring explaining
that DBOS interprets `cron_timezone` independently of the container's
`TZ` env var (D-1).

## Out of Scope

The proposal documents additional validated findings that this change
explicitly does NOT address. Each is listed with a justification:

- **`D-2 automatic_backfill=False`** — behavioural design decision,
  deferred to a separate "backfill semantics" change.
- **`B-5 ~/.tdt/config.toml`** — frozen legacy artifact; trivial PR
  outside this scope.
- **`C8 no rollback automation`** — architectural; deserves a dedicated
  "deploy rollback contract" change.
- **`F-5 crash_recovery.scheduling_enabled`** — was originally flagged as
  a wrong key in `config.yaml.example`. Re-validation confirmed it is a
  legitimate key in `CrashRecoverySettings`, which is an **orthogonal**
  settings system from `SchedulerSettings`. Not a bug.
- **`C9 webhook-secondary.url atomicity`** and **`C12 incident-report.sh
  fallback path`** — operator-script concerns, not service-level.
- **`E-4 jira-daily-reports log rotation`** — already partially rotated
  by the existing `~/.tdt/scripts/rotate-logs.sh`. This change adds the
  LaunchAgent wiring + extension to LaunchAgent stdout/stderr logs. The
  existing manual-rotation behaviour stays.
