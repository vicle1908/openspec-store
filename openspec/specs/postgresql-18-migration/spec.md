# postgresql-18-migration

## Purpose

PostgreSQL migration is a staged, operator-authorized handoff from preserved source volumes to PostgreSQL 18.6 owner-managed targets. A fresh start uses a new PostgreSQL-18-versioned volume only after data classification; retained data requires writer quiescence, an immutable dump and checksum, staged restore with schema, representative-data, and consumer verification, one bounded DSN or network-alias cutover, preserved source state, and rollback and retirement evidence.

## Requirements

### Requirement: PGM-001: Fresh Start

The system SHALL start PostgreSQL 18.6 on a new PostgreSQL-18-versioned volume when an operator explicitly selects a fresh start. Existing PostgreSQL volumes MUST remain preserved and detached until their data is classified, any required migration or backup succeeds, and a separate retirement action is explicitly authorized.

#### Scenario: Fresh Start

- **GIVEN** an existing PostgreSQL volume classified as disposable with retained classification evidence
- **WHEN** an authorized operator selects a fresh PostgreSQL 18.6 start
- **THEN** the system SHALL stop the old owning project
- **AND** it SHALL preserve and detach the old volume
- **AND** it SHALL create a new PostgreSQL-18-versioned volume
- **AND** it SHALL initialize and verify the required databases on PostgreSQL 18.6

#### Scenario: Existing data classification is absent

- **GIVEN** an existing PostgreSQL volume whose ownership or retention class is unknown
- **WHEN** a fresh start is requested
- **THEN** the system SHALL fail closed before volume deletion or replacement
- **AND** it SHALL report the missing ownership, backup, or authorization evidence

#### Scenario: Old volume retirement is authorized later

- **GIVEN** a preserved old volume and a passing replacement deployment
- **WHEN** an operator separately authorizes retirement after reviewing ownership, backup, migration, rollback, and acceptance evidence
- **THEN** only that exact approved volume MAY be removed
- **AND** the removal result SHALL be retained in the deployment manifest

### Requirement: PGM-002: Service Verification

The system SHALL verify all services can connect to PostgreSQL 18.6 after fresh start.

#### Scenario: Verify Services
Given PostgreSQL 18.6 running fresh
When all services are started
Then they shall connect successfully
And all operations shall work correctly
And database shall be initialized by services

### Requirement: PGM-003: Data Initialization

The system SHALL initialize fresh data through service startup.

#### Scenario: Initialize Data
Given PostgreSQL 18.6 fresh
When services start
Then they shall run database migrations
And they shall initialize required data
And they shall verify data integrity

### Requirement: PGM-004: Rollback Capability

The system SHALL support rollback to the preserved prior PostgreSQL image and volume whenever fresh-start or migration acceptance fails. Rollback MUST NOT depend on recreating data that the deployment deleted during the failed attempt.

#### Scenario: Rollback

- **GIVEN** the prior PostgreSQL volume remains preserved
- **WHEN** PostgreSQL 18.6 initialization, migration, or consumer verification fails
- **THEN** the operator SHALL be able to stop the candidate project and restart the prior image against its original volume
- **AND** required services SHALL verify connectivity before rollback is declared successful

#### Scenario: Prior volume was already retired

- **GIVEN** rollback is requested after the prior volume was removed
- **WHEN** no verified restorable backup exists
- **THEN** rollback SHALL be reported blocked
- **AND** the system SHALL not claim recovery capability

### Requirement: Retained-data migration is staged and writer-free

A retained-data migration SHALL require explicit operator authorization and a per-database source-to-target map. The system MUST quiesce all source writers, capture an immutable dump and checksum plus the prior image, configuration, and restart recipe, restore into a disposable staged target, verify schema and representative data, probe every consumer, and perform one bounded DSN or network-alias cutover while preserving the source. It SHALL record phase states and SHALL reject partial targets without restoring in place.

#### Scenario: Authorized retained-data cutover succeeds

- **WHEN** the operator approves a retained-data migration and all writers are quiesced
- **THEN** the dump checksum, staged restore, schema and data verification, consumer probes, cutover, and post-cutover probes SHALL pass in order
- **AND** the manifest SHALL retain every phase result and the prior restart recipe
- **AND** the source volume SHALL remain intact for rollback

#### Scenario: Dump or staged restore fails

- **WHEN** dump creation, checksum verification, restore, schema verification, or consumer probing fails
- **THEN** the staged target SHALL be rejected
- **AND** consumers SHALL remain on or return to the prior source using the retained recipe
- **AND** no in-place restore or source retirement SHALL occur

#### Scenario: Migration lacks operator authorization

- **WHEN** retained data is discovered but no explicit migration or disposable-data decision is authorized
- **THEN** the migration SHALL stop before writer quiescence or target mutation
- **AND** the resource SHALL remain preserved and reported as a decision gate
