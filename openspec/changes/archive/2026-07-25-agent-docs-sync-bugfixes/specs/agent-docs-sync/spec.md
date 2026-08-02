## MODIFIED Requirements

### Requirement: Tool Implementation

The system SHALL implement tools using BaseTool with pydantic args models, and all callers (tests, pipeline, CLI) SHALL use the same Args model interface.

#### Scenario: Tool Implementation
- **WHEN** tools are implemented
- **THEN** they SHALL inherit from `BaseTool[Args]`
- **AND** they SHALL have `args_schema` class attribute
- **AND** they SHALL implement `metadata` property returning `ToolMetadata`
- **AND** they SHALL implement `execute(args)` method returning `ToolResult`
- **AND** `execute()` SHALL accept a single pydantic model instance, NOT keyword arguments

#### Scenario: Test API compliance
- **WHEN** tests invoke tool.execute()
- **THEN** they SHALL pass a pydantic Args model instance, NOT kwargs
- **AND** the test SHALL import the Args model from the tool module

#### Scenario: Pipeline API compliance
- **WHEN** workflow steps invoke tool.execute()
- **THEN** they SHALL pass a pydantic Args model instance, NOT kwargs

### Requirement: Logging

The system SHALL integrate agent-core's logging infrastructure with scoped verbosity.

#### Scenario: Verbose flag
- **WHEN** `--verbose` or `-v` flag is provided
- **THEN** the system SHALL set logging level to DEBUG for `agent_docs_sync` logger only
- **AND** it SHALL NOT set root logger to DEBUG (to avoid library debug spam)
- **AND** third-party library loggers (markdown_it, httpx) SHALL remain at WARNING or above
- **AND** it SHALL display detailed agent activity

#### Scenario: Quiet flag
- **WHEN** `--quiet` or `-q` flag is provided
- **THEN** the system SHALL set logging level to WARNING
- **AND** it SHALL suppress all output except errors

### Requirement: Gap detection

The system SHALL identify documentation gaps across the entire codebase.

#### Scenario: Diátaxis violations
- **WHEN** a doc file violates its assigned Diátaxis quadrant rules
- **THEN** it SHALL be reported with file path, violation type, and severity
- **AND** reference quadrant SHALL allow up to 1000 words at tier 2 (default)
- **AND** reference quadrant SHALL NOT require `signature` or `examples` sections at tier 2
