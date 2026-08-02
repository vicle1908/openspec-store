# scheduler-engine Specification (delta)

> Spec delta for the `fix-jira-scheduler-dispatch-cwd` change. After this
> change is archived, these scenarios are promoted to the existing
> `scheduler-engine` capability spec at
> `tdt-meta/openspec/specs/scheduler-engine/spec.md`.

## ADDED Requirements

### Requirement: `dbos.workflow_schedules` persistence gap MUST be tracked as follow-up

MUST be investigated as a separate OpenSpec change (not addressed by
`fix-jira-scheduler-dispatch-cwd`). The `tdt-scheduler` Docker container
currently exposes 22 schedules via `GET /scheduler/schedules`
(in-process registry) but the `dbos.workflow_schedules` table in Postgres
(`tdt_scheduler_dbos_sys_dbos_sys`) is empty. This delta SHALL observe
and document the gap, then track it via `tasks.md` §10.

Description (non-normative): the empty table means schedule spec rows
are not persisted across container restarts; recovery depends entirely
on re-running the setup module at boot.

#### Scenario: Observed mismatch

- **WHEN** the scheduler container is healthy and `/scheduler/schedules`
  returns 22 entries
- **THEN** `SELECT COUNT(*) FROM dbos.workflow_schedules;` SHALL return
  a non-zero value reflecting the registered set
- **AND** the gap SHALL be investigated as a separate change (not
  addressed by `fix-jira-scheduler-dispatch-cwd`)

#### Scenario: Restart-recovery currently relies on `tdt-scheduler serve` re-importing `scheduler_setup`

- **WHEN** the scheduler container restarts
- **THEN** all 22 schedules SHALL be re-registered via the in-process
  registry on `serve` startup, without depending on the empty
  `dbos.workflow_schedules` table

#### Scenario: Tracked as follow-up

- **WHEN** this change is archived
- **THEN** a follow-up OpenSpec change SHALL be opened (separately) to
  investigate the persistence gap and either fix it or document it as
  accepted behaviour