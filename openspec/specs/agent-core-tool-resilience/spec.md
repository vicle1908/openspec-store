## Purpose

Define tool-level resilience patterns: retry policies for flaky tools, circuit breaker integration for tool registries, timeout enforcement per tool call, and degraded-mode fallbacks when tools are unavailable.

## Requirements

### Requirement: Resilient tool decorator
A `@resilient_tool` decorator SHALL provide retry and circuit-breaker wrapping for tool execution.

#### Scenario: Transient error retry
- **WHEN** a tool raises a transient error (ConnectionError, TimeoutError, OSError)
- **THEN** the decorator SHALL retry up to `max_retries` times with exponential backoff via `retry_with_jitter`
- **AND** non-transient errors SHALL be raised immediately
- **AND** `CircuitBreakerOpenError` SHALL NOT be retried

#### Scenario: Circuit breaker per tool
- **WHEN** a tool fails `failure_threshold` times
- **THEN** subsequent calls SHALL raise `CircuitBreakerOpenError` immediately
- **AND** after `recovery_timeout_seconds`, a probe call SHALL be attempted

#### Scenario: Configurable retryable predicate
- **WHEN** `retryable=my_classifier` is passed to the decorator
- **THEN** the custom classifier SHALL determine which errors trigger retry
- **AND** the default predicate SHALL retry ConnectionError, TimeoutError, OSError

#### Scenario: ToolResult not retried
- **WHEN** a tool returns `ToolResult(success=False)`
- **THEN** the decorator SHALL NOT retry (handled failures are not transient errors)

### Requirement: Module-level tool breaker registry
A `CircuitBreakerRegistry` instance SHALL manage per-tool circuit breakers.

#### Scenario: Breaker per tool name
- **WHEN** a resilient tool is executed
- **THEN** a `CircuitBreaker` SHALL be created with the tool's `metadata.name`
- **AND** subsequent calls to the same tool SHALL share the same breaker
