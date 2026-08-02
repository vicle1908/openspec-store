## MODIFIED Requirements

### Requirement: shipping-service owns the shipping Postgres schema and CDC topic

The `shipping` schema SHALL contain the `shipments`, `shipping_events`,
`shipping_outbox`, and `shipping_idempotency_keys` tables. The CDC connector
SHALL publish every row added to `shipping_outbox` to the
`shipping.events.v1` Kafka topic with at-least-once delivery. Both HTTP
dispatch and Nexus dispatch SHALL commit the shipment mutation and its
versioned integration fact atomically. The `deploy/init-scripts/05-shipping-cdc.sql`
migration SHALL create the schema, tables, Debezium publication, and
publication slot.

#### Scenario: HTTP dispatch creates an outbox fact

- **WHEN** `POST /api/v1/shipments` successfully dispatches a new shipment
- **THEN** the same transaction contains one `shipments` row and one
  versioned `shipping_outbox` row for the dispatch fact

#### Scenario: Nexus dispatch creates an outbox fact

- **WHEN** the Shipping Nexus operation successfully dispatches a new
  shipment
- **THEN** the same transaction contains one `shipments` row and one
  versioned `shipping_outbox` row for the dispatch fact

#### Scenario: Outbox event lands on shipping.events.v1

- **WHEN** either dispatch entry point commits a uniquely identified outbox
  event
- **THEN** the Debezium connector publishes that event to `shipping.events.v1`
  within the bounded local acceptance interval

### Requirement: shipping-service exposes a REST API for shipments

The `shipping-api` container SHALL serve `POST /api/v1/shipments`,
`POST /api/v1/shipments/{id}/cancel`,
`POST /api/v1/shipments/{id}/complete`,
`GET /api/v1/shipments/{id}`,
`GET /health/live`, `GET /health/ready`, `GET /health/startup`, and
`GET /metrics` on `:8085`. The read endpoint SHALL return the persisted
shipment state for an existing identifier and a stable `404` problem response
for an unknown identifier. The startup endpoint SHALL return `503` until
service setup is complete and `200` thereafter. Every write SHALL preserve
the existing idempotency contract.

#### Scenario: Existing shipment can be read

- **WHEN** a caller requests `GET /api/v1/shipments/{id}` for a persisted
  shipment
- **THEN** the service returns `200` with the current status, carrier, and
  tracking information

#### Scenario: Unknown shipment is handled

- **WHEN** a caller requests an unknown shipment identifier
- **THEN** the service returns `404` with a typed not-found response and does
  not create or mutate data

#### Scenario: Startup probe reflects setup

- **WHEN** migrations, topic provisioning, connector registration, or worker
  setup is incomplete
- **THEN** `/health/startup` returns `503`
- **AND WHEN** all required setup has completed
- **THEN** `/health/startup` returns `200`

#### Scenario: HTTP replay does not duplicate

- **WHEN** the same HTTP dispatch idempotency key is submitted twice
- **THEN** both responses identify the same shipment and exactly one shipment
  and one dispatch outbox fact exist
