## Why

The agent-core architecture analysis revealed that while composition is already used in key areas (Memory Facade, AgentRuntime, ToolRegistry), there are opportunities to improve extendability and maintainability by:

1. Extracting configuration into dataclasses for better organization
2. Adding a GatewayFactory pattern for dynamic provider registration
3. Using Protocol instead of ABC for new backends (more flexible)
4. Creating a unified configuration system

These improvements align with Python best practices (composition over inheritance) and make the codebase easier to extend and maintain.

## What Changes

- Extract `AgentConfig` dataclass for agent runtime configuration
- Extract `MemoryConfig` dataclass for memory layer configuration
- Add `GatewayFactory` class for dynamic LLM gateway registration
- Create `Protocol`-based interfaces for new memory backends
- Maintain ABC for critical interfaces (LLMGateway, BaseTool) where enforcement is desired

## Capabilities

### New Capabilities
- `agent-config`: Centralized configuration dataclasses for agent, memory, and gateway settings
- `gateway-factory`: Dynamic provider registration and factory pattern for LLM gateways

### Modified Capabilities
- `agent-runtime`: Accept `AgentConfig` dataclass instead of individual parameters
- `memory`: Accept `MemoryConfig` dataclass instead of individual parameters

## Impact

- **Code:** `agent_core/_ai/agent.py`, `agent_core/memory/facade.py`, `agent_core/llm_gateway/gateway.py`
- **New files:** `agent_core/_ai/config.py`, `agent_core/memory/config.py`
- **Tests:** Update existing tests to use new config dataclasses
- **Backward compatibility:** Add deprecation warnings for old constructor signatures
