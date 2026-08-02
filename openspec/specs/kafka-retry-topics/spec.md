# kafka-retry-topics Specification

## Purpose
The platform implements Kafka retry-topic chain for reliable message processing. Failed messages are retried with exponential backoff before being sent to a dead-letter topic for manual inspection.

## Requirements

> **Status**: IMPLEMENTED. RetryConsumer with configurable retry chains, exponential backoff, dead-letter topics, and retry metadata headers.

### Requirement: Retry topic chain

> **Status**: IMPLEMENTED. RetryConsumer exists in platform/kafka with configurable retry chains.

The platform SHALL support configurable retry-topic chains for all Kafka consumers. Each retry level SHALL have its own topic with increasing TTL delays. The retry chain SHALL route failed messages through `retry-1`, `retry-2`, ..., `retry-N` topics before sending to the dead-letter topic.

#### Scenario: Message fails and enters retry chain
- **WHEN** a consumer fails to process a message from `topic.order.created`
- **THEN** the message is published to `topic.order.created.retry-1` with a TTL of 30 seconds

#### Scenario: Message exhausted retries
- **WHEN** a message fails processing on the final retry level (`retry-N`)
- **THEN** the message is published to `topic.order.created.dead-letter` with all retry metadata preserved

### Requirement: Retry metadata

> **Status**: IMPLEMENTED. Retry headers (x-retry-count, x-original-topic) implemented in RetryConsumer.

Each retried message SHALL include headers `x-retry-count` (integer, incremented per retry) and `x-original-topic` (string, the first topic the message was published to). The consumer SHALL NOT increment `x-retry-count` beyond the configured maximum.

#### Scenario: Retry count is preserved across retries
- **WHEN** a message with `x-retry-count=2` fails processing
- **THEN** the message is republished with `x-retry-count=3`

#### Scenario: Retry count is not exceeded
- **WHEN** a message with `x-retry-count=3` (the maximum) fails processing
- **THEN** the message is published to the dead-letter topic, not back to the retry chain

### Requirement: Dead-letter topic

> **Status**: IMPLEMENTED. Dead-letter topic support exists in Kafka retry chain.

The dead-letter topic SHALL retain messages for 7 days (configurable). Messages in the dead-letter topic SHALL include the original payload, retry count, original topic, and the error message from the final failure. A dead-letter consumer SHALL be available for manual inspection and replay.

#### Scenario: Dead-letter message includes error context
- **WHEN** a message lands in the dead-letter topic
- **THEN** the message headers include `x-error-message` (string) with the last processing error

### Requirement: Exponential backoff

> **Status**: IMPLEMENTED. Exponential backoff with configurable base delay and multiplier implemented.

The retry delay SHALL follow exponential backoff: `base_delay * backoff_multiplier^(retry_count - 1)`. The base delay defaults to 30 seconds and the multiplier defaults to 2.0. Jitter of up to 10% SHALL be applied to prevent thundering herd.

#### Scenario: Retry delays increase exponentially
- **WHEN** a message enters retry-1 with base_delay=30000ms and multiplier=2.0
- **THEN** retry-1 has TTL ~30s, retry-2 has TTL ~60s, retry-3 has TTL ~120s

### Requirement: Consumer integration

> **Status**: IMPLEMENTED. Retry logic integrated via platform/kafka package; consumers signal success/failure.

The retry-topic producer SHALL be injected into consumers via the `pkg/kafkax` package. Consumers SHALL NOT need to implement retry logic directly; they SHALL only signal success or failure.

#### Scenario: Consumer signals failure
- **WHEN** a consumer returns an error from message processing
- **THEN** the retry-topic producer automatically routes the message to the appropriate retry level

#### Scenario: Consumer signals success
- **WHEN** a consumer returns nil from message processing
- **THEN** the message is committed and no retry is triggered
