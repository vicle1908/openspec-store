## MODIFIED Requirements

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
