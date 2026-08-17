# infrastructure-postgresql Specification

## Purpose
TBD - created by archiving change postgresql-18-6-infrastructure-baseline. Update Purpose after archive.

## Requirements

### Requirement: PostgreSQL 18.6 is the infrastructure baseline

All first-party PostgreSQL infrastructure used by the agent-core local Compose stack and agent-harness integration tests MUST use the immutable image tag `postgres:18.6-trixie`. Third-party service databases in the same Compose stack (Langfuse and MLflow) SHALL use the same baseline because their documented PostgreSQL backend contracts support PostgreSQL 18.6.

#### Scenario: Compose services use the latest approved PostgreSQL 18 patch

- **GIVEN** the agent-core `compose.yaml`
- **WHEN** PostgreSQL service images are inspected
- **THEN** the primary, scheduler, Langfuse, and MLflow services SHALL all use `postgres:18.6-trixie`
- **AND** no service SHALL use `postgres:16` or `postgres:18.4-trixie`

#### Scenario: Agent-harness integration uses the same baseline

- **GIVEN** the agent-harness PostgreSQL integration fixture
- **WHEN** its container image is selected
- **THEN** it SHALL use `postgres:18.6-trixie`

#### Scenario: Existing data is not implicitly migrated

- **GIVEN** existing PostgreSQL volumes
- **WHEN** the image baseline is upgraded
- **THEN** the upgrade SHALL preserve existing fresh-start/no-data-migration semantics
- **AND** the deployment SHALL not silently delete or rewrite application data

#### Scenario: PostgreSQL 18.6 is verified before promotion

- **GIVEN** the approved image tag
- **WHEN** infrastructure promotion is evaluated
- **THEN** Docker Hub availability, Compose syntax, `pg_isready`, and `SHOW server_version` SHALL be verified
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
