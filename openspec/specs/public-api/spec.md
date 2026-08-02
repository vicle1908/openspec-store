# public-api Specification

## Purpose
Freezes the agent-core public symbol signatures and consumer compatibility guarantees (ai-review, code-daily-scan) through the pydantic-ai v2 migration.
## Requirements
### Requirement: PA-1: Frozen Public Symbols

The following symbols SHALL retain their current signatures and behavior and SHALL NOT be renamed, removed, or have their return types changed in this migration:

- `agent_core.agent_base.BaseAgent`
- `agent_core.agent_base.BaseAgent.effective_max_iterations` (property)
- `agent_core.agent_base.BaseAgent.effective_timeout` (property)
- `agent_core.agent_base.AgentRequest`
- `agent_core.agent_base.AgentResult`
- `agent_core.agent_base.Flavor`, `FlavorPrompt`, `FlavorToolPolicy`, `FlavorDefaults`
- `agent_core.agent_base.AgentThought`
- `agent_core.agent_base.HookRegistry`, `HookPoint`, `HookPhase`
- `agent_core.agent_base.RunReason`
- `agent_core.agent_base.merge_flavors()`
- `agent_core.agent_base.approval_gate()`, `approval_gate.ApprovalGateState`
- `agent_core.agent_base.otel_metrics()`, `otel_metrics.OTelMetricsState`
- `agent_core.agent_base.structured_audit()`, `structured_audit.StructuredAuditState`, `structured_audit.AuditRecord`
- `agent_core.agent_base.cost_tracker()`, `cost_tracker.CostTrackerState`
- `agent_core.agent_base.register_pack()`
- `agent_core.llm_gateway.LLMGateway`, `LLMResponse`, `LLMUsage`, `Message`, `ToolDefinition`, `ToolCall`, `LLMDelta`
- `agent_core.llm_gateway.BifrostGateway`, `LiteLLMGateway`, `create_gateway()`
- `agent_core.llm_gateway.BudgetTracker`, `get_budget_tracker()`
- `agent_core.tool_registry.ToolRegistry`
- `agent_core.tool_registry.BaseTool`
- `agent_core.tool_registry.ToolMetadata`
- `agent_core.tool_registry.ToolResult`
- `agent_core.tool_registry.register_builtin_tools()`
- `agent_core.tool_registry.builtin_tools()`
- `agent_core.foundation.HookError`

#### Scenario: Consumer import compatibility

- **GIVEN** `ai-review/` imports `from agent_core.agent_base import BaseAgent, AgentRequest, AgentResult`
- **WHEN** the module is imported
- **THEN** no `AttributeError` or `ImportError` occurs

### Requirement: PA-2: Consumer Repo Compatibility

Consumer repos `ai-review/` and `code-daily-scan/` SHALL run their test suites against the migrated `agent-core` with zero source code modifications.

#### Scenario: ai-review test suite passes

- **GIVEN** `agent-core` is migrated to pydantic-ai v2.9
- **WHEN** `pytest` runs against `ai-review/`
- **THEN** all tests pass
- **AND** no files in `ai-review/src/` are modified

#### Scenario: code-daily-scan test suite passes

- **GIVEN** `agent-core` is migrated to pydantic-ai v2.9
- **WHEN** `pytest` runs against `code-daily-scan/`
- **THEN** all tests pass
- **AND** no files in `code-daily-scan/src/` are modified

### Requirement: PA-3: Unchanged Internal Modules

The following modules SHALL NOT be modified as part of this migration:

- `agent_core/skill_system/`
- `agent_core/memory/`
- `agent_core/orchestration/`
- `agent_core/resilience/`
- `agent_core/foundation/`

#### Scenario: Unchanged modules are untouched

- **GIVEN** the migration is complete
- **WHEN** `git diff agent-core/src/agent_core/skill_system/` runs
- **THEN** no changes are shown

### Requirement: PA-4: output_schema Parameter

`BaseAgent.run(output_schema: Any = None)` SHALL continue to work.

Post-migration, `output_schema` SHALL be passed to `AgentRuntime` and used as the pydantic-ai `Agent`'s `output_type` parameter.

If `output_schema` is a Pydantic model, the agent's result SHALL be coerced to that type.

#### Scenario: Structured output via output_schema

- **GIVEN** `BaseAgent.run("Summarize this", output_schema=SummarySchema)` is called
- **WHEN** the agent run completes
- **THEN** `result.output` is an instance of `SummarySchema`

### Requirement: PA-5: Custom Tool Registration

`ToolRegistry.register()` SHALL continue to work for consumer-registered custom tools.

`BaseAgent` SHALL collect tools from `ToolRegistry` (via `registry.list_tools()`) at construction time and register them on the `AgentRuntime`.

Consumer code that calls `registry.register(CustomTool())` SHALL NOT require any changes.

#### Scenario: Custom tool registration in consumer code

- **GIVEN** `examples/custom_tool.py` calls `registry.register(WordCountTool())` and `registry.register(ReverseTextTool())`
- **WHEN** `BaseAgent.run("Count words")` is called
- **THEN** `WordCountTool` and `ReverseTextTool` are available to the agent
- **AND** no changes to `custom_tool.py` are required

