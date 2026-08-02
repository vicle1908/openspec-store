## MODIFIED Requirements

### Requirement: Projection writers never block upstream producers

Projection consumers SHALL use cooperative-sticky assignment, stable instance
identity for deployed members, disabled auto-commit, and a configured concurrent
fetch limit appropriate to their fan-in. The Reporting fan-in consumer SHALL
use at least eight concurrent fetches. A record SHALL become commit-eligible
only after its projection and processed receipt are durably committed or its
original bytes are durably quarantined. Commit-eligible offsets SHALL be marked
and committed once per bounded batch in per-partition order; consumers MUST NOT
perform synchronous per-record commits.

Because the pinned client can rebalance before or during offset commit, the
consumer SHALL preserve per-partition processing order, bound in-flight batches,
handle revocation/loss without committing records it no longer safely owns, and
accept duplicate delivery as recoverable through durable idempotency. A commit
failure SHALL be observable and MUST NOT mark an undurable projection as
successful.

#### Scenario: Projection consumer commits a bounded batch
- **WHEN** every record selected from a bounded batch has a durable terminal disposition
- **THEN** the consumer commits the highest eligible next offset per partition once for that batch
- **AND** processing does not issue a synchronous commit for each record

#### Scenario: Record is not durably disposed
- **WHEN** both projection and quarantine persistence fail for a record
- **THEN** the record remains commit-ineligible and its partition offset is not advanced past it

#### Scenario: Rebalance occurs during processing
- **WHEN** partition ownership changes before a batch is safely committed
- **THEN** the consumer does not rewind a newer owner's committed offset
- **AND** any redelivery is resolved by the durable processed-receipt contract

#### Scenario: Reporting fan-in client options are evidenced
- **WHEN** the Reporting consumer becomes ready
- **THEN** evidence reports cooperative-sticky assignment, stable instance identity, disabled auto-commit, at least eight concurrent fetches, and bounded batch commits

#### Scenario: Consumer commit fails
- **WHEN** Kafka rejects or times out a batch offset commit
- **THEN** the consumer emits topic/partition categorized telemetry and becomes degraded or unready according to the bounded failure policy
- **AND** it does not delete processed receipts or projection rows

#### Scenario: Projection consumer commits asynchronously
- **WHEN** the projection consumer processes a batch of records
- **THEN** the consumer commits offsets via `kgo.DisableAutoCommit` + `kgo.CommitMarkedOffsets` after each successful batch, verified by the absence of any synchronous per-record commit call in `platform/projection/consumer.go`

#### Scenario: Burrow reports non-zero consumer lag without alerting
- **WHEN** the projection consumer is intentionally slow (e.g., during a backfill)
- **THEN** Burrow reports the lag as a number, but the Burrow alert rule `consumer_lag_amber` only fires when the lag exceeds 10 minutes (the threshold is set in the platform's `burrow-alerts.yaml`)

## ADDED Requirements

### Requirement: Projection readiness is linked to source-owned operations

Canonical projection readiness SHALL begin with an operation accepted by the
service that owns the source aggregate. Evidence SHALL link the resulting
source transaction and immutable outbox event to the exact Kafka topic,
partition, offset, processed receipt, and field-correct projection state. A
directly injected Kafka record MAY exercise malformed, quarantine, redelivery,
or focused consumer behavior, but MUST NOT establish end-to-end projection
readiness.

#### Scenario: Owned operation reaches a projection
- **WHEN** an owning service API commits an aggregate transition and outbox event admitted by a projection consumer
- **THEN** readiness evidence identifies the event ID, Kafka coordinates, completed receipt, projection identity, expected fields, and originating operation identity

#### Scenario: Directly injected record is projected
- **WHEN** a Kafka fixture without an owning-service transaction is consumed and projected successfully
- **THEN** the result is classified as focused consumer evidence and cannot satisfy canonical projection readiness

#### Scenario: Projection row is not causally linked
- **WHEN** a projection row exists but its source operation, event ID, Kafka coordinates, or completed receipt cannot be proven
- **THEN** canonical projection readiness fails instead of accepting row existence alone
