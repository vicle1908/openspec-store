# Phase 5: Platform Features — Design

**Status:** Proposed
**Date:** 2026-07-17

## 1. Kafka Retry-Topic Chain

### Architecture

```
Producer
  |
  v
[topic.order.created]
  |
  v
Consumer (order-service)
  | failure
  v
[topic.order.created.retry-1]  (TTL: 30s)
  | failure
  v
[topic.order.created.retry-2]  (TTL: 60s)
  | failure
  v
[topic.order.created.dead-letter]  (no consumer, manual inspection)
```

### Design Decisions

- **Retry count:** Configurable per consumer, default 3 retries
- **Backoff:** Exponential with jitter, starting at 30s per retry level
- **Dead-letter retention:** 7 days, configurable
- **Message format:** Original message preserved with retry metadata header (`x-retry-count`, `x-original-topic`)

### Implementation

```
pkg/kafkax/
  retry.go          — RetryTopicProducer wraps sarama/segmentio producer
  dead_letter.go    — DeadLetterHandler for final failure
  consumer.go       — EnhancedConsumer with retry-topic routing
```

### Configuration

```yaml
kafka:
  retry:
    enabled: true
    max_retries: 3
    base_delay_ms: 30000
    backoff_multiplier: 2.0
  dead_letter:
    enabled: true
    retention_days: 7
```

## 2. Circuit Breaker Pattern

### States

```
CLOSED ──(failure threshold)──> OPEN
  ^                                |
  |                          (timeout)
  |                                v
  |                           HALF-OPEN
  |                                |
  └────(success threshold)────────┘
```

### Configuration

```yaml
circuit_breaker:
  enabled: true
  failure_threshold: 5
  recovery_timeout_ms: 30000
  half_open_max_calls: 3
  success_threshold: 2
```

### Implementation

```
pkg/resilience/
  circuit_breaker.go   — CircuitBreaker struct and state machine
  middleware.go        — HTTP and gRPC middleware wrappers
```

### Middleware Usage

```go
// HTTP client
cb := resilience.NewCircuitBreaker("order-service", config)
client := cb.HTTPClient(transport)

// gRPC client
conn, _ := grpc.Dial(addr, grpc.WithUnaryInterceptor(cb.UnaryClientInterceptor()))
```

### Failure Criteria

- HTTP: 5xx responses count as failures; 4xx does not
- gRPC: UNAVAILABLE, DEADLINE_EXCEEDED, INTERNAL count as failures
- Timeout: Calls exceeding configured deadline count as failures

## 3. Fuzz Testing Strategy

### Scope

Fuzz tests for HTTP handler input parsing across three services:

| Service | Fuzz Target | What is tested |
|---------|------------|----------------|
| customer-service | `FuzzHTTPHandler` | JSON deserialization of customer create/update payloads |
| notification-service | `FuzzHTTPHandler` | JSON deserialization of notification send payloads |
| catalog-service | `FuzzHTTPHandler` | JSON deserialization of product create/update payloads |

### Approach

1. Seed corpus includes valid JSON, empty objects, and invalid input
2. Fuzz tests verify that handlers do not panic on arbitrary input
3. Tests run in CI nightly; local developers can run with `go test -fuzz`

### File Structure

```
services/<service>/test/fuzz/http_test.go
```

## 4. Worker Versioning v2 (Design Phase)

### Current State

- Single workflow version with no migration path
- Any workflow patch requires a full restart

### Proposed Strategy

- Use Temporal's `deprecation` annotations
- Define version ranges with `workflow.GetVersion()`
- Support 2 concurrent versions during migration windows
- Deprecation policy: 30-day grace period

### Migration Steps

1. Add version checks to existing workflows
2. Create new workflow definition with patch
3. Deploy with both versions active
4. Monitor: wait for all in-flight workflows on old version to complete
5. Remove old version code
