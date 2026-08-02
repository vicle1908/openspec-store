## ADDED Requirements

### Requirement: Debezium connector publishes heartbeats
The Debezium PostgresConnector configured at `order-service/deploy/debezium-connector.json` SHALL declare `heartbeat.interval.ms=10000` and `heartbeat.topics.prefix=order-debezium-heartbeat`. Heartbeats are required so the consumer-lag signal (Burrow, see `platform-kafka-harness` Requirement 7) stays fresh even when the outbox is idle.

#### Scenario: Heartbeat topic is created automatically by the connector
- **WHEN** the connector starts and the outbox has no new rows
- **THEN** the connector publishes a heartbeat message to `order-debezium-heartbeat` every 10000 ms, verified by `kafka-consumer-groups.sh --describe` showing non-zero `CURRENT-OFFSET` on the heartbeat partition

#### Scenario: Heartbeat setting is rejected by make verify-static
- **WHEN** `heartbeat.interval.ms` is removed from `deploy/debezium-connector.json`
- **THEN** `make verify-static` exits non-zero (the verification script greps for the literal `heartbeat.interval.ms`)

### Requirement: Outbox table uses REPLICA IDENTITY DEFAULT
The `outbox` table SHALL be migrated from `REPLICA IDENTITY FULL` to `REPLICA IDENTITY DEFAULT` because the table is INSERT-only — `FULL` doubles the WAL volume for no correctness benefit. The migration is additive-only (a single ALTER statement); it can ship in any release that doesn't yet consume `outbox_delete` events.

#### Scenario: Outbox migration halves WAL volume
- **WHEN** the migration `ALTER TABLE outbox REPLICA IDENTITY DEFAULT` is applied
- **THEN** `pg_stat_replication` shows the WAL flush rate drops to approximately half of the prior `REPLICA IDENTITY FULL` baseline

#### Scenario: Debezium still publishes outbox inserts
- **WHEN** an order is created and the application inserts a row into `outbox`
- **THEN** the Debezium connector still emits the corresponding Kafka message (the migration does not break CDC since outbox is INSERT-only and PK is preserved)

### Requirement: Debezium producer uses idempotent settings
The Debezium producer (`producer.override.*` block in the connector JSON) SHALL be configured with `enable.idempotence=true`, `compression.type=lz4`, `linger.ms=10`, `batch.size=131072`, `acks=all`, `max.in.flight.requests.per.connection=5`, `delivery.timeout.ms=120000` per `platform-kafka-harness` Requirement 11.

#### Scenario: Producer settings are present in the connector JSON
- **WHEN** `jq '.config["producer.override.enable.idempotence"]' deploy/debezium-connector.json` runs
- **THEN** the output is `"true"`

#### Scenario: LZ4 compression is selected
- **WHEN** `jq '.config["producer.override.compression.type"]' deploy/debezium-connector.json` runs
- **THEN** the output is `"lz4"`

### Requirement: Publication autocreate mode is disabled
The connector SHALL declare `"publication.autocreate.mode": "disabled"` so Debezium cannot accidentally create a publication on a database it doesn't own. The platform's `make verify-static` SHALL reject a connector config that omits this setting.

#### Scenario: verify-static rejects missing publication.autocreate.mode
- **WHEN** `"publication.autocreate.mode"` is removed from `deploy/debezium-connector.json`
- **THEN** `make verify-static` exits non-zero with the error `connector config: publication.autocreate.mode must be "disabled"`

## ADDED Requirements

### Requirement: Connector configuration is documented in an ADR
`order-service/docs/adr/0004-debezium-connector-tuning.md` SHALL document the heartbeat interval choice, the REPLICA IDENTITY DEFAULT rationale, the producer override settings, and the publication.autocreate.mode policy.

#### Scenario: ADR exists and is linked from the runbook
- **WHEN** `grep -E 'debezium-connector-tuning' docs/runbooks/debezium-connector.md` runs
- **THEN** the ADR is referenced by the connector runbook

#### Scenario: ADR's "Failure Mode" section names the outbox-replay path
- **WHEN** a reviewer reads the ADR
- **THEN** the section names the operator procedure for replaying missed events when the outbox is ahead of the Kafka consumer group (link to `docs/runbooks/quarantine-replay.md`)