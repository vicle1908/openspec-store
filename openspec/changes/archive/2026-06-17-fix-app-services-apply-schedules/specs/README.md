# Spec Deltas

This change proposes two new capabilities (ADDED) and one updated capability (ADDED delta).

## ADDED Capabilities

### `tdt-scheduler-ownership-contract`

See `specs/tdt-scheduler-ownership-contract/spec.md`. Documents the ownership
contract: only `app_name=tdt-scheduler` may call `apply_schedules()`.

### `tdt-scheduler-cancel-orphan-enqueued-cli`

See `specs/tdt-scheduler-cancel-orphan-enqueued-cli/spec.md`. Documents the new
`cancel-orphan-enqueued` CLI.

### `scheduler-engine`

See `specs/scheduler-engine/spec.md`. This is an **ADDED delta** to the
`scheduler-engine` capability (the base capability is implicitly created here,
since no `scheduler-engine` spec existed in `openspec/specs/`). The only change
is the ownership guard added to `apply_schedules()`.
