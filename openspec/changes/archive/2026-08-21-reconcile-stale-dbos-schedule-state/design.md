## Context

The current scheduler already loads decorator and YAML schedule registrations,
initializes DBOS, and runs stale-workflow maintenance. The isolated deployment
showed that a shared DBOS system database can retain a scheduled reference whose
workflow is no longer registered, while a fresh pair of scheduler databases
does not reproduce the error. See `proposal.md` and the `scheduler-engine`
delta for the motivation and externally observable contract.

The implementation boundary is the `tdt-core` scheduler library. The
`tdt-scheduler` repository remains the Docker/runtime acceptance host. The
solution must operate safely when the system database is shared and must not
turn a deployment verification finding into a blanket database reset.

## Goals / Non-Goals

**Goals:**

- Establish one canonical reconciliation point after the current registry is
  known and the DBOS schema is available, but before persisted schedules can
  enqueue work.
- Keep schedule/workflow comparison, ownership filtering, dry-run reporting,
  mutation, rollback, and readiness gating separately testable.
- Make all mutation idempotent, transactional or equivalently recoverable, and
  observable without exposing credentials or serialized exception payloads.
- Preserve the existing fresh-control baseline and prove the stale-state case
  with a disposable seeded database and the real scheduler container.

**Non-Goals:**

- Re-registering or executing retired workflows such as `webhook-selftest`.
- Changing DBOS itself, truncating databases, or modifying unrelated consumers'
  rows.
- Changing manifest generation, cron cadence, workload ownership, or public
  deployment placement.

## Decisions

### Decision 1: Reconcile at the canonical scheduler lifecycle boundary

The scheduler SHALL build a normalized snapshot of current scheduler-owned
schedule names and workflow references after decorator/YAML registration and
before schedule application/readiness. A narrow reconciliation adapter SHALL
then inspect DBOS system-database schedules and actionable workflow rows. The
adapter owns comparison and cleanup; `SchedulerEngine` owns lifecycle ordering
and fail-closed readiness.

**Rationale:** Putting the hook at the common lifecycle boundary covers both
declarative and decorated registrations and prevents a stale row from reaching
the next scheduler tick. Keeping database operations behind an adapter avoids
spreading DBOS schema assumptions through registry and CLI code.

**Alternatives considered:**

- Cleanup only in the periodic stale-workflow cleaner — rejected because the
  stale scheduled reference can fire before the cleaner and the first observed
  error occurred during normal DBOS scheduling.
- Cleanup only in the Docker entrypoint — rejected because it would duplicate
  library lifecycle authority and would not cover non-Docker scheduler hosts.
- Truncate/reset the DBOS system database — rejected because the database is
  shared and reset destroys valid state.

### Decision 2: Use an explicit ownership and registry-resolution filter

The reconciliation snapshot SHALL include the canonical app identity,
application version/namespace where available, current schedule names, and
registered workflow names. A persisted candidate is mutable only when the
adapter can prove that it belongs to the canonical `tdt-scheduler` owner and
that its workflow/schedule is absent or retired from the current registry.
Unknown namespaces, ambiguous rows, current-version rows, and rows that cannot
be resolved remain untouched and are reported for operator review.

**Rationale:** A shared system database makes name-only deletion unsafe. The
filter is the protection boundary for unrelated DBOS consumers and future
workloads.

**Alternatives considered:**

- Delete every schedule not present in the current manifests — rejected because
  it cannot distinguish another consumer or a temporarily unavailable registry.
- Match only by workflow name — rejected because names and application versions
  can be reused across deployments.

### Decision 3: Separate dry-run, apply, and rollback with an explicit boundary

Dry-run performs read-only queries and emits candidate/protected counts. Apply
captures the exact selected scheduler-owned rows in a versioned reconciliation
record or equivalent rollback artifact, then performs cancellation/deletion in
one database transaction (or a DBOS-supported atomic equivalent). Rollback
restores only the captured rows and refuses to overwrite newer valid state
unless the ownership/version preconditions still match.

**Rationale:** The first production-like reproduction is persisted state, so
  the remediation must be auditable and reversible. A snapshot taken before
  mutation also makes partial-failure handling testable.

**Alternatives considered:**

- Best-effort row-by-row deletion — rejected because a mid-run failure could
  leave a mixed scheduler state with no reliable rollback point.
- Filesystem-only snapshots — rejected because they are not transactionally
  coupled to PostgreSQL and are easy to lose or misapply.

### Decision 4: Fail closed before readiness on reconciliation uncertainty

If database access, schema compatibility, registry resolution, ownership proof,
or mutation recovery fails, the scheduler SHALL preserve rows and keep cron
processing/readiness inactive. Diagnostics SHALL include a stable reason,
candidate identity where safe, and counts, while redacting connection strings,
credentials, and serialized provider payloads.

**Rationale:** Continuing with unknown persisted state can replay stale work;
  silently deleting uncertain state can destroy valid work. A readiness failure
  is safer and observable.

### Decision 5: Acceptance uses two disposable database fixtures

Tests SHALL use a fixture that seeds an owned retired schedule/workflow row and
a fresh fixture with both `tdt_scheduler` and `tdt_scheduler_dbos_sys`. The
runtime gate SHALL run the real `tdt-scheduler:local` container against both,
verify health/schedule counts, and search bounded logs for the retired workflow
error. The original 20-count included the persisted legacy
`stale_workflow_cleaner`; the accepted current baseline is therefore 19 current
schedules / 19 applied over at least 150 seconds.

**Rationale:** The clean-start control distinguishes stale database state from
  current manifest registration and prevents a deterministic unit test from
  being mistaken for end-to-end acceptance.

## Risks / Trade-offs

- **[Risk] Incorrect ownership matching deletes valid shared state** → **Mitigation:** require canonical owner/version evidence, preserve ambiguous rows, and cover consumer-boundary fixtures before enabling mutation.
- **[Risk] DBOS schema/API drift breaks reconciliation** → **Mitigation:** isolate DBOS calls behind an adapter, validate schema capabilities at startup, and fail closed with a bounded diagnostic.
- **[Risk] Partial mutation leaves an unrecoverable database** → **Mitigation:** capture exact rows, use one transaction where supported, and test rollback/conflict refusal.
- **[Risk] Startup latency increases** → **Mitigation:** bound queries, report reconciliation duration, and prove the live health start-period remains sufficient in the real container.
- **[Risk] A healthy fresh control masks stale-state behavior** → **Mitigation:** require both fresh and seeded-stale runtime fixtures in acceptance.

## Migration Plan

1. Add the reconciliation adapter and focused unit/fixture tests in the owning
   `tdt-core` worktree. Run GitNexus impact analysis before source edits and
   `detect_changes()` before commit.
2. Run the dry-run path against a disposable copy/fixture of the stale DBOS
   system state and review candidate/protected counts.
3. Apply the versioned migration transactionally, capture the rollback point,
   and start the real scheduler container against the seeded stale fixture.
4. Verify no new unregistered-workflow error, current schedules remain applied,
   health is live, and the fresh 150-second control remains green.
5. If acceptance fails, stop scheduler readiness, invoke rollback using the
   recorded version, verify row preservation, and leave the change unarchived.
6. Only after independent verification should the OpenSpec delta be synced and
   the change archived. The current local-Compose documentation change remains
   a separate planning/runbook change.

## Open Questions

None. The DBOS API/schema details are implementation inspection tasks, not
unresolved product decisions; they must be resolved in the source worktree
before code is edited.

## Implementation disposition

Implementation inspection resolved the lifecycle boundary without modifying
the CRITICAL `SchedulerEngine.initialize()` method or HIGH-risk
`apply_schedules()`/`apply_from_yaml()` methods. The canonical `serve` path now
loads YAML/register-function state, quarantines explicit retired names,
transactionally reconciles persisted DBOS rows, quiesces sibling pollers,
performs a late-row sweep, and only then launches DBOS and applies current
schedules. A one-file pre-existing Docker filesystem-capability fix was merged
as a prerequisite after the first real container rehearsal exposed the Linux
`F_FULLFSYNC` incompatibility.
