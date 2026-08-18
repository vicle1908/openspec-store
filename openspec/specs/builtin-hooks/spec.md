# builtin-hooks Specification

## Purpose
Ships standard hook packs for observability (OTel metrics), structured audit, approval gating, and cost tracking that are composable and independently registerable.
## Requirements
### Requirement: Standard hook packs provide observability, audit, approval, and cost tracking
The system MUST ship reusable hook implementations that cover the four most common cross-cutting concerns for production agents.

#### Scenario: OTel metrics hook emits real instruments on run completion
- **WHEN** the `otel_metrics` hook pack is registered and an agent run completes
- **THEN** the hook records, via OpenTelemetry meter instruments, a histogram for run duration (`agent_core.agent.run.duration`, ms), a histogram for iterations used (`agent_core.agent.run.iterations`), and a counter for tool calls (`agent_core.agent.tool.calls`)

#### Scenario: OTel metrics degrade to no-op without a configured meter
- **WHEN** the `otel_metrics` hook pack is registered but no OTel meter provider/endpoint is configured
- **THEN** the hook still tracks run duration, iterations, and tool calls in its in-memory `OTelMetricsState` and emits through a no-op meter without error

#### Scenario: Structured audit hook logs tool calls with context
- **WHEN** the `structured_audit` hook pack is registered and a tool is invoked
- **THEN** the hook emits a structured log entry containing agent_name, tool_name, args (redacted), success, and duration_ms

#### Scenario: Approval gate hook blocks unapproved dangerous tools
- **WHEN** the `approval_gate` hook pack is registered with a policy listing dangerous tools and a tool call matches
- **THEN** the hook raises a permission error before execution unless an approval callback returns True

#### Scenario: Approval gate composes with metadata-based approval
- **WHEN** a tool has `requires_approval=True` and `approval_gate` is also installed
- **THEN** both controls are honored: the hook can block early and the run loop still records `ApprovalRequest` entries for deferred approval handling

#### Scenario: Cost tracker hook accumulates token usage
- **WHEN** the `cost_tracker` hook pack is registered and LLM completions return usage data
- **THEN** the hook accumulates input/output tokens and estimated cost, accessible via `cost_tracker.total_cost_usd`

#### Scenario: Cost tracker reads pydantic-ai usage fields
- **WHEN** usage data is available from the model response
- **THEN** the hook reads `input_tokens` and `output_tokens` from pydantic-ai's `RunUsage`, maps them to `prompt_tokens` and `completion_tokens` in the structured log output, and computes estimated cost

### Requirement: Hook packs are composable and independently registerable
The system MUST allow hook packs to be registered individually or combined without conflicts.

#### Scenario: Multiple hook packs coexist on the same registry
- **WHEN** both `otel_metrics` and `structured_audit` packs are registered on the same HookRegistry
- **THEN** both fire at their respective lifecycle points without interfering with each other

#### Scenario: Hook packs accept configuration at registration time
- **WHEN** a hook pack is registered with custom configuration (e.g., approval policy, cost model)
- **THEN** the pack uses that configuration for all subsequent invocations

### Requirement: Standard hook tiers for consumer agents

The system SHALL define three tiers of hook packs for consumer agents:

- **Tier 0 (always required):** `otel_metrics`, `structured_audit` — minimum observability, zero-config
- **Tier 1 (opt-in):** `cost_tracker`, `langfuse_hooks`, `mlflow_hooks` — requires configuration
- **Tier 2 (domain):** Consumer-specific hooks — registered by consumer code

#### Scenario: Tier 0 provides minimum observability
- **WHEN** a consumer agent registers only Tier 0 hooks
- **THEN** the agent SHALL emit OTel metrics for run duration, iterations, and tool calls
- **AND** the agent SHALL emit structured audit logs for all tool executions
- **AND** no external service configuration SHALL be required

#### Scenario: Tier 1 requires explicit opt-in
- **WHEN** a consumer wants cost tracking or Langfuse integration
- **THEN** the consumer SHALL explicitly call `register_pack(hooks, "cost_tracker", ...)` or `register_pack(hooks, "langfuse_hooks")`
- **AND** the framework SHALL NOT auto-register Tier 1 packs

#### Scenario: Tier 2 is consumer responsibility
- **WHEN** a consumer needs domain-specific hooks (e.g., write path validation)
- **THEN** the consumer SHALL register them via `hooks.register(point, phase, fn, tool_filter=...)`
- **AND** the framework SHALL NOT auto-register Tier 2 packs

### Requirement: Consumer agent builders MUST register Tier 0 hooks

All consumer agent builder functions SHALL register at minimum the Tier 0 hook packs (`otel_metrics`, `structured_audit`). This can be done directly via `register_pack` or indirectly via `build_agent(hooks=HookRegistry())`.

#### Scenario: Agent builder uses build_agent with hooks
- **WHEN** a consumer calls `build_agent(config, model, hooks=HookRegistry())`
- **THEN** `build_agent` SHALL auto-register `otel_metrics` and `structured_audit`

#### Scenario: Agent builder uses register_pack directly
- **WHEN** a consumer manually constructs `BaseAgent` and calls `register_pack(hooks, "otel_metrics")` and `register_pack(hooks, "structured_audit")`
- **THEN** the agent SHALL have both Tier 0 packs registered

#### Scenario: Agent builder without hooks
- **WHEN** a consumer calls `build_agent(config, model)` without providing `hooks`
- **THEN** the agent SHALL have no hooks registered (backwards compatible)
- **AND** a deprecation warning SHALL be logged suggesting hooks be added

