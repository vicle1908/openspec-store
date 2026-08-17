## MODIFIED Requirements

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
