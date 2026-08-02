# ecosystem-consolidation Specification

## Purpose

Standardize shared Jira and GitLab infrastructure, Python project tooling, independently deployable reporting applications, sprint-report enrichment, and optional report delivery across the TDT ecosystem.

## Requirements

### Requirement: Shared infrastructure via tdt-core

The ecosystem SHALL use tdt-core as the single shared package for env loading, client factories, config models, and resilience primitives across all Python projects.

#### Scenario: New project authenticates to Jira via tdt-core

- **WHEN** a new Python project needs Jira access
- **THEN** it SHALL authenticate via `JiraClientFactory.from_env()` from tdt-core
- **AND** it SHALL NOT re-implement env loading or client construction

### Requirement: Shared env coercion helpers

All shared config parsing SHALL use `tdt_core.env` helpers instead of project-local coercion code.

#### Scenario: A service reads typed environment values

- **WHEN** a service needs bool, int, float, or path configuration values
- **THEN** it SHALL use `get_bool_env()`, `get_int_env()`, `get_float_env()`, or `get_path_env()` from tdt_core
- **AND** it SHALL NOT add a new local wrapper for the same coercion pattern

#### Scenario: New project authenticates to Jira

- **WHEN** a new Python project needs Jira access
- **THEN** it SHALL authenticate via `JiraClientFactory.from_env()` from tdt-core
- **AND** it SHALL NOT re-implement env loading or client construction

#### Scenario: New project authenticates to GitLab

- **WHEN** a new Python project needs GitLab access
- **THEN** it SHALL use `GitlabClientFactory.from_env()` from tdt-core
- **AND** it SHALL NOT shell out to glab for API calls

### Requirement: Independent application projects

Each application project SHALL be independently deployable with its own entry point, test suite, version, and deployment target.

#### Scenario: Application project is tested

- **WHEN** a project's test suite runs
- **THEN** it SHALL pass without requiring other application projects to be present
- **AND** it SHALL only depend on tdt-core and optionally jira-skill as libraries

### Requirement: Standardized toolchain

All Python projects SHALL use ruff for linting/formatting, mypy for type checking, pytest for testing, hatchling as build backend, and uv as package manager.

#### Scenario: Project passes CI checks

- **WHEN** a project is pushed to GitLab
- **THEN** CI SHALL run ruff check, ruff format --check, mypy, and pytest
- **AND** all checks SHALL pass before merge

### Requirement: Sprint report metadata enrichment

The sprint-sheet command SHALL enrich per-work-item rows with estimation, start/end dates, worklog, and sprint-level summarization using atlassian-python-api via tdt-core.

#### Scenario: Sprint metadata is unavailable

- **WHEN** the board does not support sprints or estimation
- **THEN** the report SHALL gracefully fall back and mark fields as unavailable
- **AND** it SHALL NOT fail or produce empty output

### Requirement: Optional notification delivery

The run-all command SHALL support opt-in email and Slack delivery when environment variables are configured.

#### Scenario: SMTP is not configured

- **WHEN** SMTP_HOST is not set
- **THEN** email delivery SHALL be a no-op and SHALL NOT raise errors

#### Scenario: Slack webhook is not configured

- **WHEN** SLACK_WEBHOOK_URL is not set
- **THEN** Slack delivery SHALL be a no-op and SHALL NOT raise errors

#### Scenario: Both are configured

- **WHEN** SMTP_HOST and SLACK_WEBHOOK_URL are set
- **THEN** run-all SHALL send each report via both email and Slack after writing markdown
