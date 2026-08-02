## MODIFIED Requirements

### Requirement: shipping-service owns the shipping Postgres schema and CDC topic

> **Status**: LOCAL-VERIFIED. The canonical shipping connector, exact
> publication and slot, idempotent Compose/kind registration, and a retained
> local acceptance probe prove delivery from `shipping.shipping_outbox` to
> `shipping.events.v1`. This status does not claim cloud deployment readiness.

The `shipping` schema SHALL contain the `shipments`, `shipping_events`,
`shipping_outbox`, `shipping_idempotency_keys`, and `dispatch_operations`
tables. `dispatch_operations` SHALL be the sole durable authority for dispatch
operation identity, canonical request fingerprint, claim state, lease
ownership, attempt metadata, provider idempotency key, and retained outcome.
The CDC connector SHALL publish every row added to `shipping_outbox` to the
`shipping.events.v1` Kafka topic with at-least-once delivery. The
`deploy/init-scripts/05-shipping-cdc.sql` migration SHALL create the schema,
the tables, the Debezium publication, and the publication slot. Both HTTP
dispatch and Nexus dispatch SHALL commit the shipment mutation and its
versioned integration fact atomically, and SHALL use the same operation ledger.

#### Scenario: shipping-migrate creates the shipping schema

- **WHEN** the `shipping-migrate` container runs `shipping-service migrate up`
- **THEN** the `shipping` schema exists with all five tables, the Debezium
  publication, and the publication slot
- **AND** the migration is safe to rerun without losing retained operation
  outcomes

#### Scenario: HTTP dispatch creates an outbox fact

- **WHEN** `POST /api/v1/shipments` successfully dispatches a new shipment
- **THEN** the same transaction contains one `shipments` row, one completed
  `dispatch_operations` row, and one versioned `shipping_outbox` row for the
  dispatch fact

#### Scenario: Nexus dispatch creates an outbox fact

- **WHEN** the Shipping Nexus operation successfully dispatches a new shipment
- **THEN** the same transaction contains one `shipments` row, one completed
  `dispatch_operations` row, and one versioned `shipping_outbox` row for the
  dispatch fact

#### Scenario: Outbox event lands on shipping.events.v1

- **WHEN** either dispatch entry point commits a uniquely identified outbox
  event
- **THEN** the Debezium connector publishes that event to
  `shipping.events.v1` within the bounded local acceptance interval

### Requirement: shipping-service exposes a REST API for shipments

The `shipping-api` container SHALL serve the following REST endpoints on
`:8085`:

- `POST /api/v1/shipments` — dispatches a new shipment. Body:
  `{ contract_version, order_id, address: { ... }, carrier: "stub|ups|fedex", idempotency_key }`.
  The endpoint SHALL map `idempotency_key` to a stable operation identity and
  return `201 Created` with
  `{ contract_version, shipment_id, status: "dispatched", tracking_number, carrier }`
  for both a new dispatch and an exact retained replay.
- `POST /api/v1/shipments/{id}/cancel` — cancels a dispatched shipment. The
  endpoint SHALL call `ShippingProvider.Cancel` with the tracking number; the
  carrier's cancellation confirmation is recorded. Response: `200 OK` with
  `{ contract_version, shipment_id, status: "cancelled" }`. Note: the
  order-worker's saga does NOT call this endpoint (no `CancelShipping` activity
  is registered; see `order-temporal-workflow` spec).
- `POST /api/v1/shipments/{id}/complete` — marks a shipment as delivered
  (typically called as a carrier webhook). Body:
  `{ delivered_at, signature_url? }`. Response: `200 OK` with
  `{ contract_version, shipment_id, status: "delivered" }`.
- `GET /api/v1/shipments/{id}` — returns the current state of the shipment.
- `GET /health/live`, `GET /health/ready`, `GET /health/startup`, and
  `GET /metrics`.

The read endpoint SHALL return the persisted shipment state for an existing
identifier and a stable `404` problem response for an unknown identifier. The
startup endpoint SHALL return `503` until setup and its database check are
complete and `200` thereafter. Every write SHALL preserve the idempotency
contract and SHALL map the ledger outcomes to stable public errors: a
fingerprint conflict SHALL return `409`, active operation ownership SHALL
return `409` with `Retry-After`, reconciliation or transient infrastructure
failures SHALL return the documented retryable status, and contract,
authorization, and domain failures SHALL remain non-retryable.

#### Scenario: Shipment dispatch is idempotent on idempotency_key

- **WHEN** `POST /api/v1/shipments` is called twice with the same
  `idempotency_key` and request body
- **THEN** the second call returns `201 Created` with the original response
- **AND** no second row is inserted into `shipments` or `shipping_outbox`

#### Scenario: Conflicting idempotency input is rejected

- **WHEN** the same `idempotency_key` is submitted with a different canonical
  request fingerprint
- **THEN** the API returns `409` with the stable fingerprint-conflict code
- **AND** no carrier, Shipment, operation, or outbox mutation is performed

#### Scenario: Concurrent matching dispatch is reported safely

- **WHEN** two requests for the same idempotency key arrive while the first
  request owns a live lease
- **THEN** one request completes the dispatch and the other returns
  `operation_in_progress` with `Retry-After`
- **AND** a retry after completion returns the exact retained `201` response

#### Scenario: Shipment dispatch uses the configured ShippingProvider

- **WHEN** `POST /api/v1/shipments` is called with `carrier: "stub"`
- **THEN** the `stub` adapter generates a deterministic tracking number
  `STUB-<shipment_id>` and records one dispatch
- **AND** no external HTTP call to a real carrier is made

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

- **WHEN** migrations, topic provisioning, connector registration, worker
  setup, or the database check is incomplete
- **THEN** `/health/startup` returns `503`
- **AND WHEN** all required setup and database checks have completed
- **THEN** `/health/startup` returns `200`

#### Scenario: HTTP replay does not duplicate

- **WHEN** the same HTTP dispatch idempotency key is submitted twice
- **THEN** both responses identify the same shipment and exactly one shipment,
  one completed dispatch operation, and one dispatch outbox fact exist

### Requirement: ShippingProvider port abstracts the carrier integration

The `ports.ShippingProvider` interface SHALL define
`Dispatch(ctx, DispatchRequest) (DispatchResponse, error)` and
`Cancel(ctx, TrackingNumber) error`. The `stub` adapter SHALL return
deterministic tracking numbers and SHALL record calls in-memory for testing
without data races when used by API and Worker goroutines concurrently. The
`ups` adapter SHALL call the UPS API (stubbed in local dev, real in production).
The `shipping-api` container SHALL load the configured adapter from the
`SHIPPING_PROVIDER` env var (default `stub`). The `ShippingProvider` port SHALL
be the only way the application layer interacts with carriers; the application
layer SHALL NOT import any carrier SDK directly.

#### Scenario: shipping-service uses the stub adapter in local dev

- **WHEN** the `shipping-api` container starts with `SHIPPING_PROVIDER=stub`
- **THEN** the `stub` adapter is wired in
- **AND** `POST /api/v1/shipments` returns a tracking number in the `STUB-<id>`
  format

#### Scenario: Concurrent stub calls are safe

- **WHEN** concurrent goroutines execute, look up, cancel, and snapshot calls
  on one stub adapter
- **THEN** the adapter returns consistent idempotent results without a race
- **AND** `go test -race` reports no data race

#### Scenario: Application layer does not import a carrier SDK

- **WHEN** the architecture test scans
  `services/shipping-service/internal/application/` for forbidden imports
- **THEN** the test fails if any import path matches a carrier SDK (for
  example, `github.com/ups/shipping-sdk` or `github.com/fedex/ship-api`)
- **AND** the test passes if the application layer only imports the local
  `ports` package

### Requirement: Shipping dispatch is idempotent and uses stable operation_id

The `ShippingDispatchActivity` SHALL derive a stable `operation_id` from the
Workflow identity using `platformtemporal.OperationIDFor(workflowID,
"shipping.dispatch")` and SHALL pass the canonical request fingerprint to the
Shipping application command. The activity and HTTP handler SHALL use the
`dispatch_operations` ledger rather than a Shipment column as the source of
truth. Claim, lease acquisition, reconciliation, finalization, and terminal
transitions SHALL use compare-and-swap ownership so a stale worker cannot
perform a second provider call or regress a terminal operation.

#### Scenario: Shipping dispatch is idempotent across retries

- **WHEN** `ShippingDispatchActivity` is invoked twice with the same operation
  identity and fingerprint and the first invocation succeeded
- **THEN** the second invocation observes the retained ledger result and
  returns it without performing a second dispatch

#### Scenario: Different fingerprints do not share an operation

- **WHEN** the same operation identity is invoked with a different request
  fingerprint
- **THEN** the application returns a typed fingerprint conflict before the
  carrier call
- **AND** the existing Shipment, operation result, and outbox count remain
  unchanged

#### Scenario: Stale finalization cannot regress state

- **WHEN** a worker with an expired lease attempts to mark a completed or
  definitively failed operation as reconciling
- **THEN** the compare-and-swap rejects the transition
- **AND** the terminal state and retained outcome remain unchanged
