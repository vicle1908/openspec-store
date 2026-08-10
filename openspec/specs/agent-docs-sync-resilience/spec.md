# Agent Docs Sync Resilience Specification

## Purpose

Define resilience patterns for docs-sync: provider fallback and retry around LLM calls, graceful degradation when code intelligence sources are unreachable.
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

The doc-sync LLM model SHALL support optional fallback models via the configured TDT provider boundary and a supported fallback model abstraction. When a fallback model ID is configured and constructible, a secondary provider SHALL be attempted after a primary failure covered by the fallback policy. If a route cannot be constructed because its credential is absent, docs-sync SHALL fail closed for that route and preserve a truthful diagnostic; it SHALL not misroute the request to another provider.

#### Scenario: Fallback to secondary model

- **WHEN** the primary model is unavailable for a fallback-eligible transient failure
- **AND** the secondary route is constructible from the TDT provider registry and environment
- **THEN** the fallback model SHALL be attempted in the configured order

#### Scenario: All providers exhausted

- **WHEN** all constructible models in the configured chain fail
- **THEN** an error SHALL be raised or returned with redacted details of the attempted routes
- **AND** the workflow SHALL preserve the failure reason and SHALL not report successful generation

#### Scenario: Fallback route is unconfigured

- **WHEN** a configured fallback route lacks its required credential or has incompatible provider configuration
- **THEN** that route SHALL be excluded from active construction or fail closed
- **AND** the primary route SHALL not be silently redirected through the fallback route's endpoint or credentials

#### Scenario: No fallback configured

- **WHEN** only a single model is configured
- **THEN** the error SHALL be raised or returned directly when that model fails

### Requirement: Degradation manager monitors system health
A `DegradationManager` SHALL monitor CPU usage and error rate. When CPU exceeds 85% or error rate exceeds 50/minute, the degradation level SHALL transition to REDUCED, capping agent iterations at 5. Recovery requires 60 seconds of sustained healthy metrics.

#### Scenario: Degradation triggers on high CPU
- **WHEN** CPU usage exceeds 85%
- **THEN** degradation level transitions to REDUCED and max iterations is capped at 5

#### Scenario: Recovery after sustained health
- **WHEN** CPU and error rate are healthy for 60 seconds
- **THEN** degradation level transitions back to NORMAL

