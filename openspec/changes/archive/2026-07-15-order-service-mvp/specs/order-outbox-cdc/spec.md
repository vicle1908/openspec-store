## ADDED Requirements

### Requirement: Public events use a durable outbox
The service SHALL write one outbox row per public integration event in the same transaction as its aggregate change. The row SHALL contain immutable metadata and a serialized Protobuf payload.

#### Scenario: Order created
- **WHEN** an Order creation transaction commits
- **THEN** the Order row and corresponding outbox row become visible atomically

### Requirement: Debezium publishes only routed outbox records
The Debezium PostgreSQL connector SHALL capture only `public.outbox`, use `pgoutput`, and apply the Outbox Event Router with aggregate ID as the Kafka key.

#### Scenario: Internal table update
- **WHEN** an Order or line-item table is updated without an outbox row
- **THEN** no public Kafka record is produced from that table change

### Requirement: Connector declares a value-converter delegate
The connector configuration SHALL set `value.converter=io.debezium.converters.BinaryDataConverter` together with `value.converter.delegate.converter.type=org.apache.kafka.connect.json.JsonConverter` and `value.converter.delegate.converter.type.schemas.enable=false` so Debezium-internal events (heartbeat, transaction metadata, schema change) serialize as plain JSON instead of failing the connector or stalling emission.

#### Scenario: Debezium emits a heartbeat event
- **WHEN** the connector emits a non-payload event such as a heartbeat or schema change
- **THEN** the configured JsonConverter delegate serializes it and the connector continues running without losing the routed outbox payload stream

### Requirement: Delivery is at least once
The platform SHALL treat Kafka event delivery as at least once and SHALL NOT claim end-to-end exactly-once processing.

#### Scenario: Duplicate Kafka delivery
- **WHEN** a consumer receives an event ID that it has already committed
- **THEN** it acknowledges the record without repeating its business effect

### Requirement: Ordering is aggregate scoped
Order events SHALL be keyed by aggregate ID and SHALL carry aggregate version so consumers can detect gaps or stale events.

#### Scenario: Out-of-order aggregate version
- **WHEN** a consumer observes a version that is not the expected next version for that aggregate
- **THEN** it records the gap and retries or quarantines according to consumer policy

### Requirement: CDC health is observable
The platform SHALL expose or collect replication-slot retained WAL, connector state, publication lag, topic availability, and consumer lag.

#### Scenario: Connector stops
- **WHEN** the Debezium connector enters a failed state
- **THEN** readiness or monitoring reports the failure before retained WAL exceeds its configured threshold
