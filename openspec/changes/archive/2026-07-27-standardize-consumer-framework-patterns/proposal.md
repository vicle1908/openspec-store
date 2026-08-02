## Why

The `agent-docs-sync` consumer diverges from `agent-core` framework conventions in three areas: (1) `build_toolkit` has a bug where hook registrations are discarded, (2) `build_agent` SDK helper is unused — every agent builder manually constructs `BaseAgent`, and (3) hook registration is inconsistent across agents (some use `register_pack`, some don't). Additionally, five parallel pipeline implementations exist in docs-sync, only one of which uses the framework's `WorkflowEngine`. These inconsistencies make it harder for new consumers to adopt the framework correctly and create maintenance burden when framework internals change.

## What Changes

- **Fix `build_toolkit` bug** in `agent-core/sdk/tools.py`: hook registrations are currently created but never attached to the returned `ToolRegistry`
- **Extend `build_agent`** in `agent-core/sdk/agents.py`: add optional `hooks: HookRegistry` and `harness_config: dict` parameters so consumers don't need to manually construct `BaseAgent` for common cases
- **Standardize hook registration** in `agent-docs-sync`: require `register_pack("otel_metrics")` and `register_pack("structured_audit")` in all agent builders as the minimum observability tier
- **Deprecate redundant pipelines** in `agent-docs-sync/workflows/`: consolidate `full_pipeline.py`, `sync_pipeline.py`, and `discovery_pipeline.py` into the `WorkflowEngine`-based `full_dag.py`
- **Document DynamicWorkflow** as an optional advanced orchestration pattern (not absorbed into agent-core — it's a pydantic-ai-harness capability)

## Capabilities

### Modified Capabilities
- `sdk-public-api`: `build_agent` and `build_toolkit` signatures change (additive — new optional params only)
- `builtin-hooks`: Standardize which hook packs are required for consumer agents (Layer 0: otel_metrics + structured_audit)

### Non-Goals
- Absorbing `DynamicWorkflow` into agent-core (it's a pydantic-ai-harness capability, stays there)
- Changing `BaseAgent` constructor signature (already accepts `hooks` and `harness_config`)
- Changing `ConsumerConfig` (already works correctly)
- Changing existing tool implementations (all 15 tools already follow `BaseTool[T]` correctly)

## Impact

- **agent-core**: `sdk/agents.py` (build_agent), `sdk/tools.py` (build_toolkit bug fix)
- **agent-docs-sync**: `agent.py`, `agents/discovery.py`, `agents/generation.py`, `agents/validation.py` (hook standardization), `workflows/` (pipeline consolidation)
- **Other consumers**: jira-skill, code-daily-scan — no changes needed (they don't use agent-core SDK yet)
- **Risk**: LOW — all changes are additive (new optional params) or internal refactoring
- **Dependencies**: No new dependencies required
