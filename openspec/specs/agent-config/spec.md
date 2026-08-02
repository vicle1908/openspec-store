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

### Requirement: GatewayFactory class

The system SHALL define a `GatewayFactory` class in `agent_core/llm_gateway/factory.py`.

```python
class GatewayFactory:
    def __init__(self) -> None:
        self._providers: dict[str, type[LLMGateway]] = {}
    
    def register(self, name: str, provider: type[LLMGateway]) -> None:
        """Register a gateway provider."""
        ...
    
    def create(self, name: str, **kwargs: Any) -> LLMGateway:
        """Create a gateway instance."""
        ...
    
    def list_providers(self) -> list[str]:
        """List registered provider names."""
        ...
```

#### Scenario: GatewayFactory registers providers
- **GIVEN** `factory = GatewayFactory()` is instantiated
- **WHEN** `factory.register("bifrost", BifrostGateway)` is called
- **THEN** the provider is registered and `list_providers()` includes "bifrost"

#### Scenario: GatewayFactory creates gateway
- **GIVEN** `factory.register("bifrost", BifrostGateway)` is registered
- **WHEN** `factory.create("bifrost", url="...", api_key="...")` is called
- **THEN** a `BifrostGateway` instance is returned

#### Scenario: GatewayFactory raises on unknown provider
- **GIVEN** `factory = GatewayFactory()` is instantiated
- **WHEN** `factory.create("unknown", url="...")` is called
- **THEN** a `ValueError` is raised with message "Unknown provider: unknown"

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
