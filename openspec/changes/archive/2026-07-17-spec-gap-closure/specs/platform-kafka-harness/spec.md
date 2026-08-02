# platform-kafka-harness Delta Specification

## Purpose

This delta updates the main `platform-kafka-harness` spec to reflect the actual implementation status discovered during the spec-gap-closure audit. Three requirements have modified status annotations.

## MODIFIED Requirements

### Requirement: Retry topic pattern (non-blocking retries) [DEFERRED]

> **Status**: DEFERRED. The retry-topic chain (`<source-topic>.retry.1000`, `.retry.8000`, `.retry.60000`, `.retry.300000`, `.retry.1800000`) is not implemented. The consumer publishes to a retry topic on `RetryableError` but there is no `RetryConsumer` that reads a retry topic, sleeps for the configured delay, and re-publishes to the source topic. The full chain including DLQ routing after the final attempt is not wired.

The consumer SHALL be configured with a retry topic chain: `<source-topic>.retry.1000`, `<source-topic>.retry.8000`, `<source-topic>.retry.60000`, `<source-topic>.retry.300000`, `<source-topic>.retry.1800000`. Each retry topic carries the same payload as the source topic plus a `retry-attempt` header (1-based) and the original `traceparent` and `X-Correlation-Id` headers. The consumer reads from the source topic and any retry topic assigned to its consumer group; the platform SHALL provide a `RetryConsumer` that reads a retry topic, sleeps for the configured delay, then re-publishes the record to the source topic. After the final retry attempt, the consumer SHALL route the record to `<source-topic>.dlq`.

#### Scenario: Retryable error routes to first retry topic

- **WHEN** the processor returns `RetryableError` for the first time on a record
- **THEN** the consumer publishes the record to `<source-topic>.retry.1000` with `retry-attempt: 1` and the original headers preserved

#### Scenario: Retry topic consumer delays before re-publishing

- **WHEN** the retry topic consumer reads a record with `retry-attempt: 2` from `<source-topic>.retry.1000`
- **THEN** the consumer waits 8 seconds and re-publishes the record to the source topic with `retry-attempt: 3`

#### Scenario: Terminal retry routes to DLQ

- **WHEN** the processor returns `RetryableError` for the fifth time
- **THEN** the consumer publishes the record to `<source-topic>.dlq` with the original headers, the final attempt's error reason in a `dlq-reason` header, and the diagnostic message in `dlq-diagnostics`

#### Scenario: Non-retryable error routes directly to DLQ

- **WHEN** the processor returns `NonRetryableError`
- **THEN** the consumer publishes the record to `<source-topic>.dlq` immediately, skipping the retry chain

### Requirement: Idempotent consumer pattern [PARTIAL]

> **Status**: PARTIAL. The platform provides receipt-based deduplication (`ErrReceiptDuplicate` in `platform/kafka/receipt.go`) and the `ErrSideEffectAlreadyApplied` typed error exists in `platform/temporal/operation_id.go`. However, the full `ProcessRecord` helper that wraps a processor with the receipt-insert-before-side-effect, mark-started-after-commit, and redelivery-short-circuit sequence is not complete. The `ProcessorContext.Redelivery` flag is not propagated to all processors, and the receipt-as-lock pattern (insert before side effect invocation) is not enforced in all code paths.

The consumer SHALL require every processor to be idempotent. The platform SHALL provide a `ProcessRecord` helper that wraps a processor and ensures: (1) the receipt row is inserted before the side effect is invoked (the side-effect row's primary key serves as a lock); (2) the receipt row is marked `started` after the side effect is durably committed; (3) a redelivery observes the `started` state and short-circuits. The platform SHALL expose a typed error `ErrSideEffectAlreadyApplied` that processors return when they detect their own idempotency token is already present in the destination system.

#### Scenario: Receipt insert before side effect

- **WHEN** the consumer invokes the processor
- **THEN** the receipt row is in state `started` before the processor's side effect runs (the processor can rely on the receipt as a "this is my turn" lock)

#### Scenario: Redelivery observes started receipt

- **WHEN** the consumer reads a record whose receipt is already in state `started`
- **THEN** the consumer invokes the processor with `ProcessorContext.Redelivery=true` so the processor can skip work it knows it has already done

#### Scenario: Side effect already applied returns typed error

- **WHEN** the processor detects its idempotency token is already present in the destination system
- **THEN** the processor returns `ErrSideEffectAlreadyApplied` and the consumer treats it as success

### Requirement: Producer-side idempotence and batching [PARTIAL]

> **Status**: PARTIAL. The platform's producer factory in `platform/kafka/producer.go` configures idempotent settings (`enable.idempotence=true`, `acks=all`, `compression=lz4`, `linger=10ms`, `batch.size=131072`, `delivery.timeout=120s`), but `max.in.flight.requests.per.connection=5` is not explicitly set (franz-go defaults may differ from the spec requirement). Error logging is implemented but the structured logging of the producer's internal `acks` state on error is not present in all code paths.

Any producer created by the platform (used for retry, DLQ, outbox-published-by-Debezium) SHALL configure franz-go with `enable.idempotence=true`, `compression.type=lz4`, `linger.ms=10`, `batch.size=131072`, `acks=all`, `max.in.flight.requests.per.connection=5`, `delivery.timeout.ms=120000`. The producer SHALL NOT be configured to silently swallow errors; every error SHALL be logged with the topic, partition, key, and the producer's internal `acks` state.

#### Scenario: Producer applies platform defaults

- **WHEN** a service constructs a producer through the platform's producer factory
- **THEN** the producer applies the documented idempotence and batching settings

#### Scenario: Producer error is not silently dropped

- **WHEN** the broker rejects a record (e.g., message-too-large)
- **THEN** the producer returns an error to the caller and the error is logged with the topic, key, and broker response code
