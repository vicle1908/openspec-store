## ADDED Requirements

### Requirement: SDK module provides stable public API

agent-core SHALL provide a dedicated `agent_core.sdk` package that re-exports all consumer-facing symbols from internal modules. The SDK module SHALL be the recommended import path for all consumers.

#### Scenario: Consumer imports from SDK
- **WHEN** a consumer runs `from agent_core.sdk import BaseTool, BaseAgent, WorkflowBuilder`
- **THEN** the imports SHALL resolve to the same symbols as `from agent_core.tool_registry import BaseTool` etc.
- **AND** no `ImportError` or `AttributeError` SHALL occur

#### Scenario: Internal imports remain functional
- **WHEN** existing code imports from `agent_core.tool_registry`, `agent_core.agent_base`, etc.
- **THEN** those imports SHALL continue to work without changes
- **AND** no deprecation warnings SHALL be emitted

### Requirement: SDK re-exports validated consumer symbol set

The SDK SHALL re-export the following validated consumer symbol set with preserved constructor signatures:

| Module | Symbols | Constructor/API Notes |
|--------|---------|----------------------|
| `tool_registry` | `BaseTool`, `ToolMetadata`, `ToolResult`, `ToolRegistry` | `ToolRegistry(*, include_builtins=True)`, `register(tool, *, replace=False)` |
| `agent_base` | `BaseAgent`, `HookRegistry`, `register_pack`, `Flavor`, `FlavorDefaults`, `FlavorPrompt`, `FlavorToolPolicy`, `AgentRequest`, `AgentResult` | `BaseAgent(name, gateway, tool_registry, model, instructions="", flavors=None, hooks=None, harness_config=None, max_iterations=10, timeout_seconds=120.0, memory=None)`, `HookRegistry().register(point, phase, fn, *, tool_filter=None)` |
| `agent_base.hooks` | `HookPoint`, `HookPhase` | `HookPoint.TOOL_EXECUTE`, `HookPhase.BEFORE/AFTER/ERROR` |
| `llm_gateway` | `LLMGateway`, `LiteLLMGateway`, `Message`, `ToolDefinition` | `LiteLLMGateway(base_url, api_key="", model="gpt-4o", timeout=120.0)`, `from_env()` classmethod |
| `orchestration` | `WorkflowBuilder`, `WorkflowEngine`, `NodeDescriptor`, `EdgeDescriptor`, `NodeKind`, `EdgeCondition`, `CommandResult`, `WorkflowResult`, `WorkflowState`, `NodeHandler` | `WorkflowBuilder(name).add_node(desc, handler).add_edge(edge).set_entry(name).build(checkpointer=None)`, `NodeDescriptor(name, kind=NodeKind.AGENT)`, `EdgeDescriptor(source, target, condition=EdgeCondition.ALWAYS)`, `CommandResult(goto="...")`, `NodeHandler` type alias |
| `memory` | `Memory`, `ContextMemory`, `ScratchMemory`, `PostgresMemory` | `Memory(context=, scratch=, long_term=None)`, `ContextMemory(max_messages=50)`, `ScratchMemory(scratch_dir="...")`, `await PostgresMemory.create(dsn)` |
| `foundation` | `configure_logging`, `load_settings`, `configure_tracing`, `get_meter`, `get_tracer`, `GatewayError` | `configure_logging(level, log_format, agent_id)`, `get_tracer("name")`, `GatewayError(msg, code="...", details={})` |
| `resilience` | `BreakerConfig`, `CircuitBreakerOpenError`, `CircuitBreakerRegistry`, `FallbackChain`, `FallbackEntry`, `retry_with_jitter`, `resilient_tool` | `BreakerConfig(failure_threshold=5, recovery_timeout_seconds=30.0, success_threshold=2, monitoring_window_seconds=60.0)`, `FallbackEntry(name, priority=0)`, `FallbackChain(entries, registry)`, `@resilient_tool(max_retries=3, failure_threshold=5)` decorator |
| `foundation.workspace` | `resolve_workspace_root` | `resolve_workspace_root() -> Path` |

#### Scenario: All consumer symbols accessible via SDK
- **WHEN** any symbol from the validated set is imported from `agent_core.sdk`
- **THEN** it SHALL resolve to the correct symbol from the internal module
- **AND** the type and behavior SHALL be identical to the direct import

#### Scenario: BaseAgent constructor preserved
- **WHEN** `BaseAgent(name="x", gateway=gw, tool_registry=reg, model="m")` is called
- **THEN** all documented constructor params SHALL be accepted: `name`, `gateway`, `tool_registry`, `model`, `instructions`, `flavors`, `skills`, `skill_profile`, `skill_matcher`, `hooks`, `max_iterations`, `timeout_seconds`, `source_file`, `harness_config`, `memory`
- **AND** `memory` SHALL accept a `Memory` instance (or `None` for no memory integration)
- **AND** `agent.run(task)` SHALL return `AgentResult`

#### Scenario: WorkflowBuilder fluent API preserved
- **WHEN** `WorkflowBuilder(name="x").add_node(desc, handler).add_edge(edge).set_entry("n").build()` is called
- **THEN** `build()` SHALL return `WorkflowEngine`
- **AND** `await engine.run(initial_state)` SHALL return `WorkflowResult`
- **AND** `result.state.to_dict()` SHALL return `dict`

### Requirement: ConsumerConfig composable base class

agent-core SHALL provide a `ConsumerConfig` Pydantic BaseModel that composes (not inherits) agent-core's `Settings`. Consumers subclass this to add domain-specific config.

#### Scenario: Consumer creates config subclass
- **WHEN** a consumer defines `class MyConfig(ConsumerConfig): my_field: str = "default"`
- **THEN** `MyConfig()` SHALL have both `my_field` and `settings: Settings` (framework config)
- **AND** `config.settings.gateway` SHALL expose framework gateway settings
- **AND** `config.settings.secrets` SHALL expose framework secrets

#### Scenario: ConsumerConfig loads from environment
- **WHEN** a consumer calls `MyConfig.from_env(prefix="MY_")`
- **THEN** env vars `MY_MODEL`, `MY_MAX_ITERATIONS` etc. SHALL override defaults
- **AND** framework settings SHALL be loaded from `~/.tdt/.env` + `config.yaml`

#### Scenario: ConsumerConfig loads from YAML
- **WHEN** a consumer calls `MyConfig.from_yaml(path)`
- **THEN** the `consumer:` section of the YAML SHALL be parsed into the config
- **AND** framework settings SHALL be composed from the standard settings chain

### Requirement: Tool construction helper

agent-core SHALL provide `build_toolkit()` that constructs a `ToolRegistry` from a list of tools and optional hooks.

#### Scenario: Build toolkit with tools only
- **WHEN** `build_toolkit(tools=[MyTool1(), MyTool2()])` is called
- **THEN** a `ToolRegistry(include_builtins=False)` SHALL be returned with both tools registered
- **AND** `registry.get_tool("my_tool_1")` SHALL return the registered tool

#### Scenario: Build toolkit with hooks
- **WHEN** `build_toolkit(tools=[...], hooks=[{"point": "before_tool", "fn": validate}])` is called
- **THEN** the hook SHALL be registered on the toolkit's HookRegistry
- **AND** the hook SHALL fire before the specified tool executes

### Requirement: Agent construction helper

agent-core SHALL provide `build_agent()` that constructs a `BaseAgent` from consumer config, gateway, and tools.

#### Scenario: Build agent from config
- **WHEN** `build_agent(config=my_config, gateway=gateway, tools=[...])` is called
- **THEN** a `BaseAgent` SHALL be returned with the config's model, max_iterations, and timeout
- **AND** a `Flavor` SHALL be created with the consumer's tool policy
- **AND** the agent name SHALL default to `config.consumer_name`

### Requirement: Consumer memory initialization

agent-core SHALL provide `create_consumer_memory()` that creates a `Memory` instance with auto-configured paths based on consumer name.

#### Scenario: Create memory with defaults
- **WHEN** `create_consumer_memory(consumer_name="docs-sync")` is called
- **THEN** `Memory` SHALL be returned with `ContextMemory` and `ScratchMemory`
- **AND** scratch directory SHALL be `~/.tdt/docs-sync/scratch/`
- **AND** long-term memory SHALL be disabled (no Postgres)

#### Scenario: Create memory with Postgres
- **WHEN** `create_consumer_memory(consumer_name="x", enable_postgres=True, postgres_dsn="...")` is called
- **THEN** `PostgresMemory` SHALL be attempted with a 5-second timeout
- **AND** if Postgres is unavailable, long-term SHALL be `None` (graceful degradation)

### Requirement: Observability initialization helper

agent-core SHALL provide `init_observability()` that configures both structlog logging and OTel tracing for a consumer.

#### Scenario: Initialize observability
- **WHEN** `init_observability(service_name="my-consumer")` is called
- **THEN** structlog SHALL be configured with the consumer's service name
- **AND** OTel tracing SHALL be configured using framework settings from `~/.tdt/config.yaml`
- **AND** `get_tracer()` and `get_meter()` SHALL return configured instances

### Requirement: Workspace repo discovery

agent-core SHALL provide `discover_repos()` that scans the workspace for Python repos.

#### Scenario: Discover repos from workspace root
- **WHEN** `discover_repos()` is called without arguments
- **THEN** it SHALL use `resolve_workspace_root()` to find the workspace
- **AND** it SHALL scan for `*/pyproject.toml` files
- **AND** it SHALL return `{"repo_name": Path}` dict
- **AND** `.git`, `__pycache__`, `node_modules`, `.venv` directories SHALL be excluded

#### Scenario: Discover repos with custom root
- **WHEN** `discover_repos(workspace_root=Path("/custom"))` is called
- **THEN** it SHALL scan from the specified root instead of workspace root
