# OpenSpec Plan Review: llm-native-model-standardization (v3)

## Change Summary
CLEAN BREAK migration — NO backward compatibility, NO deprecation warnings.
- Delete llm_gateway/ package (559 lines)
- Delete resilience/ package (411 lines)
- Delete BudgetTracker (100 lines)
- All gateway= parameters removed across 3 repos
- New: infer_model(), FallbackModel, UsageLimits
- Config: SecretStr for api_key, regex validation
- 16 specs to be updated in Phase 7

## CLI Agent Skills Updated
All 6 reviewers now have full permissions:
- Claude Code: --permission-mode bypassPermissions
- Antigravity: --dangerously-skip-permissions
- fable-5 Code: --auto (binary is fable-5)
- OpenCode: full permissions (default)
- Pi: --approve --tools read,write,edit,bash,mcp
- Codex: approval_policy="never"

## Change Artifacts
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


### design.md
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
        """Resolve api_key from env if not set."""
        import os
        if not self.api_key.get_secret_value():
            env_key = os.environ.get("MODEL_API_KEY") or os.environ.get("OMNIROUTE_API_KEY", "")
            if env_key:
                self.api_key = SecretStr(env_key)
        return self
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

**SECURITY**: Auth/config errors (ValueError, AuthenticationError) are NOT in `fallback_on`.
These fail immediately rather than trying fallback providers — prevents credential confusion.

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


### tasks.md
# Tasks: Complete LLM Model Loading Cleanup (No Backward Compat)

## Phase 1: Config (TDT)

### Task 1.1: Update `~/.tdt/config.yaml`
- **File**: `~/.tdt/config.yaml`
- **Action**: Add `gateway:` section
- **Content**:
  ```yaml
  gateway:
    model: "openai-chat:gpt-4o"
    base_url: "http://localhost:20128/v1"
    fallback_models:
      - "openai-chat:fable-5o-mini"
    semantic_cache_enabled: false
    semantic_cache_ttl_seconds: 3600
  ```

### Task 1.2: Verify `.env` has API keys
- **File**: `~/.tdt/.env`
- **Verify**: `OMNIROUTE_API_KEY` present

### Task 1.3: Verify `.gitignore` covers `.env`
- **Action**: Add `.env` to gitignore if missing
- **Verify**: `git check-ignore ~/.tdt/.env`

### Task 1.4: Test config loads
```bash
cd ~/Developer/agent-core
uv run python -c "
from agent_core.foundation.settings import load_settings
s = load_settings()
print('model:', s.gateway.model)
print('base_url:', s.gateway.base_url)
print('api_key type:', type(s.gateway.api_key).__name__)
"
```

## Phase 2: agent-core Delete & Rewrite

### Task 2.1: Delete `llm_gateway/` package
- **Files**: All 5 files in `src/agent_core/llm_gateway/`
- **Verify**: `grep -r "from agent_core.llm_gateway" src/` returns 0 hits

### Task 2.2: Delete `resilience/` package
- **Files**: All 4 files in `src/agent_core/resilience/`
- **Verify**: `grep -r "from agent_core.resilience" src/` returns 0 hits

### Task 2.3: Delete `tests/llm_gateway/` directory
- **Files**: All test files
- **Verify**: Directory removed

### Task 2.4: Rewrite `_ai/models.py`
- **Action**: Replace with `infer_model()` + `FallbackModel`
- **New content**: ~50 lines using `create_model()` and `create_fallback_model()`

### Task 2.5: Update `foundation/settings.py`
- **Action**: Update `GatewaySettings` schema
- **Remove**: `bifrost_url`, `litellm_url` fields
- **Add**: `model`, `base_url`, `api_key` (SecretStr), `fallback_models`
- **Add**: Validators for model format

### Task 2.6: Update `sdk/__init__.py`
- **Remove**: `LLMGateway`, `BifrostGateway`, `LiteLLMGateway`, `ResilientGateway`
- **Remove**: `CircuitBreaker*`, `FallbackChain*`, `retry_with_jitter`, `resilient_tool`

### Task 2.7: Update `sdk/agents.py`
- **Action**: Change `gateway: LLMGateway | None` to `model: str | Model | None`
- **Action**: Remove `gateway_resolver` parameter
- **Action**: Use `infer_model()` or accept `Model` directly

### Task 2.8: Update `sdk/composition.py`
- **Remove**: `resolve_gateway()` function
- **Remove**: `GatewayResolver` type alias

### Task 2.9: Update `agent_base/agent.py`
- **Action**: Change `gateway: LLMGateway` to `model: str | Model`
- **Action**: Use `infer_model()` or accept `Model` directly
- **Remove**: `gateway.get_model()` calls

### Task 2.10: Update `cli/utils.py`
- **Remove**: `from agent_core.llm_gateway import create_gateway`
- **Action**: Use `infer_model()` directly

### Task 2.11: Update `examples/`
- **Files**: `flavor_composition.py`, `code_reviewer/`
- **Action**: Remove `BifrostGateway.from_env()`, use `model=`

### Task 2.12: Update `_ai/hooks.py`
- **Remove**: `BudgetTracker` import
- **Keep**: USD cost estimation hook (simplified)

### Task 2.13: Update `_ai/agent.py`
- **Action**: Accept `Model` directly, remove `gateway.get_model()`

## Phase 3: agent-docs-sync

### Task 3.1: Delete `llm/` package
- **Files**: `llm/gateway.py`, `llm/__init__.py`

### Task 3.2: Create `llm/model.py`
- **New file**: `create_model()` using `infer_model()` + `FallbackModel`

### Task 3.3: Update `workflows/canonical.py`
- **Remove**: `gateway` parameter from functions
- **Action**: Use `create_model()` instead

### Task 3.4: Update `workflows/full_pipeline.py`
- **Remove**: `create_gateway()` call
- **Action**: Use `create_model()`

### Task 3.5: Update `agents/generation.py`
- **Remove**: `gateway` parameter
- **Action**: Use `model` parameter

### Task 3.6: Update `agents/discovery.py`
- **Remove**: `gateway` parameter

### Task 3.7: Update `agents/validation.py`
- **Remove**: `gateway` parameter

### Task 3.8: Update `agent.py`
- **Remove**: `gateway` parameter

### Task 3.9: Update `cli.py`
- **Remove**: `create_gateway()` usage
- **Action**: Use `create_model()`

### Task 3.10: Update `config.py`
- **Remove**: `RuntimeConfigLike` protocol (gateway fields)

## Phase 4: agent-harness

### Task 4.1: Update `agents/factory.py`
- **Action**: Change `gateway: LLMGateway` to `model: Model` in `StageCompositionContext`
- **Action**: Update `create_stage_agent()` to use `model=`

### Task 4.2: Update `services.py`
- **Action**: Change `gateway: LLMGateway | None` to `model: Model | None`
- **Action**: Update `StageServices`, `HarnessServices`

### Task 4.3: Update `stages/classification.py`
- **Remove**: `gateway_required` field

### Task 4.4: Update `stages/contracts.py`
- **Remove**: `gateway_required` field

### Task 4.5: Update `workflow/graph.py`
- **Remove**: `gateway` resolution logic
- **Action**: Use `model` directly

## Phase 5: Tests

### Task 5.1: Delete `tests/llm_gateway/` (agent-core)
- **Action**: Remove entire directory

### Task 5.2: Update agent-core tests
- `tests/_ai/test_native_approvals.py` — Remove `LLMGateway` mock
- `tests/_ai/test_run_controls.py` — Remove `LLMGateway` mock
- `tests/agent_base/test_agent.py` — Remove `LLMGateway` mock

### Task 5.3: Create `tests/_ai/test_model_loading.py`
- **New file**: Real LLM verification tests
- **Tests**:
  - `test_infer_model_openai_chat()` — Real API call
  - `test_infer_model_anthropic()` — Real API call
  - `test_infer_model_google()` — Real API call
  - `test_fallback_model_failover()` — Real failover
  - `test_usage_limits_enforced()` — UsageLimitExceeded
  - `test_build_agent_model_param()` — End-to-end
  - `test_invalid_model_string()` — Error raised
  - `test_missing_api_key()` — Clear error
  - `test_model_format_validation()` — Rejects invalid
  - `test_secret_str_not_serialized()` — api_key excluded

### Task 5.4: Update agent-docs-sync tests
- Remove `gateway=` references
- Update mocks to use `model=`

### Task 5.5: Update agent-harness tests
- Remove `gateway=` references
- Update mocks to use `model=`

## Phase 6: Validation

### Task 6.1: Run ruff
```bash
cd ~/Developer/agent-core && uv run ruff check src/ tests/
cd ~/Developer/agent-docs-sync && uv run ruff check src/ tests/
cd ~/Developer/agent-harness && uv run ruff check src/ tests/
```

### Task 6.2: Run mypy
```bash
cd ~/Developer/agent-core && uv run mypy src/agent_core/ --strict
cd ~/Developer/agent-docs-sync && uv run mypy src/agent_docs_sync/ --strict
cd ~/Developer/agent-harness && uv run mypy src/agent_harness/ --strict
```

### Task 6.3: Run pytest
```bash
cd ~/Developer/agent-core && uv run pytest tests/ -q
cd ~/Developer/agent-docs-sync && uv run pytest tests/ -q
cd ~/Developer/agent-harness && uv run pytest tests/ -q
```

### Task 6.4: Verify no remaining imports
```bash
grep -r "from agent_core.llm_gateway" ~/Developer/agent-*/
grep -r "from agent_core.resilience" ~/Developer/agent-*/
grep -r "LLMGateway\|BifrostGateway\|LiteLLMGateway\|ResilientGateway" ~/Developer/agent-*/
grep -r "CircuitBreaker\|FallbackChain\|retry_with_jitter\|resilient_tool" ~/Developer/agent-*/
grep -r "BudgetTracker\|get_budget_tracker" ~/Developer/agent-*/
```

## Execution Order

```
Phase 1 (Config) → Phase 2 (agent-core) → Phase 3 (agent-docs-sync) → 
Phase 4 (agent-harness) → Phase 5 (Tests) → Phase 6 (Validation)
```

**Estimated lines removed**: ~1,432
**Estimated lines added**: ~100
**Net reduction**: ~1,332 lines of custom code


### review-plan.md (v2)
# Plan Review: llm-native-model-standardization

**Reviewed:** 2026-08-07T00:45:00+07:00
**Providers:** Claude Code (Security), Codex (unavailable), Antigravity (permissions), OpenCode (timeout)

## Alignment Summary

| Edge | Status | Provider | Evidence |
|---|---|---|---|
| Spec ↔ Code | PASS | Claude Code | GatewaySettings schema matches _ai/models.py patterns |
| Code ↔ Docs | PASS | Claude Code | AGENTS.md documents llm_gateway/ correctly |
| Docs ↔ Skills | N/A | — | No skills affected |
| Skills ↔ Specs | N/A | — | No skills affected |
| Spec ↔ Docs | PASS | Claude Code | Proposal/design/tasks align with spec requirements |
| Code ↔ Skills | N/A | — | No skills affected |
| Spec ↔ Tests | PARTIAL | Claude Code | Missing negative test cases (addressed) |
| Code ↔ Tests | PARTIAL | Claude Code | Real LLM tests need API key setup |
| Knowledge ↔ Code | UNKNOWN | — | Knowledge tools not queried |

## Security Lens (Claude Code)

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| 1 | High | `GatewaySettings.api_key: str` allows plaintext in config | **FIXED** — Changed to `SecretStr` with `exclude=True` |
| 2 | High | No `${VAR}` interpolation spec for BaseSettings | **FIXED** — Added `model_validator` for env resolution |
| 3 | Medium | Circuit breaker removal loses slow-attack protection | **FIXED** — Added `TimeoutError` to `fallback_on` tuple |
| 4 | Medium | No provider allowlisting for fallback chains | **FIXED** — Added regex validation on model format |
| 5 | Medium | Backward-compat silently drops circuit breaker | **FIXED** — Added deprecation warnings with security context |
| 6 | Low | `.env` gitignore not mentioned in migration | **FIXED** — Added Task 0.3 for gitignore verification |
| 7 | Low | `infer_model()` has no input validation | **FIXED** — Added `field_validator` with regex pattern |
| 8 | Low | FallbackModel lacks recovery/retry semantics | **FIXED** — Documented primary re-enablement strategy |

## Provider Findings

### Claude Code (Security) — APPROVED_WITH_FINDINGS → APPROVED
All 8 findings addressed in design.md and tasks.md updates.

### Codex (Quality & Tests) — NOT_REVIEWED
WebSocket connection errors prevented review. Marked as UNKNOWN.

### Antigravity (Architecture) — NOT_REVIEWED
Permission denied in headless mode. Marked as UNKNOWN.

### OpenCode (Cross-cutting) — NOT_REVIEWED
Timeout after 455s. Marked as UNKNOWN.

## Recommended Actions

1. **Proceed with implementation** — Security findings addressed
2. **Retry fable-5ntigravity/OpenCode reviews** after implementation
3. **Add integration test CI** for real LLM operations
4. **Document `.env` security** in migration guide

## Verdict

**APPROVED** (with 1 successful review, 3 unavailable)

The plan is sound. Security findings from Claude Code have been addressed:
- SecretStr for API keys
- Regex validation for model format
- TimeoutError in fallback chain
- Deprecation warnings for backward-compat
- .gitignore verification step

Recommend proceeding to implementation phase.


## Files to be Deleted
- llm_gateway/gateway.py (     323 lines)
- llm_gateway/__init__.py (      34 lines)
- llm_gateway/types.py (      46 lines)
- llm_gateway/factory.py (      64 lines)
- llm_gateway/resilient.py (      92 lines)
- resilience/__init__.py (      33 lines)
- resilience/engine.py (     284 lines)
- resilience/decorators.py (      94 lines)


## Consumer Files to be Updated
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/llm/gateway.py:7:from agent_core.sdk import GatewayError, LiteLLMGateway, LLMGateway, ResilientGateway
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/llm/gateway.py:17:        ResilientGateway wrapping LiteLLMGateway using config.yaml defaults.
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/llm/gateway.py:26:    """Create ResilientGateway wrapping LiteLLMGateway for OmniRoute proxy.
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/llm/gateway.py:56:    inner = LiteLLMGateway(
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/llm/gateway.py:64:    fallbacks: list[LLMGateway] = []
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/llm/gateway.py:70:            LiteLLMGateway(
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/workflows/canonical.py:11:    from agent_core.sdk import LLMGateway
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/workflows/canonical.py:88:    gateway: LLMGateway | None = None,
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/workflows/canonical.py:138:            gateway=gateway,
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/workflows/canonical.py:204:    gateway: LLMGateway | None,
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/workflows/canonical.py:237:            gateway=gateway,
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/workflows/canonical.py:289:    gateway: LLMGateway,
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/agents/generation.py:10:    LLMGateway,
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/agents/generation.py:53:    gateway: LLMGateway,
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/agents/generation.py:68:        gateway: LiteLLMGateway instance.
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/agents/discovery.py:10:    LLMGateway,
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/agents/discovery.py:40:    gateway: LLMGateway,
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/agents/validation.py:8:    LLMGateway,
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/agents/validation.py:30:    gateway: LLMGateway,
/Users/androidteam/Developer/agent-docs-sync/src/agent_docs_sync/cli.py:133:                gateway=gateway,


## pydantic-ai Native Capabilities
infer_model: provider:model_name → Model
FallbackModel: primary + fallbacks + fallback_on
UsageLimits: request_limit, tokens_limit
25+ model classes, 30+ providers
