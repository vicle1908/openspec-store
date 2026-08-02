## ADDED Requirements

### Requirement: ResilientGateway in agent-core SDK
`ResilientGateway` SHALL be available as part of the agent-core SDK.

#### Scenario: Import from SDK
- **WHEN** a consumer does `from agent_core.llm_gateway import ResilientGateway`
- **THEN** `ResilientGateway` SHALL be importable
- **AND** it SHALL wrap any `LLMGateway` with circuit-breaking and optional fallback

#### Scenario: Import from SDK facade
- **WHEN** a consumer does `from agent_core.sdk import ResilientGateway`
- **THEN** `ResilientGateway` SHALL be re-exported from the SDK facade

### Requirement: ResilientGateway behavior unchanged
`ResilientGateway` SHALL maintain identical behavior to the agent-docs-sync implementation.

#### Scenario: Circuit breaker per provider
- **WHEN** `ResilientGateway(inner=gateway)` is constructed
- **THEN** a `CircuitBreaker` SHALL be created for the inner gateway's `provider_name`
- **AND** after `failure_threshold` failures, the breaker SHALL open
- **AND** after `recovery_timeout_seconds`, the breaker SHALL half-open

#### Scenario: Optional fallback chain
- **WHEN** `ResilientGateway(inner=gateway, fallbacks=[fallback1, fallback2])` is constructed
- **THEN** a `FallbackChain` SHALL be created with the inner gateway at priority 0 and fallbacks at higher priorities
- **AND** when the inner gateway's breaker opens, the chain SHALL try fallbacks in priority order

#### Scenario: get_model passthrough
- **WHEN** `resilient_gateway.get_model()` is called
- **THEN** it SHALL delegate to `inner.get_model()` without modification

### Requirement: Zero test breakage in agent-docs-sync
Agent-docs-sync tests SHALL pass without modification.

#### Scenario: Tests pass
- **WHEN** the migration is applied
- **THEN** `pytest tests/` in agent-docs-sync SHALL pass with zero failures
