# Proposal: Standardize on Native pydantic-ai Model Loading

## Problem

agent-core has built a custom LLM gateway abstraction layer (`llm_gateway/`)
that duplicates features already provided natively by pydantic-ai v2:

| agent-core Custom | pydantic-ai Native | Delta |
|---|---|---|
| `BifrostGateway`, `LiteLLMGateway` | `infer_model("provider:model_name")` | Custom gateways add no value over `infer_model()` |
| `ResilientGateway` (circuit breaker + fallback) | `FallbackModel(primary, fallbacks=[...])` | pydantic-ai handles failover natively |
| `GatewayFactory` | `infer_provider()` + model constructors | Registry pattern unnecessary |
| `create_gateway()` factory | `Agent(model="anthropic:claude-opus-4-5")` | Agent accepts model strings directly |
| `BudgetTracker` (USD cost) | `UsageLimits(request_limit=N, tokens_limit=N)` | pydantic-ai tracks tokens natively; USD is the only unique part |
| `retry_with_jitter` | `Agent.run(retries=N)` | Built-in retry with exponential backoff |
| `CircuitBreaker` / `FallbackChain` | `FallbackModel` | Native provider failover |
| `OpenAIChatModel(LiteLLMProvider)` only | 25+ model classes, 30+ providers | Currently locked to one format |

**Impact**: agent-core cannot use Anthropic native, Google native, OpenAI Responses API,
or any of the 30+ providers pydantic-ai supports without routing through LiteLLM proxy.

## Current Config State

```yaml
# ~/.tdt/config.yaml — NO gateway section exists
# ~/.tdt/.env — OMNIROUTE_URL=http://localhost:20128/v1 (proxy, not wired)
```

Gateway settings are **empty** — consumers rely on env vars that are never set.

## Solution

Standardize on pydantic-ai's native model resolution and remove the custom gateway layer.
Keep TDT-specific features (flavors, skills, authority, tool registry, USD budget tracking)
that pydantic-ai does not provide.

### Target Config

```yaml
# ~/.tdt/config.yaml
gateway:
  # Primary model (pydantic-ai "provider:model_name" format)
  model: "openai-chat:gpt-4o"
  # Proxy endpoint (for OmniRoute/LiteLLM/Bifrost)
  base_url: "http://localhost:20128/v1"
  api_key: "${OMNIROUTE_API_KEY}"
  # Fallback models
  fallback_models:
    - "openai-chat:fable-5o-mini"
  # Semantic cache
  semantic_cache_enabled: false
  semantic_cache_ttl_seconds: 3600
```

```bash
# ~/.tdt/.env
OMNIROUTE_URL=http://localhost:20128/v1
OMNIROUTE_API_KEY=sk-343...b53d
```

### What Gets Removed

1. **`llm_gateway/` package** (~600 lines)
   - `BifrostGateway`, `LiteLLMGateway` → `infer_model()` or direct model creation
   - `ResilientGateway` → `FallbackModel`
   - `GatewayFactory` → removed (unused in practice)
   - `create_gateway()` → `create_model_from_config()`
   - `LLMGateway` ABC → `pydantic_ai.models.Model` directly

2. **`_ai/models.py`** (109 lines)
   - `create_bifrost_model()`, `create_litellm_model()`, `create_openai_model()` → `infer_model()`
   - `create_model_from_env()` → simplified env resolution

3. **`resilience/` custom circuit breaker & retry** (~400 lines)
   - `CircuitBreaker`, `CircuitBreakerRegistry` → `FallbackModel` handles failover
   - `retry_with_jitter` → `Agent.run(retries=N)` or `AgentRetries`
   - `FallbackChain`, `FallbackEntry` → `FallbackModel.fallback_models`

4. **`BudgetTracker`** → `UsageLimits` for token budgets; USD tracking via lightweight hook

### What Gets Added

1. **`_ai/models.py`** — simplified model factory using `infer_model()`
2. **`GatewaySettings`** — extensible config for provider-native auth
3. **`ConsumerRuntimeProfile.model`** — supports `provider:model_name` format
4. **Real verification tests** — actual LLM API calls (not mocked)

### What Stays (TDT-specific, no pydantic-ai equivalent)

- `BaseAgent` — flavor composition, skill resolution
- `AgentRuntime` — thin pydantic-ai Agent wrapper (simplified)
- `ToolRegistry` + `BaseTool` — authority, approval, metadata lifecycle
- `CapabilityAuthorityPolicy` — TDT security model
- `ConsumerRuntimeProfile` — TDT config composition
- `Flavor` system — agent personality/policy
- `Skill` system — skill matching
- USD cost tracking hook — pydantic-ai only tracks tokens

## Consumers

| Repo | Impact | Change |
|---|---|---|
| agent-docs-sync | Gateway creation changes | `llm/gateway.py` uses new model factory |
| agent-harness | Transparent | Receives `Model` via injection, format is invisible |

## Migration

- `LLMGateway` replaced by `pydantic_ai.models.Model` in SDK surface
- `build_agent(gateway=...)` becomes `build_agent(model=...)` or `build_agent(model_id="provider:model")`
- Backward-compat adapter during transition window
- OpenSpec change with `skip_specs: true` for initial config/tooling work

## Verification Strategy

Real LLM operations (not mocked) for each provider format:

| Test | Provider | Assertion |
|---|---|---|
| `test_infer_model_openai_chat` | `openai-chat:gpt-4o` | Model is `OpenAIChatModel`, `run()` returns non-empty output |
| `test_infer_model_anthropic` | `anthropic:claude-sonnet-4-5` | Model is `AnthropicModel`, `run()` returns non-empty output |
| `test_infer_model_google` | `google:fable-5-2.5-flash` | Model is `GoogleModel`, `run()` returns non-empty output |
| `test_infer_model_openai_responses` | `openai:gpt-4o` | Model is `OpenAIResponsesModel`, `run()` returns non-empty output |
| `test_fallback_model_failover` | Primary fails → Fallback | Fallback model used, output returned |
| `test_usage_limits_enforced` | Any model | `UsageLimitExceeded` raised at limit |
| `test_build_agent_model_param` | `build_agent(model=...)` | Agent runs and returns `AgentResult` |
| `test_backward_compat_gateway_param` | `build_agent(gateway=...)` | Works with deprecation warning |

## Risks

- USD budget tracking loses granular per-request cost estimation (currently hooks into after_model_request)
- ResilientGateway circuit breaker has different failure semantics than FallbackModel
- agent-docs-sync's fallback endpoint pattern needs rework
