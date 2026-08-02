## ADDED Requirements

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
