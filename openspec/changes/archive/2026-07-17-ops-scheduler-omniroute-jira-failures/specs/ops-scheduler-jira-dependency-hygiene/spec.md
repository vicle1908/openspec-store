# ops-scheduler-jira-dependency-hygiene Specification

## Purpose

Define the contract for direct vs transitive Python dependencies in scheduler-managed sub-repos. The scheduler container's venv (`/opt/scheduler/.venv`) is the runtime for every DBOS scheduled workflow, so any direct import in a workflow's CLI entrypoint MUST be backed by a direct dependency declaration in that sub-repo's `pyproject.toml`.

## ADDED Requirements

### Requirement: Direct dependency declarations are mandatory for workflow entrypoints

Every Python sub-repo whose CLI is invoked from a scheduler YAML manifest MUST declare **every** module that the CLI imports at the top level as a direct dependency in `pyproject.toml`. Transitive resolution through a `[extra]` of a workspace dep is not sufficient.

#### Scenario: A workflow fails with ModuleNotFoundError on a non-declared import
- **WHEN** a CLI entrypoint registered in `~/.tdt/schedules/<owner>.yaml` imports `gitlab.exceptions`
- **AND** `pyproject.toml` for that CLI's repo does NOT list `python-gitlab` in `dependencies`
- **THEN** the scheduler workflow fails with `ModuleNotFoundError: No module named 'gitlab'`
- **AND** the failure recurs on every scheduled tick (the venv does not auto-install)

#### Scenario: Adding the direct dependency fixes the failure
- **WHEN** the CLI's repo adds `python-gitlab>=8.3.0,<9.0.0` to `pyproject.toml`
- **AND** the scheduler container is rebuilt with `uv sync`
- **THEN** the next scheduled tick succeeds with exit code 0
- **AND** the `scheduler.workflow.failed` event count for that workflow drops to zero over a 7-day window

### Requirement: Scheduler venv is the authoritative runtime

The `/opt/scheduler/.venv/` Python interpreter inside the `agent-core-local-scheduler-1` container is the only Python runtime that runs CLI workflows. The host venvs in `~/.tdt/venvs/<repo>/` SHALL NOT be relied on by the scheduler.

#### Scenario: A module installed in the host venv but not in the scheduler venv is missing
- **WHEN** `~/.tdt/venvs/jira-daily-reports/lib/python3.14/site-packages/gitlab/` exists on the host
- **AND** `/opt/scheduler/.venv/lib/python3.14/site-packages/gitlab/` does NOT exist in the scheduler container
- **THEN** `python -m jira_daily_reports <cmd>` inside the scheduler container fails with `ModuleNotFoundError`
- **AND** the host-side existence of the package is irrelevant to the scheduler

#### Scenario: Operator verifies package presence in scheduler venv
- **WHEN** an operator needs to verify that a dependency is available inside the scheduler container
- **THEN** `docker exec agent-core-local-scheduler-1 python -c "import <module>"` is the canonical verification command

### Requirement: `python-gitlab` is a required direct dependency for `jira-daily-reports`

The `jira-daily-reports` package depends on `python-gitlab>=8.3.0,<9.0.0` for the `dev_performance` and `sprint_sheet` subcommands. This dependency MUST be declared in `pyproject.toml` `dependencies` (not in `[dependency-groups].dev`).

#### Scenario: pyproject.toml declares python-gitlab at the top level
- **WHEN** an operator inspects `jira-daily-reports/pyproject.toml`
- **THEN** the `dependencies` list SHALL contain the entry `"python-gitlab>=8.3.0,<9.0.0"`
- **AND** this entry SHALL NOT be removed without a corresponding code change that also removes the `from gitlab.exceptions import …` line at `dev_performance/source.py:28`

#### Scenario: uv.lock pins python-gitlab at the declared range
- **WHEN** `cd ~/Developer/tdt/jira-daily-reports && uv lock` is run after the dependency is added
- **THEN** `uv.lock` SHALL contain a resolved package entry matching `python-gitlab` with version `>=8.3.0,<9.0.0`