# Spec Deltas

This change proposes one capability with an ADDED delta.

## ADDED Deltas

### `scheduler-engine`

See `specs/scheduler-engine/spec.md`. This is an ADDED delta to the
`scheduler-engine` capability (the base capability is implicitly created here,
since no `scheduler-engine` spec existed in `openspec/specs/`). The delta adds
an ownership guard to `apply_schedules()` that raises
`SchedulerContractViolationError` when called by a non-canonical app.

## Out of Scope

Two related capabilities were documented in early drafts but deferred to
future changes: `tdt-scheduler-ownership-contract` (the abstract ownership
policy) and `tdt-scheduler-cancel-orphan-enqueued-cli` (the orphan-ENQUEUED
cleanup command). Their substance is covered by the `scheduler-engine`
implementation and the `centralized-scheduling-module` design respectively.

