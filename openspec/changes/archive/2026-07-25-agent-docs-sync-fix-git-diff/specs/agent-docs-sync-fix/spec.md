## MODIFIED Requirements

### Requirement: Tool Implementation

The system SHALL implement tools following agent-core BaseTool standards.

#### Scenario: GitDiffTool refactoring
- **WHEN** GitDiffTool is implemented
- **THEN** it SHALL inherit from `BaseTool[GitDiffArgs]`
- **AND** it SHALL have `args_schema` class attribute
- **AND** it SHALL implement `metadata` property returning `ToolMetadata`
- **AND** it SHALL implement `execute(args)` method returning `ToolResult`

#### Scenario: ToolMetadata usage
- **WHEN** GitDiffTool metadata is defined
- **THEN** it SHALL use `agent_core.tool_registry.ToolMetadata`
- **AND** it SHALL NOT use custom ToolMetadata class
