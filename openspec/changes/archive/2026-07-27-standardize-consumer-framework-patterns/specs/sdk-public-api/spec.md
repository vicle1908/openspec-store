## MODIFIED Requirements

### Requirement: Tool construction helper

agent-core SHALL provide `build_toolkit()` that constructs a `ToolRegistry` from a list of tools and optional hooks. The returned `ToolRegistry` SHALL have a `hooks` attribute containing the populated `HookRegistry` when hooks are provided.

#### Scenario: build_toolkit with tools only
- **WHEN** `build_toolkit(tools=[tool1, tool2])` is called
- **THEN** the returned `ToolRegistry` SHALL contain both tools
- **AND** `registry.hooks` SHALL be `None`

#### Scenario: build_toolkit with hooks
- **WHEN** `build_toolkit(tools=[tool1], hooks=[{"point": "before_tool", "fn": my_hook}])` is called
- **THEN** the returned `ToolRegistry` SHALL contain the tool
- **AND** `registry.hooks` SHALL be a `HookRegistry` instance
- **AND** `registry.hooks.get_hooks(HookPoint.TOOL_EXECUTE, HookPhase.BEFORE)` SHALL contain `my_hook`

#### Scenario: build_toolkit hooks are not discarded
- **WHEN** `build_toolkit(tools=[], hooks=[{"point": "before_tool", "fn": my_hook}])` is called
- **THEN** `registry.hooks` SHALL NOT be `None`
- **AND** the hook SHALL be retrievable from the registry

### Requirement: Agent construction helper

agent-core SHALL provide `build_agent()` that constructs a `BaseAgent` from consumer config, gateway, and tools. The helper SHALL accept optional `hooks` and `harness_config` parameters. When `hooks` is provided but empty, the helper SHALL auto-register Tier 0 hook packs (`otel_metrics`, `structured_audit`).

#### Scenario: build_agent with minimal config
- **WHEN** `build_agent(config, gateway)` is called
- **THEN** a `BaseAgent` SHALL be returned with default flavor from config
- **AND** the agent's `tool_registry` SHALL be an empty `ToolRegistry`

#### Scenario: build_agent with tools list
- **WHEN** `build_agent(config, gateway, tools=[tool1, tool2])` is called
- **THEN** the agent's `tool_registry` SHALL contain both tools
- **AND** the tool policy allow list SHALL include both tool names

#### Scenario: build_agent with hooks auto-registers Tier 0
- **WHEN** `build_agent(config, gateway, hooks=HookRegistry())` is called with empty hooks
- **THEN** the hooks SHALL contain `otel_metrics` and `structured_audit` hook packs
- **AND** no Tier 1 packs (cost_tracker, langfuse, mlflow) SHALL be registered

#### Scenario: build_agent with pre-populated hooks
- **WHEN** `build_agent(config, gateway, hooks=my_hooks)` is called with non-empty hooks
- **THEN** the existing hooks SHALL be preserved
- **AND** no additional packs SHALL be auto-registered

#### Scenario: build_agent with harness_config
- **WHEN** `build_agent(config, gateway, harness_config={"guardrails": {...}})` is called
- **THEN** the agent's `harness_config` SHALL contain the provided config
