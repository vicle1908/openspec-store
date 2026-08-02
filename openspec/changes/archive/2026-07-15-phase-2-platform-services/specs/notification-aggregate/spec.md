## ADDED Requirements

### Requirement: Notification aggregate
The notification service SHALL own a `Notification` aggregate whose identity is a ULID minted at creation, with fields `recipient_id`, `channel` (one of `email`, `sms`, `push`), `template_id`, `template_version`, `payload` (validated against the template's schema), `subject`, `status` (one of `pending`, `dispatching`, `delivered`, `failed`, `cancelled`), `attempts`, `last_attempt_at`, `next_attempt_at`, `failure_reason`, and `version`. The aggregate SHALL be persisted in the `notifications` table within the `notification` schema. The aggregate SHALL be rehydrated from its persisted state without losing the version number; attempting to rehydrate with a stale `version` returns a typed concurrency conflict.

#### Scenario: Notification created from a domain event
- **WHEN** the notification consumer reads an `OrderShipped` event
- **THEN** a `Notification` aggregate is created in state `pending` with `recipient_id` from the event's customer ID and `template_id` from the event's template hint

#### Scenario: Stale version rehydrate returns a conflict
- **WHEN** the consumer rehydrates a notification with `version=3` but the persisted row has `version=5`
- **THEN** the repository returns `ErrConcurrencyConflict`

### Requirement: Notification creation idempotency
Creating a notification SHALL require an idempotency key. Two notification-creation requests carrying the same `(idempotency_key, template_id, recipient_id)` tuple SHALL produce exactly one notification row; the second request returns the original notification ID without creating a new row. The idempotency key SHALL be carried as an HTTP header on the synchronous create endpoint and as a Kafka header on the event-driven create path.

#### Scenario: Duplicate HTTP create returns the original
- **WHEN** two HTTP POSTs to `/api/v1/notifications` carry the same `Idempotency-Key`
- **THEN** the second response is `200 OK` with the original notification's ID and the database has exactly one row

#### Scenario: Duplicate event-driven create returns the original
- **WHEN** the consumer reads two records for the same `(source_event_id, template_id)` within the idempotency window
- **THEN** the second record's processing is a no-op and the receipt table records a deduplication

### Requirement: Template versioning
The notification service SHALL enforce that a `template_id` is paired with an explicit `template_version`; the dispatcher SHALL load the template by ID and version at dispatch time. Templates SHALL be immutable: once a version is published, it SHALL NOT change. New versions are added; old versions remain dispatchable for the retention window.

#### Scenario: Dispatcher uses the requested template version
- **WHEN** a notification references `template_id=order_shipped` and `template_version=3`
- **THEN** the dispatcher loads the v3 template, not the latest, and renders the payload against v3

#### Scenario: Missing template version returns a typed error
- **WHEN** a notification references a `template_version` that does not exist
- **THEN** the dispatcher returns `ErrTemplateVersionNotFound` and the notification is marked `failed` with that reason

### Requirement: Status transitions
The notification aggregate SHALL transition only through the documented states: `pending → dispatching → delivered`, `pending → dispatching → failed → pending` (retry), `pending → cancelled`, and `failed → cancelled`. Any other transition returns `ErrInvalidStatusTransition` and the change is not persisted.

#### Scenario: Invalid transition is rejected
- **WHEN** code attempts to transition a `delivered` notification back to `pending`
- **THEN** the aggregate returns `ErrInvalidStatusTransition`

#### Scenario: Retry transition is allowed
- **WHEN** a `failed` notification is dispatched again
- **THEN** the aggregate transitions `failed → pending` with the attempt counter incremented

### Requirement: Kafka best practices for notification consumption
The notification service SHALL consume `orders.events.v1` and `payments.events.v1` via the platform's Kafka harness. The consumer SHALL be configured with cooperative-sticky balancing and K8s-static membership via `kgo.InstanceID(<pod-name>)`. The consumer SHALL subscribe to a single topic per consumer group, partitioned by `customer_id` (the notification dispatcher is a fan-out consumer — every notification consumer must see every record). The consumer SHALL use the platform's retry-topic pattern; for notification the retry chain on source topic `notifications.dispatch.v1` is `notifications.dispatch.v1.retry.1000`, `notifications.dispatch.v1.retry.8000`, `notifications.dispatch.v1.retry.60000`, `notifications.dispatch.v1.retry.300000`, `notifications.dispatch.v1.retry.1800000` and the DLQ is `notifications.dispatch.v1.dlq`. The consumer SHALL persist a `processed_events` table keyed on `(consumer_group, event_id)` for inbox-style dedupe; the consumer's Postgres transaction inserts the processed-event row before invoking the dispatcher.

#### Scenario: Cooperative-sticky assignment on consumer startup
- **WHEN** the consumer starts
- **THEN** the assignment is computed by `kgo.CooperativeStickyBalancer()` and the partition assignment is sticky across rebalances

#### Scenario: Inbox dedupe before dispatch
- **WHEN** the consumer reads a record from `orders.events.v1`
- **THEN** the consumer's Postgres transaction inserts a `(consumer_group, event_id)` row; a unique violation aborts the dispatch path

#### Scenario: Retryable failure routes to retry topic
- **WHEN** the dispatcher returns a `RetryableError`
- **THEN** the consumer publishes the record to `<source-topic>.retry.1000` with `retry-attempt: 1` (for the notification event stream, the source topic is `notifications.dispatch.v1` and the retry topic is `notifications.dispatch.v1.retry.1000`; the DLQ is `notifications.dispatch.v1.dlq` and is NOT a `.retry.*` topic)

### Requirement: Temporal best practices for the dispatch workflow
The dispatch workflow SHALL use the platform's `temporal.NewSaga(...)` helper. The workflow SHALL register under `notification.dispatch.v1` and the worker SHALL be on task queue `notification.dispatch.v1` with Worker Versioning v2 `DeploymentSeriesName=notification-dispatch.v1`. The dispatch activity SHALL declare `StartToCloseTimeout=30s` and `ScheduleToCloseTimeout=5m`. The activity SHALL use `record.Heartbeat(ctx, NotificationProgress{Attempted: n})` every 10 seconds so the platform can detect a stuck dispatch. The workflow ID SHALL be derived as `notification/<notification-id>`. The workflow SHALL use `WorkflowIDReusePolicy=USE_EXISTING` for idempotent re-deliveries.

#### Scenario: Worker registers with versioning
- **WHEN** the worker starts
- **THEN** it registers under `DeploymentSeriesName=notification-dispatch.v1` with a non-empty build ID

#### Scenario: Activity heartbeats
- **WHEN** the dispatch activity runs for more than 10 seconds
- **THEN** the activity calls `RecordHeartbeat` at least once per 10 seconds

#### Scenario: Workflow ID reuse short-circuits duplicate delivery
- **WHEN** the consumer starts a workflow for `notification/<notification-id>` and the workflow already exists
- **THEN** Temporal returns the existing workflow handle