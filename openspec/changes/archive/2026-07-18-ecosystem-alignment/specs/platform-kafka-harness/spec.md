# platform-kafka-harness Delta Spec

> **Change**: ecosystem-alignment
> **Base**: openspec/specs/platform-kafka-harness/spec.md
> **Date**: 2026-07-18

## Purpose

This delta documents the DEFERRED status of the Kafka retry-topic chain with evidence of what exists and what is missing.

---

## MODIFIED Requirements

### Requirement: Retry topic pattern (non-blocking retries)

> **Status**: DEFERRED. The consumer publishes to a retry topic on `RetryableError` but the full retry-topic chain is not implemented. The existing retry topics use sequential naming without delay semantics. No RetryConsumer reads from retry topics and re-publishes after a delay. DLQ routing after final retry is not implemented.

The consumer SHALL be configured with a retry topic chain: `<source-topic>.retry.1000`, `<source-topic>.retry.8000`, `<source-topic>.retry.60000`, `<source-topic>.retry.300000`, `<source-topic>.retry.1800000`. Each retry topic carries the same payload as the source topic plus a `retry-attempt` header (1-based) and the original `traceparent` and `X-Correlation-Id` headers. The platform SHALL provide a `RetryConsumer` that reads a retry topic, sleeps for the configured delay, then re-publishes the record to the source topic. After the final retry attempt, the consumer SHALL route the record to `<source-topic>.dlq`.

#### Scenario: Retryable error routes to first retry topic with delay

- **WHEN** the processor returns `RetryableError` for the first time on a record
- **THEN** the consumer publishes the record to `<source-topic>.retry.1000` with `retry-attempt: 1` and the original headers preserved

#### Scenario: RetryConsumer delays before re-publishing

- **WHEN** the RetryConsumer reads a record with `retry-attempt: 1` from `<source-topic>.retry.1000`
- **THEN** the RetryConsumer waits 1 second and re-publishes the record to the source topic with `retry-attempt: 2`

#### Scenario: Terminal retry routes to DLQ

- **WHEN** the processor returns `RetryableError` for the fifth time (after exhausting `.retry.1800000`)
- **THEN** the consumer publishes the record to `<source-topic>.dlq` with the original headers and error reason

#### Scenario: Non-retryable error routes directly to DLQ

- **WHEN** the processor returns `NonRetryableError`
- **THEN** the consumer publishes the record to `<source-topic>.dlq` immediately, skipping the retry chain
