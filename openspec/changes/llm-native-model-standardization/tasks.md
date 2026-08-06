# Tasks: Standardize on Native pydantic-ai Model Loading

## Phase 1: Config & Model Factory (agent-core)

### Task 1.1: Update GatewaySettings schema
- **File**: `src/agent_core/foundation/settings.py`
- **Action**: Add `model`, `base_url`, `api_key`, `fallback_models` fields
- **Keep**: `bifrost_url`, `litellm_url` as deprecated aliases
- **Test**: Config loads correctly with new and legacy fields

### Task 1.2: Rewrite `_ai/models.py`
- **File**: `src/agent_core/_ai/models.py`
- **Action**: Replace 3 custom factories with `infer_model()` delegation
- **Add**: `create_model_from_config(settings, model_id)` function
- **Add**: `create_fallback_model(primary_id, fallback_ids)` function
- **Remove**: `create_bifrost_model()`, `create_litellm_model()`, `create_openai_model()`
- **Test**: Returns correct Model subclass per provider string

### Task 1.3: Update `ConsumerRuntimeProfile.model`
- **File**: `src/agent_core/sdk/config.py`
- **Action**: Document `provider:model_name` format, add validation
- **Test**: `anthropic:claude-opus-4-5` passes validation

## Phase 2: SDK Surface (agent-core)

### Task 2.1: Update `build_agent()` signature
- **File**: `src/agent_core/sdk/agents.py`
- **Action**: Add `model: str | Model | None` parameter
- **Action**: Add backward-compat `gateway` adapter (wraps in FallbackModel)
- **Deprecation**: Log warning when `gateway=` is used
- **Test**: Both `model=` and `gateway=` paths produce working agent

### Task 2.2: Update `resolve_gateway()` → `resolve_model()`
- **File**: `src/agent_core/sdk/composition.py`
- **Action**: Rename to `resolve_model()`, use `infer_model()`
- **Keep**: `resolve_gateway()` as deprecated alias
- **Test**: Model resolution from config works

### Task 2.3: Update SDK re-exports
- **File**: `src/agent_core/sdk/__init__.py`
- **Action**: Add `resolve_model` to exports
- **Action**: Deprecate `LLMGateway`, `ResilientGateway` re-exports
- **Test**: Imports work correctly

## Phase 3: Remove Custom Resilience (agent-core)

### Task 3.1: Replace ResilientGateway with FallbackModel
- **File**: `src/agent_core/llm_gateway/resilient.py` (delete)
- **File**: `src/agent_core/_ai/models.py`
- **Action**: `create_fallback_model()` uses `FallbackModel`
- **Test**: Provider failover works on connection error

### Task 3.2: Remove custom circuit breaker
- **File**: `src/agent_core/resilience/circuit_breaker.py` (delete)
- **File**: `src/agent_core/resilience/__init__.py` (update exports)
- **Test**: No remaining imports of removed classes

### Task 3.3: Remove custom retry
- **File**: `src/agent_core/resilience/retry.py` (delete)
- **Action**: Consumers use `Agent.run(retries=N)` instead
- **Test**: Retry behavior works via pydantic-ai native

### Task 3.4: Remove custom fallback chain
- **File**: `src/agent_core/resilience/fallback.py` (delete)
- **Test**: No remaining imports

### Task 3.5: Remove bulkhead
- **File**: `src/agent_core/resilience/bulkhead.py` (delete)
- **Test**: No remaining imports

## Phase 4: Simplify Agent Runtime (agent-core)

### Task 4.1: Simplify `AgentRuntime.__init__`
- **File**: `src/agent_core/_ai/agent.py`
- **Action**: Accept `Model` directly instead of calling `gateway.get_model()`
- **Test**: Agent construction works with Model instance

### Task 4.2: Simplify `BaseAgent.__init__`
- **File**: `src/agent_core/agent_base/agent.py`
- **Action**: Accept `model: str | Model` instead of `gateway: LLMGateway`
- **Action**: Use `create_model_from_config()` or `infer_model()`
- **Backward-compat**: Accept `gateway` via adapter
- **Test**: Both paths produce working agent

### Task 4.3: Simplify budget hooks
- **File**: `src/agent_core/_ai/hooks.py`
- **Action**: Remove `BudgetTracker` import, use `UsageLimits` for token budgets
- **Keep**: USD cost estimation hook (unique TDT feature)
- **Test**: Token limits enforced via UsageLimits

## Phase 5: Delete Gateway Package (agent-core)

### Task 5.1: Delete `llm_gateway/` package
- **Files**: All 5 files in `src/agent_core/llm_gateway/`
- **Action**: Delete entire package
- **Test**: No remaining imports across workspace

### Task 5.2: Update all imports
- **Files**: All files that imported from `llm_gateway`
- **Action**: Update to use `_ai/models.py` or `pydantic_ai.models` directly
- **Test**: `grep -r "llm_gateway" src/` returns zero hits

## Phase 6: Update Consumers

### Task 6.1: Update agent-docs-sync
- **File**: `src/agent_docs_sync/llm/gateway.py`
- **Action**: Rewrite to use `infer_model()` + `FallbackModel`
- **Action**: Support fallback via env vars
- **Test**: Gateway creation works with new factory

### Task 6.2: Update agent-harness
- **File**: `src/agent_harness/agents/factory.py`
- **Action**: Use `build_agent(model=...)` instead of `gateway=`
- **Test**: Stage agent construction works

### Task 6.3: Update agent-docs-sync workflow
- **File**: `src/agent_docs_sync/workflows/full_pipeline.py`
- **Action**: Update `create_gateway` → `create_model_from_config`
- **Test**: Full pipeline works with new model loading

## Phase 7: Validation

### Task 7.1: Run full test suite
```bash
cd ~/Developer/agent-core && uv run pytest tests/ -q
cd ~/Developer/agent-docs-sync && uv run pytest tests/ -q
cd ~/Developer/agent-harness && uv run pytest tests/ -q
```

### Task 7.2: Run type checks
```bash
cd ~/Developer/agent-core && uv run mypy src/agent_core/ --strict
cd ~/Developer/agent-docs-sync && uv run mypy src/agent_docs_sync/ --strict
cd ~/Developer/agent-harness && uv run mypy src/agent_harness/ --strict
```

### Task 7.3: Run lint
```bash
cd ~/Developer/agent-core && uv run ruff check src/ tests/
cd ~/Developer/agent-docs-sync && uv run ruff check src/ tests/
cd ~/Developer/agent-harness && uv run ruff check src/ tests/
```

### Task 7.4: Verify no remaining imports
```bash
grep -r "from agent_core.llm_gateway" ~/Developer/agent-*/
grep -r "from agent_core.resilience" ~/Developer/agent-*/
grep -r "BifrostGateway\|LiteLLMGateway\|ResilientGateway" ~/Developer/agent-*/
```

## Execution Order

```
Phase 1 (Config) → Phase 2 (SDK) → Phase 3 (Remove Resilience) → 
Phase 4 (Simplify Runtime) → Phase 5 (Delete Gateway) → 
Phase 6 (Update Consumers) → Phase 7 (Validation)
```

**Estimated lines removed**: ~989
**Estimated lines added/modified**: ~200 (simpler, native pydantic-ai)
**Net reduction**: ~789 lines of custom code
