## ADDED Requirements

### Requirement: PyaiDocs capability

When `AgentConfig.docs_access` is set, `AgentRuntime` SHALL create a `PyaiDocs` capability.

#### Scenario: Default docs access
- **WHEN** `docs_access={}`
- **THEN** `PyaiDocs()` SHALL be created
- **AND** the agent SHALL have a `read_pyai_docs(topic)` tool available

#### Scenario: Local docs path
- **WHEN** `docs_access={"local_docs_path": "/path/to/pydantic-ai-docs"}`
- **THEN** `PyaiDocs(local_docs_path=Path("/path/to/pydantic-ai-docs"))` SHALL be created

### Requirement: Documentation topics

The `read_pyai_docs` tool SHALL support the following topics: `capabilities`, `hooks`, `tools`, `tools_advanced`, `toolsets`, `agent`.

#### Scenario: Topic lookup
- **WHEN** the agent calls `read_pyai_docs(topic="capabilities")`
- **THEN** the Pydantic AI capabilities documentation SHALL be returned
