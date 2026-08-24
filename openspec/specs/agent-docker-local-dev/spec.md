## Purpose

This specification defines requirements for Agent Docker Local Dev.

## Requirements

### Requirement: agent-core provides a pinned local Docker development stack

The system MUST provide a repository-owned Docker Compose stack for local development that launches agent-core alongside the agent-core-owned shared runtime PostgreSQL server with exact image versions. The app image MUST build from `python:3.14.7-slim-trixie` with uv `0.12.5`, and PostgreSQL MUST use `postgres:18.6-trixie` with a PostgreSQL-18-versioned named volume mounted at `/var/lib/postgresql`. The app SHALL join configurable runtime and observability networks without redefining scheduler or observability backend services.

#### Scenario: Compose uses pinned current images

- **WHEN** the local Docker stack is inspected
- **THEN** the app image MUST build from `python:3.14.7-slim-trixie`
- **AND** build tooling MUST use uv `0.12.5`
- **AND** the database service MUST use `postgres:18.6-trixie`
- **AND** the Compose file MUST not use a floating `latest` or major-only tag for either service

#### Scenario: Compose starts the app and database for local dev

- **WHEN** a developer runs the owner-local Docker startup command
- **THEN** PostgreSQL SHALL start with a PostgreSQL-18-versioned persistent volume
- **AND** the volume SHALL be mounted at `/var/lib/postgresql`
- **AND** the app container SHALL mount only the intended workspace source and runtime paths
- **AND** the app container SHALL have the DBOS and memory DSNs needed for local durable execution
- **AND** the app container SHALL run local commands as a non-root user
- **AND** the app image SHALL declare a lightweight import healthcheck

#### Scenario: Coordinated deployment attaches agent-core without redefining it

- **WHEN** the TDT coordinator starts agent-core with observability
- **THEN** it SHALL use the owner-defined agent-core image and services
- **AND** the app SHALL join the selected runtime and observability networks
- **AND** tdt-observability SHALL not contain a duplicate agent-core service definition

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
