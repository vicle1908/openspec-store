## ADDED Requirements

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
