## Why

Reporting's normative consumer group is `reporting.projection.v1`, but Compose
uses `reporting-projection.v1` and the Kafka adapter hardcodes
`reporting-projection`; the adapter also does not prove the required
cooperative-sticky/static-membership and concurrent-fetch contract. This drift
can create separate offset histories, duplicate projection work, and false
readiness evidence during the production-contract rollout. Existing smoke
evidence observes only that an order row appears; it does not prove which owned
operation and outbox event produced the Kafka record and processed receipt, or
that the projected fields are correct.

## What Changes

- Make typed Reporting configuration the single source for consumer group,
  brokers, in-scope topics, instance identity, fetch concurrency, session, and
  heartbeat settings; remove divergent adapter constants and defaults.
- Use exactly `reporting.projection.v1` across service defaults, Compose, local
  kind, tests, evidence, dashboards, and runtime Kafka membership.
- Require one consumer group across the four currently in-scope event topics,
  cooperative-sticky assignment, non-empty static instance identity in deployed
  roles, `MaxConcurrentFetches(8)`, disabled auto-commit, and marked-offset
  bounded batch commits after durable idempotent projection writes or durable
  quarantine; prohibit synchronous per-record commits.
- Add startup and runtime evidence that reports the effective non-secret group,
  topics, instance identity, assignment strategy, fetch concurrency, and commit
  mode; reject configuration/runtime mismatch before readiness.
- Make canonical Reporting acceptance originate events through the owning
  Customer, Catalog, Order, and Notification APIs and link each source
  transaction and outbox event to exact Kafka coordinates, processed receipt,
  and field-correct projection state.
- Treat direct Kafka injection as a focused malformed-event, denial, or
  redelivery fixture only; it cannot establish production-contract projection
  readiness.
- Complete the existing Reporting capability by adding the missing
  `report_customers`, `report_products`, and `report_facts` projections and
  read-only summaries, while preserving event schemas, data ownership, offset
  semantics, and the reserved-but-not-subscribed Payments topic.

### Goals

- Eliminate all group-ID and client-option drift before secure Kafka ACLs are
  generated from the runtime contract.
- Make scaling and rebalance behavior testable with multiple Reporting replicas.
- Prove field-level projection correctness and idempotent replay through a
  retained causal ledger for all four admitted source topics.
- Correct inaccurate IMPLEMENTED claims with executable evidence.

### Non-Goals

- Adding `payments.events.v1`, changing existing event schemas, introducing
  Kafka Streams transactions, or adding command/write APIs to Reporting.
- Replacing the existing order projection or changing its processed-receipt
  key; the additional projections are additive and consume their owning topic
  payloads through the same idempotent batch contract.
- Changing the platform-wide default of `MaxConcurrentFetches(2)` for ordinary
  consumers; Reporting remains the explicit fan-in exception at eight.
- Implementing Kafka TLS/SASL or ACL infrastructure, which belongs to the
  service-runtime-security and local-readiness changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `reporting-projection`: Make the canonical group, configuration authority,
  assignment/fetch/commit behavior, startup validation, and readiness evidence
  explicit for the multi-topic Reporting consumer.
- `platform-projection`: Replace the unsupported IMPLEMENTED assertion with an
  evidence-backed fan-in consumer contract and accurate bounded batch-commit
  semantics for the pinned franz-go client.

## Impact

- **Reporting:** runtime configuration, Kafka adapter construction, role wiring,
  Compose and local kind inputs, integration tests, readiness, metrics, and
  documentation, including exact event/receipt/projection causal evidence.
- **Platform Kafka:** reuse the existing consumer factory/options without
  changing ordinary consumer defaults or delivery guarantees.
- **Compatibility:** changing a deployed consumer from either legacy hyphenated
  group to `reporting.projection.v1` creates a distinct offset history. Rollout
  MUST inspect and initialize offsets from the approved cutover point before
  starting the canonical group; simultaneous old/new groups are prohibited.
- **Rollout:** reconcile code/config/tests first, perform an empty or controlled
  local offset cutover, prove multi-replica assignment and redelivery, then feed
  the canonical group into the runtime-contract and Kafka ACL inventory.
- **Rollback:** stop the canonical group before re-enabling one selected legacy
  group at its retained offsets; never run both and never delete projection rows
  or processed-event receipts during rollback.
