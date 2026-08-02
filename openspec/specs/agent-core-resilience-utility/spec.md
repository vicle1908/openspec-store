## Purpose

Define resilience primitives for agent-core: circuit breaker state machine, retry with exponential backoff, bulkhead isolation, and timeout enforcement — usable as decorators and programmatic APIs.

## Requirements

### Requirement: CircuitBreaker as standalone utility
The system SHALL provide `CircuitBreaker` as a standalone, decoupled utility with no agent-core dependencies.

#### Scenario: Exception decoupling
- **WHEN** `CircuitBreakerOpenError` is defined
- **THEN** it SHALL extend `RuntimeError` (not `GatewayError`)
- **AND** it SHALL have a `code` attribute for error classification

#### Scenario: State machine preserved
- **WHEN** `CircuitBreaker` is instantiated with `BreakerConfig`
- **THEN** it SHALL implement closed → open → half_open → closed transitions
- **AND** the state machine behavior SHALL be unchanged from the current implementation

#### Scenario: Registry preserved
- **WHEN** `CircuitBreakerRegistry` is instantiated
- **THEN** it SHALL manage named circuit breakers with snapshot capability

### Requirement: FallbackChain as standalone utility
The system SHALL provide `FallbackChain` as a generic async chain executor.

#### Scenario: Exception decoupling
- **WHEN** `FallbackChainError` is defined
- **THEN** it SHALL extend `RuntimeError` (not `GatewayError`)

#### Scenario: Generic callback interface
- **WHEN** `FallbackChain.execute(fn)` is called
- **THEN** `fn` SHALL be called with `(provider_name, *args, **kwargs)` in priority order
- **AND** open circuit breakers SHALL be skipped

### Requirement: retry_with_jitter as standalone utility
The system SHALL provide `retry_with_jitter` as a zero-dependency async retry decorator.

#### Scenario: Pluggable retryable predicate
- **WHEN** `retry_with_jitter(fn, retryable=my_classifier)` is called
- **THEN** the custom `retryable` function SHALL determine which errors trigger retry

#### Scenario: Exponential backoff with jitter
- **WHEN** a retryable error occurs
- **THEN** the delay SHALL be between `backoff_min` and `backoff_max` seconds
- **AND** jitter SHALL be applied to prevent thundering herd

### Requirement: DegradationManager removed
The `DegradationManager`, `DegradationConfig`, and `DegradationLevel` classes SHALL be removed.

#### Scenario: Agent-loop-specific code removed
- **WHEN** the cleanup is applied
- **THEN** `DegradationManager` SHALL not exist in the codebase
- **AND** `DegradationConfig` SHALL not exist
- **AND** `DegradationLevel` SHALL not exist
- **AND** `psutil` SHALL be checked for other usage; if unused, removed from `pyproject.toml`

### Requirement: ResilienceSettings removed
The `ResilienceSettings` class SHALL be removed from `foundation/settings.py`.

#### Scenario: Settings cleanup
- **WHEN** the cleanup is applied
- **THEN** `ResilienceSettings` SHALL not exist in `foundation/settings.py`
- **AND** the `resilience` field SHALL be removed from the root `Settings` model
- **AND** `RESILIENCE_*` environment variables SHALL no longer be parsed
- **AND** the `resilience` section SHALL be removed from `config.yaml.example`
