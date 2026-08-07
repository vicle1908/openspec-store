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

### Task 2.4: Delete `GatewayError` from `foundation/errors.py`
- **Action**: Remove `GatewayError` class (L1 addressed)
- **Action**: Update 5 catch sites in `agent_base/agent.py` (1) and `cli/agent_cmd.py` (4)
- **Replace with**: `except (ModelAPIError, UsageLimitExceeded, ConnectionError)`
- **Verify**: `grep -r "GatewayError" src/` returns 0 hits

### Task 2.5: Rewrite `_ai/models.py`
- **Action**: Replace with `infer_model()` + `FallbackModel`
- **New content**: ~50 lines using `create_model()` and `create_fallback_model()`
- **Add**: `FALLBACK_EXCEPTIONS` tuple (excludes auth/config errors) — H1 addressed

### Task 2.6: Update `foundation/settings.py`
- **Action**: Rename `GatewaySettings` to `ModelSettings`
- **Add**: `env_prefix="MODEL_"` (L2 addressed — documents env var prefix)
- **Remove**: `bifrost_url`, `litellm_url`, `semantic_cache_enabled`, `semantic_cache_ttl_seconds`
- **Add**: `primary`, `base_url`, `api_key` (SecretStr + model_dump override), `fallback`, `timeout_seconds`
- **Add**: Validators for model format

### Task 2.7: Update `sdk/__init__.py`
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
- **Add**: `model_required` field (M2 addressed — replaces fail-closed validation)
- **Update**: `validate()` to check `model_required` instead of `gateway_required`

### Task 4.4: Update `stages/contracts.py`
- **Remove**: `gateway_required` field
- **Add**: `model_required` field (M2 addressed)
- **Update**: Validation logic to use `model_required`

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
grep -r "GatewayError" ~/Developer/agent-core/src/  # Should be 0 hits
```

## Phase 7: Spec Updates (C3 addressed — enumerate 16 specs)

### Task 7.1: Enumerate affected specs
- **Action**: Search for `LLMGateway`, `BifrostGateway`, `LiteLLMGateway`, `ResilientGateway`, `CircuitBreaker`, `FallbackChain`, `BudgetTracker` across all specs
- **Output**: List of 16 spec files with required changes

### Task 7.2: Update `sdk-public-api/spec.md`
- **Action**: Remove `LLMGateway` from Gateway row
- **Action**: Replace with `Model` (pydantic-ai native)
- **Action**: Update `build_agent()` scenarios to use `model=`
- **Action**: Remove "Valid gateway before construction" requirement
- **Action**: Add "Valid model before construction" requirement

### Task 7.3: Update `agent-core-budget-enforcement/spec.md`
- **Action**: Remove `BudgetTracker` references
- **Action**: Replace with `UsageLimits` (token-based)
- **Action**: Note: USD cost tracking dropped (can be re-added later)

### Task 7.4: Update `agent-core-resilience-utility/spec.md`
- **Action**: Remove `CircuitBreaker`, `FallbackChain`, `retry_with_jitter`
- **Action**: Note: Replaced by pydantic-ai native `FallbackModel` + `Agent.run(retries=N)`

### Task 7.5: Update remaining affected specs
- **Action**: Update each of the 16 affected specs

### Task 7.6: Validate specs
```bash
cd ~/Developer/openspec-store
openspec validate --all --strict
```

## Phase 8: Post-Migration Monitoring (L3 addressed)

### Task 8.1: Add monitoring section to proposal
- **Action**: Document error rate baseline before migration
- **Action**: Document fallback model activation alerting
- **Action**: Document latency comparison (old vs new)

### Task 8.2: Create monitoring checklist
- **Action**: Error rate monitoring during/after migration
- **Action**: Fallback model activation alerting
- **Action**: Latency comparison (old gateway vs native infer_model)

## Execution Order

```
Phase 1 (Config) → Phase 2 (agent-core) → Phase 3 (agent-docs-sync) → 
Phase 4 (agent-harness) → Phase 5 (Tests) → Phase 6 (Validation) →
Phase 7 (Spec Updates) → Phase 8 (Monitoring)
```

**Estimated lines removed**: ~1,432
**Estimated lines added**: ~100
**Net reduction**: ~1,332 lines of custom code
