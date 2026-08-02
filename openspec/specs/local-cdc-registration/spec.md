# Local CDC Registration

## Purpose

Define canonical, observable, fail-closed local Debezium connector
registration and outbox-to-Kafka acceptance requirements.

## Requirements

### Requirement: Every local CDC owner has a canonical connector
The local platform SHALL define one canonical Debezium PostgreSQL connector for
each CDC-owning service: order, payment, inventory, shipping, notification,
customer, and catalog. Each connector MUST identify exactly the service-owned
outbox table, publication, replication slot, database credentials, and target
Kafka topic without capturing another service's tables.

#### Scenario: Static connector ownership validation passes
- **WHEN** local deployment validation inspects every canonical connector
- **THEN** each table include list, publication, slot, and topic matches the owning service migration and no connector captures a peer schema

#### Scenario: Missing service connector fails validation
- **WHEN** a CDC-owning service has an outbox requirement but no canonical connector configuration
- **THEN** local deployment validation exits non-zero and identifies the service and missing artifact

### Requirement: Connector registration is ordered and idempotent
The local platform SHALL register required connectors only after Postgres,
Kafka, Debezium REST readiness, service migrations, and topic provisioning are
ready. Registration MUST be safe to retry, MUST preserve existing offsets for
a compatible connector, MUST treat an already-equivalent connector as
success, and MUST fail closed only after a bounded readiness budget that
accommodates documented Debezium plugin discovery. A timeout MUST retain
connector and prerequisite diagnostics.

#### Scenario: Absent connector is created
- **WHEN** all prerequisites are healthy and the required connector does not exist
- **THEN** infrastructure initialization creates it from the canonical configuration and waits until its connector and task states are running

#### Scenario: Debezium is slow but converges
- **WHEN** Debezium remains in plugin discovery longer than the normal probe interval but becomes healthy before the bounded budget expires
- **THEN** registration waits, creates or verifies the connector, and exits zero

#### Scenario: Equivalent connector reruns
- **WHEN** initialization is rerun after a connector is already running with the canonical configuration
- **THEN** initialization reports `unchanged` and exits zero without deleting offsets or recreating the connector

#### Scenario: Readiness budget is exhausted
- **WHEN** Debezium or another prerequisite remains unavailable through the bounded budget
- **THEN** initialization exits non-zero and retains the last health response, logs, and prerequisite state

### Requirement: Connector configuration preserves safe local delivery
Every local connector SHALL use `pgoutput`, an explicitly owned publication and
slot, `publication.autocreate.mode=disabled`, an exact outbox table include
list, an Outbox Event Router route field that exists in the owned table,
explicit topic routing, heartbeats, JSON-compatible value conversion, and
idempotent Kafka producer settings. Connector credentials MUST come from
deployment configuration and MUST NOT be embedded as repository secrets.

#### Scenario: Unsafe connector setting is rejected
- **WHEN** a connector omits its publication, enables publication auto-creation, captures a wildcard peer table, or disables required producer idempotence
- **THEN** static deployment validation exits non-zero with the connector and invalid setting

#### Scenario: Outbox route field is absent from the owned table
- **WHEN** a connector relies on a default or explicit Outbox Event Router field that its owning migration does not declare
- **THEN** static deployment validation exits non-zero before the connector can fail on its first emitted row

#### Scenario: Repository connector contains a credential
- **WHEN** validation detects a literal database password, API token, or other deployment secret in canonical connector JSON
- **THEN** validation exits non-zero and identifies the secret-bearing field without printing its value

### Requirement: Local acceptance proves outbox-to-Kafka delivery
Local acceptance SHALL prove more than connector existence. For every newly
wired service connector it MUST retain connector/task status and MUST verify a
uniquely identified representative committed outbox event is observable on the
configured Kafka topic within a bounded interval. When both HTTP and Nexus
dispatch paths are enabled, acceptance SHALL verify a uniquely identified
representative event from each path and MUST retain the outbox identity, topic,
partition or offset evidence, and connector/task state.

#### Scenario: Representative event is delivered
- **WHEN** a service transaction commits a uniquely identified outbox event
- **THEN** the connector publishes an event with that identity to the configured topic within the acceptance timeout and evidence records the service, connector, topic, and result

#### Scenario: Connector runs but delivery is broken
- **WHEN** connector status is running but the representative event is not observed before timeout
- **THEN** local acceptance fails and retains connector status, task trace, outbox row, publication/slot, and Kafka diagnostics

#### Scenario: Nexus event advances Kafka
- **WHEN** a Nexus dispatch commits a uniquely identified outbox event
- **THEN** the matching event is observable on `shipping.events.v1` within the acceptance timeout and evidence records the Kafka offset

#### Scenario: HTTP and Nexus paths are equivalent
- **WHEN** one representative dispatch is issued through HTTP and one through Nexus
- **THEN** both produce versioned outbox facts and observable topic events without duplicate side effects

### Requirement: Local CDC readiness is observable and fail-closed
A local service that claims CDC-backed publication SHALL NOT report complete
startup readiness until its required connector registration has succeeded.
Connector absence or failure MUST be visible through infrastructure-init logs
and retained deployment evidence.

#### Scenario: Connector task fails after registration
- **WHEN** a required connector or connector task enters failed state
- **THEN** the local readiness/acceptance gate becomes unsuccessful and reports the owning service plus Debezium trace without exposing credentials

#### Scenario: All local connectors converge
- **WHEN** every required connector and task is running and representative delivery checks pass
- **THEN** the local CDC acceptance summary reports success independently from cloud deployment and CI/CD readiness
