## MODIFIED Requirements

### Requirement: Connector registration is ordered and idempotent

The local platform SHALL register required connectors only after Postgres,
Kafka, Debezium REST readiness, service migrations, and topic provisioning are
ready. Registration MUST be safe to retry, MUST preserve existing offsets for
a compatible connector, MUST treat an already-equivalent connector as
success, and MUST fail closed only after a bounded readiness budget that
accommodates documented Debezium plugin discovery. A timeout MUST retain
connector and prerequisite diagnostics.

#### Scenario: Debezium is slow but converges

- **WHEN** Debezium remains in plugin discovery longer than the normal probe
  interval but becomes healthy before the bounded budget expires
- **THEN** registration waits, creates or verifies the connector, and exits
  zero

#### Scenario: Equivalent connector reruns

- **WHEN** initialization is rerun after a connector is already running with
  the canonical configuration
- **THEN** initialization reports `unchanged` and exits zero without deleting
  offsets or recreating the connector

#### Scenario: Readiness budget is exhausted

- **WHEN** Debezium or another prerequisite remains unavailable through the
  bounded budget
- **THEN** initialization exits non-zero and retains the last health response,
  logs, and prerequisite state

### Requirement: Local acceptance proves outbox-to-Kafka delivery

Local acceptance SHALL prove connector/task status and verify a uniquely
identified representative event from both HTTP and Nexus dispatch paths when
both paths are enabled. It MUST retain the outbox identity, topic, partition or
offset evidence, and connector/task state.

#### Scenario: Nexus event advances Kafka

- **WHEN** a Nexus dispatch commits a uniquely identified outbox event
- **THEN** the matching event is observable on `shipping.events.v1` within the
  acceptance timeout and evidence records the Kafka offset

#### Scenario: HTTP and Nexus paths are equivalent

- **WHEN** one representative dispatch is issued through HTTP and one through
  Nexus
- **THEN** both produce versioned outbox facts and observable topic events
  without duplicate side effects
