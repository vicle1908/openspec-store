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
model = infer_model("anthropic:fable-5-4-5")     # AnthropicModel
model = infer_model("openai-chat:gpt-4o")              # OpenAIChatModel
model = infer_model("google:fable-5-2.5-pro")           # GoogleModel
model = infer_model("openai:fable-5")                     # OpenAIResponsesModel
model = infer_model("groq:fable-5.3-70b-versatile")    # GroqModel
```

**No custom factory needed.** The `GatewayFactory` registry, `BifrostGateway`,
`LiteLLMGateway`, and `create_gateway()` are all removed.

### 2. Fallback: `FallbackModel` Replaces `ResilientGateway`

```python
from pydantic_ai.models.fallback import FallbackModel

# Primary + fallback chain
model = FallbackModel(
    default_model=infer_model("anthropic:fable-5-4-5"),
    fallback_models=[
        infer_model("openai-chat:fable-5o"),
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
    
    # Proxy/compatible endpoint (for LiteLLM, Bifrost, OmniRoute)
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

## Config Changes

### `~/.tdt/config.yaml` — Add Gateway Section

```yaml
gateway:
  # Primary model (pydantic-ai "provider:model_name" format)
  model: "openai-chat:gpt-4o"
  # Proxy endpoint (for OmniRoute/LiteLLM/Bifrost)
  base_url: "http://localhost:20128/v1"
  # Fallback models
  fallback_models:
    - "openai-chat:fable-5o-mini"
  # Semantic cache
  semantic_cache_enabled: false
  semantic_cache_ttl_seconds: 3600
```

### `~/.tdt/.env` — Keep Existing Keys

```bash
# OmniRoute proxy (already configured)
OMNIROUTE_URL=http://localhost:20128/v1
OMNIROUTE_API_KEY=sk-343...b53d
```

### Environment Variable Mapping

| Config Field | Env Var | Source |
|---|---|---|
| `gateway.model` | `GATEWAY_MODEL` | New |
| `gateway.base_url` | `GATEWAY_BASE_URL` | Maps from `OMNIROUTE_URL` |
| `gateway.api_key` | `GATEWAY_API_KEY` | Maps from `OMNIROUTE_API_KEY` |
| `gateway.fallback_models` | `GATEWAY_FALLBACK_MODELS` | New (comma-separated) |

## Verification Tests

Real LLM operations (not mocked) for each provider format:

### Test 1: `infer_model()` Returns Correct Type

```python
import pytest
from pydantic_ai.models import infer_model
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIResponsesModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel

@pytest.mark.parametrize("model_id,expected_type", [
    ("openai-chat:gpt-4o", OpenAIChatModel),
    ("anthropic:claude-sonnet-4-5", AnthropicModel),
    ("google:fable-5-2.5-flash", GoogleModel),
    ("openai:fable-5o", OpenAIResponsesModel),
])
def test_infer_model_returns_correct_type(model_id, expected_type):
    model = infer_model(model_id)
    assert isinstance(model, expected_type)
```

### Test 2: `create_model_from_config()` Integration

```python
import pytest
from agent_core._ai.models import create_model_from_config

def test_create_model_from_config_with_proxy():
    config = MagicMock()
    config.gateway.model = "openai-chat:gpt-4o"
    config.gateway.base_url = "http://localhost:20128/v1"
    config.gateway.api_key = "sk-test"
    
    model = create_model_from_config(config, "openai-chat:fable-5o")
    assert isinstance(model, OpenAIChatModel)
```

### Test 3: `FallbackModel` Failover

```python
import pytest
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.exceptions import ModelAPIError

async def test_fallback_model_failover():
    # Mock primary to fail, fallback to succeed
    primary = AsyncMock()
    primary.run.side_effect = ModelAPIError("Primary down")
    
    fallback = AsyncMock()
    fallback.run.return_value = MagicMock(output="Fallback response")
    
    model = FallbackModel(default_model=primary, fallback_models=[fallback])
    result = await model.run(...)
    assert result.output == "Fallback response"
```

### Test 4: `UsageLimits` Enforcement

```python
async def test_usage_limits_enforced():
    model = infer_model("openai-chat:gpt-4o")
    agent = Agent(model, instructions="Say hello")
    
    with pytest.raises(UsageLimitExceeded):
        await agent.run(
            "task",
            usage_limits=UsageLimits(request_limit=1),
        )
        await agent.run("task again")  # Should fail
```

### Test 5: `build_agent(model=...)` Integration

```python
async def test_build_agent_with_model_param():
    profile = ConsumerRuntimeProfile(
        consumer_name="test-agent",
        tools_allowed=("echo",),
    )
    
    agent = build_agent(
        profile=profile,
        model="openai-chat:gpt-4o",
        tools=[EchoTool()],
    )
    
    result = await agent.run("Say hello")
    assert result.completed is True
    assert result.output is not None
```

### Test 6: Backward Compatibility

```python
async def test_build_agent_backward_compat_gateway():
    gateway = LiteLLMGateway(
        base_url="http://localhost:20128/v1",
        api_key="sk-test",
    )
    
    with pytest.warns(DeprecationWarning, match="gateway="):
        agent = build_agent(
            profile=profile,
            gateway=gateway,  # Deprecated but works
        )
    
    result = await agent.run("task")
    assert result.completed is True
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
| `tests/_ai/test_model_loading.py` | Add | Real LLM verification tests |

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
6. **Real LLM tests**: actual API calls to verify end-to-end model loading

## Rollback

If native model loading causes issues:
1. Restore `llm_gateway/` from git history
2. `build_agent(gateway=...)` is the primary rollback path
3. No schema migration needed — config is additive
