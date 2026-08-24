# infrastructure-postgresql Specification

## Purpose
PostgreSQL infrastructure is federated across owner-defined projects: agent-core owns the single shared runtime PostgreSQL 18.6 service, its PostgreSQL-18-versioned volume, initialization, and rollback, while optional Langfuse and MLflow profiles own isolated PostgreSQL 18.6 services and versioned volumes. Existing volumes remain preserved until data is classified and an explicitly authorized fresh start, retained-data migration, or later retirement is evidenced; no deployment step implicitly deletes or rewrites PostgreSQL data.

## Requirements

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

### Requirement: IPG-001: PostgreSQL versioned volume layout

The system SHALL mount PostgreSQL data at `/var/lib/postgresql` for PostgreSQL 18 images, preserving the upstream default layout. Named volumes SHALL include the PostgreSQL major version to prevent accidental cross-version data directory reuse.

#### Scenario: Fresh PostgreSQL 18 initialization

- **GIVEN** a Docker Compose service with `postgres:18.6-trixie`
- **WHEN** the service starts with a fresh named volume (e.g., `langfuse-postgres-18-data`)
- **THEN** PostgreSQL 18 SHALL initialize successfully
- **AND** `SHOW server_version` SHALL return a version string starting with `18.`

#### Scenario: Cross-version volume isolation

- **GIVEN** an existing PostgreSQL 16 named volume
- **WHEN** the Compose service is updated to use `postgres:18.6-trixie` with a different named volume
- **THEN** the old PG16 volume SHALL NOT be mounted or deleted
- **AND** the service SHALL start against the new PG18 volume

### Requirement: IPG-002: PostgreSQL 16→18 migration procedure

The system SHALL document a `pg_dump`/`pg_restore` migration path for environments where PostgreSQL data must be retained across a PG16→18 upgrade.

#### Scenario: Data-preserving migration

- **GIVEN** a PostgreSQL 16 volume with production data
- **WHEN** upgrading to PostgreSQL 18
- **THEN** the procedure SHALL: (1) start PG16 against the original volume, (2) run `pg_dump`, (3) create a fresh PG18 volume, (4) restore with `pg_restore`
- **AND** the original PG16 volume SHALL be preserved intact for rollback

#### Scenario: Disposable metadata fresh start

- **GIVEN** a PostgreSQL volume containing only disposable observability metadata (Langfuse traces, MLflow experiments)
- **WHEN** upgrading PostgreSQL major versions
- **THEN** a fresh PG18 volume MAY be used without migration
- **AND** the decision to discard data SHALL be documented
