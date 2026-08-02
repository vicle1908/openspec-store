# kafka-aggregate-version-tracking Specification

## Purpose

Extends the Kafka consumer harness to detect and quarantine out-of-order events by tracking the last processed aggregate version per consumer group.

## Background

The existing receipt store tracks `(consumer_group, event_id)` for deduplication. This spec adds version tracking per `(consumer_group, aggregate_id)` to detect gaps.

## Requirements

### Requirement: Aggregate version store

The platform SHALL provide an `AggregateVersionStore` interface that persists `last_aggregate_version` per `(consumer_group, aggregate_id)` pair.

```go
type AggregateVersionStore interface {
    // Get returns the last processed version for the aggregate,
    // or 0 if no version has been recorded.
    Get(ctx context.Context, consumerGroup, aggregateID string) (uint64, error)
    // Update atomically sets the new version if it is greater than the stored version.
    // Returns whether the update was applied.
    Update(ctx context.Context, consumerGroup, aggregateID string, version uint64) (bool, error)
}
```

#### Scenario: First event from aggregate

- **WHEN** an aggregate emits its first event (version=1)
- **THEN** `Get` returns 0, `Update(1)` returns true

#### Scenario: Monotonic version processed

- **WHEN** current version is 5 and new event has version=6
- **THEN** `Update(6)` returns true

#### Scenario: Out-of-order version rejected

- **WHEN** current version is 5 and new event has version=4
- **THEN** `Update(4)` returns false

### Requirement: Consumer checks aggregate version before processing

The consumer SHALL extract `aggregate_id` and `aggregate_version` from the event envelope headers and check the aggregate version store before invoking the processor.

#### Scenario: Out-of-order event quarantined

- **WHEN** a record arrives with `aggregate_version` less than the stored `last_aggregate_version`
- **THEN** the consumer quarantines the record with reason `aggregate_version_gap`
- **AND** the diagnostic message includes: current version, incoming version, gap size

#### Scenario: Valid version processed

- **WHEN** a record arrives with `aggregate_version` greater than stored version
- **THEN** the processor is invoked
- **AND** the aggregate version store is updated

#### Scenario: First event from aggregate passes through

- **WHEN** no version exists for the aggregate and incoming version is 1
- **THEN** the processor is invoked
- **AND** the aggregate version is set to 1

### Requirement: Quarantine preserves original record

The quarantine row SHALL preserve the original record bytes, topic, partition, offset, key, headers, and a diagnostic message describing the gap.

#### Scenario: Quarantine row contains gap diagnostic

- **WHEN** an out-of-order event is quarantined
- **THEN** the quarantine row contains: original bytes, reason `aggregate_version_gap`, and diagnostic: `"gap detected: last=5 incoming=3 gap=2"`
