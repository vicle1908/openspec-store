# Design: Complete LLM Model Loading Cleanup (No Backward Compat)

## Architecture: Before → After

### Before
```
GatewaySettings (bifrost_url, litellm_url)
  → create_gateway(bifrost_url, litellm_url)
    → BifrostGateway / LiteLLMGateway
      → .get_model() → OpenAIChatModel(LiteLLMProvider(...))
        → ResilientGateway wrapping inner
          → BaseAgent(gateway=resilient_gateway)
            → AgentRuntime(model=gateway.get_model())
              → BudgetTracker hooks
                → pydantic_ai.Agent(model=cached_model)
```

### After
```
GatewaySettings (model, base_url, api_key, fallback_models)
  → create_model("openai-chat:gpt-4o")
    → infer_model("openai-chat:gpt-4o") → OpenAIChatModel
      → FallbackModel(primary, fallbacks=[...]) (optional)
        → BaseAgent(model=fallback_model)
          → AgentRuntime(model=model)
            → UsageLimits(request_limit=N)
              → pydantic_ai.Agent(model=model)
```

## File Changes

### Delete (agent-core)

| File | Lines | Reason |
|---|---|---|
| `llm_gateway/types.py` | 46 | `LLMGateway` ABC → `pydantic_ai.models.Model` |
| `llm_gateway/gateway.py` | 323 | `BifrostGateway`, `LiteLLMGateway`, `BudgetTracker` |
| `llm_gateway/resilient.py` | 92 | `ResilientGateway` → `FallbackModel` |
| `llm_gateway/factory.py` | 64 | `GatewayFactory` → `infer_model()` |
| `llm_gateway/__init__.py` | 34 | Package re-exports |
| `resilience/engine.py` | 284 | `CircuitBreaker`, `FallbackChain`, `retry_with_jitter` |
| `resilience/decorators.py` | 94 | `resilient_tool` |
| `resilience/__init__.py` | 33 | Package re-exports |
| `tests/llm_gateway/` | 269 | All gateway tests |
| **Total deleted** | **~1,239** | |

### Rewrite (agent-core)

| File | Action | New Lines |
|---|---|---|
| `_ai/models.py` | Rewrite | ~50 (infer_model + FallbackModel) |
| `_ai/hooks.py` | Simplify | Remove BudgetTracker, keep USD hook |
| `foundation/settings.py` | Update | GatewaySettings new schema |
| `sdk/__init__.py` | Update | Remove old re-exports |
| `sdk/agents.py` | Update | `build_agent(model=...)` |
| `sdk/composition.py` | Update | Remove `resolve_gateway()` |
| `agent_base/agent.py` | Update | Accept `model` not `gateway` |
| `cli/utils.py` | Update | Use `infer_model()` |

### Delete (agent-docs-sync)

| File | Lines | Reason |
|---|---|---|
| `llm/gateway.py` | 93 | `create_gateway()`, `ResilientGateway` |
| `llm/__init__.py` | 5 | Package re-exports |
| **Total deleted** | **98** | |

### Rewrite (agent-docs-sync)

| File | Action | Changes |
|---|---|---|
| `llm/model.py` | NEW | `create_model()` using `infer_model()` |
| `workflows/canonical.py` | Update | Remove `gateway` parameter |
| `workflows/full_pipeline.py` | Update | Use `create_model()` |
| `agents/generation.py` | Update | Remove `gateway` parameter |
| `agents/discovery.py` | Update | Remove `gateway` parameter |
| `agents/validation.py` | Update | Remove `gateway` parameter |
| `agent.py` | Update | Remove `gateway` parameter |
| `cli.py` | Update | Use `create_model()` |
| `config.py` | Update | Remove `RuntimeConfigLike` protocol |

### Update (agent-harness)

| File | Action | Changes |
|---|---|---|
| `agents/factory.py` | Update | `gateway` → `model` in `StageCompositionContext` |
| `services.py` | Update | `gateway` → `model` in `StageServices`, `HarnessServices` |
| `stages/classification.py` | Update | Remove `gateway_required` |
| `stages/contracts.py` | Update | Remove `gateway_required` |
| `workflow/graph.py` | Update | Remove `gateway` resolution |

### Update (tests)

| File | Action |
|---|---|
| `tests/llm_gateway/` | Delete entire directory |
| `tests/_ai/test_native_approvals.py` | Remove `LLMGateway` mock |
| `tests/_ai/test_run_controls.py` | Remove `LLMGateway` mock |
| `tests/agent_base/test_agent.py` | Remove `LLMGateway` mock |
| `tests/_ai/test_model_loading.py` | NEW — Real LLM verification |

## Config Schema

```python
class GatewaySettings(BaseSettings):
    """LLM gateway — native pydantic-ai model resolution.
    
    SECURITY: api_key uses SecretStr to prevent accidental logging.
    Prefer GATEWAY_API_KEY env var over config.yaml.
    """
    
    model: str = "openai-chat:fable-5o"
    base_url: str = ""
    api_key: SecretStr = Field(default=SecretStr(""), exclude=True)
    fallback_models: list[str] = []
    semantic_cache_enabled: bool = False
    semantic_cache_ttl_seconds: int = Field(default=3600, ge=0)
    
    @field_validator("model", "fallback_models")
    @classmethod
    def _validate_model_format(cls, v: Any) -> Any:
        """Validate provider:model_name format."""
        import re
        pattern = re.compile(r"^[a-z][a-z0-9_-]*:[a-zA-Z0-9._-]+$")
        if isinstance(v, str) and not pattern.match(v):
            raise ValueError(f"Invalid model format: {v!r}")
        if isinstance(v, list):
            for item in v:
                if not pattern.match(item):
                    raise ValueError(f"Invalid fallback model: {item!r}")
        return v
    
    @model_validator(mode="after")
    def _resolve_env_secrets(self) -> "GatewaySettings":
        """Resolve api_key from env if not set."""
        import os
        if not self.api_key.get_secret_value():
            env_key = os.environ.get("GATEWAY_API_KEY") or os.environ.get("OMNIROUTE_API_KEY", "")
            if env_key:
                self.api_key = SecretStr(env_key)
        return self
```

## SDK Surface

```python
# BEFORE (removed)
from agent_core.sdk import (
    LLMGateway, BifrostGateway, LiteLLMGateway, ResilientGateway,
    CircuitBreaker, CircuitBreakerRegistry, CircuitBreakerOpenError,
    FallbackChain, FallbackEntry, FallbackChainError,
    retry_with_jitter, resilient_tool,
    build_agent,  # gateway= parameter
)

# AFTER (new)
from agent_core.sdk import (
    build_agent,  # model= parameter
    # No gateway/resilience re-exports — use pydantic_ai directly
)
```

## Verification Tests

Real LLM operations (not mocked):

| Test | Provider | Assertion |
|---|---|---|
| `test_infer_model_openai_chat` | `openai-chat:gpt-4o` | Model type + real API call |
| `test_infer_model_anthropic` | `anthropic:claude-sonnet-4-5` | Model type + real API call |
| `test_infer_model_google` | `google:fable-5-2.5-flash` | Model type + real API call |
| `test_infer_model_openai_responses` | `openai:gpt-4o` | Model type + real API call |
| `test_fallback_model_failover` | Primary fails → Fallback | Real failover |
| `test_usage_limits_enforced` | Any model | UsageLimitExceeded |
| `test_build_agent_model_param` | `build_agent(model=...)` | Agent runs |
| `test_invalid_model_string` | `infer_model("invalid")` | Error raised |
| `test_missing_api_key` | Model creation | Clear error |
| `test_model_format_validation` | `GatewaySettings` | Rejects invalid |
| `test_secret_str_not_serialized` | `model_dump()` | api_key excluded |

## Rollback

If issues arise:
1. `git revert` the migration commit
2. Old code exists in git history
3. No config migration needed — old config was empty
