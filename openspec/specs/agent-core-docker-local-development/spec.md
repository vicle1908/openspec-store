# agent-core-docker-local-development Specification

## Purpose
Docker Compose stack for local agent-core development with pinned image versions, DBOS bootstrap, and developer documentation.

## Requirements

### Requirement: ripgrep is installed in the scheduler image
The scheduler `Dockerfile`'s `apt-get install` line MUST include `ripgrep` (the `rg` binary) alongside `ca-certificates curl gcc git libpq-dev tzdata`.

#### Scenario: ripgrep available on PATH inside container
- **WHEN** the scheduler container is running
- **THEN** `uv run rg --version` exits 0 and prints the `ripgrep` version
- **AND** `which rg` resolves to `/usr/bin/rg`

### Requirement: Test asserts ripgrep install is not regressed
The test `tests/test_docker_local_dev.py::test_dockerfile_matches_compose_versions` MUST assert that the `apt-get install` line contains the literal string `ripgrep`.

#### Scenario: Regression test catches Dockerfile change
- **WHEN** an operator removes `ripgrep` from the `apt-get install` list
- **THEN** `pytest tests/test_docker_local_dev.py::test_dockerfile_matches_compose_versions` fails
- **AND** the failure message identifies the missing dependency

### Requirement: agent-core provides a pinned local Docker development stack

The system SHALL provide a Docker Compose stack for local development that launches agent-core alongside Postgres with pinned image versions. The scheduler service SHALL NOT be part of agent-core's compose stack — it has its own `tdt-scheduler/compose.yaml`.

#### Scenario: Compose uses pinned current images

- **WHEN** the local Docker stack is inspected
- **THEN** the app image MUST build from `python:3.14.5-slim-trixie`
- **AND** the database service MUST use `postgres:18.6-trixie`

#### Scenario: Compose starts the app and database for local dev

- **WHEN** `docker compose up -d` is run from `agent-core/`
- **THEN** the `app` and `postgres` services SHALL start
- **AND** the `scheduler` service SHALL NOT be started (it lives in `tdt-scheduler/`)

#### Scenario: agent-core compose does not include scheduler

- **WHEN** `docker compose -f agent-core/compose.yaml config --services` runs
- **THEN** the output SHALL NOT list `scheduler`
- **AND** the scheduler SHALL be managed separately via `tdt-scheduler/compose.yaml`

#### Scenario: Postgres is shared between stacks

- **WHEN** both `agent-core/compose.yaml` and `tdt-scheduler/compose.yaml` are running
- **THEN** both SHALL connect to the same ecosystem PostgreSQL server
- **AND** the scheduler SHALL use its own logical database (`tdt_scheduler`) distinct from agent-core's (`agent_core`)

### Requirement: agent-core documents the local Docker workflow
The system MUST document how to start, stop, and test the local Docker stack.

#### Scenario: README explains the Docker workflow
- **WHEN** a developer reads the main README
- **THEN** they can find the Docker local development command sequence
- **AND** they can see which pinned image versions the stack uses

### Requirement: settings validation accepts DBOS database URLs for local Docker bootstrap
The system MUST allow local durable execution validation to succeed when the DBOS database URL is provided through `DBOS_DATABASE_URL`.

#### Scenario: DBOS_DATABASE_URL satisfies durable execution validation
- **WHEN** `crash_recovery.enabled=true` and `DBOS_DATABASE_URL` is set
- **THEN** required-secret validation MUST succeed even if `POSTGRES_URL` is unset
