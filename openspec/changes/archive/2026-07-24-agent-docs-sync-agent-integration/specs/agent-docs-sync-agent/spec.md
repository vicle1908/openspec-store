## MODIFIED Requirements

### Requirement: Agent Integration

The system SHALL integrate the LLM agent into CLI commands where needed.

#### Scenario: Update command with agent
- **WHEN** `docs-sync update` is run
- **THEN** the system SHALL use agent.run() for doc generation
- **AND** the agent SHALL have access to read_doc, write_doc tools
- **AND** deterministic steps (detect, analyze, validate) SHALL run without agent

#### Scenario: Sync command with agent
- **WHEN** `docs-sync sync` is run
- **THEN** the system SHALL use build_sync_pipeline(use_agent=True)
- **AND** the generate_updates step SHALL use the agent
- **AND** other steps SHALL remain deterministic

#### Scenario: Check command without agent
- **WHEN** `docs-sync check` is run
- **THEN** the system SHALL NOT use the agent
- **AND** all steps SHALL be deterministic (git diff + config lookup)

#### Scenario: Validate command without agent
- **WHEN** `docs-sync validate` is run
- **THEN** the system SHALL NOT use the agent
- **AND** link checking SHALL be deterministic

### Requirement: Agent Invocation

The system SHALL properly invoke the agent for doc generation.

#### Scenario: Agent task creation
- **WHEN** agent is needed for doc generation
- **THEN** the system SHALL create a task describing the doc update
- **AND** the task SHALL include affected files and context

#### Scenario: Agent execution
- **WHEN** agent.run() is called
- **THEN** the agent SHALL use tools (read_doc, write_doc, etc.)
- **AND** the agent SHALL return ToolResult with updates
- **AND** the system SHALL handle agent completion/failure

#### Scenario: Agent cleanup
- **WHEN** agent execution completes
- **THEN** the system SHALL close the gateway connection
- **AND** it SHALL not leave dangling connections
