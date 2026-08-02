## Context

`ResilientGateway` wraps any `LLMGateway` with circuit-breaking and optional fallback chain. It lives in agent-docs-sync but imports exclusively from `agent_core.resilience` and `agent_core.llm_gateway`. Moving it to agent-core makes it available to all consumers.

### Current Architecture

```
agent-docs-sync/llm/resilient.py
├── imports from agent_core.resilience (BreakerConfig, CircuitBreaker, FallbackChain)
├── imports from agent_core.llm_gateway (LLMGateway)
├── wraps inner LLMateway with CircuitBreaker + FallbackChain
└── duck-types LLMateway interface (get_model, is_available, close)
```

### Target Architecture

```
agent-core/llm_gateway/resilient.py
├── imports from agent_core.resilience (same primitives)
├── imports from agent_core.llm_gateway.types (LLMGateway)
├── wraps inner LLMateway with CircuitBreaker + FallbackChain
└── exports via llm_gateway/__init__.py and sdk/__init__.py

agent-docs-sync/llm/gateway.py
└── imports ResilientGateway from agent_core.llm_gateway (instead of .resilient)
```

## Goals / Non-Goals

**Goals:**
- Move ResilientGateway to agent-core SDK
- Update agent-docs-sync imports
- Zero test breakage

**Non-Goals:**
- Modifying ResilientGateway's behavior
- Adding retry at AgentRuntime level
- Changing GatewayFactory API

## Decisions

### D1: Composition wrapper (not inheritance)

**Decision:** Keep ResilientGateway as a composition wrapper around LLMGateway, not a subclass.

**Rationale:** ResilientGateway duck-types the LLMGateway interface (get_model, is_available, close) but wraps an inner gateway. This is already validated by agent-docs-sync. Making it a subclass would add complexity without benefit.

**Alternatives considered:**
- Inheritance from LLMGateway → rejected; would require implementing all abstract methods that delegate to inner gateway
- Protocol-based typing → rejected; current duck-typing works

### D2: Keep in llm_gateway/ not resilience/

**Decision:** Place ResilientGateway in `llm_gateway/resilient.py`, not `resilience/`.

**Rationale:** ResilientGateway is gateway-specific — it wraps LLMGateway, not general-purpose resilience. The `resilience/` module contains reusable primitives (CircuitBreaker, FallbackChain). ResilientGateway composes those primitives specifically for LLM gateways.

## Risks / Trade-offs

- **[Risk] Import path change breaks agent-docs-sync** → Mitigation: Simple find-replace of `from .resilient import` to `from agent_core.llm_gateway import`. Tests don't import ResilientGateway directly.
