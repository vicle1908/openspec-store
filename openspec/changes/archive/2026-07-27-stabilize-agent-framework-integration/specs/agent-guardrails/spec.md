## ADDED Requirements

### Requirement: Configured guard preservation

When a consumer configures an official Harness `InputGuard` or `OutputGuard`, `agent-core` SHALL preserve that capability and its guard function. When a consumer supplies a supported callable, `agent-core` SHALL wrap that callable without changing its decision semantics.

#### Scenario: Existing InputGuard is supplied

- **WHEN** `agent-docs-sync` supplies a configured `InputGuard`
- **THEN** the installed agent capability SHALL use the same configured guard
- **AND** a write-intent prompt SHALL be blocked in an execution-level test

#### Scenario: Guard callable is supplied

- **WHEN** a consumer supplies a supported guard callable
- **THEN** the callable SHALL receive the official framework input
- **AND** its allow, block, replace, or retry result SHALL be honored

### Requirement: Guardrails fail closed

A configured safety guard SHALL NOT silently become an allow-all guard because of a type mismatch, import failure, or unexpected exception.

#### Scenario: Guard contract is invalid

- **WHEN** the configured guard value violates the supported contract
- **THEN** construction SHALL raise a configuration error before the agent runs

#### Scenario: Guard execution fails

- **WHEN** a guard raises an unexpected error while evaluating a protected operation
- **THEN** the protected operation SHALL not execute
- **AND** the failure SHALL be logged without secret prompt or credential contents

#### Scenario: Guardrail integration test

- **WHEN** the consumer integration test enables discovery guardrails
- **THEN** the test SHALL execute allowed and blocked prompts
- **AND** it SHALL fail rather than catch and ignore construction or execution errors
