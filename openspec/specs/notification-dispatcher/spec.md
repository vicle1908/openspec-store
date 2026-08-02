# notification-dispatcher Specification

## Purpose
Define durable notification dispatch through an atomic transactional outbox,
Debezium CDC, Kafka delivery, provider abstraction, and retry-safe state
transitions.
## Requirements
### Requirement: Outbox-driven dispatch

> **Status**: PARTIAL. Compose/kind now register a canonical connector and
> retained local acceptance proves synthetic `notification.outbox` delivery to
> the implemented `notifications.events.v1` stream. The application unit of
> work does not yet persist its buffered outbox records atomically, and the
> required `notifications.dispatch.v1` dispatcher stream therefore remains
> unimplemented.

The notification service SHALL publish an outbox record in the same transaction as the notification's status change to `dispatching`. A Debezium connector SHALL read the outbox table and publish the corresponding record to the `notifications.dispatch.v1` topic. The dispatcher SHALL consume that topic, perform the provider call, and update the notification's status. This pattern SHALL ensure that the dispatch is at-least-once and that the database and Kafka are kept consistent.

#### Scenario: Outbox record is created atomically with state change
- **WHEN** the application transitions a notification from `pending` to `dispatching`
- **THEN** an outbox row referencing the notification ID is created in the same database transaction

#### Scenario: Outbox record is published to Kafka via Debezium
- **WHEN** the Debezium outbox connector observes a new outbox row
- **THEN** a record is published to `notifications.dispatch.v1` with the notification ID as the key and the dispatch request as the value

### Requirement: Provider abstraction

> **Status**: PARTIAL. Provider interface exists; concrete providers (SMTP, SES, Twilio, FCM) may be partial.

The dispatcher SHALL define a `NotificationProvider` interface with methods `Send(ctx, notification) (providerMessageID, error)`. The service SHALL register concrete providers for SMTP, SES, Twilio, and FCM; the active provider is selected per channel via configuration. New providers SHALL be added without changes to the dispatcher's core flow.

#### Scenario: SMTP provider sends email
- **WHEN** the dispatcher processes a notification with `channel=email` and the configured provider for email is `smtp`
- **THEN** the SMTP provider's `Send` is invoked and the provider's message ID is stored on the notification

#### Scenario: Provider failure causes retry
- **WHEN** the provider's `Send` returns a transient error
- **THEN** the notification transitions `dispatching → failed` with `failure_reason=<error>` and `next_attempt_at` is set using exponential backoff

#### Scenario: Provider non-retryable failure causes cancellation
- **WHEN** the provider's `Send` returns a `NonRetryableError`
- **THEN** the notification transitions `dispatching → failed` and the dispatch attempt is not retried

### Requirement: Exponential backoff

> **Status**: IMPLEMENTED. Exponential backoff with configurable base and max delay implemented.

The dispatcher SHALL retry transient failures with exponential backoff: `delay = base * 2^(attempt-1)` capped at `max_delay`. The default base is 30 seconds and the default max is 1 hour. Attempt count is part of the notification's persisted state; the dispatcher SHALL NOT re-read the count from external state.

#### Scenario: First retry delay is the base
- **WHEN** a notification fails on attempt 1
- **THEN** `next_attempt_at` is set to `now + 30s`

#### Scenario: Later retry delay is capped at max
- **WHEN** a notification fails on attempt 10 with `base=30s` and `max=1h`
- **THEN** `next_attempt_at` is set to `now + 1h`

### Requirement: Rate limiting per channel

> **Status**: PARTIAL. Rate limiting schema exists; token-bucket implementation may be partial.

The dispatcher SHALL enforce a configurable per-channel rate limit (default 100 requests per second per channel) using a token-bucket algorithm. When the bucket is empty, the dispatcher SHALL delay the dispatch by the replenishment interval rather than failing the notification.

#### Scenario: Channel rate limit delays dispatch
- **WHEN** the email channel's bucket is empty
- **THEN** the dispatcher schedules `next_attempt_at` to `now + replenishment_interval` and the notification remains in `pending`

#### Scenario: Channel rate limit does not affect other channels
- **WHEN** the SMS channel's bucket is full but the email channel's bucket is empty
- **THEN** SMS dispatches proceed normally

### Requirement: Provider-call idempotency

> **Status**: IMPLEMENTED. Idempotency key derived from notification_id and attempt; deduplication enforced.

Each provider call SHALL carry an idempotency key derived from `(notification_id, attempt)`. The provider SHALL NOT receive the same idempotency key twice for the same notification. If the provider acknowledges a duplicate idempotency key, the dispatcher SHALL treat the call as a no-op success.

#### Scenario: Same notification, same attempt, replays are deduplicated
- **WHEN** the dispatcher retries a notification with the same attempt count
- **THEN** the provider receives the same idempotency key and treats the call as a duplicate

### Requirement: Dispatch observability

> **Status**: IMPLEMENTED. Dispatch metrics emitted; structured logging with notification_id, attempt, channel.

The dispatcher SHALL emit metrics `notifications_dispatch_total{channel, status}`, `notifications_dispatch_duration_seconds{channel}`, and `notifications_dispatch_attempts_total{channel}`. The dispatcher SHALL emit a structured log per dispatch attempt including `notification_id`, `attempt`, `channel`, `provider`, `provider_message_id` (when available), and `trace.id`.

#### Scenario: Dispatch success increments the success counter
- **WHEN** the dispatcher successfully sends a notification
- **THEN** `notifications_dispatch_total{channel="email",status="success"}` is incremented by 1

#### Scenario: Dispatch failure increments the failure counter
- **WHEN** the provider returns a transient error
- **THEN** `notifications_dispatch_total{channel="email",status="retry"}` is incremented by 1 and the structured log records the failure reason

### Requirement: Durable receipts and gap detection

> **Status**: IMPLEMENTED. Durable receipts persisted; duplicate notifications prevented via receipt table.

The dispatcher SHALL persist a durable receipt per `(source_event_id, template_id, recipient_id)` so a replayed source event cannot create a duplicate notification. The receipt table SHALL be consulted before any new notification is created; an existing receipt short-circuits the creation path.

#### Scenario: Receipt prevents duplicate notifications from event replay
- **WHEN** the consumer processes two records for the same `OrderShipped` event
- **THEN** the second record's processing is a no-op and the receipt table records the deduplication

### Requirement: Replayable quarantine

> **Status**: PARTIAL. Quarantine schema exists; operator retry mechanism may be partial.

Notifications that fail dispatch after the maximum attempt count SHALL be marked `failed` with `failure_reason=max_attempts_exceeded` and quarantined for operator review. An operator SHALL be able to retry a quarantined notification via a CLI command that transitions the notification back to `pending` with `attempts=0`.

#### Scenario: Max-attempts notification is quarantined
- **WHEN** a notification reaches the maximum attempt count
- **THEN** the notification is in state `failed` with reason `max_attempts_exceeded` and an entry exists in the quarantine table

#### Scenario: Operator retries a quarantined notification
- **WHEN** an operator runs `notification retry --id <notification-id>`
- **THEN** the notification transitions back to `pending` with `attempts=0` and the dispatcher picks it up on the next tick

### Requirement: Provider rate limiting via the cache (capability-gated)

> **Status**: DEFERRED. Cache-based rate limiting not yet implemented; relies on provider native rate limiting.

When the dispatcher needs per-channel rate limiting beyond what the SMTP/SES/Twilio/FCM providers offer natively, the service SHALL use the platform's cache module with a Redis or Valkey adapter. The canonical cache key SHALL be `notification:ratelimit:{<provider_channel>}:{<minute_epoch>}` (a 4-segment key matching `platform-cache` Requirement 3, with the `<provider_channel>` wrapped in `{...}` so Redis Cluster hashes the composite keys to the same slot, see the Multi-key operations and hash tags requirement in `platform-cache`). The TTL SHALL be `TTLShort` (5 seconds, with the `{<minute_epoch>}` segment intentionally rolling to a new value at the next minute boundary so any key naturally expires before the next slot needs it). The rate-limit operation SHALL be implemented as a Lua script (or `INCR` + `EXPIRE NX` piped) to avoid the INCR/EXPIRE race. If the platform's cache module is not admitted by the service's ADR, the dispatcher SHALL rely on the provider's native rate limiting and the platform's `kafka_consumer_records_throttled_total` metric for monitoring.

#### Scenario: Per-minute rate limit delays dispatch
- **WHEN** the email channel's per-minute counter exceeds the limit
- **THEN** the dispatcher sets `next_attempt_at = now + 5s` and the notification remains in `pending`

#### Scenario: Rate limit respects the hash tag pattern
- **WHEN** the rate-limit Lua script is called
- **THEN** all keys carry the same `{<provider_channel>}` hash tag so they share a slot in Cluster mode

#### Scenario: Service without cache ADR does not use cache
- **WHEN** the service's ADR file does not authorize a cache dependency
- **THEN** the dispatcher does NOT import the cache package and the architecture test fails if it does
