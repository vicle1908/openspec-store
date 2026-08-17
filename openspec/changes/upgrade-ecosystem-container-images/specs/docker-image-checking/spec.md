# docker-image-checking — ADDED Requirements

## ADDED Requirements

### Requirement: DIC-006: Exact release pins for stateful infrastructure

The system SHALL use exact semver or immutable release tags for stateful infrastructure images (databases, message brokers, observability backends). Floating tags SHALL NOT be used for these services except where upstream publishes no immutable tag and a documented exception is approved.

#### Scenario: Stateful services use exact release tags

- **GIVEN** a Compose service using a stateful image (PostgreSQL, ClickHouse, Redis, MinIO, Kafka)
- **WHEN** the image tag is inspected
- **THEN** it SHALL use an exact semver or release tag
- **AND** no service SHALL use `latest` or a mutable major-only tag

#### Scenario: Documented floating-tag exception

- **GIVEN** an upstream image that publishes no immutable release tag
- **WHEN** a floating tag is used
- **THEN** the rationale SHALL be documented in the Compose file comments
- **AND** the image digest SHALL be recorded
- **AND** architecture verification SHALL be performed for `linux/amd64` and `linux/arm64`

### Requirement: DIC-007: Coupled service version parity

The system SHALL ensure that coupled service pairs (e.g., Langfuse server + worker) use the exact same release version at all times.

#### Scenario: Coupled services match

- **GIVEN** a Compose file with coupled service images (e.g., `langfuse` + `langfuse-worker`)
- **WHEN** versions are inspected
- **THEN** both SHALL use the same exact version tag
- **AND** upgrading one SHALL require upgrading the other atomically

### Requirement: DIC-008: Multi-architecture manifest verification

The system SHALL verify that pinned images support the required architectures (`linux/amd64` and `linux/arm64`) before promotion.

#### Scenario: Architecture check passes

- **GIVEN** a pinned image tag
- **WHEN** the multi-architecture manifest is inspected
- **THEN** both `linux/amd64` and `linux/arm64` SHALL be present
- **AND** the verification SHALL be recorded in the commit evidence

#### Scenario: Architecture check fails

- **GIVEN** a pinned image tag missing a required architecture
- **WHEN** the multi-architecture manifest is inspected
- **THEN** the upgrade SHALL be blocked until an alternative image is found
- **AND** the failure SHALL be reported to the user

### Requirement: DIC-009: Major-version migration evidence

The system SHALL produce migration evidence before upgrading any stateful image across a major version boundary.

#### Scenario: Major-version upgrade requires migration plan

- **GIVEN** a major-version image upgrade (e.g., Langfuse 3→4, Redis 7→8, PostgreSQL 16→18)
- **WHEN** the upgrade is implemented
- **THEN** a migration plan SHALL be documented
- **AND** the upgrade SHALL be tested with fresh volumes first
- **AND** the upgrade SHALL be tested with existing volumes (if applicable)
- **AND** the data preservation strategy SHALL be documented
