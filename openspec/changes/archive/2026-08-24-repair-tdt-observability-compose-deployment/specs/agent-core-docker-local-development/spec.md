## MODIFIED Requirements

### Requirement: agent-core provides a pinned local Docker development stack

The system SHALL provide a repository-owned Docker Compose stack for local development that launches agent-core alongside the single shared runtime PostgreSQL service. The app image MUST build from `python:3.14.7-slim-trixie` with uv `0.12.5`, and the database MUST use `postgres:18.6-trixie` with a PostgreSQL-18-versioned named volume mounted at `/var/lib/postgresql`. The owner-local build SHALL have explicit access to tdt-core without copying outside its declared build contexts. The agent-core app and PostgreSQL services SHALL join a configurable runtime network, the app SHALL also join a configurable observability network, and the app SHALL export OTLP to `http://otel-gateway:4317`. The scheduler SHALL NOT be defined in agent-core or tdt-observability Compose; it remains owned by `tdt-scheduler/compose.yaml`.

#### Scenario: Compose uses pinned current images

- **WHEN** the local Docker stack is inspected
- **THEN** the app image MUST build from `python:3.14.7-slim-trixie`
- **AND** build tooling MUST use uv `0.12.5`
- **AND** the database service MUST use `postgres:18.6-trixie`
- **AND** no service SHALL use a floating or fallback image outside the approved deployment inventory

#### Scenario: Compose starts the app and database for local dev

- **WHEN** the owner-defined agent-core startup command runs
- **THEN** the `app` and `postgres` services SHALL start
- **AND** the PostgreSQL volume SHALL be PostgreSQL-18-versioned and mounted at `/var/lib/postgresql`
- **AND** the `scheduler` service SHALL NOT be started by the agent-core project

#### Scenario: agent-core compose does not include scheduler

- **WHEN** `docker compose -f agent-core/compose.yaml config --services` runs
- **THEN** the output SHALL NOT list `scheduler`
- **AND** the scheduler SHALL remain managed through `tdt-scheduler/compose.yaml`

#### Scenario: Agent-core image builds from declared contexts

- **WHEN** the app image is built from a clean agent-core checkout
- **THEN** every copied agent-core and tdt-core input SHALL be reachable through an explicit build context
- **AND** locked synchronization and the agent-core import healthcheck SHALL pass under the runtime environment

#### Scenario: Required logical databases are bootstrapped

- **WHEN** PostgreSQL initializes a fresh versioned volume
- **THEN** the owner-managed initialization SHALL create `agent_core`, `tdt_scheduler`, `tdt_scheduler_dbos_sys`, and `agent_harness`
- **AND** repeated startup against the retained volume SHALL preserve their durable data

#### Scenario: Postgres is shared between stacks

- **WHEN** agent-core and scheduler projects run together
- **THEN** both SHALL resolve the agent-core-owned PostgreSQL service through the selected runtime network
- **AND** each SHALL use its own logical database
- **AND** tdt-observability SHALL not define a duplicate runtime database service

#### Scenario: App joins observability routing

- **WHEN** an observability profile is active
- **THEN** the app SHALL resolve `otel-gateway` on the selected observability network
- **AND** coordinated profiles SHALL select Collector mode for Langfuse and MLflow
- **AND** direct Langfuse processing and MLflow autolog SHALL be disabled
- **AND** Collector initialization failure SHALL not fall back to either direct route

### Requirement: agent-core documents the local Docker workflow

The system MUST document how to build, start, stop, and test the owner-defined agent-core project and how the coordinated TDT deployment attaches it to runtime and observability networks. Documentation SHALL identify agent-core as the runtime PostgreSQL owner and SHALL not describe removed Langfuse, MLflow, MinIO, or Collector services as members of `agent-core/compose.yaml`.

#### Scenario: README explains the Docker workflow

- **WHEN** a developer reads the agent-core Docker documentation
- **THEN** they SHALL find the owner-local Docker command sequence and exact image versions
- **AND** they SHALL understand which coordinator command joins agent-core to scheduler and observability projects
- **AND** the documented service inventory SHALL match the rendered agent-core Compose model
