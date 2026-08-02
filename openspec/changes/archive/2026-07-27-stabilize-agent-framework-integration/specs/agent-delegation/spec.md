## ADDED Requirements

### Requirement: Valid SubAgent descriptors

`SubAgents` configuration SHALL use Harness `SubAgent` descriptors with a concrete agent and stable resolved name. `agent-core` SHALL reject invalid catalog entries before a run begins.

#### Scenario: Valid validator delegate

- **WHEN** `agent-docs-sync` enables its validator delegate
- **THEN** it SHALL pass `SubAgent(agent=validator_agent, name="validator", ...)`
- **AND** the parent SHALL expose the delegation tool

#### Scenario: Raw Agent passed to SubAgents

- **WHEN** a raw Pydantic `Agent` is supplied where `SubAgent` is required
- **THEN** construction SHALL fail with an error that identifies the required wrapper
- **AND** the error SHALL not be swallowed by the consumer

#### Scenario: Delegation executes

- **WHEN** a test parent delegates a validation task
- **THEN** the configured delegate SHALL execute with its timeout and usage limits
- **AND** the result SHALL be returned to the parent

### Requirement: Delegation authority

Delegated agents SHALL receive only explicitly configured inherited tools and shared capabilities.

#### Scenario: Tool inheritance disabled

- **WHEN** `inherit_tools` is false
- **THEN** the delegate SHALL not receive parent write tools

#### Scenario: Tool inheritance enabled

- **WHEN** `inherit_tools` is true for an authorized delegate
- **THEN** only tools allowed by the parent's effective run policy SHALL be inherited
- **AND** approval and containment metadata SHALL remain enforced
