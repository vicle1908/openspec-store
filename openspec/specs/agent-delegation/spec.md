# agent-delegation

## Purpose

Enables multi-agent delegation via SubAgents capability, allowing parent agents to delegate tasks to sub-agents with isolated context, configurable budgets, timeouts, and tool inheritance.

## Requirements

### Requirement: Multi-agent delegation via SubAgents

When `AgentConfig.subagents` is set, `AgentRuntime` SHALL create a `SubAgents` capability.

#### Scenario: Delegation with named sub-agents
- **WHEN** `subagents={"agents": claude-opus-4.8}`
- **THEN** `SubAgents(agents=[SubAgent(agent=researcher, name="researcher")])` SHALL be created
- **AND** the parent agent SHALL have a `delegate_task(agent_name, task)` tool available

#### Scenario: Per-delegate budgets
- **WHEN** a sub-agent is configured with `usage_limits: {"request_limit": 5}`
- **THEN** the sub-agent SHALL be limited to 5 requests per delegation
- **AND** exceeding the budget SHALL return a soft steering message (not a hard error)

#### Scenario: Per-delegate timeout
- **WHEN** a sub-agent is configured with `timeout_seconds: 30`
- **THEN** the sub-agent SHALL be cancelled after 30 seconds
- **AND** the parent SHALL receive a timeout steering message

### Requirement: Tool inheritance

`SubAgents` SHALL support inheriting parent tools to sub-agents.

#### Scenario: inherit_tools=true
- **WHEN** `subagents={"inherit_tools": true}`
- **THEN** all sub-agents SHALL have access to the parent's tools

#### Scenario: inherit_tools=false (default)
- **WHEN** `subagents={"inherit_tools": false}`
- **THEN** sub-agents SHALL NOT have access to the parent's tools
- **AND** sub-agents SHALL only have tools explicitly registered on them

### Requirement: Isolation

Each delegation SHALL run in isolation — the sub-agent does NOT see the parent's conversation.

#### Scenario: Clean context
- **WHEN** the parent delegates task "Research X" to sub-agent "researcher"
- **THEN** the sub-agent SHALL receive only the task string
- **AND** SHALL NOT see any prior parent messages or tool calls

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
