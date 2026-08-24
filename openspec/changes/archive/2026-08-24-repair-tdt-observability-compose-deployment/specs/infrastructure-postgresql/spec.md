## MODIFIED Requirements

### Requirement: PostgreSQL 18.6 is the infrastructure baseline

All first-party PostgreSQL infrastructure used by the coordinated agent-core, scheduler, observability, and agent-harness local deployment MUST use the immutable image tag `postgres:18.6-trixie`. The agent-core project SHALL own the single shared runtime PostgreSQL service, while Langfuse and MLflow SHALL own isolated PostgreSQL services selected only by their optional observability profiles. Every PostgreSQL 18 service SHALL use a major-versioned named volume mounted at `/var/lib/postgresql`.

#### Scenario: Compose services use the latest approved PostgreSQL 18 patch

- **GIVEN** the rendered owner-defined agent-core project and selected observability profile
- **WHEN** PostgreSQL service images and volumes are inspected
- **THEN** runtime, Langfuse, and MLflow PostgreSQL services SHALL use `postgres:18.6-trixie`
- **AND** each selected volume name SHALL include PostgreSQL major version 18
- **AND** no selected service SHALL use `postgres:18.6-alpine`, `postgres:16`, or `postgres:18.4-trixie`

#### Scenario: Agent-harness integration uses the same baseline

- **GIVEN** the agent-harness PostgreSQL integration fixture
- **WHEN** its container image is selected
- **THEN** it SHALL use `postgres:18.6-trixie`

#### Scenario: Existing data is not implicitly migrated

- **GIVEN** existing PostgreSQL volumes
- **WHEN** image flavor, ownership, or volume identity changes
- **THEN** the deployment SHALL preserve every old volume until its data is classified and migration or disposal is explicitly approved
- **AND** it SHALL not silently delete, rewrite, or attach cross-version application data

#### Scenario: PostgreSQL 18.6 is verified before promotion

- **GIVEN** the approved image tag and selected versioned volume
- **WHEN** infrastructure promotion is evaluated
- **THEN** image availability, required architectures, Compose syntax, `pg_isready`, `SHOW server_version`, fresh initialization, and existing-volume compatibility SHALL be verified
- **AND** repository test and static-analysis gates SHALL pass
