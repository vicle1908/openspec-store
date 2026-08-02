# Capability: scheduler-timezone-clarification

## Purpose

The Docker `scheduler` service sets `TZ=Asia/Ho_Chi_Minh` in
`agent-core/compose.yaml:92`, but DBOS interprets `cron_timezone`
per-decorator and ignores the container's `TZ` env var. The result is
that 3 schedules fire in UTC and the rest fire in `Asia/Ho_Chi_Minh`,
even though the container's `TZ` suggests "Asia everywhere". The actual
firing times are correct — DBOS is doing the right thing — but the
mismatch is misleading to anyone reading the schedule list or editing a
cron expression. This capability documents the timezone of each schedule
inline and in `tdt_core/scheduler/README.md`.

## ADDED Requirements

### Requirement: Every `@scheduled_workflow` decorator carries an inline timezone comment

Every decorator invocation in `agent-core/scheduler_setup.py` SHALL be
followed by an inline comment that names the timezone the schedule
actually fires in and explains why the comment is needed.

#### Scenario: UTC schedule decorator

- **GIVEN** a decorator `@_ENGINE.scheduled_workflow(cron="*/5 * * * *",
  name="webhook-selftest", cron_timezone="UTC", ...)`
- **WHEN** a reader scrolls to the line directly below the decorator
- **THEN** they SHALL see a comment in the form
  `# Fires every 5 min UTC. DBOS interprets cron_timezone independently
  of the container TZ env var (compose.yaml sets TZ=Asia/Ho_Chi_Minh,
  but that does not affect this schedule).`

#### Scenario: Local-time schedule decorator

- **GIVEN** a decorator with `cron_timezone=workspace_timezone_name()`
- **WHEN** a reader scrolls to the line directly below the decorator
- **THEN** they SHALL see a comment that names
  `workspace_timezone_name()` as the source of the timezone and notes
  that the value comes from `~/.tdt/config.yaml` (or `TDT_HOME`).

### Requirement: Module docstring describes the timezone model

`agent-core/scheduler_setup.py` SHALL carry a module-level docstring
section titled "Timezones" that explains the model in three short
paragraphs:

1. DBOS interprets `cron_timezone` per-decorator; the container's `TZ`
   env var is **not consulted** by DBOS for cron firing.
2. The container `TZ=Asia/Ho_Chi_Minh` (set in `compose.yaml:92`) is
   used by Python `datetime.now()` inside the workflow bodies for log
   timestamps and human-readable reporting. It does not affect cron.
3. UTC schedules use `cron_timezone="UTC"` to anchor the firing time to
   UTC regardless of where the operator is located. Local schedules use
   `workspace_timezone_name()` to anchor firing to the workspace's
   configured timezone.

#### Scenario: Reader consults the module docstring

- **WHEN** a developer opens `agent-core/scheduler_setup.py` for the
  first time
- **AND** they read the module docstring
- **THEN** the "Timezones" section SHALL appear before the first
  `@_ENGINE.scheduled_workflow` decorator

### Requirement: `tdt_core/scheduler/README.md` documents the timezone model

The existing README at `tdt-core/src/tdt_core/scheduler/README.md` SHALL
include a "Timezones" section that mirrors the module docstring, with
the additional guidance:

- When adding a new scheduled workflow, prefer `cron_timezone="UTC"` for
  schedules that are global (e.g., health probes, debouncer cleanup).
- Prefer `cron_timezone=workspace_timezone_name()` for schedules tied
  to business hours (standups, daily reports).
- Document the choice in the decorator's inline comment.

#### Scenario: Adding a new schedule

- **GIVEN** a developer adds a new `@_ENGINE.scheduled_workflow` to
  `scheduler_setup.py`
- **WHEN** they consult the README's "Timezones" section
- **THEN** the section SHALL recommend which `cron_timezone` value to
  use based on the schedule's purpose
- **AND** the section SHALL instruct the developer to add an inline
  comment to the decorator

### Requirement: Cron firing times SHALL NOT change as a result of this change

SHALL NOT change the set of cron expressions and their `cron_timezone`
values. The 21 schedules registered today (`tdt-scheduler schedules list`
returns 21 rows as of 2026-06-27) SHALL continue to fire with identical
cron expressions and `cron_timezone` values after this change ships.

#### Scenario: Cron firing regression check

- **WHEN** the scheduler service is restarted after this change
- **THEN** `tdt-scheduler schedules list` SHALL return the same 21
  schedules with the same cron expressions and timezones as before
- **AND** a 24-hour observation window SHALL show each schedule firing
  at the expected wall-clock time
