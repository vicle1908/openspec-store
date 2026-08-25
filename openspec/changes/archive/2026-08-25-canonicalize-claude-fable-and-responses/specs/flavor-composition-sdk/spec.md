# flavor-composition-sdk Delta

## MODIFIED Requirements

### Requirement: build_agent SHALL accept flavors parameter
`build_agent()` SHALL accept an optional `flavors: list[Flavor] | None = None` parameter (keyword-only). When provided, these flavors SHALL be passed to `BaseAgent(flavors=...)`. When None, the current default behavior (building a Flavor from config) SHALL be preserved.

**Verified current signature (sdk/agents.py:13-22):**
```python
def build_agent(
    config: ConsumerConfig,
    model: str | Model = "openai-chat:Claude-Fable",
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
- **WHEN** `build_agent(config, model="openai-chat:Claude-Fable", flavors=[my_flavor])` is called
- **THEN** the provided flavors SHALL be passed directly to `BaseAgent(flavors=[my_flavor])`
- **AND** the default Flavor from config SHALL NOT be created

#### Scenario: Flavors not provided
- **WHEN** `build_agent(config, model="openai-chat:Claude-Fable")` is called without flavors parameter
- **THEN** a default Flavor SHALL be built from config (current behavior preserved)

#### Scenario: Empty flavors list
- **WHEN** `build_agent(config, model="openai-chat:Claude-Fable", flavors=[])` is called
- **THEN** an empty list SHALL be passed to BaseAgent (no flavors applied)
