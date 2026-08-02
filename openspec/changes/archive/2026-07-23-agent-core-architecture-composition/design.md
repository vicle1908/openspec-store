## Context

The agent-core codebase has grown to include multiple modules (_ai, agent_base, memory, llm_gateway, orchestration, evaluation, etc.) with increasing configuration complexity. The current approach passes many individual parameters to constructors, which becomes unwieldy as features are added.

The architecture analysis identified that:
- Composition is already used in key areas (Memory Facade, AgentRuntime, ToolRegistry)
- Inheritance is used for interfaces (MemoryBackend, LLMGateway, BaseTool)
- Configuration is scattered across multiple constructor parameters

## Goals / Non-Goals

**Goals:**
- Extract configuration into dataclasses for better organization
- Add GatewayFactory for dynamic provider registration
- Use Protocol for new backends (more flexible than ABC)
- Maintain backward compatibility with deprecation warnings

**Non-Goals:**
- Remove existing ABC interfaces (they work well for enforcement)
- Change the public API significantly (incremental improvements only)
- Add new memory backends or LLM gateways (just improve the extension mechanism)

## Decisions

### Decision 1: Configuration Dataclasses

**Choice:** Create `AgentConfig`, `MemoryConfig`, and `GatewayConfig` dataclasses

**Rationale:**
- Centralizes configuration in one place
- Makes it easier to pass configuration around
- Enables serialization/deserialization
- Better IDE support and documentation

**Alternatives considered:**
- Pydantic BaseModel: Overkill for internal configuration
- TypedDict: Less ergonomic than dataclasses
- Plain dicts: No type safety

### Decision 2: GatewayFactory Pattern

**Choice:** Replace `create_gateway()` function with `GatewayFactory` class

**Rationale:**
- Enables dynamic provider registration
- Easier to add new providers without modifying factory code
- Better testability (can mock providers)
- Follows Factory pattern best practices

**Alternatives considered:**
- Keep function: Simpler but less flexible
- Abstract factory: Overkill for current needs

### Decision 3: Protocol for New Backends

**Choice:** Use `Protocol` for new memory backends

**Rationale:**
- Structural typing (duck typing with type safety)
- No inheritance required
- More flexible for third-party integrations
- Easier to mock in tests

**Alternatives considered:**
- ABC: Enforces implementation at class definition time (keep for critical interfaces)
- No interface: Loses type safety

## Risks / Trade-offs

**[Risk] Breaking existing code** → Mitigation: Add deprecation warnings, support both old and new signatures during transition

**[Risk] Increased complexity** → Mitigation: Keep changes minimal, focus on configuration extraction only

**[Risk] Performance overhead** → Mitigation: Dataclasses have minimal overhead, Factory pattern adds one level of indirection

## Migration Plan

1. Add new config dataclasses alongside existing constructors
2. Add GatewayFactory class
3. Update tests to use new config pattern
4. Add deprecation warnings to old constructors
5. Remove old constructors after one release cycle

## Open Questions

- Should we also extract `SkillConfig` for the skill system?
- Should we add a unified `AgentCoreConfig` that composes all configs?
- Should we support YAML/JSON configuration files for agents?
