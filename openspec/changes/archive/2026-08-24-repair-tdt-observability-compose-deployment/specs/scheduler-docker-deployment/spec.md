## MODIFIED Requirements

### Requirement: Docker scheduler service on the single ecosystem PostgreSQL server

The system SHALL provide a Docker `scheduler` service as the long-lived DBOS host for every movable cron or interval workload. The scheduler SHALL remain defined and built by the dedicated `tdt-scheduler` repository using its canonical workspace-root build context, and tdt-observability SHALL not redefine it. All Python execution in the scheduler container SHALL use the locked scheduler environment through `uv run`. The scheduler SHALL connect through a configurable shared runtime network to the single ecosystem PostgreSQL server owned by agent-core, SHALL use its own `tdt_scheduler` application database and auto-derived `tdt_scheduler_dbos_sys` system database, and SHALL NOT stand up or select a second generic runtime PostgreSQL server. The scheduler SHALL also join the configurable observability network and export OTLP only to `http://otel-gateway:4317` after the compatibility transition.

#### Scenario: Scheduler starts against the ecosystem Postgres server

- **WHEN** the coordinated operator command starts the scheduler project
- **THEN** the repository-owned `scheduler` service SHALL run `agent-core-scheduler serve`
- **AND** it SHALL connect to the agent-core-owned `tdt_scheduler` database over the selected runtime network
- **AND** no scheduler-owned or tdt-observability-owned generic runtime PostgreSQL service SHALL be created

#### Scenario: Scheduler does not launch against an unready database

- **WHEN** the scheduler starts in a separate Compose project from PostgreSQL
- **THEN** its entrypoint SHALL perform a bounded reachability and required-database probe before DBOS initialization
- **AND** failure SHALL produce actionable diagnostics and a non-ready scheduler state rather than relying on invalid cross-project `depends_on`

#### Scenario: Own logical database on the shared server

- **WHEN** the scheduler initializes its durable engine
- **THEN** its application connection SHALL target `tdt_scheduler`
- **AND** its DBOS system connection SHALL target `tdt_scheduler_dbos_sys`
- **AND** both SHALL live on the one agent-core-owned PostgreSQL server

#### Scenario: Scheduler compose is independent from agent-core

- **WHEN** `docker compose -f tdt-scheduler/compose.yaml config --services` runs
- **THEN** the output SHALL list `scheduler` and MAY list `postgres-backup`, but SHALL NOT list agent-core or tdt-observability services
- **AND** `build.context` SHALL resolve to the workspace root
- **AND** `build.dockerfile` SHALL resolve to `tdt-scheduler/Dockerfile`

#### Scenario: Scheduler joins both shared networks

- **WHEN** the coordinated deployment renders the scheduler service
- **THEN** the scheduler SHALL join the selected runtime network for PostgreSQL and the selected observability network for OTLP
- **AND** both network names SHALL be overridable for isolated verification

#### Scenario: Scheduler backup reaches only the runtime database network

- **WHEN** the repository-owned `postgres-backup` service is enabled
- **THEN** it SHALL join the selected runtime network and resolve the agent-core-owned `postgres` alias
- **AND** it SHALL not require the observability network
- **AND** the owner implementation SHALL produce a bounded `pg_dump` artifact for the configured scheduler database
- **AND** backup acceptance SHALL verify its readability and checksum without printing database credentials

#### Scenario: Scheduler host inputs preserve owner parity

- **WHEN** the coordinated deployment supplies scheduler TDT home, workload source, mobile repository, configuration, or credential mounts
- **THEN** the rendered inputs SHALL match the repository-owned scheduler Compose contract at the same source revision
- **AND** the host TDT home source SHALL not default to a container-only path
