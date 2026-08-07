# Agent Docs Sync Resilience Specification

## Purpose

Define resilience patterns for docs-sync: circuit breaker and retry around LLM calls, degradation management for unavailable services, and graceful fallback when code intelligence sources are unreachable.

## Requirements

### Requirement: Fallback model with retry
The doc-sync LLM model wrapper SHALL use pydantic-ai's `FallbackModel` with native retry for provider resilience. The fallback SHALL attempt the primary model first, then fall back to secondary providers. Transient errors SHALL be retried up to 3 times with exponential backoff.

#### Scenario: Fallback to secondary model
- **WHEN** the primary model (OmniRoute) is unavailable
- **THEN** the fallback model is attempted via FallbackModel

#### Scenario: All models exhausted
- **WHEN** all models in the fallback chain have failed
- **THEN** an error is raised with details of all attempts

#### Scenario: No fallback configured
- **WHEN** only a single model is configured
- **THEN** the error is raised directly when the model fails

### Requirement: Retry with backoff on transient errors
LLM calls SHALL use pydantic-ai's native retry mechanism. Transient errors (5xx, timeouts, connection errors) SHALL be retried up to 3 times with exponential backoff. Non-transient errors (4xx, auth failures) SHALL NOT be retried.

#### Scenario: Transient error retried
- **WHEN** an LLM call fails with a 500 error
- **THEN** the call is retried up to 3 times with exponential backoff

#### Scenario: Non-transient error not retried
- **WHEN** an LLM call fails with a 401 auth error
- **THEN** the error is raised immediately without retry

### Requirement: Fallback model for provider failover
The doc-sync LLM model SHALL support optional fallback models via pydantic-ai's `FallbackModel`. When a fallback model ID is configured, a secondary provider is available. If the primary provider fails, the fallback model SHALL be attempted. If all providers fail, an error SHALL be raised.

#### Scenario: Fallback to secondary model
- **WHEN** the primary model (OmniRoute) is unavailable
- **THEN** the fallback model is attempted via FallbackModel

#### Scenario: All providers exhausted
- **WHEN** all models in the fallback chain have failed
- **THEN** an error is raised with details of all attempts

#### Scenario: No fallback configured
- **WHEN** only a single model is configured
- **THEN** the error is raised directly when the model fails

### Requirement: Degradation manager monitors system health
A `DegradationManager` SHALL monitor CPU usage and error rate. When CPU exceeds 85% or error rate exceeds 50/minute, the degradation level SHALL transition to REDUCED, capping agent iterations at 5. Recovery requires 60 seconds of sustained healthy metrics.

#### Scenario: Degradation triggers on high CPU
- **WHEN** CPU usage exceeds 85%
- **THEN** degradation level transitions to REDUCED and max iterations is capped at 5

#### Scenario: Recovery after sustained health
- **WHEN** CPU and error rate are healthy for 60 seconds
- **THEN** degradation level transitions back to NORMAL
