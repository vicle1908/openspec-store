# reporting-projection Specification

## Purpose
The platform implements Read-only projection store The reporting service SHALL consume every domain event topic (`orders.events.v1`, `customers.events.v1`, `catalog.events.v1`, `notifications.events.v1`) and persist a denormalized projection of those events into the `report
## Requirements
> **Status**: IMPLEMENTED. Reporting service exists at services/reporting-service/ with Kafka consumers, projection writers, query API, and reporting schema migrations.

### Requirement: Read-only projection store
The reporting service SHALL consume every domain event topic (`orders.events.v1`, `customers.events.v1`, `catalog.events.v1`, `notifications.events.v1`) and persist a denormalized projection of those events into the `reporting` schema. The reporting service SHALL NOT write to any other service's schema. The reporting service SHALL NOT participate in any command path; its database transactions are read-from-Kafka-only and never block upstream producers. The `payments.events.v1` topic is RESERVED for a future payment service that is explicitly a non-goal of Phase 2 (the order-service keeps payment processing in-module per the proposal's Non-Goals section); when (and only when) that future service ships, the reporting consumer SHALL subscribe to it via the same fan-in mechanism — until then, the topic is not declared in the reporting consumer's subscription list and a missing-topic alert in the lgtm profile SHALL fire if a `payments.events.v1` topic is created without a corresponding reporting consumer registration.

#### Scenario: Reporting consumer is consumer-only
- **WHEN** the architecture tests run with the reporting service's module included
- **THEN** the test fails any code path that imports a producer SDK or that writes to a non-`reporting` schema

#### Scenario: Reporting does not block producers
- **WHEN** the reporting consumer is slower than the upstream producers
- **THEN** the producer's write path is not delayed by the reporting consumer

### Requirement: Projection tables
The reporting service SHALL maintain the projection tables `report_orders`, `report_customers`, `report_products`, `report_daily_revenue`, and `report_facts`. Each projection table SHALL carry `last_event_id` (the event envelope's `event_id`) and `last_event_offset` (the Kafka offset) so re-consumption after a consumer crash picks up where it left off. Every projection row SHALL be keyed by the original domain entity ID and SHALL include the source event's `occurred_at`, `correlation_id`, and `trace_id` for cross-referencing.

#### Scenario: Projection row stores cross-reference metadata
- **WHEN** the consumer processes a `ProductActivated` event
- **THEN** the `report_products` row stores `last_event_id`, `last_event_offset`, `occurred_at`, `correlation_id`, and `trace_id`

#### Scenario: Re-consumption resumes from the last offset
- **WHEN** the consumer restarts after a crash
- **THEN** it resumes from the last `last_event_offset` for the partition it owns

### Requirement: Reporting query API
The service SHALL expose `GET /api/v1/reports/orders?from=<iso>&to=<iso>&cursor=<token>`, `GET /api/v1/reports/customers/{id}/summary`, `GET /api/v1/reports/products/{id}/summary`, `GET /api/v1/reports/revenue?from=<iso>&to=<iso>&granularity=day|week|month>`, and `GET /api/v1/reports/facts/<name>?from=<iso>&to=<iso>`. The query API SHALL support pagination via cursor tokens and SHALL return `404 Not Found` for entities that exist in the source system but have not yet been projected.

#### Scenario: Orders report within a date range
- **WHEN** the API receives `GET /api/v1/reports/orders?from=2026-07-01&to=2026-07-15`
- **THEN** the response includes all orders whose `created_at` falls in the range and a `next_cursor` if more exist

#### Scenario: Customer summary returns 404 if not yet projected
- **WHEN** the API receives a customer summary request for a customer whose events have not yet been consumed
- **THEN** the response is `404 Not Found` with code `not_yet_projected`

### Requirement: Read consistency
The reporting query API SHALL return eventually-consistent results. The service SHALL document a freshness SLO (default: 95% of queries return data within 5 seconds of the source event being published) and SHALL expose `report_freshness_seconds` as a metric that operators can monitor.

#### Scenario: Freshness metric tracks lag
- **WHEN** the consumer processes a record
- **THEN** `report_freshness_seconds{topic="orders.events.v1",partition="0"}` is set to `now - record.occurred_at`

#### Scenario: SLO breach is observable
- **WHEN** `report_freshness_seconds` exceeds the SLO threshold
- **THEN** the metric exceeds the configured alert threshold and operators are notified

### Requirement: Late-arriving events
The reporting service SHALL handle late-arriving events by reconciling the projection row against the event's contents. If a projection row already exists for the entity, the late event SHALL trigger a deterministic merge that overwrites the projection with the event's contents, recording the source `event_id` and `occurred_at` in the row's `last_event_*` fields. The service SHALL NEVER silently lose a late event.

#### Scenario: Late event overwrites the projection
- **WHEN** an `OrderUpdated` event arrives after a `ProductActivated` event that referenced the same order
- **THEN** the `report_orders` row is updated to the latest contents of the order and `last_event_id` records the late event

#### Scenario: Late event does not duplicate revenue totals
- **WHEN** a `PaymentCaptured` event arrives twice for the same payment
- **THEN** the `report_daily_revenue` table is updated deterministically and the row count does not grow

### Requirement: Replay support
The reporting service SHALL expose a CLI command `reporting replay --topic=<topic> --from-offset=<n> --to-offset=<n>` that re-consumes events in the offset range and re-applies the projection logic. The replay SHALL be idempotent: re-applying events to the same projection produces the same row contents. The replay SHALL emit a metric `reporting_replay_events_total{topic}` so operators can monitor progress.

#### Scenario: Replay is idempotent
- **WHEN** the operator replays an event range twice
- **THEN** the projection rows are identical after both runs

#### Scenario: Replay emits a progress metric
- **WHEN** the replay processes a record
- **THEN** `reporting_replay_events_total{topic="orders.events.v1"}` is incremented by 1

### Requirement: Observability
The reporting service SHALL emit metrics for consumer lag (`report_consumer_lag_seconds{topic,partition}`), event consumption rate (`report_events_consumed_total{topic,event_type}`), projection table size (`report_table_rows{table}`), and query latency (`report_query_duration_seconds{endpoint}`). The service SHALL emit a structured log per consumer error including the event ID, the topic, the partition, the offset, the error reason, and the trace ID.

#### Scenario: Consumer lag metric is exposed
- **WHEN** the consumer is running
- **THEN** `report_consumer_lag_seconds` reflects the time between `now` and the most recent record's `occurred_at`

#### Scenario: Consumer error is logged
- **WHEN** the consumer fails to apply an event
- **THEN** the structured log records the event ID, topic, partition, offset, error reason, and trace ID

### Requirement: Kafka best practices for fan-in consumer groups
The reporting service SHALL subscribe to every in-scope domain event topic (`orders.events.v1`, `customers.events.v1`, `catalog.events.v1`, `notifications.events.v1`) via a single consumer group `reporting.projection.v1` with multiple consumer instances (one consumer per partition across all topics). The reporting service SHALL NOT use a separate consumer group per topic (a single group guarantees offset-commit ordering across topics, which the projection writers depend on). The reporting service SHALL use cooperative-sticky + static membership and SHALL configure `kgo.MaxConcurrentFetches(8)` to read from many topics concurrently. The reporting service SHALL NOT use a Kafka Streams EOS transaction; the projection writers SHALL be idempotent via the `(topic, partition, offset, event_id)` primary key on the `report_processed_events` table. The `payments.events.v1` topic is reserved (see the Read-only projection store requirement) but is NOT yet in this consumer group's subscription list.

#### Scenario: Single consumer group spans all topics
- **WHEN** the reporting consumer starts
- **THEN** it joins `reporting.projection.v1` and reads from every in-scope `<domain>.events.v1` topic (`orders`, `customers`, `catalog`, `notifications`)

#### Scenario: Multiple consumer instances share the partitions
- **WHEN** the reporting service scales to three replicas
- **THEN** each replica receives a subset of partitions across all topics via cooperative-sticky rebalancing

#### Scenario: Projection writes are idempotent
- **WHEN** a record is redelivered (consumer crash between projection write and offset commit)
- **THEN** the `(topic, partition, offset, event_id)` primary key on `report_processed_events` rejects the duplicate and the projection writer short-circuits

### Requirement: Burrow lag monitoring for the projection consumer
The reporting service SHALL export its consumer-group state to Burrow via the OTel Collector so the reporting-projection freshness SLO is observable from the platform's Grafana dashboard. The reporting service SHALL publish a Grafana panel that combines Burrow's `STOP`/`WARNING` state with the per-topic `report_consumer_lag_seconds` metric.

#### Scenario: Burrow classifies the projection consumer
- **WHEN** the reporting consumer is running and within SLO
- **THEN** Burrow reports `status=OK` and the Grafana panel shows green

#### Scenario: Burrow fires a STOP alert
- **WHEN** the reporting consumer falls more than 5 minutes behind
- **THEN** Burrow reports `status=STOP` and the platform alerts the on-call rota

### Requirement: Late-arriving event reconciliation
The reporting service SHALL handle late-arriving events by checking the `(aggregate_id, event_occurred_at, event_id)` tuple against the projection row. If the late event's `occurred_at` is older than the projection row's `last_event_occurred_at`, the late event is reconciled by replaying the aggregate's event history from the source topic starting at the offset of the late event. The replay SHALL be idempotent (the projection writer's primary key dedupes) and SHALL NOT block the main consumer (the replay runs on a dedicated Temporal workflow or a separate goroutine pool).

#### Scenario: Late event triggers replay
- **WHEN** an `OrderUpdated` event arrives whose `occurred_at` is older than the projection row's `last_event_occurred_at`
- **THEN** the reporting service enqueues a replay workflow that re-reads the aggregate's events from the offset of the late event and re-applies them idempotently

#### Scenario: Replay does not block the main consumer
- **WHEN** a replay is in progress
- **THEN** the main consumer continues processing new events from its assigned partitions

### Requirement: Temporal Schedules for daily reporting rollups
The reporting service SHALL use Temporal's Schedule API to schedule daily reporting rollups (e.g., `report_daily_revenue` aggregation). The Schedule SHALL run at `0 1 * * *` (1 AM UTC) and SHALL invoke the `ReportingRollupWorkflow` on task queue `reporting.rollup.v1`. The rollup workflow SHALL aggregate the day's events into the `report_daily_revenue` table and SHALL emit a `RollupCompleted` event.

#### Scenario: Schedule triggers daily rollup
- **WHEN** 1 AM UTC arrives
- **THEN** Temporal fires the `ReportingRollupWorkflow` and the rollup completes within 10 minutes

#### Scenario: Schedule recovers from a missed firing
- **WHEN** Temporal is unavailable during the scheduled time
- **THEN** the schedule's catchup window fires the workflow on the next available worker

