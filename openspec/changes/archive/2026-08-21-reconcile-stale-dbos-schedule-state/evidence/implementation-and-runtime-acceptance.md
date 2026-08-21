# Implementation and Runtime Acceptance

## Ownership and immutable identities

- Planning store: `/Users/androidteam/Developer/openspec-store`
- Accepted implementation repository: `tdt-core`
- Immutable clean base: `afd4a89042afcf65a36a340743de360447d60d3b`
- Pre-edit dirty fingerprint: empty SHA-1 stream (`da39a3ee5e6b4b0d3255bfef95601890afd80709`)
- Reconciliation source commit: `a4baee611fa2388f5e11dabfc76bb2f4d6601fc3`
- Reconciliation graph commit: `d4f5af40259a51f02a5f7e238340998f7a1b4868`
- Docker filesystem prerequisite: `e0b0a0ea6d6a877042d24f4db8822819e8a5bf62`
- Final accepted `tdt-core/main`: `fa72c9c341c3db339e6671513248283efc73b2c1`
- Runtime host: `tdt-scheduler`; `tdt-observability` source was not edited by this change.
- DBOS dependency: `2.23.0`, verified from `uv.lock`, installed signatures, Context7, and installed package source.

The unrelated `~/Developer/tdt-core` feature checkout remained outside the
integration path and advanced concurrently. Docker acceptance explicitly bound
the accepted main worktree to `/workspace/tdt-core`.

## Pre-edit analysis and red boundary

Graphify located the `serve -> apply_from_yaml -> apply_schedules` flow and
existing stale-row cleanup. The first GitNexus lookup failed because only the
unrelated feature branch was indexed; a separate accepted-main branch index was
created before impact analysis.

Exact GitNexus impact:

- `SchedulerEngine.initialize`: CRITICAL, 20 dependants, 5 affected flows.
- `SchedulerEngine.apply_schedules`: HIGH, 13 dependants, 4 affected flows.
- `ScheduleRegistryLoader.apply_from_yaml`: HIGH, 7 dependants, 3 affected flows.
- `_serve`: LOW, one direct caller.
- `ScheduleRegistry.register`: LOW.
- `PlatformCapabilities.supported`: LOW, no indexed upstream callers.

The implementation deliberately did not edit the CRITICAL/HIGH methods. The
first focused red test failed at collection because
`tdt_core.scheduler.state_reconciliation` did not exist.

## Implemented behavior

- Pure current-registry/persisted-state classifier with canonical owner/queue boundaries.
- Explicit quarantine for retired `webhook-selftest`, `dlq-reaper`, `stale_workflow_cleaner`, `coverage-scan`, `scan-recent-mr`, and `jira-ticket-intelligence-hourly` registrations.
- DBOS schema capability validation with fresh-schema allowance and partial-schema failure.
- Transactional snapshot, schedule deletion, and PENDING/ENQUEUED/ERROR cancellation.
- Versioned rollback with current-registry, row-presence, and advanced-state conflict checks.
- Reverse-order rollback compatibility for overlapping late-row migrations.
- Pre-DBOS startup reconciliation, bounded poller quiescence, and a second late-row sweep.
- Credential-free CLI dry-run, apply, and rollback modes.
- Short-lived SQLAlchemy engine disposal.
- Canonical YAML/register-function startup without importing the legacy module-level `agent_core.scheduler_setup` apply path.
- Operator documentation with no-truncate/no-reset safeguards.

## Deterministic verification

- Focused reconciliation and scheduler tests: all passed.
- Full repository: 563 collected; 557 passed and 6 macOS `SIGSTOP` timing tests skipped by their existing marker.
- Ruff check: passed.
- Ruff format check: 85 files formatted.
- Strict mypy, all production `tdt_core`: 44 files, no issues.
- Strict mypy, scheduler source plus scheduler tests: 23 files, no issues.
- `uv lock --check`: passed.
- `git diff --check`: passed.
- Required staged `gitnexus detect-changes`: 9 files, 197 symbols, 32 flows, CRITICAL risk; scope matched the reviewed scheduler lifecycle.
- Independent Grok review: APPROVE, no blockers. Its SQLAlchemy-disposal finding was fixed; its remaining exception-syntax note was pre-existing and unrelated.
- Graphify AST index updated after implementation and after the Docker filesystem prerequisite.

## Reversible PostgreSQL rehearsal

A disposable PostgreSQL 18.6 database was initialized with DBOS 2.23.0. A
one-second retired `webhook-selftest` schedule reproduced three consecutive
`not a registered workflow function` errors when DBOS launched without that
workflow registered.

The implemented CLI then proved:

1. Dry-run found one stale schedule and three actionable workflow rows without mutation.
2. Apply removed the schedule and cancelled all three rows in one transaction.
3. A second apply returned `noop`.
4. Rollback restored exactly one schedule and all three original PENDING states.
5. A stale host manifest rehearsal loaded 21 registrations, quarantined both `webhook-selftest` and `dlq-reaper`, and left no retired registry entries.
6. A simulated late row produced a second workflow-only migration; reverse-order rollback restored exactly one schedule and three PENDING rows.

## Real Docker acceptance

Image build:

- Image: `tdt-scheduler:local`
- Image ID: `sha256:a2c0051e784f27a880dc05e849fe85b4b55ce2ecc1d4594dd8643287886c8d01`
- Build-time dependency-integrity gate: 7 workloads passed.
- Runtime dependency-integrity gate: 5 workloads passed in both controls.

The first container rehearsal exposed an inherited Linux Docker blocker:
`PlatformCapabilities.supported` incorrectly required macOS-only
`F_FULLFSYNC`. The existing isolated commit
`2ff42a9f9d2d5530634773c1f454975e17042bd0` was impact-reviewed, cherry-picked
as `e0b0a0ea6d6a877042d24f4db8822819e8a5bf62`, and all quality gates reran.

### Shared stale database

- Project: `tdt-scheduler-stale-acceptance`
- Endpoint: `127.0.0.1:19100`
- Pre-state: ACTIVE `webhook-selftest`, `dlq-reaper`, and legacy `stale_workflow_cleaner`; 15 PENDING webhook rows.
- Migration: `tdt-scheduler-6905723b-35b0-40f3-af00-4ae0691f419d`, version `scheduler-state-v1`, status `applied`.
- Post-state: zero retired schedules; 15 webhook rows CANCELLED; two webhook SUCCESS rows and three cleaner SUCCESS rows preserved.
- Health: initialized, DBOS connected, 19 schedules, 19 applied.

### Fresh database

- Project: `tdt-scheduler-fresh-acceptance`
- Endpoint: `127.0.0.1:19200`
- PostgreSQL: fresh `tdt_scheduler` and `tdt_scheduler_dbos_sys` databases.
- Reconciliation: `status=fresh`, no mutation.
- Health: initialized, DBOS connected, 19 schedules, 19 applied.
- Retired schedules: zero.

The original 20-count baseline included the persisted legacy
`stale_workflow_cleaner`; 19/19 is the canonical current baseline after
retirement.

## Bounded monitoring

Both controls were sampled from `11:53:26Z` through `11:56:16Z` (170 seconds).
Every sample reported:

- container running and Docker health `healthy`;
- failing streak zero;
- restart count zero;
- OOM killed false;
- `initialized=true`;
- `dbos_connected=true`;
- `schedule_count=19` and `schedules_applied=19`;
- zero `not a registered workflow function` log events.

The ambient `agent-core-local` and provider-adapter projects remained running.
Concurrent `agent-core`, `tdt-observability`, and
`consolidate-observability-docker-deployment` work was preserved and excluded.

## Rollback disposition

Rollback was fully rehearsed in the disposable PostgreSQL fixture. The shared
runtime migration remains applied because both real acceptance controls passed;
its migration identifier is retained in the system database for a future
operator rollback if conflict checks permit. No production credential value or
serialized provider payload appears in this evidence.
