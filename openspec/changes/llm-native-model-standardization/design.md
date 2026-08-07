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
ModelSettings (primary, base_url, api_key, fallback)
  → create_model("openai-chat:fable-5o")
    → infer_model("openai-chat:fable-5o") → OpenAIChatModel
      → FallbackModel(primary, fallbacks=[...]) (optional)
        → BaseAgent(model=fallback_model)
          → AgentRuntime(model=model)
            → UsageLimits(request_limit=N)
              → pydantic_ai.Agent(model=model)
```

## Config Schema (renamed from GatewaySettings)

```python
class ModelSettings(BaseSettings):
    """LLM model settings — native pydantic-ai model resolution.
    
    SECURITY: api_key uses SecretStr to prevent accidental logging.
    Prefer MODEL_API_KEY env var over config.yaml.
    """
    
    primary: str = "openai-chat:fable-5o"
    base_url: str = ""  # Used by proxy endpoints (OmniRoute/LiteLLM)
    api_key: SecretStr = Field(default=SecretStr(""), exclude=True)
    fallback: list[str] = []
    timeout_seconds: float = Field(default=120.0, gt=0)
    
    @field_validator("primary", "fallback")
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
    def _resolve_env_secrets(self) -> "ModelSettings":
        """Resolve api_key from env if not set. NEVER read from yaml."""
        import os
        # H2 addressed: api_key MUST come from env vars, never from yaml
        env_key = os.environ.get("MODEL_API_KEY") or os.environ.get("OMNIROUTE_API_KEY", "")
        if env_key:
            self.api_key = SecretStr(env_key)
        elif not self.api_key.get_secret_value():
            # No env var and no explicit api_key — leave empty (will fail at runtime)
            pass
        return self
    
    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override to always exclude api_key from serialization."""
        kwargs.setdefault("exclude", set())
        if isinstance(kwargs["exclude"], set):
            kwargs["exclude"].add("api_key")
        elif isinstance(kwargs["exclude"], dict):
            kwargs["exclude"]["api_key"] = True
        return super().model_dump(**kwargs)
```

**NOTE**: The old `GatewaySettings` with `bifrost_url`/`litellm_url` is fully removed.
The new `ModelSettings` has no concept of "gateway" — it directly models providers.

## FallbackModel Configuration

```python
from pydantic_ai.models.fallback import FallbackModel

# Narrow fallback_on to exclude auth/config errors
FALLBACK_EXCEPTIONS = (
    ConnectionError,    # Network failures
    TimeoutError,       # Slow responses
    OSError,           # Socket errors
    # NOT: ValueError, AuthenticationError — these should fail immediately
)

model = FallbackModel(
    default_model=infer_model("openai-chat:fable-5o"),
    fallback_models=[infer_model(fid) for fid in fallback_ids],
    fallback_on=FALLBACK_EXCEPTIONS,
)
```

**SECURITY (H1 addressed)**: Auth/config errors (ValueError, AuthenticationError) are NOT in `fallback_on`.
These fail immediately rather than trying fallback providers — prevents credential confusion.
The `FALLBACK_EXCEPTIONS` tuple is the single source of truth — design.md and _ai/models.py both reference it.

## GatewayError Catch Blocks

The old `GatewayError` is caught in 5 places in agent-core:
- `cli/agent_cmd.py` ×4
- `agent_base/agent.py` ×1

These must be updated to catch pydantic-ai exceptions instead:
- `ModelAPIError` — provider errors
- `UsageLimitExceeded` — token/request limits
- `ConnectionError` — network issues

**TASK**: Add explicit error mapping in each catch site.

## File Changes

### Delete (agent-core)

| File | Lines | Reason |
|---|---|---|
| `llm_gateway/types.py` | 46 | `LLMGateway` ABC |
| `llm_gateway/gateway.py` | 323 | `BifrostGateway`, `LiteLLMGateway`, `BudgetTracker` |
| `llm_gateway/resilient.py` | 92 | `ResilientGateway` |
| `llm_gateway/factory.py` | 64 | `GatewayFactory` |
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
| `foundation/settings.py` | Update | `ModelSettings` (replaces GatewaySettings) |
| `sdk/__init__.py` | Update | Remove old re-exports |
| `sdk/agents.py` | Update | `build_agent(model=...)` |
| `sdk/composition.py` | Update | Remove `resolve_gateway()` |
| `agent_base/agent.py` | Update | Accept `model` not `gateway` |
| `cli/utils.py` | Update | Use `infer_model()` |
| `cli/agent_cmd.py` | Update | Update 4x `GatewayError` catch blocks |

### Delete (agent-docs-sync)

| File | Lines | Reason |
|---|---|---|
| `llm/gateway.py` | 93 | `create_gateway()` |
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
| `agents/factory.py` | Update | `gateway` → `model` |
| `services.py` | Update | `gateway` → `model` |
| `stages/classification.py` | Update | Remove `gateway_required` |
| `stages/contracts.py` | Update | Remove `gateway_required` |
| `workflow/graph.py` | Update | Remove `gateway` resolution |

## USD Cost Tracking

**NOTE**: The old `BudgetTracker` provided USD cost enforcement.
pydantic-ai's `UsageLimits` provides token-level limits only.

**Decision**: USD cost tracking is dropped in this change.
It can be re-added later as a pydantic-ai hook if needed.
The `budget_usd` parameter on `BaseAgent.run()` is removed.

## Verification Tests

Real LLM operations (not mocked):

| Test | Provider | Assertion |
|---|---|---|
| `test_infer_model_openai_chat` | `openai-chat:fable-5o` | Model type + real API call |
| `test_infer_model_anthropic` | `anthropic:claude-sonnet-4-5` | Model type + real API call |
| `test_infer_model_google` | `google:fable-5-2.5-flash` | Model type + real API call |
| `test_fallback_model_failover` | Primary fails → Fallback | Real failover |
| `test_usage_limits_enforced` | Any model | UsageLimitExceeded |
| `test_build_agent_model_param` | `build_agent(model=...)` | Agent runs |
| `test_invalid_model_string` | `infer_model("invalid")` | Error raised |
| `test_missing_api_key` | Model creation | Clear error |
| `test_model_format_validation` | `ModelSettings` | Rejects invalid |
| `test_secret_str_not_serialized` | `model_dump()` | api_key excluded |

## Rollback

If issues arise:
1. `git revert` the migration commit
2. Old code exists in git history
3. No config migration needed — old config was empty
