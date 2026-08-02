## ADDED Requirements

### Requirement: YAML/JSON agent config loading

The system SHALL provide `load_agent_config(path: str | Path, *, registry: ToolRegistry | None = None) -> AgentConfig` in `agent_core/_ai/config_loader.py`.

#### Scenario: Load agent from YAML via AgentSpec
- **WHEN** `load_agent_config("agents/review.yaml", registry=my_registry)` is called
- **AND** the file contains a valid Pydantic AI `AgentSpec` with `model`, `name`, `instructions`
- **THEN** the returned `AgentConfig` SHALL have fields populated from the spec
- **AND** tool name strings SHALL be resolved via `ToolRegistry` to actual tool functions

#### Scenario: Load agent from JSON
- **WHEN** `load_agent_config("agents/review.json")` is called
- **THEN** behavior SHALL be identical to YAML loading

#### Scenario: Invalid config file
- **WHEN** the file contains an invalid spec (missing `model`, invalid capability names)
- **THEN** a `ValidationError` SHALL be raised with a descriptive error message

### Requirement: AgentConfig source_file field

`AgentConfig` SHALL have a `source_file: str | None = None` field.

#### Scenario: AgentRuntime with source_file
- **WHEN** `AgentConfig(source_file="agents/review.yaml")` is passed to `AgentRuntime`
- **THEN** `AgentRuntime` SHALL call `load_agent_config()` to load the config
- **AND** merge file-specified fields with any inline `AgentConfig` fields (file takes precedence)

### Requirement: Tool name resolution from ToolRegistry

YAML/JSON tool name strings SHALL be resolved via `ToolRegistry`.

#### Scenario: Known tool name
- **WHEN** the spec specifies `tools: ["shell_execute"]`
- **AND** `ToolRegistry` has that tool registered
- **THEN** the resolved tool function SHALL be passed to `AgentRuntime`

#### Scenario: Unknown tool name
- **WHEN** the spec specifies `tools: ["nonexistent_tool"]`
- **THEN** a `ValueError` SHALL be raised at load time with the tool name

### Requirement: Capability spec resolution

Capability specs in YAML/JSON SHALL be resolved to Pydantic AI capability instances.

#### Scenario: Thinking from config
- **WHEN** the spec specifies capabilities including `thinking: "medium"`
- **THEN** a `Thinking(effort="medium")` capability SHALL be created

#### Scenario: MCP servers from config
- **WHEN** the spec specifies `mcp_servers: ["http://localhost:3000"]`
- **THEN** `MCP("http://localhost:3000")` capabilities SHALL be added
