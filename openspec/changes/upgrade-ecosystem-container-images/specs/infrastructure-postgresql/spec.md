# infrastructure-postgresql — ADDED Requirements

## ADDED Requirements

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
