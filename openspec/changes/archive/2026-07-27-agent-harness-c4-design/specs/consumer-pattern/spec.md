## ADDED Requirements

### Requirement: ConsumerConfig Extension

The harness SHALL extend `ConsumerConfig` from agent-core's SDK for all configuration.

#### Scenario: HarnessConfig definition
- **WHEN** defining the harness configuration
- **THEN** it SHALL extend ConsumerConfig:
  ```python
  from agent_core.sdk import ConsumerConfig

  class HarnessConfig(ConsumerConfig):
      consumer_name: str = "agent-harness"
      consumer_version: str = "0.1.0"

      # Harness-specific fields
      workspace_repos: dict[str, dict] = {}
      gates_enabled: bool = True
      gate_configs: dict[str, GateConfig] = {}
      validation_tiers: ValidationTierConfig = ValidationTierConfig()
      max_backtrack_depth: int = 3
      trace_retention_days: int = 90
  ```

#### Scenario: Config loading
- **WHEN** loading configuration
- **THEN** the harness SHALL use `ConsumerConfig.from_env()`:
  ```python
  config = HarnessConfig.from_env(prefix="HARNESS_")
  ```
- **THEN** env vars SHALL override YAML values:
  - `HARNESS_GATES_ENABLED=false` → `config.gates_enabled = False`
  - `HARNESS_MAX_BACKTRACK_DEPTH=5` → `config.max_backtrack_depth = 5`

#### Scenario: Framework settings access
- **WHEN** accessing framework settings
- **THEN** the harness SHALL use `config.settings`:
  ```python
  model = config.settings.agent.default_model  # from ~/.tdt/config.yaml
  gateway_url = config.settings.gateway.litellm_url
  ```

### Requirement: Agent Construction

The harness SHALL use `build_agent` from agent-core's SDK for agent construction.

#### Scenario: Stage agent construction
- **WHEN** building a stage agent
- **THEN** the harness SHALL use `build_agent`:
  ```python
  from agent_core.sdk import build_agent

  clarify_agent = build_agent(
      config=config,
      tools=registry,
      name="clarify-agent",
      instructions="You are a requirements analyst...",
      flavors=[clarify_flavor],
      memory=memory,
  )
  ```
- **THEN** `build_agent` SHALL handle:
  - Gateway creation from config
  - Tool registration
  - Hook auto-registration (otel_metrics, structured_audit)
  - MemoryCapability wiring
  - Harness capability wiring (from harness_config)

#### Scenario: Tool registry construction
- **WHEN** building the tool registry
- **THEN** the harness SHALL use `build_toolkit`:
  ```python
  from agent_core.sdk import build_toolkit

  tools = [
      GitNexusQueryTool(),
      GitNexusImpactTool(),
      GraphifyPathTool(),
      JiraReaderTool(),
      OpenSpecOpsTool(),
  ]
  registry = build_toolkit(tools, include_builtins=True)
  ```
- **THEN** built-in tools (read_file, grep_search, etc.) SHALL be included

#### Scenario: Memory construction
- **WHEN** building memory
- **THEN** the harness SHALL use `create_consumer_memory`:
  ```python
  from agent_core.sdk import create_consumer_memory

  memory = await create_consumer_memory(
      consumer_name="agent-harness",
      enable_postgres=True,
  )
  ```

### Requirement: Flavor Composition

The harness SHALL use Flavor composition for agent specialization.

#### Scenario: Stage-specific flavors
- **WHEN** defining stage behavior
- **THEN** the harness SHALL create Flavors:
  ```python
  from agent_core.agent_base import Flavor, FlavorPrompt, FlavorToolPolicy, FlavorDefaults

  clarify_flavor = Flavor(
      name="clarify-agent",
      prompts=[
          FlavorPrompt(content="You are a requirements analyst.", position="prepend"),
          FlavorPrompt(content="Always reference codebase context.", position="append"),
      ],
      tool_policy=FlavorToolPolicy(
          allow=["gitnexus_query", "graphify_path", "read_file"],
          deny=["shell_execute", "write_file"],
      ),
      defaults=FlavorDefaults(
          max_iterations=10,
          timeout_seconds=120.0,
      ),
  )
  ```

#### Scenario: Flavor merging
- **WHEN** multiple flavors are provided
- **THEN** they SHALL merge:
  - Instructions concatenate
  - Tool policies union (allow/deny lists append)
  - Runtime defaults use last non-None wins

#### Scenario: Flavor from config
- **WHEN** loading flavors from config
- **THEN** the harness SHALL build from HarnessConfig:
  ```python
  flavors = build_flavors_from_config(config)
  agent = build_agent(config=config, tools=registry, flavors=flavors)
  ```

### Requirement: Hook Registration

The harness SHALL register hooks for observability and domain-specific behavior.

#### Scenario: Tier 0 hooks (auto-registered)
- **WHEN** building an agent via `build_agent`
- **THEN** Tier 0 hooks SHALL be auto-registered:
  - `otel_metrics` — OTel metrics for runs, iterations, tool calls
  - `structured_audit` — Audit trail for tool executions

#### Scenario: Domain-specific hooks
- **WHEN** adding harness-specific behavior
- **THEN** the harness SHALL register hooks:
  ```python
  from agent_core.agent_base.hooks import HookRegistry, HookPoint, HookPhase, register_pack

  hooks = HookRegistry()

  # Tier 0: auto-registered by build_agent
  register_pack(hooks, "otel_metrics")
  register_pack(hooks, "structured_audit")

  # Domain-specific: harness validation
  hooks.register(
      point=HookPoint.TOOL_EXECUTE,
      phase=HookPhase.BEFORE,
      fn=validate_tool_args,
      tool_filter=["gitnexus_query"],
  )
  hooks.register(
      point=HookPoint.OUTPUT_VALIDATE,
      phase=HookPhase.AFTER,
      fn=validate_artifact_output,
  )
  ```

#### Scenario: Hook lifecycle points
- **WHEN** hooks fire
- **THEN** the following points SHALL be available:
  - `HookPoint.RUN` — before/after agent run
  - `HookPoint.NODE` — before/after workflow node
  - `HookPoint.MODEL_REQUEST` — before/after LLM call
  - `HookPoint.TOOL_VALIDATE` — before tool validation
  - `HookPoint.TOOL_EXECUTE` — before/after tool execution
  - `HookPoint.OUTPUT_VALIDATE` — after output validation
  - `HookPoint.OUTPUT_PROCESS` — after output processing

### Requirement: Gateway Configuration

The harness SHALL use agent-core's LLM gateway for all LLM calls.

#### Scenario: Gateway from config
- **WHEN** initializing the gateway
- **THEN** the harness SHALL use `LiteLLMGateway`:
  ```python
  from agent_core.sdk import LiteLLMGateway

  gateway = LiteLLMGateway.from_env()
  ```
- **THEN** the gateway SHALL be configured via:
  - `GATEWAY_LITELLM_URL` env var
  - Or `~/.tdt/config.yaml` gateway section

#### Scenario: Gateway fallback
- **WHEN** primary LLM provider is unavailable
- **THEN** the gateway SHALL fall back to secondary providers
- **THEN** fallback behavior SHALL be configurable via `GatewayConfig`

### Requirement: Observability Initialization

The harness SHALL use `init_observability` for tracing and logging setup.

#### Scenario: Observability setup
- **WHEN** starting the harness
- **THEN** the harness SHALL call:
  ```python
  from agent_core.sdk import init_observability

  init_observability(
      service_name="agent-harness",
      level=config.settings.agent.log_level,
      log_format=config.settings.agent.log_format,
  )
  ```
- **THEN** this SHALL configure:
  - structlog with console/JSON output
  - OTel tracing with GenAI semantic conventions
  - Langfuse integration (via OTel)
  - MLflow integration (for experiments)

#### Scenario: Per-stage tracing
- **WHEN** a stage executes
- **THEN** the harness SHALL emit OTel spans:
  ```python
  from agent_core.foundation.tracing import get_tracer

  tracer = get_tracer("agent_harness.stages")
  with tracer.start_as_current_span(stage_name) as span:
      span.set_attribute("ticket_id", ticket_id)
      span.set_attribute("stage_name", stage_name)
      # ... stage execution ...
  ```

### Requirement: Workspace Discovery

The harness SHALL use `discover_repos` for workspace scanning.

#### Scenario: Repo discovery
- **WHEN** starting the harness
- **THEN** the harness SHALL call:
  ```python
  from agent_core.sdk import discover_repos

  repos = discover_repos()  # returns {name: Path}
  ```
- **THEN** repos SHALL be discovered by scanning for `pyproject.toml` files

#### Scenario: Repo enrichment
- **WHEN** combining discovery with config
- **THEN** the harness SHALL merge with workspace.yaml:
  ```python
  repos = discover_repos()
  for name, path in repos.items():
      if name in config.workspace_repos:
          repos[name] = {
              "path": path,
              "type": config.workspace_repos[name]["type"],
              "gitnexus_indexed": config.workspace_repos[name]["gitnexus_indexed"],
          }
  ```

### Requirement: Error Handling

The harness SHALL handle consumer-level errors gracefully.

#### Scenario: Config validation error
- **WHEN** config is invalid
- **THEN** the harness SHALL raise `ConfigError` with clear message
- **THEN** the harness SHALL NOT start

#### Scenario: Gateway initialization error
- **WHEN** gateway fails to initialize
- **THEN** the harness SHALL raise `GatewayError` with clear message
- **THEN** the harness SHALL NOT start

#### Scenario: Memory initialization error
- **WHEN** memory fails to initialize
- **THEN** the harness SHALL log a warning
- **THEN** the harness SHALL continue without memory
- **THEN** artifacts SHALL still be in state dict (in-memory)

### Requirement: SDK Import Convention

The harness SHALL import only from `agent_core.sdk`, not from internal modules.

#### Scenario: Allowed imports
- **WHEN** importing from agent-core
- **THEN** the harness SHALL use:
  ```python
  from agent_core.sdk import (
      ConsumerConfig, build_agent, build_toolkit,
      create_consumer_memory, init_observability, discover_repos,
      WorkflowBuilder, WorkflowEngine, NodeDescriptor, NodeKind,
      EdgeDescriptor, EdgeCondition, CommandResult,
      BaseTool, ToolMetadata, ToolResult, ToolRegistry,
      Memory, ContextMemory, ScratchMemory,
  )
  ```

#### Scenario: Forbidden imports
- **WHEN** importing from agent-core
- **THEN** the harness SHALL NOT use:
  ```python
  # FORBIDDEN - internal modules
  from agent_core.agent_base.agent import BaseAgent  # use from sdk
  from agent_core.orchestration.graph import WorkflowBuilder  # use from sdk
  from agent_core.memory.facade import Memory  # use from sdk
  from agent_core._ai.agent import AgentRuntime  # use build_agent
  ```

### Requirement: Testing Pattern

The harness SHALL follow agent-core's testing patterns.

#### Scenario: Unit tests
- **WHEN** testing harness components
- **THEN** the harness SHALL use:
  ```python
  import pytest
  from agent_core.sdk import ConsumerConfig

  class TestHarnessConfig:
      def test_default_values(self):
          config = HarnessConfig()
          assert config.consumer_name == "agent-harness"
          assert config.gates_enabled is True
  ```

#### Scenario: Integration tests
- **WHEN** testing workflow execution
- **THEN** the harness SHALL use:
  ```python
  import pytest
  from agent_core.sdk import WorkflowBuilder

  @pytest.mark.asyncio
  async def test_workflow_dag():
      builder = build_harness_dag()
      engine = builder.build()
      result = await engine.run({"ticket_id": "TEST-001"})
      assert result.state["completed"] is True
  ```

#### Scenario: Mock patterns
- **WHEN** mocking external services
- **THEN** the harness SHALL use:
  ```python
  from unittest.mock import AsyncMock, patch

  @patch("agent_harness.tools.gitnexus_client.subprocess.run")
  async def test_gitnexus_query(mock_run):
      mock_run.return_value = AsyncMock(stdout='{"processes": []}')
      result = await gitnexus_query("test", "repo")
      assert result.success is True
  ```
