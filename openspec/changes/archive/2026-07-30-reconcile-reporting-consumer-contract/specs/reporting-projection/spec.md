## MODIFIED Requirements

### Requirement: Kafka best practices for fan-in consumer groups

The Reporting service SHALL read its effective brokers, topics, consumer group,
instance identity, session timeout, heartbeat interval, rebalance timeout, and
fetch concurrency from one typed configuration passed unchanged to the Kafka
client. It SHALL subscribe to exactly `orders.events.v1`,
`customers.events.v1`, `catalog.events.v1`, and `notifications.events.v1`
through the single group `reporting.projection.v1`; `payments.events.v1` SHALL
remain reserved and unsubscribed. Deployed instances MUST supply a non-empty,
unique, stable instance identity and SHALL use cooperative-sticky assignment,
45-second session timeout, 3-second heartbeat interval,
`MaxConcurrentFetches(8)`, and disabled auto-commit.

The consumer SHALL mark an offset only after the projection write and processed
receipt are durably committed, or after the original record is durably stored
in quarantine. It SHALL commit marked offsets once per bounded processed batch,
MUST NOT perform a synchronous commit per record, and MUST preserve per-partition
commit ordering across rebalances. The projection remains idempotent through
the `(topic, partition, offset, event_id)` processed-receipt key and SHALL NOT
use a Kafka Streams EOS transaction.

Readiness SHALL expose the effective non-secret group, sorted topic set,
instance identity, assignment strategy, fetch concurrency, auto-commit mode,
and batch-commit mode. A configured/runtime mismatch MUST keep the consumer
unready.

#### Scenario: Single consumer group spans all topics
- **WHEN** the Reporting consumer starts with valid typed configuration
- **THEN** it joins `reporting.projection.v1` and subscribes to the four in-scope domain topics through one client
- **AND** readiness reports the same group and topic set

#### Scenario: Legacy group is configured
- **WHEN** configuration selects `reporting-projection`, `reporting-projection.v1`, or any group other than `reporting.projection.v1`
- **THEN** startup fails before polling and identifies the invalid non-secret group

#### Scenario: Static instance identity is absent
- **WHEN** a deployed Reporting orchestrator starts without a non-empty stable instance identity
- **THEN** startup fails before joining the consumer group

#### Scenario: Multiple consumer instances share the partitions
- **WHEN** three Reporting orchestrators join with unique stable identities
- **THEN** cooperative-sticky assignment gives each instance a subset of partitions across the four topics
- **AND** a rolling restart preserves unaffected assignments where Kafka permits

#### Scenario: Projection writes are idempotent
- **WHEN** a record is redelivered after its projection and receipt committed but before its Kafka offset committed
- **THEN** the processed-receipt key short-circuits the duplicate
- **AND** no projection row regresses or duplicates

#### Scenario: Projection and quarantine both fail
- **WHEN** a record cannot be applied and cannot be durably quarantined
- **THEN** its offset remains unmarked and uncommitted so redelivery can recover it

#### Scenario: Bounded batch is committed
- **WHEN** a bounded poll batch reaches durable terminal disposition for its records
- **THEN** marked offsets are committed once for the batch in per-partition order
- **AND** no synchronous per-record commit is issued

#### Scenario: Payments topic remains reserved
- **WHEN** the effective topic set is validated
- **THEN** `payments.events.v1` is absent until a separate capability change admits it

## ADDED Requirements

### Requirement: Reporting projections are causally and semantically verified

Canonical Reporting acceptance SHALL invoke the owning Customer, Catalog,
Order, and Notification APIs to produce representative events for each admitted
topic. Orders SHALL populate `report_orders`, Customer events SHALL populate
`report_customers`, Catalog events SHALL populate `report_products`, and
Notification events SHALL populate `report_facts`. For every selected event it
SHALL retain the originating request and aggregate identity, immutable outbox
event ID, Kafka topic/partition/offset, Reporting processed-receipt state,
projection identity, and expected projected fields. The projection fields SHALL
be compared with the owning operation's committed values, not merely checked
for row existence. Redelivery, rebalance, and cutover SHALL preserve this
linkage and MUST NOT duplicate or regress the logical projection.

#### Scenario: Four-topic operation cohort is projected
- **WHEN** owning APIs commit representative Customer, Catalog, Order, and Notification operations
- **THEN** Reporting consumes their events through `reporting.projection.v1` and records completed receipts for the exact Kafka coordinates
- **AND** each resulting projection contains the expected fields from its originating committed operation

#### Scenario: Topic-specific projection ownership is preserved
- **WHEN** a Customer, Catalog, Order, or Notification event is consumed
- **THEN** exactly its owning Reporting projection (`report_customers`, `report_products`, `report_orders`, or `report_facts`) is mutated
- **AND** no source service schema or command API is written

#### Scenario: Owned event is redelivered
- **WHEN** an admitted event with a completed receipt is delivered again before or after rebalance
- **THEN** Reporting preserves the existing field-correct projection and one logical receipt disposition
- **AND** causal evidence records the duplicate attempt without creating a second logical projection

#### Scenario: Receipt or projection does not match the event
- **WHEN** the event ID, Kafka coordinates, completed receipt, projection identity, or expected projected fields cannot be joined consistently
- **THEN** Reporting readiness fails with non-secret causal diagnostics

#### Scenario: Direct Kafka fixture reaches Reporting
- **WHEN** a record is injected directly for malformed-event, quarantine, or focused redelivery testing
- **THEN** it may satisfy the focused fixture but cannot satisfy canonical operation-led Reporting readiness

### Requirement: Reporting consumer-group cutover is controlled and reversible

Changing from a legacy Reporting group to `reporting.projection.v1` SHALL be a
single-writer cutover. The old group MUST be stopped before the canonical group
starts. For each topic partition, the canonical group SHALL start at the first
offset not proven durably applied by the Reporting processed-receipt state; an
ambiguous gap MUST choose the earlier safe offset and rely on idempotent replay.
The cutover SHALL retain old and new group identities, per-partition source and
target offsets, receipt evidence, operator intent, and rollback instructions.

#### Scenario: Empty local environment cuts over
- **WHEN** no legacy offsets or projection receipts exist
- **THEN** the canonical group starts from the configured new-group reset policy and records that decision

#### Scenario: Durable receipts cover the legacy offsets
- **WHEN** every legacy partition offset through N has a durable completed receipt
- **THEN** the canonical group starts at N+1 for that partition

#### Scenario: Receipt history contains a gap
- **WHEN** a partition has a missing or non-completed receipt before its legacy committed offset
- **THEN** cutover selects the earliest unproven offset and replays idempotently

#### Scenario: Legacy and canonical groups overlap
- **WHEN** validation detects active members in both group identities during cutover
- **THEN** cutover fails before the canonical consumer becomes ready

#### Scenario: Rollback is approved
- **WHEN** the canonical group is stopped and rollback is requested
- **THEN** one selected legacy group may resume from its retained reviewed offsets
- **AND** processed receipts and projection rows remain intact
