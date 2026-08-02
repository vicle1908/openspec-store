## ADDED Requirements

### Requirement: Repo context via RepoContext capability

When `AgentConfig.repo_context` is set, `AgentRuntime` SHALL create a `RepoContext` capability.

#### Scenario: Basic repo context
- **WHEN** `repo_context={"workspace_dir": "/path/to/repo"}`
- **THEN** `RepoContext(workspace_dir=Path("/path/to/repo"))` SHALL be created
- **AND** AGENTS.md / CLAUDE.md files SHALL be auto-loaded as system instructions

#### Scenario: Custom filenames
- **WHEN** `repo_context={"workspace_dir": "/path", "filenames": ["CONVENTIONS.md"]}`
- **THEN** only `CONVENTIONS.md` SHALL be loaded

### Requirement: Inventory tool

`RepoContext` SHALL expose an `inventory_agent_context` tool for the agent to discover available context files.

#### Scenario: Inventory tool available
- **WHEN** `repo_context={"workspace_dir": "/path", "expose_inventory_tool": true}`
- **THEN** the agent SHALL have an `inventory_agent_context` tool
- **AND** calling it SHALL list available context files in the workspace
