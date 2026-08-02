## ADDED Requirements

### Requirement: pydantic-ai-harness dependency

`pyproject.toml` SHALL declare `pydantic-ai-harness>=0.10.0,<1` as a dependency.

#### Scenario: Harness installed
- **WHEN** `uv sync` is run in agent-core
- **THEN** `pydantic-ai-harness>=0.10.0` SHALL be installed
- **AND** `pydantic-ai>=2.16.0` SHALL be installed (transitive upgrade)
- **AND** all existing 398 tests SHALL pass without modification

### Requirement: AgentConfig harness fields

`AgentConfig` SHALL have optional fields for each harness capability:
- `source_file: str | None = None`
- `context_compaction: dict[str, Any] | None = None`
- `guardrails: dict[str, Any] | None = None`
- `step_persistence: dict[str, Any] | None = None`
- `subagents: dict[str, Any] | None = None`
- `planning: dict[str, Any] | None = None`
- `repo_context: dict[str, Any] | None = None`
- `output_overflow: dict[str, Any] | None = None`
- `cache_monitoring: dict[str, Any] | None = None`
- `limit_warnings: dict[str, Any] | None = None`
- `docs_access: dict[str, Any] | None = None`

#### Scenario: Default config
- **WHEN** `AgentConfig(model=...)` is created with no harness fields
- **THEN** all harness fields SHALL be `None`
- **AND** no harness capabilities SHALL be added

#### Scenario: Harness fields populated
- **WHEN** `AgentConfig(model=..., context_compaction={"max_messages": 50})` is created
- **THEN** `AgentRuntime` SHALL create the corresponding capability and add it to the agent

### Requirement: AgentRuntime harness wiring

`AgentRuntime.__init__()` SHALL inspect `AgentConfig` harness fields and create corresponding capability instances.

#### Scenario: Context compaction enabled
- **WHEN** `context_compaction` is set with strategy and params
- **THEN** the appropriate compaction capability SHALL be created and added

#### Scenario: Guardrails enabled
- **WHEN** `guardrails` is set
- **THEN** `InputGuard`/`OutputGuard` instances SHALL be created and added

#### Scenario: Step persistence enabled
- **WHEN** `step_persistence` is set
- **THEN** `StepPersistence(store=SqliteStepStore(...))` SHALL be created and added

#### Scenario: Subagents enabled
- **WHEN** `subagents` is set
- **THEN** `SubAgents(agents=[...])` SHALL be created and added

#### Scenario: Planning enabled
- **WHEN** `planning` is set
- **THEN** `Planning(...)` SHALL be created and added

#### Scenario: Repo context enabled
- **WHEN** `repo_context` is set
- **THEN** `RepoContext(...)` SHALL be created and added

#### Scenario: Output overflow enabled
- **WHEN** `output_overflow` is set
- **THEN** `OverflowingToolOutput(...)` SHALL be created and added

#### Scenario: Cache monitoring enabled
- **WHEN** `cache_monitoring` is set
- **THEN** `CacheStabilityMonitor(...)` SHALL be created and added

#### Scenario: Limit warnings enabled
- **WHEN** `limit_warnings` is set
- **THEN** `LimitWarner(...)` SHALL be created and added

#### Scenario: Docs access enabled
- **WHEN** `docs_access` is set
- **THEN** `PyaiDocs(...)` SHALL be created and added

### Requirement: Backward compatibility

Existing agents without harness fields SHALL work unchanged.

#### Scenario: No harness fields
- **WHEN** `AgentConfig(model=..., tools=[...], instructions="...")` is created
- **THEN** the agent SHALL function identically to the pre-harness version
