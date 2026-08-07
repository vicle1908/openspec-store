## Purpose

This specification defines requirements for Agent Config.

## Requirements

### Requirement: AgentConfig dataclass

The system SHALL define an `AgentConfig` dataclass in `agent_core/_ai/config.py` with the following fields:

```python
@dataclass
class AgentConfig:
    model: Model
    tools: list[Any] = field(default_factory=list)
    instructions: str = ""
    capabilities: list[Any] = field(default_factory=list)
    max_iterations: int = 10
    timeout_seconds: float = 120.0
    mcp_servers: list[str] | None = None
    thinking: str | bool | None = None
    tool_search: str | bool | None = None
    record_metrics: bool = True
```

#### Scenario: AgentConfig is constructable with defaults
- **GIVEN** `AgentConfig(model=mock_model)` is instantiated
- **WHEN** the object is accessed
- **THEN** all optional fields have sensible defaults

#### Scenario: AgentConfig validates required fields
- **GIVEN** `AgentConfig()` is instantiated without model
- **WHEN** the object is created
- **THEN** a `TypeError` is raised (model is required)

### Requirement: AgentRuntime accepts AgentConfig

`AgentRuntime.__init__()` SHALL accept `config: AgentConfig` as the primary constructor parameter. Individual parameters are removed.

#### Scenario: AgentRuntime uses config
- **GIVEN** `AgentRuntime(config=AgentConfig(model=mock_model))` is instantiated
- **WHEN** the agent runs
- **THEN** it uses the configuration from the config object

### Requirement: MemoryConfig dataclass

The system SHALL define a `MemoryConfig` dataclass in `agent_core/memory/config.py` with the following fields:

```python
@dataclass
class MemoryConfig:
    context: ContextMemory
    scratch: ScratchMemory
    long_term: PostgresMemory | None = None
    feedback: FeedbackStore | None = None
    vector: VectorMemory | None = None
```

#### Scenario: MemoryConfig is constructable with defaults
- **GIVEN** `MemoryConfig(context=ctx, scratch=scratch)` is instantiated
- **WHEN** the object is accessed
- **THEN** optional fields default to None

### Requirement: Memory accepts MemoryConfig

`Memory.__init__()` SHALL accept `config: MemoryConfig` as the primary constructor parameter. Individual parameters are removed.

#### Scenario: Memory uses config
- **GIVEN** `Memory(config=MemoryConfig(context=ctx, scratch=scratch))` is instantiated
- **WHEN** memory operations are performed
- **THEN** it uses the configuration from the config object

### Requirement: Model resolution via create_model

The system SHALL provide a `create_model()` function in `agent_core/_ai/models.py` that resolves provider:model_name strings to pydantic-ai Model instances.

```python
def create_model(model: str | Model) -> Model:
    """Create a pydantic-ai Model from a provider:model_name string or pass through a Model instance."""
    ...
```

#### Scenario: create_model resolves provider string
- **GIVEN** `create_model("openai-chat:fable-5")` is called
- **WHEN** the function executes
- **THEN** a pydantic-ai Model instance is returned

#### Scenario: create_model passes through Model instance
- **GIVEN** `create_model(existing_model)` where `existing_model` is a Model instance
- **WHEN** the function executes
- **THEN** the same Model instance is returned unchanged

#### Scenario: create_model raises on invalid format
- **GIVEN** `create_model("invalid")` is called without provider prefix
- **WHEN** the function executes
- **THEN** a `ValueError` is raised with message indicating expected 'provider:model_name' format

### Requirement: Protocol for new backends

New memory backends SHALL implement the `MemoryBackend` Protocol interface. Existing backends MAY continue using ABC inheritance.

```python
class MemoryBackend(Protocol):
    async def store(self, session: str, key: str, value: Any, **kwargs: Any) -> None: ...
    async def retrieve(self, session: str, key: str) -> Any | None: ...
    async def list_keys(self, session: str) -> list[str]: ...
```

#### Scenario: New backend implements Protocol
- **GIVEN** a new `RedisMemory` class is created
- **WHEN** it implements the `MemoryBackend` Protocol methods
- **THEN** it can be used with the `Memory` facade without inheritance

#### Scenario: Existing backends continue working
- **GIVEN** existing `ContextMemory`, `ScratchMemory`, etc. that inherit from ABC
- **WHEN** the `Memory` facade is updated
- **THEN** all existing backends continue to work without changes
