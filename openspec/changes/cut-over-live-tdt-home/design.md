# Design: Live TDT_HOME Cutover

## Context

The installed provider has only inspected the current `~/.tdt`; it has not
repaired permissions, broken links, duplicate config, literal DSNs, or runtime
state. A live cutover must make those choices explicit and reversible instead
of turning a doctor report into an implicit authorization.

## Decisions

### Decision 1: Preflight is a hard gate

Execution requires a current value-free root inventory, provider release and
staging evidence, source-conformance results for every consumer, a synthetic
recovery pass, explicit owner/principal attestations, a maintenance window,
and an approved destination mapping. Unknown, conflicting, or secret-bearing
inputs block the plan.

### Decision 2: Snapshot before mutation

The operator retains a restorable snapshot or backup whose identity, scope,
timestamp, and restore procedure are recorded without copying secret values
into the plan. The plan identifies duplicate sources, broken links, runtime
state, and permission drift as typed decisions rather than silently selecting
one pathname.

### Decision 3: Quiesce readers and use the migration engine

Known readers/writers are stopped or placed in an agreed maintenance mode. The
approved migration engine opens the root once, uses descriptor-relative
operations, journals every boundary, and stops on identity/capability drift.
No ad-hoc `cp`, recursive `mkdir`, pathname `rename`, or broad cleanup is
permitted in the execution procedure.

### Decision 4: Recovery is the default failure path

An interruption, health failure, or approval withdrawal stops forward work and
invokes the tested recovery/rollback path. Resumption requires the same root
identity and journal chain; a changed root, principal, or mapping requires a
new plan and approval.

### Decision 5: Post-cutover evidence is scoped

Provider doctor, consumer smoke tests, service health, permissions, links,
config ownership, and scheduler/database checks are recorded separately. A
passing provider doctor cannot mark a consumer or deployment ready.

## Transaction Boundaries

1. Plan approval and root snapshot binding.
2. Reader/writer quiescence confirmation.
3. Journal preparation and per-operation migration.
4. Final root identity and provider doctor verification.
5. Consumer/deployment smoke checks and release of maintenance mode.

## Evidence Gates

- Every preflight and post-cutover result is timestamped, owner-attributed, and
  value-free.
- A failed gate leaves the live root unchanged or invokes the recorded
  rollback, with no claim of success.
- The final worktree/store review separates planning edits from runtime state.

## Rollback

Rollback restores the approved snapshot or journal inverse under the same
quiescence and descriptor-relative rules. It must not delete unknown files,
rewrite credentials, or broaden the plan after execution begins.
