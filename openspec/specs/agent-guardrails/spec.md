# agent-guardrails

## Purpose

Provides input and output guardrails for agents, enabling tool call filtering, content blocking, output size limits, and content sanitization with configurable guard actions.

## Requirements

### Requirement: Input guardrails via InputGuard

When `AgentConfig.guardrails` includes `input_filters`, `AgentRuntime` SHALL create `InputGuard` instances.

#### Scenario: Input filter with allow list
- **WHEN** `guardrails={"input_filters": [{"allowed_tools": ["read_file", "grep_search"]}]}`
- **THEN** an `InputGuard` SHALL be created that allows only specified tools
- **AND** blocked tool calls SHALL receive a `GuardResult.block()` response

#### Scenario: Input filter with deny list
- **WHEN** `guardrails={"input_filters": [{"blocked_patterns": ["*.env", "*.key"]}]}`
- **THEN** an `InputGuard` SHALL be created that blocks matching patterns

### Requirement: Output guardrails via OutputGuard

When `AgentConfig.guardrails` includes `output_filters`, `AgentRuntime` SHALL create `OutputGuard` instances.

#### Scenario: Output size limit
- **WHEN** `guardrails={"output_filters": [{"max_output_tokens": 4000}]}`
- **THEN** an `OutputGuard` SHALL be created that truncates oversized outputs

#### Scenario: Output content filter
- **WHEN** `guardrails={"output_filters": [{"block_patterns": ["password", "secret"]}]}`
- **THEN** an `OutputGuard` SHALL be created that blocks matching content

### Requirement: Guard result semantics

Guards SHALL support four actions: `allow`, `block`, `replace`, `retry`.

#### Scenario: Block action
- **WHEN** a guard returns `GuardResult.block(message="Not allowed")`
- **THEN** the tool call SHALL be blocked and the model SHALL receive the refusal message

#### Scenario: Replace action
- **WHEN** a guard returns `GuardResult.replace(replacement=sanitized_value)`
- **THEN** the original value SHALL be replaced with the sanitized value

#### Scenario: Retry action
- **WHEN** a guard returns `GuardResult.retry(message="Please try again with different parameters")`
- **THEN** the model SHALL receive the retry instruction

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
