## Purpose

This specification defines requirements for Flavor Composition Sdk.

## Requirements

### Requirement: build_agent SHALL accept flavors parameter
`build_agent()` SHALL accept an optional `flavors: list[Flavor] | None = None` parameter (keyword-only). When provided, these flavors SHALL be passed to `BaseAgent(flavors=...)`. When None, the current default behavior (building a Flavor from config) SHALL be preserved.

**Verified current signature (sdk/agents.py:13-22):**
```python
def build_agent(
    config: ConsumerConfig,
    model: str | Model = "openai-chat:fable-5",
    tools: list[Any] | None = None,
    name: str | None = None,
    instructions: str = "",
    memory: Any = None,
    hooks: HookRegistry | None = None,
    harness_config: dict[str, Any] | None = None,
) -> BaseAgent:
```

**Flavor type (agent_base/types.py:120):**
```python
@dataclass
class Flavor:
    name: str
    prompts: list[FlavorPrompt] = field(default_factory=list)
    tool_policy: FlavorToolPolicy = field(default_factory=FlavorToolPolicy)
    defaults: FlavorDefaults = field(default_factory=FlavorDefaults)
    telemetry_tags: dict[str, str] = field(default_factory=dict)
```

#### Scenario: Flavors provided
- **WHEN** `build_agent(config, model="openai-chat:fable-5", flavors=[my_flavor])` is called
- **THEN** the provided flavors SHALL be passed directly to `BaseAgent(flavors=[my_flavor])`
- **AND** the default Flavor from config SHALL NOT be created

#### Scenario: Flavors not provided
- **WHEN** `build_agent(config, model="openai-chat:fable-5")` is called without flavors parameter
- **THEN** a default Flavor SHALL be built from config (current behavior preserved)

#### Scenario: Empty flavors list
- **WHEN** `build_agent(config, model="openai-chat:fable-5", flavors=[])` is called
- **THEN** an empty list SHALL be passed to BaseAgent (no flavors applied)

### Requirement: build_toolkit SHALL support include_builtins
`build_toolkit()` SHALL accept an optional `include_builtins: bool = True` parameter. This SHALL be passed through to `ToolRegistry(include_builtins=include_builtins)`.

**Verified current signature (sdk/tools.py:11-15):**
```python
def build_toolkit(
    tools: list[BaseTool[Any]],
    hooks: list[dict[str, Any]] | None = None,
) -> ToolRegistry:
```

**Current behavior:** Creates `ToolRegistry(include_builtins=False)` — builtins are always excluded.

#### Scenario: Builtins included (default)
- **WHEN** `build_toolkit(tools)` is called without include_builtins
- **THEN** the ToolRegistry SHALL include all 7 built-in tools alongside the provided tools

#### Scenario: Builtins explicitly excluded
- **WHEN** `build_toolkit(tools, include_builtins=False)` is called
- **THEN** the ToolRegistry SHALL contain only the provided tools (current behavior)

### Requirement: hooks vs capabilities SHALL be documented
AGENTS.md SHALL include a decision matrix explaining when to use hooks vs harness capabilities.

#### Scenario: Developer reads decision matrix
- **WHEN** a developer reads AGENTS.md looking for guidance on hooks vs capabilities
- **THEN** a clear decision matrix SHALL be present with the rule: hooks = cross-cutting concerns (metrics, audit, approval), capabilities = agent behavior (compaction, planning, tools)
