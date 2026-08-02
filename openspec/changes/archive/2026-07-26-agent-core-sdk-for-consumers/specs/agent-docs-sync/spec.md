## MODIFIED Requirements

### Requirement: CLI commands

The system SHALL provide CLI commands for doc sync operations via Typer. The CLI SHALL initialize observability and config via `agent_core.sdk`.

#### Scenario: CLI initialization
- **WHEN** `docs-sync` is invoked
- **THEN** it SHALL load config via `DocsSyncConfig` (subclass of `ConsumerConfig`)
- **AND** it SHALL call `init_observability(service_name="agent-docs-sync")` for logging and tracing
- **AND** it SHALL NOT import from `agent_core.foundation.settings` or `agent_core.foundation.logging` directly (use SDK)

#### Scenario: CLI logging scope
- **WHEN** `--verbose` is passed
- **THEN** verbose logging SHALL be scoped to `agent_docs_sync` only
- **AND** `markdown_it` and `httpx` loggers SHALL be set to WARNING

### Requirement: Agents

The system SHALL build agents using agent-core's `BaseAgent` with SDK imports.

#### Scenario: Main agent builder uses SDK
- **WHEN** `build_doc_sync_agent()` is called in `agent.py`
- **THEN** it SHALL import `BaseAgent`, `HookRegistry`, `register_pack` from `agent_core.sdk`
- **AND** it SHALL NOT import from `agent_core.agent_base` directly

#### Scenario: Generation agent uses SDK
- **WHEN** `build_generation_agent()` is called in `agents/generation.py`
- **THEN** it SHALL import `BaseAgent`, `Flavor`, `FlavorDefaults`, `FlavorPrompt`, `FlavorToolPolicy`, `HookRegistry` from `agent_core.sdk`
- **AND** it SHALL import `ToolRegistry` from `agent_core.sdk`

#### Scenario: Validation agent uses SDK
- **WHEN** `build_validation_agent()` is called in `agents/validation.py`
- **THEN** it SHALL import `BaseAgent` and `ToolRegistry` from `agent_core.sdk`

#### Scenario: Discovery agent uses SDK
- **WHEN** `build_discovery_agent()` is called in `agents/discovery.py`
- **THEN** it SHALL import `BaseAgent` and `ToolRegistry` from `agent_core.sdk`

### Requirement: Tools use SDK imports

All tool implementations SHALL import `BaseTool`, `ToolMetadata`, `ToolResult` from `agent_core.sdk` instead of `agent_core.tool_registry`.

#### Scenario: Tool file imports
- **WHEN** any file in `src/agent_docs_sync/tools/` is imported
- **THEN** it SHALL use `from agent_core.sdk import BaseTool, ToolMetadata, ToolResult`
- **AND** it SHALL NOT use `from agent_core.tool_registry import BaseTool, ToolMetadata, ToolResult`

### Requirement: Workflows use SDK imports

All workflow implementations SHALL import orchestration types from `agent_core.sdk` instead of `agent_core.orchestration`.

#### Scenario: Workflow file imports
- **WHEN** any file in `src/agent_docs_sync/workflows/` is imported
- **THEN** it SHALL use `from agent_core.sdk import WorkflowBuilder, EdgeDescriptor, NodeDescriptor, NodeKind, EdgeCondition, CommandResult, create_checkpointer`
- **AND** it SHALL NOT use `from agent_core.orchestration import ...` directly

#### Scenario: full_pipeline uses SDK
- **WHEN** `workflows/full_pipeline.py` is imported
- **THEN** it SHALL use `from agent_core.sdk import get_tracer` (not `from agent_core.foundation.tracing`)

### Requirement: Memory uses SDK helper

Memory initialization SHALL use `create_consumer_memory()` from `agent_core.sdk`.

#### Scenario: Memory creation
- **WHEN** `create_memory()` is called in `memory/__init__.py`
- **THEN** it SHALL delegate to `create_consumer_memory(consumer_name="docs-sync")`
- **AND** it SHALL NOT construct `ContextMemory` or `ScratchMemory` directly
- **AND** it SHALL NOT import `PostgresMemory` directly (SDK handles it)

### Requirement: Multi-repo uses dynamic discovery

Multi-repo orchestration SHALL discover repos dynamically via `discover_repos()` from `agent_core.sdk` instead of hardcoded paths.

#### Scenario: Dynamic repo discovery
- **WHEN** `get_tdt_repos()` is called in `multi_repo.py`
- **THEN** it SHALL use `discover_repos(resolve_workspace_root())`
- **AND** it SHALL NOT contain hardcoded `Path.home() / "Developer/tdt/..."` paths

### Requirement: LlmConfig replaced by ConsumerConfig subclass

`agent_docs_sync/llm/config.py` SHALL be removed. Consumer config SHALL be defined as `DocsSyncConfig(ConsumerConfig)` in `agent_docs_sync/config.py`.

#### Scenario: Config class location
- **WHEN** `agent_docs_sync.config` is imported
- **THEN** `DocsSyncConfig` SHALL be available as a subclass of `ConsumerConfig`
- **AND** `LlmConfig` SHALL NOT exist in `agent_docs_sync/llm/config.py`

#### Scenario: Config backward compatibility
- **WHEN** existing code calls `load_config(app_root)`
- **THEN** it SHALL return a `DocsSyncConfig` instance
- **AND** `config.model`, `config.gateway` SHALL still be accessible

### Requirement: LLM gateway uses SDK imports

`llm/gateway.py` SHALL import gateway types from `agent_core.sdk`.

#### Scenario: Gateway factory uses SDK
- **WHEN** `llm/gateway.py` creates a gateway
- **THEN** it SHALL import `LiteLLMGateway`, `GatewayError` from `agent_core.sdk`
- **AND** it SHALL NOT import from `agent_core.foundation.errors` or `agent_core.llm_gateway` directly

## ADDED Requirements

### Requirement: Fix stale ResilientGateway methods

`agent_docs_sync/llm/resilient.py` references `LLMDelta`, `LLMResponse`, `complete()`, and `stream()` which do not exist in agent-core's `LLMGateway` (removed during pydantic-ai v2 migration). The `ResilientGateway` SHALL be updated to match the current `LLMGateway` interface.

#### Scenario: ResilientGateway matches LLMGateway interface
- **WHEN** `ResilientGateway` is instantiated
- **THEN** it SHALL implement only the current `LLMGateway` interface: `get_model()`, `is_available()`, `close()`
- **AND** it SHALL NOT reference `LLMDelta`, `LLMResponse`, `complete()`, or `stream()`
- **AND** it SHALL delegate `get_model()` to the inner gateway's `get_model()`

#### Scenario: TYPE_CHECKING imports cleaned up
- **WHEN** `llm/resilient.py` is parsed by mypy
- **THEN** it SHALL NOT import non-existent types `LLMDelta` or `LLMResponse` from `agent_core.llm_gateway.types`
- **AND** it SHALL use `from agent_core.sdk import LLMGateway, Message, ToolDefinition` instead

#### Scenario: ResilientGateway resilience imports via SDK
- **WHEN** `llm/resilient.py` imports resilience classes
- **THEN** it SHALL use `from agent_core.sdk import BreakerConfig, CircuitBreakerOpenError, CircuitBreakerRegistry, FallbackChain, FallbackEntry, retry_with_jitter`
- **AND** it SHALL NOT import from `agent_core.resilience` directly
