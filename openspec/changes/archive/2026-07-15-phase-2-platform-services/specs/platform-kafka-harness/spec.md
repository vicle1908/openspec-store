## ADDED Requirements

### Requirement: Kafka consumer with durable receipts
The platform SHALL provide a Kafka consumer that reads records from a configured topic and consumer group, decodes each record's envelope, calls a caller-supplied processor, and commits the Kafka offset only after the processor reports success, terminal failure (which triggers quarantine), or a recoverable retryable error (which leaves the offset uncommitted so the broker redelivers). The consumer SHALL persist a durable receipt row keyed by `(consumer_group, topic, partition, offset)` in the same PostgreSQL transaction as the consumer's state change; a unique violation on the receipt row's primary key MUST be treated as a successful no-op so duplicate deliveries are deduplicated. The consumer SHALL use franz-go `v1.21.5` as the underlying Kafka client.

#### Scenario: Duplicate delivery commits without re-running the side effect
- **WHEN** the consumer reads a record whose `(consumer_group, topic, partition, offset)` receipt row already exists in state `started` or `completed`
- **THEN** the consumer commits the offset and does not re-invoke the processor

#### Scenario: Processor returns retryable error
- **WHEN** the processor returns `RetryableError`
- **THEN** the consumer publishes the record to the configured retry topic (see `Retry topic pattern` requirement), does NOT commit the Kafka offset to the source topic, and does NOT mark the receipt as started

#### Scenario: Processor returns success
- **WHEN** the processor returns nil
- **THEN** the consumer commits the Kafka offset and the receipt is in state `started` or `completed`

#### Scenario: Receipt table primary key prevents duplicate processing
- **WHEN** two consumers in the same group race to insert a receipt for the same `(consumer_group, topic, partition, offset)`
- **THEN** one insert succeeds and the other returns a unique-violation that is treated as a successful no-op

### Requirement: Aggregate-version gap detection
The consumer SHALL persist a `last_aggregate_version` per `(consumer_group, aggregate_id)` alongside the receipts. When a new record arrives whose `aggregate_version` is less than or equal to the recorded `last_aggregate_version`, the consumer SHALL quarantine the record with the original bytes, the reason `aggregate_version_gap`, and a diagnostic message describing the gap. The quarantine row SHALL preserve the original record bytes so an operator can replay or investigate.

#### Scenario: Out-of-order aggregate version is quarantined
- **WHEN** a record arrives with `aggregate_version` less than the persisted `last_aggregate_version`
- **THEN** the record's bytes are persisted to the quarantine table with reason `aggregate_version_gap`

#### Scenario: Monotonic aggregate version is processed normally
- **WHEN** a record arrives with `aggregate_version` greater than the persisted `last_aggregate_version`
- **THEN** the processor is invoked and `last_aggregate_version` is updated

### Requirement: Decode-failure quarantine
The consumer SHALL quarantine records whose envelope cannot be decoded, preserving the original bytes, the topic, partition, offset, key, and a diagnostic message describing the decode failure. The quarantine SHALL NOT cause the consumer to stop; the offset is committed and processing continues.

#### Scenario: Malformed envelope bytes are quarantined
- **WHEN** the consumer reads a record whose bytes are not a valid `EventEnvelope`
- **THEN** the consumer quarantines the record with the original bytes and continues

### Requirement: Retry topic pattern (non-blocking retries)
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

### Requirement: Idempotent consumer pattern
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

### Requirement: Consumer crash recovery
The consumer SHALL tolerate a crash at any point in the processing path. A crash between `PutPending` (pending receipt) and `MarkStarted` (started receipt) SHALL be reconciled on restart by checking whether the consumer's intended side effect already exists; if it does, the receipt is marked `started` without re-starting the side effect. The consumer SHALL NEVER treat a `pending` receipt as completed.

#### Scenario: Crash between pending and started is reconciled on restart
- **WHEN** the consumer starts and finds a receipt in state `pending` for an offset
- **THEN** the consumer reconciles the receipt against the side-effect store and marks the receipt `started` only if the side effect exists

#### Scenario: Pending receipt whose side effect does not exist is retried
- **WHEN** the consumer starts and finds a receipt in state `pending` and the side effect does not exist
- **THEN** the consumer invokes the side effect again, treating the duplicate-delivery invariant

### Requirement: Configurable consumer group, topic, and Kafka client settings
The consumer SHALL read its consumer group ID, topic, brokers, session timeout, and heartbeat interval from typed configuration. The consumer group ID SHALL match the convention `<service>.<role>.vN`. The consumer SHALL configure franz-go with `enable.auto.commit=false`, `kgo.Balancers(kgo.CooperativeStickyBalancer())`, `kgo.InstanceID(<pod-name>)` for K8s static membership, `kgo.SessionTimeout(45s)`, `kgo.HeartbeatInterval(3s)`, `kgo.MaxConcurrentFetches(2)`, `kgo.FetchMinBytes(1MB)`, and `kgo.MaxPartitionFetchBytes(1MB)`. The idempotent producer used by the consumer for retry and DLQ topics SHALL configure `enable.idempotence=true`, `compression.type=lz4`, `linger.ms=10`, `batch.size=131072`, `acks=all` + `min.insync.replicas=2`. (The producer-only parameter `max.in.flight.requests.per.connection` is documented under the producer requirement below — `franz-go` does not expose that parameter on the consumer.)

#### Scenario: Consumer starts with valid configuration
- **WHEN** the consumer is constructed with valid configuration
- **THEN** it joins the configured group with cooperative-sticky balancing and static membership

#### Scenario: Consumer rejects empty consumer group
- **WHEN** the consumer is constructed with an empty `ConsumerGroup` value
- **THEN** construction fails with a typed validation error

#### Scenario: Producer settings applied to retry topic
- **WHEN** the consumer publishes a record to a retry topic
- **THEN** the franz-go producer applies the idempotent settings listed above

### Requirement: OpenTelemetry context propagation across Kafka boundaries
The consumer SHALL extract `traceparent`, `X-Correlation-Id`, `X-Request-Id`, and `X-Causation-Id` from record headers and attach them to the processor's `context.Context`. The consumer's producer (used for retry and DLQ topics) SHALL inject the same headers so the trace context flows across retries.

#### Scenario: Inbound Kafka record extracts propagation headers for processor context
- **WHEN** the consumer reads a record whose headers include `traceparent` and `X-Correlation-Id`
- **THEN** the processor's `context.Context` carries the extracted trace ID and correlation ID

#### Scenario: Retry record carries propagation headers
- **WHEN** the consumer publishes a record to a retry topic
- **THEN** the record's headers include `traceparent`, `X-Correlation-Id`, `X-Request-Id`, and `X-Causation-Id` matching the current context

### Requirement: Quarantine replay support
The platform SHALL provide a CLI subcommand `replay-quarantine` that, given a quarantine row's primary key, re-emits the original bytes to the original topic so an operator can replay a quarantined record after the underlying cause is fixed. The replay SHALL be idempotent against the consumer's receipts table — a replayed record whose receipt already exists is a no-op.

#### Scenario: Replay re-emits the original bytes
- **WHEN** an operator runs `replay-quarantine --id <row-id>`
- **THEN** the consumer reads the quarantine row, re-publishes the original bytes to the original topic with `traceparent` and `X-Correlation-Id` headers, and marks the quarantine row as resolved

#### Scenario: Replayed record is deduplicated by the receipt
- **WHEN** a replayed record arrives and its `(consumer_group, topic, partition, offset)` already has a `started` receipt
- **THEN** the consumer commits the offset without re-invoking the processor

### Requirement: Consumer observability
The consumer SHALL emit metrics `kafka_consumer_records_total{topic, status}`, `kafka_consumer_duration_seconds{topic}` (poll-to-commit), `kafka_consumer_lag_seconds{topic, partition}` (computed as `now - record.occurred_at`), `kafka_retry_attempts_total{topic, attempt}`, `kafka_dlq_records_total{topic, reason}`, and `kafka_quarantine_records_total{topic, reason}`. The consumer SHALL emit a structured log per record including the topic, partition, offset, `event_id`, `aggregate_id`, `correlation_id`, `trace.id`, and the processing outcome.

#### Scenario: Consumer lag metric exposed
- **WHEN** the consumer commits an offset
- **THEN** `kafka_consumer_lag_seconds{topic, partition}` is set to `now - record.occurred_at`

#### Scenario: Retry attempt counter increments
- **WHEN** the consumer routes a record to a retry topic
- **THEN** `kafka_retry_attempts_total{topic, attempt=<n>}` is incremented by 1

#### Scenario: DLQ counter increments on terminal failure
- **WHEN** the consumer routes a record to the DLQ
- **THEN** `kafka_dlq_records_total{topic, reason=<reason>}` is incremented by 1

### Requirement: Burrow-based consumer lag alerting
The consumer SHALL export lag metrics in a format compatible with LinkedIn Burrow (a Burrow-sidecar config in the OTel Collector receives Kafka consumer-group lag via `kafka_consumergroup_lag` Prometheus metrics). The platform SHALL configure alerting rules that fire when Burrow reports a consumer group in `STOP` state for more than 5 minutes or in `WARNING` state for more than 15 minutes.

#### Scenario: Stopped consumer alert fires
- **WHEN** Burrow classifies a consumer group as `STOP` for 5 minutes
- **THEN** the alert fires and the on-call rota is notified via PagerDuty or equivalent

#### Scenario: Warning consumer alert fires
- **WHEN** Burrow classifies a consumer group as `WARNING` for 15 minutes
- **THEN** a warning alert is recorded in the monitoring channel

### Requirement: Producer-side idempotence and batching
Any producer created by the platform (used for retry, DLQ, outbox-published-by-Debezium) SHALL configure franz-go with `enable.idempotence=true`, `compression.type=lz4`, `linger.ms=10`, `batch.size=131072`, `acks=all`, `max.in.flight.requests.per.connection=5`, `delivery.timeout.ms=120000`. The producer SHALL NOT be configured to silently swallow errors; every error SHALL be logged with the topic, partition, key, and the producer's internal `acks` state.

#### Scenario: Producer applies platform defaults
- **WHEN** a service constructs a producer through the platform's producer factory
- **THEN** the producer applies the documented idempotence and batching settings

#### Scenario: Producer error is not silently dropped
- **WHEN** the broker rejects a record (e.g., message-too-large)
- **THEN** the producer returns an error to the caller and the error is logged with the topic, key, and broker response code