## Purpose

This specification defines requirements for Docs Sync Resilience.

## Requirements

### Requirement: Circuit breaker around LLM calls
The doc-sync LLM gateway wrapper SHALL use `agent_core.resilience.CircuitBreaker` per provider. The breaker SHALL open after 5 consecutive failures and recover after 30 seconds. When the breaker is open, LLM calls SHALL raise `CircuitBreakerOpenError` instead of making network requests.

#### Scenario: Circuit opens after consecutive failures
- **WHEN** the LLM provider returns 5 consecutive 5xx errors
- **THEN** the circuit breaker state transitions to OPEN

#### Scenario: Circuit rejects calls when open
- **WHEN** the circuit breaker is OPEN and a new LLM call is attempted
- **THEN** a `CircuitBreakerOpenError` is raised without making a network request

#### Scenario: Circuit half-opens after recovery timeout
- **WHEN** the circuit breaker has been OPEN for 30 seconds
- **THEN** the state transitions to HALF_OPEN and the next call is allowed through

### Requirement: Retry with jitter on transient errors
LLM calls SHALL be wrapped with `agent_core.resilience.retry_with_jitter`. Transient errors (5xx, timeouts, connection errors) SHALL be retried up to 3 times with exponential backoff (0.5s base, 30s max) plus random jitter. Non-transient errors (4xx, auth failures) SHALL NOT be retried.

#### Scenario: Transient error retried
- **WHEN** an LLM call fails with a 500 error
- **THEN** the call is retried up to 3 times with exponential backoff

#### Scenario: Non-transient error not retried
- **WHEN** an LLM call fails with a 401 auth error
- **THEN** the error is raised immediately without retry

### Requirement: Fallback chain for provider failover
The doc-sync gateway SHALL support optional fallback gateways via `agent_core.resilience.FallbackChain`. When `FALLBACK_LITELLM_URL` environment variable is set, a secondary provider is configured. If the primary provider's circuit is open, the next provider in the chain SHALL be attempted. If all providers fail, a `FallbackChainError` SHALL be raised.

#### Scenario: Fallback to secondary provider
- **WHEN** the primary provider (OmniRoute) circuit breaker is OPEN and FALLBACK_LITELLM_URL is configured
- **THEN** the fallback provider is attempted

#### Scenario: All providers exhausted
- **WHEN** all providers in the fallback chain have failed or have open circuits
- **THEN** a `FallbackChainError` is raised with details of all attempts

#### Scenario: No fallback configured
- **WHEN** FALLBACK_LITELLM_URL is not set
- **THEN** CircuitBreakerOpenError is raised directly when primary circuit opens

### Requirement: Degradation manager monitors system health
A `DegradationManager` SHALL monitor CPU usage and error rate. When CPU exceeds 85% or error rate exceeds 50/minute, the degradation level SHALL transition to REDUCED, capping agent iterations at 5. Recovery requires 60 seconds of sustained healthy metrics.

#### Scenario: Degradation triggers on high CPU
- **WHEN** CPU usage exceeds 85%
- **THEN** degradation level transitions to REDUCED and max iterations is capped at 5

#### Scenario: Recovery after sustained health
- **WHEN** CPU and error rate are healthy for 60 seconds
- **THEN** degradation level transitions back to NORMAL
