## ADDED Requirements

### Requirement: Price authority
The catalog service SHALL be the sole writer of the `prices` table within the `catalog` schema. The Order service SHALL NOT write price rows. Prices are versioned: a price row is immutable once `effective_at` is in the past. Editing a price that is referenced by an order produces a new price row with a new `price_id` (ULID), a new `effective_at`, and the previous price row remains in the table for historical reconstruction.

#### Scenario: Price assignment is immutable
- **WHEN** the service receives a request to edit a price whose `effective_at` is in the past
- **THEN** the service creates a new price row with a new `price_id` and the original is unchanged

#### Scenario: Order service cannot write the prices table
- **WHEN** the architecture tests run with the Order service's module included
- **THEN** the test fails any code path that imports `catalog.prices` directly from the Order service

### Requirement: Price quote endpoint
The service SHALL expose `GET /api/v1/products/{id}/quote` returning `{product_id, variant_id, base_price, currency, tax_class, discount_windows, valid_from, valid_to, snapshot_id}`. The endpoint SHALL evaluate active discount windows and return the effective price (base minus the highest applicable discount). The endpoint SHALL cache quotes for the duration of the order-creation transaction (default 5 seconds) so the Order service can call it multiple times without surprise price changes. The cache key includes `product_id`, `variant_id`, `requested_at`, and `requested_by_service`.

#### Scenario: Quote returns the effective price
- **WHEN** the API receives a quote request for a product with one active discount window
- **THEN** the response includes `base_price` and a discounted `effective_price`

#### Scenario: Quote caches the result for 5 seconds
- **WHEN** two quote requests arrive within 5 seconds with the same cache key
- **THEN** the second response returns the same `snapshot_id` and does not re-evaluate discount windows

#### Scenario: Quote returns 404 for unknown product
- **WHEN** the API receives a quote request for an unknown product ID
- **THEN** the response is `404 Not Found`

#### Scenario: Quote returns 422 for unpriced product
- **WHEN** the API receives a quote request for a product with no price
- **THEN** the response is `422 Unprocessable Entity` with code `no_price_for_product`

### Requirement: Currency and tax class
Every price SHALL carry `currency` (ISO 4217) and `tax_class` (one of `standard`, `reduced`, `zero`, `exempt`). The quote endpoint SHALL reject requests that mix currencies across multiple line items (this is enforced at the Order service, not the catalog service).

#### Scenario: Currency is enforced
- **WHEN** a price is assigned with `currency=USD`
- **THEN** the quote response includes `currency=USD`

#### Scenario: Tax class is enforced
- **WHEN** a price is assigned with `tax_class=reduced`
- **THEN** the quote response includes `tax_class=reduced`

### Requirement: Price snapshot durability
The Order service SHALL persist a `price_snapshot_id` for each line item so the order can be reconstructed later even if the catalog service's price history is archived. The Order service SHALL store the snapshot fields (`base_price`, `currency`, `tax_class`, `discount_applied`, `snapshot_id`, `quoted_at`) on the order line item. The catalog service SHALL be able to look up a snapshot by `snapshot_id` for the snapshot-retention window (default 7 years).

#### Scenario: Order stores the price snapshot
- **WHEN** the Order service adds a line item with a quoted price
- **THEN** the line item row includes `price_snapshot_id`, `base_price`, `currency`, `tax_class`, `discount_applied`, `quoted_at`

#### Scenario: Catalog retains the price snapshot
- **WHEN** a snapshot is requested by ID after the price has been superseded
- **THEN** the catalog service returns the snapshot fields within the retention window

### Requirement: Discount windows
A discount SHALL have `discount_id` (ULID), `name`, `kind` (`percent` or `fixed`), `value` (numeric), `applies_to` (product IDs or category IDs), `starts_at`, `ends_at`, and `priority`. The quote endpoint SHALL evaluate discount windows and return the discount with the highest priority that is currently active. Overlapping discount windows SHALL NOT be combined; only the highest-priority window applies.

#### Scenario: Highest-priority discount wins
- **WHEN** two active discount windows apply to the product with priorities `1` and `5`
- **THEN** the quote response applies priority `5` and reports `discount_id=<priority-5>`

#### Scenario: Discount windows outside their time range do not apply
- **WHEN** a discount window's `ends_at` is in the past
- **THEN** the quote response uses the base price without that discount

### Requirement: Price observability
The catalog service SHALL emit metrics `catalog_quote_requests_total{status, cache_hit}`, `catalog_quote_duration_seconds`, `catalog_price_assignments_total{kind}`. The service SHALL emit a structured log per price assignment and per price change including the actor (subject ID or `system`), the before/after price diff, and the trace ID.

#### Scenario: Quote metric tracks cache hits
- **WHEN** a quote request is served from cache
- **THEN** `catalog_quote_requests_total{cache_hit="true"}` is incremented by 1

#### Scenario: Price change emits a log record
- **WHEN** a price is changed
- **THEN** the structured log records the old and new price, the actor, and the trace ID

### Requirement: Synchronous price quote from Order
The Order service SHALL call `GET /catalog-service/api/v1/products/{id}/quote` before persisting each line item. The Order service SHALL set the request timeout to 2 seconds. If the call fails or times out, the Order service SHALL surface `ErrPriceQuoteUnavailable` to the API caller and SHALL NOT proceed with the order.

#### Scenario: Order captures the quote before persisting the line item
- **WHEN** the Order service creates a line item
- **THEN** the catalog quote is captured and stored on the line item

#### Scenario: Quote timeout aborts the order
- **WHEN** the catalog service does not respond within 2 seconds
- **THEN** the Order service returns `503 Service Unavailable` with code `price_quote_unavailable` and does not persist the line item

### Requirement: Price-quote cache (capability-gated)
The catalog service MAY cache price quotes in the platform's cache module. The canonical cache key is `catalog:quote:{<product_id>}:{<requested_at_minute_epoch>}` (a 4-segment key with `<product_id>` as the `<scope>` and `<requested_at_minute_epoch>` as the `<id>`, matching `platform-cache` Requirement 3). The TTL SHALL be `TTLShort` (5 seconds); the minute-precision epoch in the key is intentional — two requests within the same minute share a key, but the 5-second TTL ensures stale entries are dropped well before the next minute boundary so cache invalidation aligns with the documented 5-second quote freshness window (see the Price quote endpoint requirement, which already documents "the duration of the order-creation transaction (default 5 seconds)"). The cache SHALL be a cache-aside layer; the source of truth is the `catalog.prices` PostgreSQL table. The cache hit rate is exposed via `cache_hit_total{cache_purpose=quote}` and the cache miss rate via `cache_miss_total{cache_purpose=quote}`. If the cache is admitted, the service's ADR SHALL document why the quote latency cannot be met by Postgres alone (the platform's `docs/adr/0004-optional-infrastructure.md` is the gating document). If the cache is not admitted, the catalog service SHALL rely on the database and the existing 5-second quote cache documented in `catalog-pricing-snapshot` Requirement 2.

#### Scenario: Cache hit serves the cached quote
- **WHEN** two quote requests for the same `(product_id, minute_epoch)` arrive within 5 seconds
- **THEN** the second response is served from the cache and `cache_hit_total{cache_purpose=quote}` is incremented by 1

#### Scenario: Cache miss falls back to Postgres
- **WHEN** a quote request misses the cache
- **THEN** the catalog service computes the quote from `catalog.prices`, stores it in the cache with `TTLShort`, returns it, and increments `cache_miss_total{cache_purpose=quote}` by 1

#### Scenario: Cache outage falls back to Postgres
- **WHEN** the cache adapter returns `ErrCacheOutage`
- **THEN** the catalog service computes the quote from `catalog.prices` and returns it; `cache_outage_duration_seconds` increases

#### Scenario: Cache keyspace is documented
- **WHEN** the catalog service admits a cache dependency
- **THEN** `services/catalog-service/docs/cache-keyspace.md` lists the `catalog:quote:*` key prefix, the `TTLShort` band, and the recovery procedure

### Requirement: Cache invalidation on price change
When the catalog service updates a price, the service SHALL invalidate every cached quote whose `product_id` matches the changed product. The invalidation SHALL use the platform's `Cache.Del(ctx, keys...)` with a pattern-match scan via `SCAN MATCH catalog:quote:<product_id>:*` (the `SCAN` cursor SHALL iterate without blocking the single-threaded cache event loop; the trailing `*` matches the trailing `:{<minute_epoch>}` segment of the canonical 4-segment key shape). The invalidation SHALL complete within 100 ms of the price update commit.

#### Scenario: Price change invalidates cached quotes
- **WHEN** a `PUT /api/v1/products/{id}/price` request commits a price change
- **THEN** within 100 ms every cached quote for that product is deleted from the cache

#### Scenario: Invalidation uses SCAN not KEYS
- **WHEN** the catalog service invalidates cached quotes
- **THEN** the cache call uses `SCAN MATCH catalog:quote:<product_id>:*` not `KEYS catalog:quote:<product_id>:*`