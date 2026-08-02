## MODIFIED Requirements

### Requirement: Services own data and deployment

Each service SHALL be the sole writer of its authoritative data and SHALL have
independent credentials, migrations, configuration validation, health
endpoints, and deployment lifecycle. Where services share a PostgreSQL
instance, each service SHALL use a non-login owner identity, a runtime identity
limited to required data operations in its owned schema, a migration identity
that can assume only its owner identity, and—when CDC applies—a replication
identity limited to the service's publication and outbox data. Runtime and
migration connection inputs MUST remain distinct.
Canonical ownership acceptance SHALL create mutations through the owning
service API or reviewed migration role and SHALL use a service-scoped read-only
diagnostic identity for database assertions. A shared administrative connection
or direct acceptance-runner mutation MUST NOT establish service ownership.

#### Scenario: Shared local PostgreSQL instance preserves ownership
- **WHEN** multiple services use one PostgreSQL container in local development
- **THEN** each service uses distinct owner, runtime, migration, and applicable CDC identities
- **AND** its runtime identity can access only the tables and sequences required by that service

#### Scenario: Shared local PostgreSQL instance preserves ownership
- **WHEN** multiple services use one PostgreSQL container in local development
- **THEN** each service still uses a distinct database or schema owner and cannot write another service's tables

#### Scenario: Runtime identity attempts cross-schema access
- **WHEN** one service's runtime identity attempts to read or write another service's authoritative schema
- **THEN** PostgreSQL denies the operation and no row changes

#### Scenario: Runtime identity attempts DDL
- **WHEN** a service runtime identity attempts to create, alter, or drop an owned object
- **THEN** PostgreSQL denies the operation while the service migration identity remains able to apply its reviewed migrations

#### Scenario: CDC identity reads a non-owned table
- **WHEN** a service CDC identity attempts to read outside its authorized publication or outbox scope
- **THEN** PostgreSQL denies the operation and connector readiness reports the authorization failure without exposing credentials

#### Scenario: Owning API performs runtime DML
- **WHEN** an authorized service API executes a purposeful command that changes its aggregate and outbox atomically
- **THEN** the service runtime identity performs only the required owned-schema DML
- **AND** read-only evidence links the resulting domain row and outbox event to the originating operation

#### Scenario: Shared administrator performs the acceptance mutation
- **WHEN** canonical acceptance attempts to create a domain or outbox row through a shared administrator, owner, or migration identity
- **THEN** evidence validation rejects the operation as non-representative
