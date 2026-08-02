## ADDED Requirements

### Requirement: YAML/JSON agent loading documentation

The system SHALL provide documentation for loading agents from YAML/JSON files via `load_agent_config()`.

#### Scenario: Agent config guide exists
- **WHEN** a developer opens `agent-core/docs/agent-config.md`
- **THEN** it SHALL document `load_agent_config(path, registry)` with complete examples

#### Scenario: YAML example
- **WHEN** a developer reads `agent-config.md`
- **THEN** it SHALL show a complete YAML agent definition with `name`, `model`, `instructions`, `capabilities`, and `tools`

#### Scenario: Tool resolution
- **WHEN** a developer reads `agent-config.md`
- **THEN** it SHALL explain how tools are resolved from `ToolRegistry` and raise `ValueError` for unknowns

#### Scenario: Capability resolution
- **WHEN** a developer reads `agent-config.md`
- **THEN** it SHALL document supported capabilities: `thinking`, `mcp`, `tool_search`

### Requirement: ToolSearch and Thinking documented

`extending.md` SHALL include examples for ToolSearch and Thinking capabilities.

#### Scenario: ToolSearch example
- **WHEN** a developer reads `extending.md`
- **THEN** it SHALL show `ToolSearch()` capability usage

#### Scenario: Thinking example
- **WHEN** a developer reads `extending.md`
- **THEN** it SHALL show `Thinking(effort="high")` with valid effort levels

### Requirement: Example YAML agent

An example YAML agent file SHALL exist at `examples/agents/review-agent.yaml`.

#### Scenario: Example exists
- **WHEN** a developer looks at `agent-core/examples/agents/`
- **THEN** `review-agent.yaml` SHALL exist with a valid agent definition
