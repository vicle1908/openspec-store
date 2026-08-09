# agent-config Specification

## Purpose

Define the AgentConfig dataclass, MemoryConfig, and related configuration structures for the agent-core runtime.

## Requirements

### Requirement: AgentConfig dataclass

The system SHALL define an `AgentConfig` dataclass in `agent_core/_ai/config.py` with the following fields:

```python
@dataclass
class AgentConfig:
    model: Any
    tools: list[Any] = field(default_factory=list)
    instructions: str = ""
    capabilities: list[Any] = field(default_factory=list)
    toolsets: list[Any] = field(default_factory=list)
    max_iterations: int = 10
    timeout_seconds: float = 120.0
    mcp_servers: list[str] | None = None
    tool_search: str | bool | None = None
    record_metrics: bool = True
    name: str | None = None
    description: Any = None
    model_settings: dict[str, Any] | None = None
    retries: Any = None
    end_strategy: str = "graceful"
    tool_timeout: float | None = None
    metadata: dict[str, Any] | None = None
    deps_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    spec: Any = None
    runtime_agent: Any = None
    source_file: str | None = None
    context_compaction: dict[str, Any] | None = None
    guardrails: dict[str, Any] | None = None
    step_persistence: dict[str, Any] | None = None
    subagents: dict[str, Any] | None = None
    planning: dict[str, Any] | None = None
    repo_context: dict[str, Any] | None = None
    output_overflow: dict[str, Any] | None = None
    cache_monitoring: dict[str, Any] | None = None
    limit_warnings: dict[str, Any] | None = None
    docs_access: dict[str, Any] | None = None
    durable_execution: dict[str, Any] | None = None
```

#### Scenario: AgentConfig is constructable with defaults
- **GIVEN** `AgentConfig(model=mock_model)` is instantiated
- **WHEN** the object is accessed
- **THEN** all optional fields have sensible defaults

#### Scenario: AgentConfig validates required fields
- **GIVEN** `AgentConfig()` is instantiated without model
- **WHEN** the object is created
- **THEN** a `TypeError` is raised (model is required)

### Requirement: No AgentConfig.thinking

**WHEN** `AgentConfig` is constructed
**THEN** the system SHALL NOT have a `thinking` field on `AgentConfig`

- `thinking` lives on `ModelSettings` (foundation/settings.py), not AgentConfig
- AgentConfig uses `model_settings: dict[str, Any]` for per-run overrides
- The `thinking` parameter is passed through `model_settings` dict

#### Scenario: thinking is on ModelSettings, not AgentConfig
- **GIVEN** a `ModelSettings` instance with `thinking="high"`
- **WHEN** the agent is created via `build_agent(model="anthropic:Advance", thinking="high")`
- **THEN** the `thinking` parameter SHALL be placed in `model_settings` dict
- **AND** AgentConfig SHALL NOT have a top-level `thinking` field

#### Scenario: AgentConfig has tool_search, not thinking
- **GIVEN** `AgentConfig(model=mock_model, tool_search="semantic")`
- **WHEN** the object is accessed
- **THEN** `tool_search` SHALL be `"semantic"`
- **AND** `thinking` SHALL NOT be an attribute

### Requirement: AgentRuntime accepts AgentConfig

**WHEN** `AgentRuntime` is constructed
**THEN** it SHALL accept `config: AgentConfig` as the primary constructor parameter

#### Scenario: AgentRuntime uses config
- **GIVEN** `AgentRuntime(config=AgentConfig(model=mock_model))` is instantiated
- **WHEN** the agent runs
- **THEN** it uses the configuration from the config object

#### Scenario: AgentRuntime extracts fields from config
- **GIVEN** an `AgentConfig` with `max_iterations=20`
- **WHEN** `AgentRuntime` is constructed
- **THEN** `max_iterations` SHALL be read from the config

### Requirement: MemoryConfig dataclass

**WHEN** memory is configured
**THEN** the system SHALL define a `MemoryConfig` dataclass in `agent_core/memory/config.py`

#### Scenario: MemoryConfig is constructable
- **GIVEN** required memory instances are created
- **WHEN** `MemoryConfig` is instantiated
- **THEN** the object SHALL hold the memory configuration

### Requirement: Memory accepts MemoryConfig

**WHEN** `Memory` is constructed
**THEN** it SHALL accept `config: MemoryConfig` as the primary constructor parameter

#### Scenario: Memory uses config
- **GIVEN** `Memory(config=MemoryConfig(context=ctx, scratch=scratch))` is instantiated
- **WHEN** memory operations are performed
- **THEN** it uses the configuration from the config object

### Requirement: Model resolution via create_model

**WHEN** a provider:model_name string is passed to `create_model()`
**THEN** the system SHALL resolve it to a pydantic-ai Model instance

#### Scenario: create_model resolves provider:model_name
- **GIVEN** `create_model("anthropic:Advance")` is called
- **WHEN** the model is created
- **THEN** a pydantic-ai Model instance SHALL be returned

### Requirement: Config template alignment

**WHEN** `config.yaml.example` is read
**THEN** it SHALL use the current model resolution and provider configuration format

#### Scenario: config.yaml.example uses current format
- **GIVEN** the `config.yaml.example` file is read
- **WHEN** the model section is inspected
- **THEN** it SHALL use `model.primary: anthropic:Advance`
- **AND** it SHALL NOT contain `agent.default_model: fable-5o` or `gateway:` sections
