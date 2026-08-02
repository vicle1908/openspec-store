## ADDED Requirements

### Requirement: Platform projection pattern is generic and reusable
The platform SHALL export a generic projection library (`platform/projection`) that any service MAY use to build a consumer-only projection of domain events. The library SHALL provide:

1. A consumer group registry keyed by projection name.
2. A writer abstraction (`ProjectionWriter`) that atomically applies a projected row + advances `last_event_offset` in the same transaction.
3. A freshness reporter (`FreshnessReporter`) that publishes `report_freshness_seconds` to OTel metrics.
4. A reconciliation tool that, given a topic and a projection name, scans the projection table for partitions where `last_event_offset` is more than 5 minutes behind the broker's high-water mark, and emits a structured report.

#### Scenario: Platform projection library is imported by reporting-service
- **WHEN** the reporting-service module's `internal/adapters/projection/writer.go` is read
- **THEN** the writer imports `github.com/victory1908/platform/projection` and uses the platform's `ProjectionWriter` interface, not a hand-rolled Kafka-to-Postgres pipeline

#### Scenario: Platform projection library is NOT imported by command-path services
- **WHEN** the architecture test runs across every Phase-2 service module
- **THEN** no command-path service (`order-service`, `customer-service`, `catalog-service`, `notification-service`) imports `platform/projection` — only `reporting-service` does

### Requirement: Projection tables track source-event cursor
Every projection table written via `platform/projection` SHALL carry `last_event_id`, `last_event_offset`, `last_event_partition`, and `last_event_published_at` columns, indexed by `(topic, partition)`. The platform SHALL provide a SQL migration scaffold that emits the canonical columns.

#### Scenario: Canonical columns are present in every projection table
- **WHEN** `pg_attribute` is queried for the columns of a table created via the platform's projection migration scaffold
- **THEN** the columns `last_event_id`, `last_event_offset`, `last_event_partition`, `last_event_published_at` are present (verified by `tests/platform/projection_columns_test.go`)

#### Scenario: Consumer crash recovery resumes from the last offset
- **WHEN** the consumer restarts after a crash
- **THEN** the platform's consumer reads `last_event_offset` from the projection row for `(topic, partition)` and seeks to that offset, verified by `report_facts.last_event_offset` advancing monotonically across the run

### Requirement: Projection writes are atomic with cursor advance
The platform SHALL guarantee that the projection row write and the cursor advance happen in the same Postgres transaction. If the transaction aborts, both the projection row and the cursor are unchanged.

#### Scenario: Projection writer rolls back on duplicate key
- **WHEN** the projection writer applies a row that collides with an existing primary key
- **THEN** the transaction is rolled back, the cursor is not advanced, and the event is retried after a consumer rebalance

#### Scenario: Projection writer rolls back on connection loss
- **WHEN** the Postgres connection is severed mid-transaction
- **THEN** the writer returns a wrapped `ErrProjectionWriteAborted`, the cursor is not advanced, and the event is re-delivered on the next poll

### Requirement: Freshness metric is published per projection
Every projection SHALL publish `report_freshness_seconds{projection="<name>",topic="<topic>",partition="<partition>"}` to OTel metrics. The metric is updated on every successful projection write and exposes the wall-clock lag between the source event's `published_at` and the projection write timestamp.

#### Scenario: Freshness metric advances on each projection write
- **WHEN** the consumer applies a projected row
- **THEN** the platform's `FreshnessReporter` records the lag (`now - last_event_published_at`) to the `report_freshness_seconds` histogram

#### Scenario: Freshness metric is queryable in Mimir
- **WHEN** an operator queries `rate(report_freshness_seconds_sum[5m]) / rate(report_freshness_seconds_count[5m])` in Mimir
- **THEN** the result is the rolling average projection lag in seconds, scoped per projection name, topic, and partition

### Requirement: Reconciliation tool surfaces stuck projections
The platform SHALL export a CLI `cmd/projection-reconcile` that, given a topic and a projection name, scans the projection table for partitions where the broker's high-water mark is more than 5 minutes ahead of the projection's `last_event_offset`, and writes a JSON report to stdout (or to the path given by `--output`).

#### Scenario: Reconciliation tool exits 0 when projections are caught up
- **WHEN** the platform's `cmd/projection-reconcile` runs and every partition's `last_event_offset` is within 5 minutes of the broker's high-water mark
- **THEN** the tool exits 0 and the JSON report's `stuck_partitions` array is empty

#### Scenario: Reconciliation tool exits 1 when projections lag
- **WHEN** the platform's `cmd/projection-reconcile` runs and at least one partition's `last_event_offset` is more than 5 minutes behind the broker's high-water mark
- **THEN** the tool exits 1 and the JSON report's `stuck_partitions` array lists the offending `(topic, partition, lag_seconds)` triples

### Requirement: Projection writers never block upstream producers
The platform's projection consumer SHALL be configured to consume at a rate that does not impose backpressure on the upstream broker. The platform SHALL NOT use `MaxConcurrentFetches=1`; it SHALL use `kgo.MaxConcurrentFetches(8)` (or higher) and SHALL commit offsets asynchronously. The consumer SHALL use `kgo.DisableAutoCommit()` plus `kgo.CommitMarkedOffsets(...)` after each successful batch (the platform's `platform/kafka` consumer pattern documented in `platform-kafka-harness` Requirement 9); franz-go does not expose a `kafka.CommitMessageSync` API, and a synchronous per-record commit would impose backpressure on upstream producers.

#### Scenario: Projection consumer commits asynchronously
- **WHEN** the projection consumer processes a batch of records
- **THEN** the consumer commits offsets via `kgo.DisableAutoCommit` + `kgo.CommitMarkedOffsets` after each successful batch, verified by the absence of any synchronous per-record commit call in `platform/projection/consumer.go`

#### Scenario: Burrow reports non-zero consumer lag without alerting
- **WHEN** the projection consumer is intentionally slow (e.g., during a backfill)
- **THEN** Burrow reports the lag as a number, but the Burrow alert rule `consumer_lag_amber` only fires when the lag exceeds 10 minutes (the threshold is set in the platform's `burrow-alerts.yaml`)