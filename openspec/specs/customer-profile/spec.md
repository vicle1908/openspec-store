# customer-profile Specification

## Purpose
The platform implements Customer aggregate The customer service SHALL own a `Customer` aggregate with identity `customer_id` (ULID), fields `email` (validated, unique per environment), `display_name`, `default_shipping_address_id`, `default_billing_address_id`, `status` (on
## Requirements
### Requirement: Customer aggregate

> **Status**: IMPLEMENTED. Customer aggregate exists in customer-service/internal/domain with ULID identity and status lifecycle.

The customer service SHALL own a `Customer` aggregate with identity `customer_id` (ULID), fields `email` (validated, unique per environment), `display_name`, `default_shipping_address_id`, `default_billing_address_id`, `status` (one of `active`, `suspended`, `soft_deleted`), `created_at`, `updated_at`, and `version`. The aggregate SHALL be persisted in the `customers` table within the `customer` schema. Each customer SHALL own zero or more `Address` aggregates keyed by `address_id` (ULID) with `customer_id`, `kind` (`shipping` or `billing`), `line1`, `line2` (optional), `city`, `region`, `postal_code`, `country`, and `is_default_*` flags.

#### Scenario: Customer is created via HTTP
- **WHEN** the API receives `POST /api/v1/customers` with a valid `email` and `display_name`
- **THEN** a `Customer` aggregate is created in state `active` with a ULID and the response is `201 Created` with the customer's ID

#### Scenario: Customer is created via event
- **WHEN** the consumer reads a `CustomerRegistered` external event
- **THEN** a `Customer` aggregate is created in state `active` using the event's `customer_id` as the aggregate ID

#### Scenario: Duplicate email is rejected
- **WHEN** the API receives a request to create a customer with an `email` that already exists
- **THEN** the response is `409 Conflict` with code `email_already_exists`

### Requirement: Email and address validation

> **Status**: IMPLEMENTED. Email and address validation exists in customer-service adapters.

The service SHALL validate `email` against RFC 5321 syntax on create and update; an invalid email returns `400 Bad Request`. The service SHALL validate address fields against ISO 3166-1 alpha-2 country codes; an unknown country returns `400 Bad Request`. The service SHALL validate `postal_code` against the country-specific regex; an invalid postal code returns `400 Bad Request`.

#### Scenario: Invalid email is rejected
- **WHEN** a customer create request includes `email=not-an-email`
- **THEN** the response is `400 Bad Request` with code `invalid_email`

#### Scenario: Invalid country is rejected
- **WHEN** an address create request includes `country=ZZ`
- **THEN** the response is `400 Bad Request` with code `invalid_country`

### Requirement: Address management

> **Status**: IMPLEMENTED. Address CRUD operations exist in customer-service with default address handling.

A customer SHALL be able to add, update, and remove addresses via the API. Removing the `default_shipping_address_id` or `default_billing_address_id` SHALL require that the customer first assigns a new default; otherwise the request returns `409 Conflict` with code `cannot_remove_default_address`. A customer SHALL have at most one default address per kind.

#### Scenario: Removing the default shipping address is rejected without replacement
- **WHEN** an API request removes the customer's `default_shipping_address_id` and no replacement is provided
- **THEN** the response is `409 Conflict` with code `cannot_remove_default_address`

#### Scenario: Replacing the default shipping address succeeds
- **WHEN** an API request removes the default shipping address and assigns a new one in the same request
- **THEN** both changes are persisted atomically

### Requirement: Soft delete and retention

> **Status**: IMPLEMENTED. Soft-delete with email placeholder exists; retention workflow may be partial.

A customer SHALL be soft-deletable: the aggregate transitions to `soft_deleted` and the `email` is replaced with a placeholder of the form `deleted-<ulid>@deleted.local`. The placeholder email SHALL be unique per environment. The customer SHALL remain in soft-deleted state for the retention window (default 30 days) and SHALL then be transitioned to `purged` by the GDPR purge workflow (see `customer-gdpr-export` Requirement 2). Once purged, the customer's row is cryptographically erased and unreadable. `DELETE /api/v1/customers/{id}` is the synchronous soft-delete trigger; it is the only soft-delete entry point and SHALL enqueue the purge workflow via the platform's Temporal worker in the same transaction as the state transition.

#### Scenario: Soft delete is reversible
- **WHEN** an operator runs `customer unsuspend --id <customer-id>` against a `suspended` customer
- **THEN** the customer transitions back to `active`

#### Scenario: Soft delete is irreversible after retention
- **WHEN** a customer's retention timer expires
- **THEN** the GDPR purge workflow transitions the customer to `purged` and the row is unreadable

#### Scenario: DELETE /customers/{id} soft-deletes and enqueues the purge workflow
- **WHEN** the API receives `DELETE /api/v1/customers/{id}` against an `active` or `suspended` customer
- **THEN** the customer's status becomes `soft_deleted`, the email is replaced with the placeholder, and a `CustomerPurgeWorkflow` Temporal workflow is started on task queue `customer.purge.v1` with `WorkflowID = "customer-purge-<customer-id>"`

#### Scenario: Customer is suspended by an operator
- **WHEN** an operator runs `customer suspend --id <customer-id>` against an `active` customer
- **THEN** the customer transitions to `suspended` and a `CustomerStatusChanged` event with `status=suspended` is published

#### Scenario: Customer is unsuspended by an operator
- **WHEN** an operator runs `customer unsuspend --id <customer-id>` against a `suspended` customer
- **THEN** the customer transitions back to `active` and a `CustomerStatusChanged` event with `status=active` is published

### Requirement: Public REST API

> **Status**: IMPLEMENTED. REST endpoints exist in customer-service/internal/adapters/http with idempotency and concurrency control.

The service SHALL expose `POST /api/v1/customers`, `GET /api/v1/customers/{id}`, `PATCH /api/v1/customers/{id}`, `DELETE /api/v1/customers/{id}` (soft delete), `POST /api/v1/customers/{id}/addresses`, `GET /api/v1/customers/{id}/addresses`, `PATCH /api/v1/customers/{id}/addresses/{address_id}`, `DELETE /api/v1/customers/{id}/addresses/{address_id}`. Every mutating endpoint SHALL accept an `Idempotency-Key` header. The service SHALL return `404 Not Found` for unknown customer IDs and `409 Conflict` for concurrency conflicts. The service SHALL NOT expose address data of one customer to another customer; cross-tenant access is rejected at the application boundary.

#### Scenario: Idempotent customer create
- **WHEN** two `POST /api/v1/customers` requests carry the same `Idempotency-Key`
- **THEN** only one customer is created and the second response returns the first customer's ID with `200 OK`

#### Scenario: Unknown customer returns 404
- **WHEN** the API receives `GET /api/v1/customers/<unknown-ulid>`
- **THEN** the response is `404 Not Found`

#### Scenario: Concurrency conflict returns 409
- **WHEN** two `PATCH /api/v1/customers/{id}` requests race with the same `version`
- **THEN** the first succeeds and the second response is `409 Conflict` with code `concurrency_conflict`

### Requirement: Customer reference snapshot in Order

> **Status**: IMPLEMENTED. Reference endpoint exists; Order service captures customer snapshot.

The customer service SHALL expose `GET /api/v1/customers/{id}/reference` returning `{customer_id, display_name, status}` so the Order service can capture a reference snapshot when creating an order. The endpoint SHALL return `404 Not Found` for soft-deleted customers so the Order service treats them as non-existent.

#### Scenario: Order captures a customer reference snapshot
- **WHEN** the Order service calls `GET /customer-service/api/v1/customers/{id}/reference` before creating an order
- **THEN** the response includes `customer_id`, `display_name`, and `status`

#### Scenario: Soft-deleted customer returns 404 to Order
- **WHEN** the Order service calls the reference endpoint for a soft-deleted customer
- **THEN** the response is `404 Not Found` and the Order service surfaces a typed error to the API caller

### Requirement: Event publication

> **Status**: LOCAL-VERIFIED. Customer events use the transactional outbox, and
> the canonical connector plus idempotent Compose/kind registration and retained
> local acceptance prove `customer.outbox` delivery to `customers.events.v1`.
> This status does not claim cloud deployment readiness.

The customer service SHALL publish the events `CustomerRegistered`, `CustomerUpdated`, `CustomerSoftDeleted`, `CustomerPurged`, `CustomerAddressAdded`, `CustomerAddressUpdated`, `CustomerAddressRemoved`, and `CustomerStatusChanged` to the `customers.events.v1` topic. Each event SHALL carry the envelope fields specified by `platform-contracts` and SHALL carry the snapshot fields needed by downstream consumers to maintain their own denormalized views (e.g., Order's `Order.customer_snapshot`).

#### Scenario: CustomerRegistered event is published
- **WHEN** a customer is created
- **THEN** the `customers.events.v1` topic receives a `CustomerRegistered` event with the envelope and the customer snapshot fields

#### Scenario: CustomerUpdated event is published on patch
- **WHEN** a customer's `display_name` is patched
- **THEN** the topic receives a `CustomerUpdated` event with the changed fields and the new version

### Requirement: Kafka best practices for the customer event stream

> **Status**: LOCAL-VERIFIED. The required connector configuration is
> statically validated against the owning migration and a retained local probe
> verifies connector/task, publication/slot, and Kafka delivery state. This
> status does not claim cloud deployment readiness.

The customer service SHALL publish to `customers.events.v1` via the transactional outbox pattern. The Debezium connector configuration SHALL use `plugin.name=pgoutput`, `slot.name=customer_outbox_slot`, `publication.name=customer_outbox_publication`, `publication.autocreate.mode=disabled`, `table.include.list=customer.outbox`, `transforms=outbox`, `transforms.outbox.route.by.field=aggregate_type`, `transforms.outbox.route.topic.replacement=customers.events.v1`, `heartbeat.interval.ms=10000`, `tombstones.on.delete=false`, and `snapshot.mode=no_data`. The customer outbox table SHALL use `REPLICA IDENTITY DEFAULT` (INSERT-only outbox halves WAL write amplification). The Debezium internal producer SHALL configure `enable.idempotence=true`, `compression.type=lz4`, `linger.ms=10`, `batch.size=131072`, `acks=all`, `min.insync.replicas=2`.

#### Scenario: Outbox transaction publishes to Kafka atomically
- **WHEN** the customer service commits a customer update
- **THEN** the same transaction inserts a row into `customer.outbox`; the Debezium connector observes the row within `heartbeat.interval.ms` and publishes the corresponding record to `customers.events.v1`

#### Scenario: Connector restart resumes from last LSN
- **WHEN** the Debezium connector restarts after a crash
- **THEN** it resumes from the LSN recorded in `pg_replication_slots` for `customer_outbox_slot`

#### Scenario: Outbox table cleanup
- **WHEN** the cleanup job runs `DELETE FROM customer.outbox WHERE created_at < now() - interval '7 days'`
- **THEN** the rows are removed without affecting already-published events (consumers reference `event_id` from the envelope, not the outbox row)

### Requirement: Temporal best practices for the GDPR purge workflow

> **Status**: PARTIAL. Temporal integration exists; saga pattern and versioning may be partial.

The `CustomerPurgeWorkflow` SHALL use the platform's `temporal.NewSaga(...)` helper. The workflow SHALL register under `customer.purge.v1` and the worker SHALL be on task queue `customer.purge.v1` with Worker Versioning v2 `DeploymentSeriesName=customer-workflows-v1`. The retention-timer activity SHALL declare `StartToCloseTimeout=60s` and `HeartbeatTimeout=10s` (the timer is a long sleep but emits a heartbeat to keep the slot healthy). The cryptographic-erasure activity SHALL declare `StartToCloseTimeout=30s`. The workflow SHALL use Temporal's Schedule API for the periodic audit retention review (legacy Cron API is forbidden by the architecture test).

#### Scenario: Customer purge worker registers with versioning
- **WHEN** the purge worker starts
- **THEN** it registers under `DeploymentSeriesName=customer-workflows-v1`

#### Scenario: Retention timer activity heartbeats
- **WHEN** the retention-timer activity runs for 30 days
- **THEN** it emits a heartbeat every 10 seconds via `RecordHeartbeat(ctx, RetentionProgress{DaysElapsed: n})`

#### Scenario: Legacy Cron API is rejected
- **WHEN** the architecture test scans the customer-service codebase
- **THEN** any reference to `workflow.NewCronSchedule` fails the build
