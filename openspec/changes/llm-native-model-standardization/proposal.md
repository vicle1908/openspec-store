# Proposal: Complete LLM Model Loading Cleanup (No Backward Compat)

## Problem

agent-core has built a custom LLM gateway abstraction layer (`llm_gateway/`)
that duplicates features already provided natively by pydantic-ai v2:

| agent-core Custom | pydantic-ai Native | Lines |
|---|---|---|
| `BifrostGateway` | `infer_model("provider:model_name")` | 323 |
| `LiteLLMGateway` | `infer_model("provider:model_name")` | 215 |
| `ResilientGateway` | `FallbackModel(primary, fallbacks=[...])` | 92 |
| `GatewayFactory` | `infer_provider()` | 64 |
| `LLMGateway` ABC | `pydantic_ai.models.Model` | 46 |
| `create_gateway()` | `infer_model()` | 34 |
| `CircuitBreaker` + `Registry` | `FallbackModel` | 284 |
| `FallbackChain` + `Entry` | `FallbackModel.fallback_models` | 100 |
| `retry_with_jitter` | `Agent.run(retries=N)` | 80 |
| `BudgetTracker` | `UsageLimits` (tokens) | 100 |
| `resilient_tool` decorator | Native retry | 94 |
| **Total** | | **~1,432 lines** |

**Current state**: agent-core is locked to `OpenAIChatModel(LiteLLMProvider)` only.
Cannot use Anthropic native, Google native, OpenAI Responses API, or 30+ other providers.

**Config state**: `~/.tdt/config.yaml` has NO gateway section. All settings empty.

## Solution

**Complete removal** of custom gateway/resilience/budget layers. No backward compatibility.
No deprecation warnings. Clean break to native pydantic-ai patterns.

### What Gets Deleted

#### agent-core `llm_gateway/` package (5 files, 559 lines)
- `llm_gateway/types.py` — `LLMGateway` ABC
- `llm_gateway/gateway.py` — `BifrostGateway`, `LiteLLMGateway`, `BudgetTracker`, `create_gateway()`
- `llm_gateway/resilient.py` — `ResilientGateway`
- `llm_gateway/factory.py` — `GatewayFactory`
- `llm_gateway/__init__.py` — Package re-exports

#### agent-core `resilience/` package (4 files, ~411 lines)
- `resilience/engine.py` — `CircuitBreaker`, `CircuitBreakerRegistry`, `FallbackChain`, `FallbackEntry`, `retry_with_jitter`
- `resilience/decorators.py` — `resilient_tool`
- `resilience/__init__.py` — Package re-exports

#### agent-core `_ai/models.py` (109 lines rewritten)
- `create_bifrost_model()`, `create_litellm_model()`, `create_openai_model()` — replaced with `infer_model()`
- `create_model_from_env()` — simplified

#### agent-core SDK re-exports (sdk/__init__.py)
- Remove `LLMGateway`, `BifrostGateway`, `LiteLLMGateway`, `ResilientGateway`
- Remove `CircuitBreaker`, `CircuitBreakerRegistry`, `CircuitBreakerOpenError`
- Remove `FallbackChain`, `FallbackEntry`, `FallbackChainError`
- Remove `retry_with_jitter`, `resilient_tool`

#### agent-core CLI (cli/utils.py)
- Remove `create_gateway()` import and usage
- Use `infer_model()` directly

#### agent-core examples (3 files)
- `examples/flavor_composition.py` — Remove `BifrostGateway.from_env()`
- `examples/code_reviewer/` — Remove `LLMGateway` usage

#### agent-docs-sync (entire `llm/` package + consumers)
- `llm/gateway.py` — Delete (93 lines)
- `llm/__init__.py` — Delete
- `workflows/canonical.py` — Remove `gateway` parameter
- `workflows/full_pipeline.py` — Remove `create_gateway()` call
- `agents/generation.py` — Remove `gateway` parameter
- `agents/discovery.py` — Remove `gateway` parameter
- `agents/validation.py` — Remove `gateway` parameter
- `agent.py` — Remove `gateway` parameter
- `cli.py` — Remove `create_gateway()` usage
- `config.py` — Remove `RuntimeConfigLike` protocol (gateway fields)

#### agent-harness (consumers)
- `agents/factory.py` — Remove `gateway` from `StageCompositionContext`
- `services.py` — Remove `gateway` from `StageServices`, `HarnessServices`
- `stages/classification.py` — Remove `gateway_required`
- `stages/contracts.py` — Remove `gateway_required`
- `workflow/graph.py` — Remove `gateway` resolution

#### Tests (all repos)
- `tests/llm_gateway/` — Delete entire directory (269 lines)
- All test files referencing `LLMGateway`, `gateway=`, `ResilientGateway`

### What Gets Added

#### agent-core `_ai/models.py` (rewritten, ~50 lines)
```python
"""Model factory — native pydantic-ai model resolution."""

from pydantic_ai.models import infer_model, Model

def create_model(model_id: str) -> Model:
    """Create a pydantic-ai Model from 'provider:model_name' string."""
    return infer_model(model_id)

def create_fallback_model(
    primary_id: str,
    fallback_ids: list[str],
) -> Model:
    """Create a FallbackModel with primary and fallback chains."""
    from pydantic_ai.models.fallback import FallbackModel
    return FallbackModel(
        default_model=infer_model(primary_id),
        fallback_models=[infer_model(fid) for fid in fallback_ids],
        fallback_on=(Exception,),  # Failover on any error
    )
```

#### agent-core `foundation/settings.py` (GatewaySettings updated)
```python
class GatewaySettings(BaseSettings):
    """LLM gateway settings — native pydantic-ai model resolution."""
    
    model: str = "openai-chat:fable-5o"
    base_url: str = ""
    api_key: SecretStr = Field(default=SecretStr(""), exclude=True)
    fallback_models: list[str] = []
    semantic_cache_enabled: bool = False
    semantic_cache_ttl_seconds: int = Field(default=3600, ge=0)
```

#### agent-core SDK (sdk/agents.py updated)
```python
def build_agent(
    profile: ConsumerRuntimeProfile | None = None,
    model: str | Model | None = None,  # NEW: replaces gateway=
    tools: list[Any] | ToolRegistry | None = None,
    ...
) -> BaseAgent:
    """Build a BaseAgent with typed composition."""
    if model is None:
        raise ValueError("build_agent requires model= parameter")
    ...
```

#### agent-docs-sync `llm/model.py` (replaces gateway.py)
```python
"""Model factory for agent-docs-sync."""

from pydantic_ai.models import infer_model, Model
from pydantic_ai.models.fallback import FallbackModel

def create_model(config: RuntimeConfigLike) -> Model:
    """Create model from consumer config."""
    settings = config.settings.gateway
    model_id = config.model or settings.model or "openai-chat:gpt-4o"
    
    if settings.fallback_models:
        return FallbackModel(
            default_model=infer_model(model_id),
            fallback_models=[infer_model(fid) for fid in settings.fallback_models],
            fallback_on=(Exception,),
        )
    return infer_model(model_id)
```

#### agent-harness (services.py updated)
```python
@dataclass(frozen=True, slots=True)
class StageServices:
    stage: Stage
    runtime: ConsumerRuntimeProfile | None
    model: Model | None  # replaces gateway: LLMGateway | None
    ...

@dataclass(frozen=True, slots=True)
class HarnessServices:
    model: Model | None = None  # replaces gateway
    ...
```

## Config Changes

### `~/.tdt/config.yaml` — New Gateway Section
```yaml
gateway:
  model: "openai-chat:gpt-4o"
  base_url: "http://localhost:20128/v1"
  fallback_models:
    - "openai-chat:fable-5o-mini"
  semantic_cache_enabled: false
  semantic_cache_ttl_seconds: 3600
```

### `~/.tdt/.env` — Keep Existing Keys
```bash
OMNIROUTE_URL=http://localhost:20128/v1
OMNIROUTE_API_KEY=sk-343...b53d
```

## Consumers

| Repo | Changes | Lines Affected |
|---|---|---|
| agent-core | Delete llm_gateway/, resilience/, rewrite _ai/models.py, sdk/ | ~1,432 removed, ~100 added |
| agent-docs-sync | Delete llm/gateway.py, update all agents/workflows | ~200 affected |
| agent-harness | Update services.py, factory.py, stages, workflow | ~100 affected |

## Verification

Real LLM operations (not mocked):
- `infer_model("openai-chat:gpt-4o")` → `OpenAIChatModel` + real API call
- `infer_model("anthropic:claude-sonnet-4-5")` → `AnthropicModel` + real API call
- `infer_model("google:fable-5-2.5-flash")` → `GoogleModel` + real API call
- `FallbackModel` failover with real providers
- `build_agent(model=...)` end-to-end with real API

## Execution Order

```
Phase 1: Config (update ~/.tdt/config.yaml + .env)
Phase 2: agent-core (delete packages, rewrite models, update SDK)
Phase 3: agent-docs-sync (delete llm/, update consumers)
Phase 4: agent-harness (update services, factory, stages)
Phase 5: Tests (delete old, add new verification)
Phase 6: Validation (ruff, mypy, pytest, import checks)
```
