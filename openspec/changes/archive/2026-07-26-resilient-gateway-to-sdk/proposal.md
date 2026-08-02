## Why

`ResilientGateway` — a wrapper that adds circuit-breaking and fallback to LLM gateways — currently lives in agent-docs-sync. It should be in agent-core so all consumers benefit. agent-docs-sync is the only consumer, and it imports exclusively from `agent_core.resilience` and `agent_core.llm_gateway`, so moving it upstream has zero dependency issues.

## What Changes

### Move ResilientGateway to agent-core
- Create `agent_core/llm_gateway/resilient.py` with the `ResilientGateway` class
- Export from `llm_gateway/__init__.py` and `sdk/__init__.py`
- Add `create_resilient_gateway()` convenience function

### Update agent-docs-sync to consume from SDK
- Delete `agent-docs-sync/llm/resilient.py`
- Update `agent-docs-sync/llm/gateway.py` to import from `agent_core.llm_gateway`

## Capabilities

### New Capabilities
- `resilient-gateway-sdk`: ResilientGateway as part of agent-core SDK for all consumers

### Modified Capabilities
- `gateway`: Add ResilientGateway wrapper to LLMGateway module

## Impact

### Cross-Repo Compatibility
- **agent-core**: New file, updated exports — no breaking changes
- **agent-docs-sync**: Import path change only — `from .resilient` → `from agent_core.llm_gateway`
- **Other repos**: No impact

### Code Changes
- **New**: `agent-core/llm_gateway/resilient.py` (~93 lines, moved from agent-docs-sync)
- **Modified**: `agent-core/llm_gateway/__init__.py` (add exports)
- **Modified**: `agent-core/sdk/__init__.py` (add SDK re-export)
- **Deleted**: `agent-docs-sync/llm/resilient.py`
- **Modified**: `agent-docs-sync/llm/gateway.py` (update import path)

### Non-Goals
- Adding retry at the AgentRuntime level (separate design effort)
- Modifying the ResilientGateway class itself
- Changing the GatewayFactory API
