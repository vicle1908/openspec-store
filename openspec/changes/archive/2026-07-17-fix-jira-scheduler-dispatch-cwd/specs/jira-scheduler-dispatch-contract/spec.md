# jira-scheduler-dispatch-contract Specification

> Spec delta for the `fix-jira-scheduler-dispatch-cwd` change. See `proposal.md`
> for context and `tasks.md` for implementation steps. After this change is
> archived, this file is promoted to `tdt-meta/openspec/specs/jira-scheduler-dispatch-contract/spec.md`.

## ADDED Requirements

### Requirement: Use sys.executable + python -m jira_daily_reports

`jira_daily_reports.dbos_scheduling._run_report` SHALL invoke each
report CLI via `[sys.executable, "-m", "jira_daily_reports", <command>]`
without going through `uv`. The spawned process SHALL run with the
scheduler venv's Python interpreter. Because the scheduler venv
(`agent-core/deployments/scheduler/Dockerfile`,
`UV_PROJECT_ENVIRONMENT=/opt/scheduler/.venv`) does NOT have
`jira_daily_reports` installed as a package, `_run_report` SHALL inject
`PYTHONPATH=/workspace/jira-daily-reports/src` into the spawned
environment so the module is importable. This mirrors the canonical
pattern in `agent-core/scheduler_setup.py::_run_webhook_selftest` and
sibling helpers, which inject `PYTHONPATH` pointing at the workload
repo's `src/` directory.

#### Scenario: sprint-sheet is invoked via sys.executable

- **WHEN** `jira-sprint-sheet` scheduled workflow fires
- **THEN** `_run_report("sprint-sheet", env_extra)` SHALL spawn
  `[sys.executable, "-m", "jira_daily_reports", "sprint-sheet"]`
- **AND** the spawned process SHALL exit 0 on success
- **AND** `subprocess.run(..., check=True)` SHALL propagate non-zero
  exits as `CalledProcessError`

#### Scenario: env_extra is forwarded to the spawned process

- **WHEN** `_run_report` is called with `env_extra={"REPORT_FRESHNESS_SOURCE": "schedule"}`
- **THEN** the spawned process SHALL receive `REPORT_FRESHNESS_SOURCE=schedule`
  in its environment, alongside every other key from `os.environ`

#### Scenario: PYTHONPATH includes jira-daily-reports/src

- **WHEN** `_run_report` builds the spawned environment
- **THEN** `env["PYTHONPATH"]` SHALL start with `/workspace/jira-daily-reports/src`
- **AND** an existing `os.environ["PYTHONPATH"]` (if set) SHALL be
  appended after, not overwritten

#### Scenario: No `uv` invocation

- **WHEN** `_run_report` builds its subprocess command
- **THEN** the first element of `cmd` SHALL be `sys.executable` (a
  Python interpreter path), NOT `uv` or any wrapper script

#### Scenario: No cwd requirement

- **WHEN** `_run_report` builds its subprocess command
- **THEN** `subprocess.run` SHALL NOT specify a `cwd=` argument (the
  spawned process resolves `jira_daily_reports` via `PYTHONPATH`,
  which is independent of the current working directory)

### Requirement: Drop dead helpers

`jira_daily_reports.dbos_scheduling` SHALL NOT export `_find_uv` or
`_repo_dir` after this contract takes effect. They exist solely to
support the broken `uv run …` shortcut and have no remaining
callers.

#### Scenario: _find_uv removed

- **WHEN** the module is imported
- **THEN** `_find_uv` SHALL NOT be defined as a module-level function

#### Scenario: _repo_dir removed

- **WHEN** the module is imported
- **THEN** `_repo_dir` SHALL NOT be defined as a module-level function

### Requirement: Live verification — freshness state file updates SHALL pass

SHALL update the freshness state file on a manual trigger. After the
scheduler container is rebuilt and restarted with the new code, a manual
trigger of `jira-sprint-sheet` SHALL update
`~/.tdt/state/jira-daily-reports/freshness/<spreadsheet_id>.json` with a
`refreshed_at` timestamp within the last 5 minutes. The contract is
verifiable end-to-end via the manual trigger + state-file read-back in
`tasks.md` §6.

#### Scenario: Trigger refreshes the Sprint 17 freshness state file

- **WHEN** `curl -X POST http://127.0.0.1:9100/scheduler/schedules/jira-sprint-sheet/trigger`
  is executed after the container restart
- **THEN** within 5 minutes, the freshness state file for the Sprint 17
  workbook (`1o5AJA589GElhqwACZn6v5uvFsVfruF25YS9Y_0LJhcw`) SHALL have
  `refreshed_at` set to the current UTC time
- **AND** the `run_id` SHALL be a fresh 16-character hex string
- **AND** the `source` field SHALL be `"schedule"`