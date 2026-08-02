## ADDED Requirements

### Requirement: Product aggregate
The catalog service SHALL own a `Product` aggregate with identity `product_id` (ULID), fields `sku` (unique per environment), `display_name`, `description`, `status` (one of `draft`, `active`, `archived`), `category_id`, `attribute_set` (key-value map constrained by an attribute schema), `created_at`, `updated_at`, and `version`. The aggregate SHALL be persisted in the `products` table within the `catalog` schema. A product MAY have variants via the `ProductVariant` child aggregate with `variant_id` (ULID), `sku` (unique per environment), `display_name`, and `attribute_set`.

#### Scenario: Product is created in draft state
- **WHEN** `POST /api/v1/products` is called with a valid payload
- **THEN** a `Product` aggregate is created in state `draft` with a ULID

#### Scenario: Product transitions to active
- **WHEN** `POST /api/v1/products/{id}/activate` is called on a `draft` product
- **THEN** the product transitions to `active` and a `ProductActivated` event is published

#### Scenario: Archived product cannot be reactivated
- **WHEN** `POST /api/v1/products/{id}/activate` is called on an `archived` product
- **THEN** the response is `409 Conflict` with code `invalid_transition`

### Requirement: Variant management
A product SHALL be able to add, update, and remove variants. Removing a variant SHALL require that the variant has no open order references; otherwise the response is `409 Conflict`. A variant SHALL have its own `sku` and SHALL NOT inherit its parent's `sku`.

#### Scenario: Variant add succeeds
- **WHEN** `POST /api/v1/products/{id}/variants` is called with a unique `sku`
- **THEN** a `ProductVariant` is created and a `ProductVariantAdded` event is published

#### Scenario: Variant remove fails when order references exist
- **WHEN** an order references the variant
- **THEN** `DELETE /api/v1/products/{id}/variants/{variant_id}` returns `409 Conflict` with code `variant_in_use`

### Requirement: Public REST API
The service SHALL expose `POST /api/v1/products`, `GET /api/v1/products/{id}`, `PATCH /api/v1/products/{id}`, `POST /api/v1/products/{id}/activate`, `POST /api/v1/products/{id}/archive`, and the variant sub-resource routes. The list endpoint SHALL support pagination via `?limit=N&cursor=<token>` and SHALL return `next_cursor` for follow-up requests. Every mutating endpoint SHALL accept an `Idempotency-Key` header.

#### Scenario: List pagination
- **WHEN** the API receives `GET /api/v1/products?limit=10&cursor=<token>`
- **THEN** the response includes up to 10 products and a `next_cursor` if more exist

#### Scenario: Idempotent product create
- **WHEN** two `POST /api/v1/products` requests carry the same `Idempotency-Key`
- **THEN** only one product is created

#### Scenario: Unknown product returns 404
- **WHEN** the API receives `GET /api/v1/products/<unknown-ulid>`
- **THEN** the response is `404 Not Found`

### Requirement: Attribute schema enforcement
The service SHALL enforce that every product's `attribute_set` conforms to the `attribute_schema` defined per `category_id`. Unknown attributes return `400 Bad Request`; missing required attributes return `400 Bad Request`; wrong-typed attributes return `400 Bad Request`.

#### Scenario: Unknown attribute is rejected
- **WHEN** a product create request includes an attribute not in the category's schema
- **THEN** the response is `400 Bad Request` with code `unknown_attribute`

#### Scenario: Missing required attribute is rejected
- **WHEN** a product create request omits a required attribute
- **THEN** the response is `400 Bad Request` with code `missing_required_attribute`

### Requirement: Category management
The service SHALL own a `Category` aggregate with `category_id`, `parent_category_id` (nullable, forming a tree), `slug` (unique per environment), `display_name`, and `attribute_schema` (JSON Schema draft 2020-12). Categories SHALL be soft-deletable; products in a soft-deleted category SHALL continue to exist but SHALL be flagged `category_unavailable` in the price quote endpoint.

#### Scenario: Category tree is enforced
- **WHEN** a category's `parent_category_id` would create a cycle
- **THEN** the create request returns `409 Conflict` with code `category_cycle`

#### Scenario: Soft-deleted category flags products
- **WHEN** a price quote is requested for a product in a soft-deleted category
- **THEN** the quote response includes `category_status=deleted`

### Requirement: Event publication
The catalog service SHALL publish `ProductCreated`, `ProductUpdated`, `ProductActivated`, `ProductArchived`, `ProductVariantAdded`, `ProductVariantUpdated`, `ProductVariantRemoved`, `PriceAssigned`, and `PriceChanged` events to the `catalog.events.v1` topic. Each event SHALL carry the envelope fields and a snapshot suitable for downstream consumers (Order, Reporting, Notification).

#### Scenario: PriceAssigned is published on first price assignment
- **WHEN** a price is assigned to a product for the first time
- **THEN** the topic receives `PriceAssigned` with the product snapshot and the price snapshot

#### Scenario: PriceChanged is published on price update
- **WHEN** an existing price is updated
- **THEN** the topic receives `PriceChanged` with the old and new price snapshots

### Requirement: Kafka best practices for the catalog event stream
The catalog service SHALL publish to `catalog.events.v1` via the transactional outbox pattern. The Debezium connector configuration SHALL mirror the customer-service pattern: `slot.name=catalog_outbox_slot`, `publication.name=catalog_outbox_publication`, `transforms.outbox.route.topic.replacement=catalog.events.v1`, `heartbeat.interval.ms=10000`, `REPLICA IDENTITY DEFAULT` on `catalog.outbox`. The connector SHALL be configured with `transforms.outbox.route.by.field=aggregate_type` so events for `Product`, `ProductVariant`, `Category`, and `Price` aggregates all flow into the same topic with the `aggregate_type` field preserved for downstream filtering. Catalog consumers (Order, Reporting) SHALL subscribe via the platform's Kafka harness with the same cooperative-sticky + static-membership configuration.

#### Scenario: Aggregate-type routing preserves the source type
- **WHEN** a `PriceAssigned` event is committed to `catalog.outbox`
- **THEN** the resulting Kafka record has `aggregate_type=Price` and the envelope's `aggregate_id` is the price's ULID

#### Scenario: Multiple aggregate types share the topic
- **WHEN** the catalog service publishes events for `Product`, `Variant`, and `Price` aggregates
- **THEN** all three flow to `catalog.events.v1` keyed by their respective aggregate IDs

#### Scenario: Outbox cleanup is safe
- **WHEN** the cleanup job runs `DELETE FROM catalog.outbox WHERE created_at < now() - interval '7 days'`
- **THEN** cleanup does not affect the catalog's source-of-truth tables (`catalog.products`, `catalog.prices`)

### Requirement: Temporal best practices for the catalog service
The catalog service SHALL NOT use Temporal workflows for product CRUD operations (they are synchronous REST calls). The catalog service SHALL use Temporal ONLY when a long-running operation is required: bulk catalog import, scheduled price-window transitions (a Temporal Schedule activates a workflow at the price window's `starts_at` and `ends_at`), or large-scale variant migration. When Temporal is used, the workflow SHALL follow the platform's Worker Versioning v2 + deterministic-API rules from `platform-temporal-versioning`. Catalog workflows SHALL use the task queue `catalog.admin.v1`.

#### Scenario: Bulk import uses a Temporal workflow
- **WHEN** an operator triggers a bulk catalog import of N products
- **THEN** the workflow fans the import into chunks of 100 products per activity and uses the saga pattern so a partial failure can roll back the partially-imported products

#### Scenario: Scheduled price window uses Temporal Schedule API
- **WHEN** a price window's `starts_at` arrives
- **THEN** Temporal fires the workflow that activates the price; the workflow uses the platform's `temporal.NewSchedule(spec, action)` helper (legacy Cron API forbidden)

#### Scenario: Synchronous CRUD does not use Temporal
- **WHEN** the catalog service handles a `POST /api/v1/products` request
- **THEN** the request is processed synchronously in the HTTP handler; no Temporal workflow is started