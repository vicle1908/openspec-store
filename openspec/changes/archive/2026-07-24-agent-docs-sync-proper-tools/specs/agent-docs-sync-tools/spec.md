## MODIFIED Requirements

### Requirement: Tool Implementation

The system SHALL implement tools following agent-core BaseTool standards.

#### Scenario: BaseTool interface
- **WHEN** a tool is implemented
- **THEN** it SHALL inherit from `BaseTool[Args]` where Args is a Pydantic BaseModel
- **AND** it SHALL have `args_schema` class attribute
- **AND** it SHALL implement `metadata` property returning `ToolMetadata`
- **AND** it SHALL implement `execute(args)` method returning `ToolResult`

#### Scenario: ToolMetadata usage
- **WHEN** tool metadata is defined
- **THEN** it SHALL use `agent_core.tool_registry.ToolMetadata`
- **AND** it SHALL include `name`, `description`, `source` fields
- **AND** it SHALL set `requires_approval=True` for write tools

#### Scenario: ToolResult contract
- **WHEN** tool execution completes
- **THEN** it SHALL return `ToolResult(success=True, output=...)` on success
- **AND** it SHALL return `ToolResult(success=False, error=...)` on failure
- **AND** it SHALL never raise exceptions to the agent loop

#### Scenario: Tool registration
- **WHEN** tools are created
- **THEN** they SHALL be registered via `ToolRegistry.register()`
- **AND** they SHALL be discoverable via `ToolRegistry.list_tools()`

### Requirement: Skills

The system SHALL provide domain knowledge via skills.

#### Scenario: Skill definition
- **WHEN** agent-docs-sync is used
- **THEN** it SHALL have a `doc-sync` skill in `.agents/skills/doc-sync/SKILL.md`
- **AND** the skill SHALL define allowed tools
- **AND** the skill SHALL provide domain-specific instructions

#### Scenario: Skill matching
- **WHEN** a doc sync task is detected
- **THEN** the skill matcher SHALL activate the doc-sync skill
- **AND** it SHALL contribute prompts and tool policies

### Requirement: Harness Integration

The system SHALL integrate pydantic-ai-harness capabilities.

#### Scenario: Context compaction
- **WHEN** document context is large
- **THEN** the system SHALL use ContextCompaction capability
- **AND** it SHALL summarize older context to stay within limits

#### Scenario: Guardrails
- **WHEN** doc generation runs
- **THEN** the system SHALL validate outputs via Guardrails capability
- **AND** it SHALL reject invalid documentation formats

### Requirement: Real Agent Verification

The system SHALL verify tools work correctly with real agent execution.

#### Scenario: Agent with read_doc tool
- **WHEN** agent is triggered with a doc reading task
- **THEN** the agent SHALL use ReadDocTool to read markdown files
- **AND** it SHALL return the content via ToolResult
- **AND** the agent loop SHALL complete without exceptions

#### Scenario: Agent with check_links tool
- **WHEN** agent is triggered with a link validation task
- **THEN** the agent SHALL use CheckLinksTool to validate links
- **AND** it SHALL return validation results via ToolResult
- **AND** broken links SHALL be reported correctly

#### Scenario: Agent with parse_source tool
- **WHEN** agent is triggered with a code parsing task
- **THEN** the agent SHALL use ParseSourceTool to extract API info
- **AND** it SHALL return functions, classes, docstrings via ToolResult

#### Scenario: Multi-tool agent run
- **WHEN** agent is triggered with a complex doc sync task
- **THEN** the agent SHALL use multiple tools in sequence
- **AND** each tool SHALL return valid ToolResult
- **AND** the agent SHALL aggregate results correctly

#### Scenario: Approval flow for write tools
- **WHEN** agent attempts to use WriteDocTool
- **THEN** the system SHALL trigger approval flow (requires_approval=True)
- **AND** the tool SHALL NOT execute without approval
- **AND** the approval request SHALL be surfaced to the user

#### Scenario: Skill matching verification
- **WHEN** a doc sync task is submitted
- **THEN** the doc-sync skill SHALL be activated
- **AND** the skill SHALL contribute allowed tools list
- **AND** the agent SHALL have access to skill-defined tools
