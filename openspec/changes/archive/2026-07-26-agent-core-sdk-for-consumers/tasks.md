## 1. agent-core: Create SDK Module

- [x] 1.1 Create `src/agent_core/sdk/__init__.py` with validated symbol set — re-export from internal modules:
  - tool_registry: BaseTool, ToolMetadata, ToolResult, ToolRegistry
  - agent_base: BaseAgent, HookRegistry, register_pack, Flavor, FlavorDefaults, FlavorPrompt, FlavorToolPolicy, AgentRequest, AgentResult
  - agent_base.hooks: HookPoint, HookPhase
  - llm_gateway: LLMGateway, LiteLLMGateway, Message, ToolDefinition
  - orchestration: WorkflowBuilder, WorkflowEngine, NodeDescriptor, EdgeDescriptor, NodeKind, EdgeCondition, CommandResult, WorkflowResult, WorkflowState, NodeHandler
  - memory: Memory, ContextMemory, ScratchMemory, PostgresMemory (from memory.postgres)
  - foundation: configure_logging, load_settings, configure_tracing, get_meter, get_tracer, GatewayError
  - resilience: BreakerConfig, CircuitBreakerOpenError, CircuitBreakerRegistry, FallbackChain, FallbackEntry, retry_with_jitter, resilient_tool
  - foundation.workspace: resolve_workspace_root
- [x] 1.2 Create `src/agent_core/sdk/config.py` with `ConsumerConfig` BaseModel composing `Settings`, providing `from_env(prefix)`, `from_yaml(path)`, shortcut properties `.gateway`, `.observability`, `.secrets`
- [x] 1.3 Create `src/agent_core/sdk/tools.py` with `build_toolkit(tools, hooks=None)` — creates ToolRegistry(include_builtins=False), registers tools and optional hooks
- [x] 1.4 Create `src/agent_core/sdk/agents.py` with `build_agent(config, gateway, tools, name, instructions, memory=None)` — builds BaseAgent with Flavor from config, passes memory to BaseAgent
- [x] 1.5 Create `src/agent_core/sdk/memory.py` with `create_consumer_memory(consumer_name, enable_postgres, postgres_dsn, context_max_messages, scratch_dir)` — auto-configures paths
- [x] 1.6 Create `src/agent_core/sdk/observability.py` with `init_observability(service_name, level, log_format)` — configures structlog + OTel from Settings
- [x] 1.7 Create `src/agent_core/sdk/workspace.py` with `discover_repos(workspace_root, pattern, exclude)` — scans for pyproject.toml markers
- [x] 1.8 Run `uv run ruff check src/agent_core/sdk/` and `uv run mypy src/agent_core/sdk/ --strict` to validate

## 2. agent-docs-sync: Config Migration

- [x] 2.1 Create `src/agent_docs_sync/config.py` with `DocsSyncConfig(ConsumerConfig)` subclass adding `allowed_doc_roots`, `planning_guidance`, `planning_cache_ttl`, `checkpointing_enabled`, `diataxis_quadrants`
- [x] 2.2 Update `src/agent_docs_sync/llm/gateway.py` to accept `ConsumerConfig` instead of `LlmConfig`, use `config.settings.gateway` for gateway settings, import from SDK
- [x] 2.3 Update `src/agent_docs_sync/cli.py` to import `configure_logging`, `DocsSyncConfig` from SDK, use `init_observability()`, scope verbose to `agent_docs_sync` only
- [x] 2.4 Delete `src/agent_docs_sync/llm/config.py` (replaced by config.py)

## 3. agent-docs-sync: Fix ResilientGateway (Bug Fix)

- [x] 3.1 In `src/agent_docs_sync/llm/resilient.py` — remove TYPE_CHECKING imports of `LLMDelta` and `LLMResponse` from `agent_core.llm_gateway.types` (these don't exist in agent-core)
- [x] 3.2 In `src/agent_docs_sync/llm/resilient.py` — remove `complete()` and `stream()` method stubs (these don't exist on LLMGateway post pydantic-ai v2)
- [x] 3.3 In `src/agent_docs_sync/llm/resilient.py` — change `from agent_core.resilience import ...` to `from agent_core.sdk import ...`
- [x] 3.4 In `src/agent_docs_sync/llm/resilient.py` — change `from agent_core.foundation.tracing import get_tracer` to `from agent_core.sdk import get_tracer`
- [x] 3.5 Verify ResilientGateway exposes only: `get_model()`, `is_available()`, `close()`, `breaker_status` property

## 4. agent-docs-sync: Tool Import Migration (15 files)

- [x] 4.1 `src/agent_docs_sync/tools/scanner.py` — change `from agent_core.tool_registry import ...` to `from agent_core.sdk import BaseTool, ToolMetadata, ToolResult`
- [x] 4.2 `src/agent_docs_sync/tools/classifier.py` — same
- [x] 4.3 `src/agent_docs_sync/tools/read_doc.py` — same
- [x] 4.4 `src/agent_docs_sync/tools/write_doc.py` — same
- [x] 4.5 `src/agent_docs_sync/tools/check_links.py` — same
- [x] 4.6 `src/agent_docs_sync/tools/enforcer.py` — same
- [x] 4.7 `src/agent_docs_sync/tools/git_diff.py` — same
- [x] 4.8 `src/agent_docs_sync/tools/graphify_loader.py` — same
- [x] 4.9 `src/agent_docs_sync/tools/gitnexus_loader.py` — same
- [x] 4.10 `src/agent_docs_sync/tools/parse_source.py` — same
- [x] 4.11 `src/agent_docs_sync/tools/read_skill.py` — same
- [x] 4.12 `src/agent_docs_sync/tools/read_pyproject.py` — same
- [x] 4.13 `src/agent_docs_sync/tools/read_deployment.py` — same
- [x] 4.14 `src/agent_docs_sync/tools/sync_spec.py` — same
- [x] 4.15 `src/agent_docs_sync/tools/state.py` — same

## 5. agent-docs-sync: Agent Import Migration (4 files)

- [x] 5.1 `src/agent_docs_sync/agent.py` — change `from agent_core.agent_base import BaseAgent, HookRegistry, register_pack` to `from agent_core.sdk import BaseAgent, HookRegistry, register_pack`
- [x] 5.2 `src/agent_docs_sync/agents/generation.py` — change `from agent_core.agent_base import BaseAgent, Flavor, ...` and `from agent_core.tool_registry import ToolRegistry` to SDK imports
- [x] 5.3 `src/agent_docs_sync/agents/validation.py` — change `from agent_core.agent_base import BaseAgent` and `from agent_core.tool_registry import ToolRegistry` to SDK imports
- [x] 5.4 `src/agent_docs_sync/agents/discovery.py` — change `from agent_core.agent_base import BaseAgent` and `from agent_core.tool_registry import ToolRegistry` to SDK imports

## 6. agent-docs-sync: Workflow Import Migration (4 files)

- [x] 6.1 `src/agent_docs_sync/workflows/full_dag.py` — change `from agent_core.orchestration import ...` to `from agent_core.sdk import WorkflowBuilder, EdgeDescriptor, NodeDescriptor, NodeKind, EdgeCondition, CommandResult, create_checkpointer`
- [x] 6.2 `src/agent_docs_sync/workflows/discovery_pipeline.py` — same pattern
- [x] 6.3 `src/agent_docs_sync/workflows/sync_pipeline.py` — same pattern
- [x] 6.4 `src/agent_docs_sync/workflows/full_pipeline.py` — change `from agent_core.foundation.tracing import get_tracer` to `from agent_core.sdk import get_tracer`

## 7. agent-docs-sync: Memory & Observability Migration

- [x] 7.1 `src/agent_docs_sync/memory/__init__.py` — use `create_consumer_memory()` from SDK, remove direct ContextMemory/ScratchMemory/PostgresMemory construction
- [x] 7.2 `src/agent_docs_sync/memory/sync_state.py` — change `from agent_core.memory import Memory` to `from agent_core.sdk import Memory`
- [x] 7.3 `src/agent_docs_sync/memory/metrics.py` — change `from agent_core.memory import Memory` to `from agent_core.sdk import Memory`
- [x] 7.4 `src/agent_docs_sync/memory/migrate.py` — change `from agent_core.memory import Memory` to `from agent_core.sdk import Memory`
- [x] 7.5 `src/agent_docs_sync/observability/__init__.py` — use `init_observability()` one-liner from SDK

## 8. agent-docs-sync: Multi-Repo Migration

- [x] 8.1 `src/agent_docs_sync/multi_repo.py` — use `discover_repos()` and `resolve_workspace_root()` from SDK, remove hardcoded `TDT_REPOS` dict and `DOC_MAPPING` dict
- [x] 8.2 Verify `src/agent_docs_sync/agents/subagents.py` — no agent_core imports to migrate (only uses pydantic_ai)

## 9. Validation

- [x] 9.1 `cd agent-core && uv run ruff check src/agent_core/sdk/` — lint SDK module
- [x] 9.2 `cd agent-core && uv run mypy src/agent_core/sdk/ --strict` — type-check SDK module
- [x] 9.3 `cd agent-docs-sync && uv run ruff check src/ tests/` — lint consumer
- [x] 9.4 `cd agent-docs-sync && uv run mypy src/agent_docs_sync/ --strict` — type-check consumer
- [x] 9.5 `cd agent-docs-sync && uv run pytest tests/ -x -q` — run consumer tests
- [x] 9.6 Verify zero remaining `from agent_core.tool_registry`, `from agent_core.agent_base`, `from agent_core.orchestration`, `from agent_core.memory`, `from agent_core.foundation`, `from agent_core.resilience` imports in agent-docs-sync production code (SDK re-exports are fine)
