## Context

See `proposal.md` for motivation. Reporting configuration already defaults to
`reporting.projection.v1`, while its Compose overlay and adapter constant select
two different legacy groups. The direct Reporting adapter constructs franz-go
without explicit cooperative-sticky balancing, static membership, session and
heartbeat settings, or eight concurrent fetches. It disables auto-commit,
marks records, and calls `CommitMarkedOffsets` after each poll result.

The current cross-service smoke query waits only for an Order projection row
whose `order_id` is non-empty. It does not capture the source outbox event or
Kafka coordinates, inspect the completed Reporting receipt, compare projected
fields with committed source values, or distinguish a causally related row from
stale state. Existing direct Kafka fixtures remain useful for focused consumer
failure paths but are not a readiness source.

The platform Kafka and projection packages already contain most intended client
options, but Reporting owns a specialized four-topic handler, processed-receipt
store, quarantine path, and freshness reporting. A direct migration to the
generic consumer would couple this correction to wider receipt/retry behavior.

Current official franz-go documentation and the repository's v1.21.5 pin agree
that cooperative-sticky is supported, static membership requires Kafka 2.4 or
newer, commits advance to offset+1, out-of-order commits can rewind offsets, and
`CommitMarkedOffsets` is synchronous. The repository Kafka 4.3.1 pin satisfies
the static-membership requirement. Therefore the existing spec phrase
"asynchronous commits" is replaced by bounded once-per-batch commits and a
prohibition on synchronous per-record commits.

## Goals / Non-Goals

**Goals:**

- Make typed Reporting configuration the only source of Kafka client identity
  and options.
- Preserve per-partition ordering and idempotent replay across rebalances,
  partial commit failures, and group cutover.
- Produce readiness evidence from the effective running client rather than from
  YAML or constants alone.
- Prove source-operation, outbox, Kafka, receipt, and field-correct projection
  causality for all four admitted topics.
- Keep the change small enough to land before Kafka security ACL generation.

**Non-Goals:**

- Replacing the Reporting projection handler with the generic platform
  consumer, changing retry/quarantine schemas, or admitting new event topics.
- Kafka TLS/SASL/ACL implementation.
- Exactly-once processing; the contract remains at-least-once plus durable
  idempotency.

## Decisions

### 1. Typed runtime configuration is authoritative

Extend Reporting's typed Kafka configuration with brokers, ordered topic set,
group, client identity, instance identity, session timeout, heartbeat interval,
rebalance timeout, concurrent fetch count, bounded records per poll, and batch
processing deadline. The runtime role passes this structure unchanged to the
adapter. Remove the adapter group constant and any hidden fallback that can
override a validated non-empty value.

Defaults are:

- group `reporting.projection.v1`;
- the existing four in-scope topics in canonical sorted order;
- session 45 seconds, heartbeat 3 seconds, rebalance 60 seconds;
- eight concurrent fetches;
- auto-commit disabled and cooperative-sticky explicitly configured.

The instance identity resolves from an explicit Reporting setting, then the
deployed pod/container identity supplied by orchestration. It is required for
deployed roles and may use a deterministic test identity in unit/integration
tests. Each concurrent member must be unique.

Alternative considered: keep the adapter constant and validate it against
configuration. Rejected because two authorities can drift again.

### 2. Share Kafka option construction, not Reporting processing semantics

Extract or extend a narrow platform Kafka client-option builder for validated
consumer identity, topics, balancing, membership, timeouts, fetch limits,
autocommit, and observability hooks. Use it from the existing platform consumer
and the Reporting adapter. Reporting continues to own envelope decoding,
projection application, processed receipts, quarantine, and freshness metrics.

This removes option drift without forcing Reporting into generic retry/DLQ
semantics or changing its database transaction boundaries.

Alternative considered: migrate Reporting wholesale to `platform/kafka.Consumer`.
Rejected for this change because its receipt/quarantine interfaces and retry
behavior differ and would expand the compatibility surface.

### 3. Polling and rebalances use a bounded ownership window

Use bounded record polling together with the client option that blocks group
rebalancing while a non-empty batch is being processed. The batch size and
deadline remain below the configured rebalance timeout. After every record has
reached durable terminal disposition, commit marked offsets for the batch and
release the rebalance block. Every exit path releases it, including context
cancellation and processing or commit failure.

This prevents committing records after ownership is revoked. The tradeoff is
that slow processing can cause the member to exceed its rebalance bound, so
batch size/deadline validation and telemetry are required.

Alternative considered: allow rebalances during processing and commit from
revocation callbacks. Rejected because coordinating Reporting database writes,
quarantine, and partial batches across callbacks is more complex and harder to
verify in this focused change.

### 4. Offset eligibility follows durable terminal disposition

For a successfully applied event, the projection mutation and completed
processed receipt must be durable before the record is marked. For an event that
cannot be applied, the original bytes and diagnostic metadata must be durably
quarantined before it is marked. If neither succeeds, do not mark or advance
past the record.

Marked offsets are committed once after a bounded batch, using the pinned
client's synchronous batch operation. Since a multi-partition commit can
partially succeed, failure telemetry records affected topic/partition results
where available; redelivery is safe because completed receipts are durable.
Commit order is monotonic per partition, and processing never starts a second
batch for the same partition before the current batch releases ownership.

Alternative considered: commit each record synchronously. Rejected because it
adds broker round trips and consumer backpressure without improving the
at-least-once/idempotent guarantee.

### 5. Readiness comes from validated effective settings and membership

The orchestrator remains unready until static validation passes, the client is
constructed with the canonical settings, and group metadata confirms membership
under `reporting.projection.v1`. Evidence contains the sorted topic set, group,
client/instance identity, balancer, timeout values, concurrent fetch count,
autocommit disabled, batch bound, and commit mode. It contains no broker
credential or security material.

Architecture tests scan Compose, local kind, defaults, dashboards, fixtures,
and code for legacy group strings. Runtime tests use broker group metadata to
prove the actual membership rather than trusting configuration output.

### 6. Four-topic projections align with the existing Reporting capability

The repository's main `reporting-projection` specification already defines
`report_customers`, `report_products`, and `report_facts` plus read-only summary
queries. The consumer contract therefore keeps all four admitted topics and
adds these projections rather than treating three topics as receipt-only. Each
topic has one owning projection writer: Orders writes `report_orders`, Customer
writes `report_customers`, Catalog writes `report_products`, and Notification
writes `report_facts`. All writers participate in the same processed-receipt
transaction and carry event ID, Kafka coordinate, occurred time, correlation,
and trace metadata. The change is additive: existing order tables, event
schemas, public order/revenue APIs, and receipt keys are preserved.

Payload decoding is contract-owned in Reporting and accepts the two formats
actually emitted by the pinned Debezium connectors: the Order connector's
BinaryDataConverter carries the versioned protobuf envelope, while Customer,
Catalog, and Notification use JsonConverter with expanded JSON payloads.
For JSON records, Event Router places the outbox event ID in the `id` header,
the aggregate ID in the Kafka key, and the expanded payload in the value;
Reporting normalizes those fields into the same internal envelope and retains
the raw JSON for the domain projection. Catalog product snapshots are merged
with the existing read model for price-only events so additive price facts
cannot erase product identity fields. Unknown or malformed event values are
durably quarantined and never become commit-eligible without a terminal
receipt or quarantine disposition.

### 7. Consumer group cutover derives offsets from durable receipts

Add a dry-run-first cutover command/report. It stops or verifies absence of
legacy group members, reads legacy committed offsets, reads durable Reporting
receipts by topic/partition, and proposes the first offset not proven completed.
If receipt history is contiguous through N, start at N+1. If a gap or pending
receipt exists, choose the earliest unproven offset. Earlier replay is preferred
to skipping because projection writes are idempotent.

Application requires an explicit apply flag plus the exact source and group
identities. It records old/new offsets and receipt basis. No projection or
receipt rows are deleted. Local empty-state cutover records the configured
new-group reset policy. Validation rejects active members in old and canonical
groups simultaneously.

Alternative considered: start the new group at latest. Rejected because it can
silently skip events not represented in the projection database.

### 8. The Reporting fan-in exception does not alter platform defaults

Ordinary platform consumers retain the default concurrent fetch count of two.
The shared option builder accepts a validated override, and Reporting supplies
eight. No event schema, topic partitioning, producer, retry/DLQ, or security
setting changes in this change.

### 9. Canonical projection evidence starts at the owning service

Add an operation-led acceptance cohort for each admitted topic. Customer,
Catalog, Order, and Notification commands run through their owning APIs using
stable request, correlation, and idempotency identities. The harness observes
the immutable outbox event emitted by that transaction, records its Kafka
topic/partition/offset, and then queries Reporting's processed receipt and
public or service-owned projection read path.

Each oracle compares the complete set of contract-relevant projected fields
with values committed by the source operation. The evidence record contains
source aggregate/version, outbox event ID/type/version, Kafka coordinates,
Reporting instance/group, receipt state, projection identity, expected and
observed field digests, processing timestamps, and trace/correlation identity.
It never stores sensitive payloads or broker credentials.

Redelivery tests repeat the exact captured record or reset the controlled test
consumer position after the first completed receipt. They prove that the same
receipt key short-circuits duplicate work and that fields neither duplicate nor
regress. Rebalance and cutover tests carry the same event identities through
member movement and offset initialization.

Direct Kafka injection is reserved for malformed envelopes, quarantine,
authorization denial, and narrowly isolated commit/redelivery behavior. Such
fixtures are labeled focused and cannot satisfy the operation-led acceptance
cohort.

Alternative considered: accept projection row existence plus consumer-group
membership. Rejected because those signals can be healthy while the wrong
event, stale data, or incorrect field mapping produced the row.

## Risks / Trade-offs

- **New group starts at the wrong offset** → derive from durable receipts,
  prefer earlier replay on ambiguity, require dry-run review, and retain
  per-partition evidence.
- **Two legacy/canonical groups process simultaneously** → check live membership
  before cutover and keep readiness false while any legacy member exists.
- **Blocked rebalance exceeds timeout** → bound poll size and processing time,
  release on every path, and alert on callback-blocked or deadline metrics.
- **Batch commit partially succeeds** → preserve durable receipts, emit
  per-partition diagnostics, and accept idempotent redelivery.
- **Shared option helper changes ordinary consumers** → retain current defaults
  and add equivalence tests before adopting it in Reporting.
- **Static identity collides after scaling** → require non-empty unique identity
  and test three concurrent deployed members.
- **Projection exists but is stale or unrelated to the operation** → require an
  exact event/coordinate/receipt join and field-level source comparison.

## Migration Plan

1. Add typed settings, validation, effective-setting evidence, and shared option
   construction while retaining the current group at runtime.
2. Correct durable mark/quarantine/commit ordering and add rebalance, partial
   failure, redelivery, and multi-instance integration tests.
3. Update defaults, Compose, local kind, fixtures, dashboards, and docs to
   `reporting.projection.v1`; add legacy-string architecture checks.
4. Run cutover dry-run. For empty local state, record the reset policy; for
   retained state, review the receipt-derived per-partition offsets.
5. Stop all legacy members, apply canonical offsets, start only the canonical
   group, verify group metadata/readiness, and run the four-topic
   owning-operation causal cohort through rebalance and redelivery.
6. Add the canonical group, causal evidence contract, and principal intent to
   the downstream runtime contract and Kafka ACL inventory.

Rollback stops all canonical members, retains diagnostics and canonical
offsets, restores exactly one selected legacy group at reviewed retained
offsets, and verifies idempotent projection behavior. It never runs both groups
and never deletes projection or processed-receipt state.
