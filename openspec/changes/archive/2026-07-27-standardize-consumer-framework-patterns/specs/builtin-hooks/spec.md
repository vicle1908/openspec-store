## ADDED Requirements

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
- **WHEN** a consumer calls `build_agent(config, gateway, hooks=HookRegistry())`
- **THEN** `build_agent` SHALL auto-register `otel_metrics` and `structured_audit`

#### Scenario: Agent builder uses register_pack directly
- **WHEN** a consumer manually constructs `BaseAgent` and calls `register_pack(hooks, "otel_metrics")` and `register_pack(hooks, "structured_audit")`
- **THEN** the agent SHALL have both Tier 0 packs registered

#### Scenario: Agent builder without hooks
- **WHEN** a consumer calls `build_agent(config, gateway)` without providing `hooks`
- **THEN** the agent SHALL have no hooks registered (backwards compatible)
- **AND** a deprecation warning SHALL be logged suggesting hooks be added
