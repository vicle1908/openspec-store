# Design: Standardize on Native pydantic-ai Model Loading

## Architecture

### Current Flow
```
Consumer config (GatewaySettings)
  → create_gateway(bifrost_url, litellm_url)
    → BifrostGateway / LiteLLMGateway
      → .get_model() → OpenAIChatModel(LiteLLMProvider(...))
        → ResilientGateway wrapping inner
          → BaseAgent(gateway=resilient_gateway)
            → AgentRuntime(model=gateway.get_model())
              → pydantic_ai.Agent(model=cached_model)
```

### Proposed Flow
```
Consumer config (GatewaySettings)
  → create_model_from_config(settings, model_id)
    → infer_model("anthropic:claude-opus-4-5") or infer_model("openai-chat:gpt-4o")
      → AnthropicModel / OpenAIChatModel / GoogleModel / etc.
        → FallbackModel(primary, fallbacks=[...]) (optional)
          → BaseAgent(model=fallback_model)
            → AgentRuntime(model=model)
              → pydantic_ai.Agent(model=model)
```

## Key Design Decisions

### 1. Model Resolution: `infer_model()` as Single Entry Point

pydantic-ai's `infer_model(model_id)` accepts `"provider:model_name"` strings
and returns the correct `Model` subclass automatically:

```python
from pydantic_ai.models import infer_model

# These all work:
model = infer_model("anthropic:claude-opus-4-5")     # AnthropicModel
model = infer_model("openai-chat:gpt-4o")              # OpenAIChatModel
model = infer_model("google:fable-5-2.5-pro")           # GoogleModel
model = infer_model("openai:gpt-5")                     # OpenAIResponsesModel
model = infer_model("groq:fable-5.3-70b-versatile")    # GroqModel
```

**No custom factory needed.** The `GatewayFactory` registry, `BifrostGateway`,
`LiteLLMGateway`, and `create_gateway()` are all removed.

### 2. Fallback: `FallbackModel` Replaces `ResilientGateway`

```python
from pydantic_ai.models.fallback import FallbackModel

# Primary + fallback chain
model = FallbackModel(
    default_model=infer_model("anthropic:claude-opus-4-5"),
    fallback_models=[
        infer_model("openai-chat:gpt-4o"),
        infer_model("google:fable-5-2.5-pro"),
    ],
    fallback_on=(ModelAPIError, ConnectionError),
)
```

**Circuit breaker semantics change**: FallbackModel triggers on exceptions,
not on a configurable failure count. This is simpler and sufficient —
pydantic-ai's own retry mechanism handles transient failures within a
single provider.

### 3. Budget: `UsageLimits` for Tokens, USD Hook for Cost

```python
# Token-level limits (native pydantic-ai)
from pydantic_ai.usage import UsageLimits

result = await agent.run(
    "task",
    usage_limits=UsageLimits(
        request_limit=15,           # replaces max_iterations
        input_tokens_limit=100_000,
        output_tokens_limit=50_000,
        total_tokens_limit=150_000,
    ),
)

# USD cost tracking (custom hook, lightweight)
# Keep the hook adapter but remove BudgetTracker class.
# Use after_model_request to estimate cost from RequestUsage.
```

### 4. Retries: Native `Agent.run(retries=N)`

```python
# Replace retry_with_jitter with:
result = await agent.run(
    "task",
    retries=AgentRetries(
        max_retries=3,
        retry_delay_min=1.0,
        retry_delay_max=10.0,
    ),
)
```

### 5. Config Schema

```python
class GatewaySettings(BaseSettings):
    """LLM gateway settings — maps to pydantic-ai model resolution."""
    
    # Model identifier: "provider:model_name" format
    model: str = "openai-chat:gpt-4o"
    
    # Proxy/compatible endpoint (for LiteLLM, Bifrost, etc.)
    base_url: str = ""
    api_key: str = ""   # from secrets
    
    # Fallback models (optional)
    fallback_models: list[str] = []
    
    # Semantic cache
    semantic_cache_enabled: bool = False
    semantic_cache_ttl_seconds: int = Field(default=3600, ge=0)
    
    # Legacy backward-compat (deprecated, maps to base_url)
    bifrost_url: str = ""
    litellm_url: str = ""
```

### 6. SDK Surface Change

```python
# Current
from agent_core.sdk import build_agent, LLMGateway, ResilientGateway

agent = build_agent(
    profile=profile,
    gateway=my_resilient_gateway,  # LLMGateway subclass
    ...
)

# Proposed
from agent_core.sdk import build_agent

agent = build_agent(
    profile=profile,
    model="anthropic:claude-opus-4-5",  # or Model instance
    ...
)

# Backward-compat adapter (during transition)
agent = build_agent(
    profile=profile,
    gateway=my_old_gateway,  # still works via adapter
    ...
)
```

## File Changes

### Remove

| File | Lines | Reason |
|---|---|---|
| `llm_gateway/gateway.py` | 323 | BifrostGateway, LiteLLMGateway, BudgetTracker |
| `llm_gateway/resilient.py` | 92 | ResilientGateway |
| `llm_gateway/factory.py` | 64 | GatewayFactory |
| `llm_gateway/types.py` | 46 | LLMGateway ABC |
| `llm_gateway/__init__.py` | 34 | Package re-exports |
| `resilience/circuit_breaker.py` | ~200 | CircuitBreaker, Registry |
| `resilience/fallback.py` | ~100 | FallbackChain, FallbackEntry |
| `resilience/retry.py` | ~80 | retry_with_jitter |
| `resilience/bulkhead.py` | ~50 | Bulkhead (unused in practice) |
| **Total removed** | **~989** | |

### Add/Modify

| File | Action | Reason |
|---|---|---|
| `_ai/models.py` | Rewrite | `infer_model()` delegation, env resolution |
| `_ai/agent.py` | Simplify | Remove gateway.get_model() call |
| `foundation/settings.py` | Modify | `GatewaySettings` new schema |
| `sdk/composition.py` | Modify | `resolve_gateway()` → `resolve_model()` |
| `sdk/agents.py` | Modify | `build_agent(model=...)` |
| `sdk/__init__.py` | Modify | Update re-exports |

### Simplify

| File | Action | Reason |
|---|---|---|
| `_ai/hooks.py` | Simplify | Remove BudgetTracker dependency, keep USD hook |
| `agent_base/agent.py` | Simplify | Use `model` instead of `gateway.get_model()` |
| `cli/utils.py` | Simplify | Use new config |

## Backward Compatibility

### Transition Window (2 minor releases, 30 days)

1. `LLMGateway` → deprecated alias for `pydantic_ai.models.Model`
2. `build_agent(gateway=...)` → accepted, logs deprecation, wraps in adapter
3. `GatewaySettings.bifrost_url` → maps to `base_url` with warning
4. `GatewaySettings.litellm_url` → maps to `base_url` with warning
5. `ResilientGateway` → accepted, wraps in `FallbackModel`

### Removal Gate

- Zero active callers across workspace (verified by `git grep`)
- All consumers updated to use `model=` parameter
- agent-docs-sync `llm/gateway.py` rewritten
- agent-harness transparent (no change needed)

## Testing Strategy

1. **Unit tests**: `infer_model()` returns correct model type per provider string
2. **Integration tests**: `FallbackModel` failover between providers
3. **Regression tests**: `build_agent(model=...)` produces equivalent behavior
4. **Consumer tests**: agent-docs-sync, agent-harness work with new config
5. **Backward-compat tests**: old `gateway=` parameter still works during transition

## Rollback

If native model loading causes issues:
1. Restore `llm_gateway/` from git history
2. `build_agent(gateway=...)` is the primary rollback path
3. No schema migration needed — config is additive
