## ADDED Requirements

### Requirement: DynamicWorkflow capability is configurable via harness_config

The system SHALL support a `dynamic_workflow` configuration key in the `harness_config` dict passed to `AgentRuntime`. This enables DynamicWorkflow capability for agents.

**Implementation:** In `_ai/agent.py:_build_harness_capabilities()`, add handling for the `dynamic_workflow` key. Import `DynamicWorkflow` from `pydantic_ai_harness.dynamic_workflow` with try/except ImportError for graceful degradation.

#### Scenario: DynamicWorkflow enabled with default settings
- **WHEN** `harness_config={"dynamic_workflow": {}}` is passed to `AgentRuntime`
- **THEN** `_build_harness_capabilities()` SHALL instantiate `DynamicWorkflow(agents=[])` and append it to the capabilities list

#### Scenario: DynamicWorkflow disabled by default
- **WHEN** `harness_config` does not contain `dynamic_workflow` key
- **THEN** no DynamicWorkflow capability SHALL be added to the agent

#### Scenario: DynamicWorkflow with sub-agent references
- **WHEN** `harness_config={"dynamic_workflow": {"agents": [agent1, agent2]}}` is passed
- **THEN** the capability SHALL be instantiated with the referenced agent objects
- **AND** sub-agents SHALL be accessible as async functions in the model-written script

#### Scenario: DynamicWorkflow with max_agent_calls
- **WHEN** `harness_config={"dynamic_workflow": {"max_agent_calls": 5}}` is passed
- **THEN** `DynamicWorkflow(agents=[], max_agent_calls=5)` SHALL be instantiated
- **AND** the hard ceiling SHALL hold even during concurrent fan-out

### Requirement: BaseAgent passes harness_config to AgentRuntime

`BaseAgent.__init__()` SHALL accept an optional `harness_config: dict[str, Any] | None` parameter and pass it to `AgentRuntime()`.

**Implementation:** Add `harness_config` parameter to `BaseAgent.__init__()`. Pass it to `AgentRuntime()` constructor. Update `minimal_agent.py` example to show harness_config usage.

#### Scenario: BaseAgent with harness_config
- **WHEN** `BaseAgent(harness_config={"dynamic_workflow": {}, "context_compaction": {"strategy": "summarizing"}})` is constructed
- **THEN** `AgentRuntime` SHALL receive the harness_config and process it via `_build_harness_capabilities()`

#### Scenario: BaseAgent without harness_config (backward compatible)
- **WHEN** `BaseAgent()` is constructed without `harness_config`
- **THEN** `AgentRuntime` SHALL receive `harness_config=None` and no harness capabilities SHALL be added

### Requirement: Monty sandbox is required for DynamicWorkflow

The system SHALL require `pydantic-monty>=0.0.16` to be installed for DynamicWorkflow to function. Monty provides a Rust-based Python interpreter with worker subprocess isolation.

**Monty v0.0.19 capabilities:**
- Supports: `asyncio`, `json`, `re`, `datetime`, `sys`, `os`, `typing`, `unicodedata`
- Supports: async/sync code, type hints (via ty), user-defined classes, class decorators
- Supports: `iter(callable, sentinel)`, encode/decode codecs, pytest-style assertions
- Supports: WebSocket protocol (initial)
- Does NOT support: `match` statements, third-party libraries, full standard library
- Resource limits: memory usage, stack depth, execution time (configurable, async memory limits)
- Security: filesystem/network/env access blocked by default, only via `external_lookup`
- API: `AsyncMonty()` pool → `pool.checkout()` session → `session.feed_run(code, inputs, external_lookup)`
- Performance: subprocess pool execution, StringBuilder, regex optimizations

#### Scenario: Monty installed
- **WHEN** `pydantic-monty>=0.0.16` is available in the Python environment
- **AND** `dynamic_workflow` config is enabled
- **THEN** DynamicWorkflow capability SHALL be successfully instantiated
- **AND** Monty pool SHALL be created with default resource limits (memory, stack, time)

#### Scenario: Monty not installed
- **WHEN** `pydantic-monty` is NOT available in the Python environment
- **AND** `dynamic_workflow` config is enabled
- **THEN** `_build_harness_capabilities()` SHALL log a warning via structlog and skip DynamicWorkflow capability (graceful degradation, no crash)

#### Scenario: Monty version compatibility
- **WHEN** `pydantic-monty` version is < 0.0.16
- **AND** `dynamic_workflow` config is enabled
- **THEN** the system SHALL log a warning about version incompatibility
- **AND** DynamicWorkflow capability MAY fail at runtime if API changes are breaking

### Requirement: DynamicWorkflow composes with existing capabilities

The system SHALL allow DynamicWorkflow to coexist with LangGraph orchestration, built-in tools, and other harness capabilities.

#### Scenario: DynamicWorkflow alongside LangGraph
- **WHEN** an agent has both `dynamic_workflow` config and LangGraph orchestration enabled
- **THEN** both capabilities SHALL be available to the agent
- **AND** the agent can use DynamicWorkflow for ad-hoc tasks and LangGraph for deterministic workflows

#### Scenario: DynamicWorkflow with CodeMode
- **WHEN** an agent has both `dynamic_workflow` and `code_mode` config enabled
- **THEN** both capabilities SHALL be instantiated and composed in the capabilities list

#### Scenario: DynamicWorkflow with compaction
- **WHEN** an agent has both `dynamic_workflow` and `context_compaction` config enabled
- **THEN** both capabilities SHALL be instantiated independently

### Requirement: DynamicWorkflow supports parallel sub-agent execution

DynamicWorkflow SHALL enable the orchestrator agent to write Python scripts that invoke sub-agents in parallel via `asyncio.gain`. The model writes a single Python script; Monty v0.0.19 executes it in a sandboxed worker subprocess.

**Monty v0.0.19 execution model:**
- Subprocess pool execution (new in v0.0.19)
- Async memory limits (new in v0.0.19)
- StringBuilder for performance (new in v0.0.19)
- `resume_auto()` for iterative snapshots (new in v0.0.19)

**Model-written script example:**
```python
import asyncio
reports = await asyncio.gather(
    reviewer(task="Review auth.py for bugs:\n<file contents>"),
    reviewer(task="Review parser.py for bugs:\n<file contents>"),
)
await summarizer(task="Summarize these findings:\n" + "\n\n".join(reports))
```

Key behavior: "fan out, chain, and only the last line's value returns to context" — intermediate results stay within the sandbox and don't bloat the orchestrator's prompt.

#### Scenario: Fan-out parallel execution
- **WHEN** the orchestrator agent writes a script using `asyncio.gather(reviewer(task="A"), reviewer(task="B"))`
- **THEN** both sub-agent calls SHALL execute concurrently within the Monty sandbox
- **AND** results SHALL be collected and returned to the orchestrator context
- **AND** Monty SHALL enforce async memory limits during concurrent execution

#### Scenario: Sequential chaining
- **WHEN** the orchestrator agent writes a script with sequential sub-agent calls
- **THEN** each call SHALL complete before the next begins
- **AND** intermediate results SHALL stay within the sandbox (not bloat orchestrator context)

#### Scenario: Last expression returns to orchestrator
- **WHEN** the model-written script completes
- **THEN** only the last expression's value SHALL be returned to the orchestrator's context
- **AND** intermediate results SHALL NOT flow through the orchestrator's prompt

#### Scenario: User-defined classes in scripts (new in v0.0.19)
- **WHEN** the model-written script defines a class (e.g., `class Reviewer:`)
- **THEN** Monty v0.0.19 SHALL support class instantiation and method calls
- **AND** classes SHALL work with type hints and class decorators

#### Scenario: WebSocket communication (new in v0.0.19)
- **WHEN** the model-written script uses WebSocket protocol
- **THEN** Monty v0.0.19 SHALL support initial WebSocket functionality
- **AND** WebSocket connections SHALL be sandboxed within the worker subprocess

### Requirement: DynamicWorkflow enforces budget limits

The system SHALL enforce `max_agent_calls` limit on sub-agent invocations within DynamicWorkflow scripts. This is a host-enforced ceiling that holds under concurrent fan-out.

#### Scenario: Budget exceeded
- **WHEN** a DynamicWorkflow script attempts more than `max_agent_calls` sub-agent invocations
- **THEN** the execution SHALL be terminated with a budget-exceeded error
- **AND** partial results from completed sub-agents SHALL be available

#### Scenario: Budget tracking rolls up to parent
- **WHEN** sub-agents execute within DynamicWorkflow
- **THEN** token usage from all sub-agents SHALL be aggregated into the parent run's usage metrics

#### Scenario: Deferred loading for prompt cache efficiency
- **WHEN** `defer_loading=True` is passed to DynamicWorkflow
- **THEN** the sub-agent catalog SHALL NOT be included in the prompt until the model explicitly loads the capability
- **AND** `reveal()` method SHALL allow adding sub-agents mid-run without disturbing prompt cache

### Requirement: DynamicWorkflow config is documented in config.yaml.example

The `dynamic_workflow` config key SHALL be documented in `agent-core/config.yaml.example` with usage comments.

#### Scenario: Config template includes dynamic_workflow
- **WHEN** a user copies `config.yaml.example` to `~/.tdt/config.yaml`
- **THEN** the template SHALL include a commented `dynamic_workflow` section with example configuration
