## Context

The TDT ecosystem runs all scheduled workflows (`daily_android_scan`,
`daily_ios_scan`, `jira-standup`, `webhook-selftest`, etc.) through a single
DBOS scheduler hosted in the Docker `tdt-scheduler:local` container. This
container runs continuously on the operator's macOS host.

The scheduler writes workflow status rows to the shared PostgreSQL system
database (`tdt_scheduler_dbos_sys`). Three operational realities drive the
need for automated stale-workflow cleanup:

1. **Scheduled workflows fail when their target environment is unavailable**
   (bind-mounted `.git` is read-only inside the container, the repo path is
   missing, the git command itself errors). DBOS catches the exception,
   writes a `status=ERROR` row with the pickled exception blob, and leaves
   the row in place forever.

2. **ERROR rows accumulate** because the existing
   `_cancel_stale_error_workflows` utility only matches a narrow set of
   exception class names (`ModuleNotFoundError`, `AttributeError`,
   `ImportError`, `UnpicklingError`). Real-world stale exceptions include
   `FileNotFoundError`, `OSError`, and `subprocess.CalledProcessError` —
   none of which match the default filter.

3. **Cleanup only happens at scheduler startup**, not on a schedule. The
   README at `tdt-core/src/tdt_core/scheduler/README.md:99` explicitly
   acknowledges: "Cleanup is **NOT** scheduled to run periodically (no
   `*/30 * * * *` schedule exists). Operators wanting periodic cleanup
   must either restart the scheduler (which triggers the startup path) or
   run `tdt-scheduler cancel-stale-errors` manually."

The third point is the root cause of the manual intervention burden. The
existing helper functions are battle-tested (used by the CLI commands
since the original `dbos-stale-workflow-auto-cleanup` change). They just
need to be wired into a periodic schedule and the filter widened.

The first two points (stderr surfacing + filter widening) are minor
ergonomic improvements that reduce the operator's debug loop from
"reproduce the failure by hand" to "read the actual git error".

## Goals / Non-Goals

**Goals:**
- Make the scheduler self-healing — stale `ERROR` and `ENQUEUED` rows are
  cancelled automatically every 30 minutes, without operator intervention.
- Broaden the default exception class filter so common stale-workflow
  exceptions are caught by default.
- Surface the captured stderr from `git worktree add` so operators can see
  why the scan is failing on any given day.
- Be idempotent — multiple runs with no stale rows must be no-ops.
- Require zero changes to deployed services other than the scheduler
  container restart.
- Resolve the long-standing mis-archive of
  `dbos-stale-workflow-auto-cleanup` (the documented behaviour matches the
  intent of this change exactly).

**Non-Goals:**
- Modifying the DBOS library itself.
- Adding a YAML schedule manifest for the cleaner — `agent-core`
  registers scheduled workflows via decorators per
  `centralized-scheduling-module` Decision 4.
- Adding a retry loop for `git worktree add` failures — operators want
  diagnostic information (stderr) and automatic cleanup, not silent
  retries.
- Implementing a proactive health-check / service-restart watchdog — that
  is a separate concern tracked as an open follow-up.
- Changing the cleanup cadence from 30 minutes.

## Decisions

### Decision 1: Implement the scheduled cleaner in `agent-core/scheduler_setup.py`

**Chosen approach**: Add `_stale_workflow_cleaner` as a
`@_ENGINE.scheduled_workflow(cron="*/30 * * * *", cron_timezone="UTC",
name="stale_workflow_cleaner")` registered in the Docker `tdt-scheduler`
container's startup, mirroring the existing pattern used for
`daily_android_scan` and `daily_ios_scan`.

**Rationale**: The Docker `tdt-scheduler:local` container is the canonical
scheduler process — it is always-on (`restart: unless-stopped`), connects
to the shared PostgreSQL, and is the only process that should call
`apply_schedules()`. Registering the cleaner here keeps the concern
co-located with other scheduled work. `webhook-receiver` and `ai-review`
are not modified.

**Alternatives rejected**:
- *YAML schedule manifest*: Inconsistent with the existing convention in
  `agent-core/scheduler_setup.py` which uses decorators for everything
  registered there.
- *Launchd interval in host*: Duplicates scheduling infrastructure; not
  crash-recoverable.
- *Cron in host crontab*: Already removed from the host (Phase 0.7);
  inconsistent with DBOS-native approach.
- *In-process in `webhook-receiver` / `ai-review`*: Would require adding
  `apply_schedules()` call to those services, violating the ownership
  contract; also cross-service DBOS access would need separate engine
  instances.

### Decision 2: Reuse the existing `_cancel_stale_error_workflows` and `_cancel_stale_enqueued_workflows` functions from `tdt-core/scheduler/cli.py`

**Chosen approach**: Rename them to public module-level
(`cancel_stale_error_workflows`, `cancel_stale_enqueued_workflows`) and
have `_stale_workflow_cleaner` call them directly.

**Rationale**: Both functions are already tested, handle the
`application_version` comparison correctly, decode the pickled error
blobs, and use `AUTOCOMMIT` isolation. No code duplication. The cleaner
workflow wraps them with DBOS durability (retry, logging,
crash-recovery). Renaming to public is a minimal change that makes the
existing internal helpers reachable across the package boundary without
adding new code paths.

**Alternative rejected**:
- *Re-implement cleanup logic in the workflow*: Would duplicate the
  error-decoding and SQL logic; risk of divergence.
- *Expose only thin wrappers that import the underscore-prefixed names*:
  Python convention discourages importing private (underscore-prefixed)
  names across module boundaries; a clean rename is the right fix.

### Decision 3: Extend the default `error_class_names` tuple

**Chosen approach**: Add `FileNotFoundError`, `OSError`,
`subprocess.CalledProcessError`, and `subprocess.SubprocessError` to the
default tuple. Callers passing their own tuple continue to override.

**Rationale**: These are the exception classes observed in production
ERROR rows that the current default filter silently skips. Widening
the default is a backwards-compatible change — the existing four
exception classes remain in the default tuple.

**Alternative rejected**:
- *Catch-all via `BaseException`*: Too aggressive — would catch
  programmer errors (`TypeError`, `KeyError`, etc.) that operators want
  to see, not silently cancel.

### Decision 4: Surface stderr at the worktree creation error boundary

**Chosen approach**: Keep `_default_command_runner`'s captured stderr and
include the captured text at `WorktreeManager.create()`'s existing
`RuntimeError` boundary. The command-runner signature is unchanged.

**Rationale**: `subprocess.run(check=True, capture_output=True, text=True)`
already captures `stderr` into the result object's `.stderr` attribute;
Python's default `CalledProcessError` does not include it in `str(exc)`.
The creation boundary appends the captured text so the operator's log line
shows the git error directly while preserving the public `RuntimeError` path.

**Alternative rejected**:
- *Define a new exception class* (`WorktreeError`): Overkill for a
  diagnostic improvement. `CalledProcessError` already carries
  `returncode`, `cmd`, `output`, and `stderr` — we just need to make
  `str(exc)` informative.

### Decision 5: Cron interval of 30 minutes

**Chosen interval**: Every 30 minutes (`CRON_TZ=UTC`).

**Rationale**: Matches the documented (but not implemented) intent of
the mis-archived `dbos-stale-workflow-auto-cleanup` change. The
observed recurrence interval for ERROR-row accumulation is 6–8 hours
(daily scans at 00:00 UTC, weekly hook errors, ad-hoc operator
deploys), so 30 minutes provides 12× redundancy against a single
missed cleanup. A 5-minute interval would be too aggressive for a
database write.

## Risks / Trade-offs

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Cleanup is too slow on large `workflow_status` table | Low | Functions use targeted `WHERE application_version <> current` and `WHERE status = 'ERROR' / 'ENQUEUED' AND created_at < threshold`; both are indexed by design. |
| Cleanup cancels a legitimately-ERROR workflow from the current version | Very Low | The function only cancels rows whose `application_version <> current_version` OR whose exception is in the known-stale class list. Legitimate errors (from current version) are preserved. |
| Docker `tdt-scheduler` is not running (e.g. host offline) | Low | The Docker container uses `restart: unless-stopped`. On host reboot, Docker Desktop auto-starts (Phase 0.2), container restarts, and the cleaner resumes. |
| Cleanup runs during active dispatch, creating race condition | Very Low | DBOS enqueues are idempotent; cancelling a row that has already been processed is harmless. Cleanup only targets stale `application_version`s or known-stale workflow names. |
| Renaming `_cancel_stale_error_workflows` to public breaks downstream callers | Low | The function was never part of any public API; the underscore prefix signals private. `grep` of all 5 TDT repos confirms only `agent-core` and `tdt-core` itself import it, both via relative paths that we update as part of this change. |
| Widening the default filter cancels ERROR rows that operators want to inspect | Very Low | Operators can still inspect the ERROR rows via the DBOS dashboard before the next 30-minute cleanup window, or set `error_class_names` to an empty tuple via the CLI's `--error-class-names` flag (which the CLI accepts as a CLI option for manual runs). |

## Open Follow-ups (out of scope for this change)

- Proactive health-check / service-restart watchdog (separate concern,
  documented in `tdt-core/openspec/changes/dbfs-stale-workflow-auto-cleanup/design.md`
  Risk table).
- Per-key dedup telemetry for ERROR rows that match the new default
  filter (helps diagnose operator confusion when an ERROR row they
  expected to inspect is gone before they get to it).
- YAML schedule manifest for the cleaner (deferred — current decorator
  approach is the convention in `agent-core`).

## Pre-execution Validation (2026-07-07)

The following was verified against the current source tree before
execution to confirm the 21 tasks are achievable without additional
discovery:

### Source state at validation time

- **tdt-core commit head** — `tdt-core/src/tdt_core/scheduler/cli.py`
  contains the three underscore-prefixed helpers
  (`_cancel_stale_error_workflows` at line 305,
  `_cancel_stale_enqueued_workflows` at line 80,
  `_cancel_stale_pending_workflows` at line 158). Only the first
  two are renamed to public in this change; the third stays private
  because it is called only from `_serve()` in the same module.
- **agent-core dead code** — `_cancel_stale_pending_workflows` at
  `agent-core/src/agent_core/scheduler_setup.py:74` is defined but
  never referenced from any caller in `agent-core/src/`. Task 2.2
  does NOT call this dead function — it imports the public
  helpers from `tdt_core.scheduler.cli` directly and wraps them
  in a NEW scheduled workflow.
- **engine API match** — `SchedulerEngine.scheduled_workflow(...)`
  signature (`engine.py:293`) confirms the
  `@_ENGINE.scheduled_workflow(cron=..., cron_timezone=...,
  name=...)` syntax from the proposal is valid. The decorator
  populates `self._schedule_registry`; `apply_schedules()`
  (called from `tdt_core/scheduler/cli.py:783` inside `_serve()`)
  pushes them to DBOS. The ownership contract requires
  `app_name='tdt-scheduler'`.
- **worktree runner state** —
  `code-daily-scan/src/code_daily_scan/scanners/worktree.py:58`
  already uses
  `subprocess.run(check=True, capture_output=True, text=True,
  timeout=timeout)`, so `CompletedProcess.stderr` is populated.
  The fix path is therefore a one-line wrapper in `create()` at
  line 280 (the existing `raise RuntimeError(...)` site) that
  reads `getattr(exc, "stderr", None)` and appends to the
  message. No behavioral change to the runner itself; no new
  exception class.
- **test infrastructure** — All three repos have a working test
  infra (`tdt-core/tests/scheduler/test_cli.py` with the
  `fake_sa` shim at line 320-328, `agent-core/tests/test_scheduler_setup.py`
  with the existing `MagicMock` engine stub at line 21-24,
  `code-daily-scan/tests/test_worktree_manager.py` with the
  existing `FakeRunner` at line 19). New tasks fit the existing
  patterns without needing new fixtures.

### Empirical backing from logs (2026-07-06 → 2026-07-07)

| Symptom | Volume | Frequency | Source |
|---------|--------|-----------|--------|
| `coverage-scan/webhook-selftest/...is not a registered workflow function` | 225 ERROR rows from ai-review stderr | Every service restart | `app-version drift` — workflows enqueued under a previous `application_version` no longer have a matching registered function in the live process |
| `No module named 'ai_review'` | 253 ERROR rows from webhook-receiver stderr | Same as above | `_dbos_debouncer_workflow` rows queued before `SCHEDULER_APP_NAME=tdt-webhook-receiver` isolation was added |
| `dbos.workflow_status` bloat | 8,527 CANCELLED rows of 15,750 total (54%) | Persistent | Cleanup runs only at `_serve()` startup (`cli.py:780-781`), no periodic timer |
| `daily_android_scan` ERROR | 1 row (current) | Daily at 00:00 UTC | `git worktree add` fails with exit 128; stderr not surfaced in the log |

This data confirms Tasks 1.3 (broaden filter) and 2.2 (register periodic
cleaner) are exactly the right fixes — the failures are real and
recurring, not edge cases.

### Manual-fallback script inventory (2026-07-07)

During validation, `agent-core/scripts/dbos-cancel-stuck-workflows.sh`
was identified as a manual-only recovery script (no cron, no LaunchAgent
wiring). It cancels ALL PENDING/ENQUEUED rows unconditionally — a much
heavier hammer than the new periodic cleaner. After Task 2.2 lands:

- The periodic cleaner handles the same workload automatically every 30 min
- The script becomes a "kill switch" for emergency use only
- It should be flagged for deprecation in a follow-up OpenSpec change
  (out of scope for this change to avoid scope creep)

The script also uses `localhost:5432` as the default DSN, which is
inconsistent with the Docker scheduler's `127.0.0.1:54329`. **Not
modified by this change** but worth noting for the deprecation follow-up.

### Spec coverage audit (2026-07-07)

The original proposal claimed `scheduler-cli` as a "Modified Capability"
but the change did not include a `specs/scheduler-cli/spec.md` to formally
capture the rename + filter extension. Validation round 2 added this
spec, closing the gap. The change now has 4 spec subdirectories
(agent-core-scheduler-setup, code-daily-scan-core, scheduler-engine,
scheduler-cli) — all matched by the 4 modified/new capabilities in the
proposal.

`openspec validate --strict` still passes after the addition.
