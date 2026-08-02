# Agent Runtime Specification

## Purpose

Define the migration of `BaseAgent` from a custom ReAct loop to `pydantic_ai.Agent` via an `AgentRuntime` composition wrapper.

## ADDED Requirements

### Requirement: AR-1: AgentRuntime Class

`AgentRuntime` SHALL be a plain class in `_ai/agent.py` with a private `_agent: pydantic_ai.Agent` attribute.

`AgentRuntime.__init__()` SHALL accept:

- `model: pydantic_ai.models.Model`
- `tools: list[Callable[..., Any]]`
- `instructions: str`
- `max_iterations: int`
- `timeout_seconds: float`

`AgentRuntime.run()` SHALL accept `(user_content: str, deps: AgentRuntimeDeps)` and return `AgentResult`.

#### Scenario: AgentRuntime.run() returns AgentResult

- **GIVEN** `AgentRuntime` is instantiated with a mocked model
- **WHEN** `run("What is 2+2?", deps=AgentRuntimeDeps())` is called
- **THEN** the return type is `AgentResult`

### Requirement: AR-2: AgentRuntimeDeps

`AgentRuntimeDeps` SHALL be a `@dataclass` in `_ai/deps.py` with fields:

- `allowed_tools: list[str] | None`
- `correlation_id: str | None`
- `extra: dict[str, Any]`

#### Scenario: AgentRuntimeDeps is constructable

- **GIVEN** `AgentRuntimeDeps(allowed_tools=["read_file"])` is instantiated
- **WHEN** the object is accessed
- **THEN** `allowed_tools == ["read_file"]`

### Requirement: AR-3: AgentRuntime Tool Restriction

`AgentRuntime` SHALL expose `restrict_tools(allow: list[str], deny: list[str])` to filter which tools are active at runtime.

#### Scenario: Tool restriction narrows active tools

- **GIVEN** `AgentRuntime` is constructed with all 7 built-in tools
- **WHEN** `restrict_tools(allow=["read_file"])` is called
- **THEN** only `read_file` is callable by the agent

### Requirement: AR-4: AgentRuntime Instructions Extension

`AgentRuntime` SHALL expose `append_instructions(extra: str)` to add instructions post-construction.

#### Scenario: Instructions are appended

- **GIVEN** `AgentRuntime` is constructed with `instructions="Base prompt"`
- **WHEN** `append_instructions("Extra context")` is called
- **THEN** the agent's effective instructions include both strings

### Requirement: AR-5: BaseAgent._react_loop Deletion

`BaseAgent._react_loop()` SHALL be deleted. The ReAct loop is replaced by `AgentRuntime`.

#### Scenario: _react_loop no longer exists

- **GIVEN** `agent_core.agent_base.agent` is imported
- **WHEN** `hasattr(BaseAgent, '_react_loop')` is checked
- **THEN** the result is `False`

### Requirement: AR-6: BaseAgent Delegation

`BaseAgent.__init__()` SHALL construct an `AgentRuntime` internally.

`BaseAgent.run()` SHALL delegate to `AgentRuntime.run()`.

`BaseAgent._build_initial_messages()` SHALL be replaced by `AgentRuntime`'s message handling.

`BaseAgent._build_tool_definitions()` SHALL be replaced by direct tool registration on the agent.

#### Scenario: BaseAgent delegates to AgentRuntime

- **GIVEN** `BaseAgent` is instantiated with a `BifrostGateway`
- **WHEN** `agent.run("Hello")` is called
- **THEN** `AgentRuntime.run()` is invoked
