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

### Task 2.3b: Delete `tests/resilience/` directory
- **Files**: `tests/resilience/test_engine.py` (22 tests, 373 lines), `tests/resilience/test_decorators.py`, `tests/resilience/__init__.py`
- **Reason**: Source code (`resilience/`) is deleted in Task 2.2; these tests import from deleted modules
- **Verify**: `ls tests/resilience/` returns "No such file or directory"

### Task 2.4: Delete `GatewayError` from `foundation/errors.py`
- **Action**: Remove `GatewayError` class (L1 addressed)
- **Action**: Remove re-export from `foundation/__init__.py` (line 10 and `__all__` line 53)
- **Action**: Update 5 catch sites in `agent_base/agent.py` (1) and `cli/agent_cmd.py` (4)
- **Replace with**: `except (ModelAPIError, UsageLimitExceeded, ConnectionError)`
- **Exception mapping**: `UsageLimitExceeded` → `RunReason.BUDGET_EXCEEDED`, `ModelAPIError` → `RunReason.PROVIDER_ERROR`, `ConnectionError` → `RunReason.CONNECTIVITY_ERROR`
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
- **Remove**: `from agent_core.llm_gateway.gateway import get_budget_tracker` (lines 16 and 35)
- **Remove**: All `BudgetTracker` usage (`pre_check`, `check_and_record` calls)
- **Replace with**: `UsageLimits` from pydantic-ai for token-based limits
- **Keep**: USD cost estimation hook (simplified — log-only, no enforcement)
- **Verify**: `grep -r "BudgetTracker\|get_budget_tracker" src/` returns 0 hits

### Task 2.13: Update `_ai/agent.py`
- **Action**: Accept `Model` directly, remove `gateway.get_model()`

### Task 2.14: Update `sdk/memory.py`
- **File**: `sdk/memory.py` line 368
- **Action**: Replace `_settings.gateway.litellm_url` / `_settings.gateway.bifrost_url` with `ModelSettings.primary`
- **Reason**: sdk/memory.py reads GatewaySettings fields for LLM endpoint resolution
- **Verify**: `grep -r "settings.gateway\|gateway\.litellm\|gateway\.bifrost" src/` returns 0 hits

### Task 2.15: Update `cli/health_cmd.py`
- **File**: `cli/health_cmd.py` lines 33-38
- **Action**: Replace `settings.gateway.bifrost_url` / `settings.gateway.litellm_url` reads with `ModelSettings` fields
- **Verify**: `grep -r "gateway\." src/cli/` returns 0 hits

### Task 2.16: Update `cli/config_cmd.py`
- **File**: `cli/config_cmd.py` line 23
- **Action**: Replace hardcoded `"gateway"` config key with `"model"` (or new section name)
- **Verify**: `grep -c '"gateway"' src/cli/config_cmd.py` returns 0

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

**Coverage target**: Maintain ≥667 agent-core tests, ≥222 agent-docs-sync tests post-migration.

### Task 5.1: Delete `tests/llm_gateway/` (agent-core)
- **Action**: Remove entire directory (269 lines, 24 test functions)

### Task 5.1b: Delete `tests/resilience/` (agent-core)
- **Action**: Remove entire directory (373 lines, 22 test functions)
- **Reason**: Source code deleted in Phase 2; tests import from deleted modules

### Task 5.1c: Delete `agent-docs-sync/tests/test_resilience.py`
- **Action**: Remove file (193 lines, 14 test functions)
- **Reason**: Imports CircuitBreaker, FallbackChain etc from agent_core.resilience which is deleted

### Task 5.2: Update agent-core tests
- `tests/_ai/test_native_approvals.py` — Remove `LLMGateway` mock
- `tests/_ai/test_run_controls.py` — Remove `LLMGateway` mock
- `tests/agent_base/test_agent.py` — Remove `LLMGateway` mock, change `gateway=` to `model=`
- `tests/sdk/test_agents.py` — Remove `LLMGateway` mock, change `gateway=` to `model=`
- `tests/cli/test_cli.py` — Update 2 `GatewayError` monkeypatches to `ModelAPIError`
- `tests/foundation/test_errors.py` — Remove `GatewayError` from parametrized hierarchy test

### Task 5.3: Create `tests/_ai/test_model_loading.py`
- **New file**: 25+ tests (expanded from original 10 to maintain coverage)
- **Real LLM verification tests**:
  - `test_infer_model_openai_chat()` — Real API call
  - `test_infer_model_anthropic()` — Real API call
  - `test_infer_model_google()` — Real API call
  - `test_fallback_model_failover()` — Real failover
  - `test_usage_limits_enforced()` — UsageLimitExceeded
  - `test_build_agent_model_param()` — End-to-end
- **Unit tests** (replacing deleted resilience/gateway tests):
  - `test_invalid_model_string()` — Error raised for bad format
  - `test_missing_api_key()` — Clear error
  - `test_model_format_validation()` — Rejects invalid
  - `test_secret_str_not_serialized()` — api_key excluded from model_dump
  - `test_empty_fallback_list()` — No FallbackModel when fallback_ids is empty
  - `test_fallback_on_connection_error()` — ConnectionError triggers fallback
  - `test_fallback_on_auth_error_no_fallback()` — Auth errors do NOT trigger fallback
  - `test_create_model_empty_string()` — Empty model ID raises ValueError
  - `test_create_model_no_separator()` — Missing `:` raises ValueError
  - `test_create_model_unknown_provider()` — Unknown provider raises error
  - `test_model_settings_construction()` — ModelSettings builds correctly
  - `test_model_settings_env_override()` — MODEL_PRIMARY env var overrides yaml
  - `test_model_settings_api_key_from_env()` — MODEL_API_KEY read from env
  - `test_model_settings_secret_excluded()` — api_key never in model_dump
  - `test_exception_to_runreason_mapping()` — UsageLimitExceeded → BUDGET_EXCEEDED

### Task 5.4: Update agent-docs-sync tests (8 files)
All define local gateway mocks that pass `gateway=` to `build_agent()`:
- `tests/test_supported_feature_paths.py` — `GatewayError` import → new error type
- `tests/test_canonical_pipeline.py` — `gateway=None` ValueError test
- `tests/test_parity.py` — `mock_gateway` with `get_model → TestModel`
- `tests/test_guardrails_integration.py` — `TestGateway` class → `TestModel`
- `tests/test_subagents_integration.py` — `TestGateway` → `TestModel`
- `tests/test_cli_canonical_commands.py` — monkeypatches `create_gateway` → `create_model`
- `tests/test_state_lifecycle.py` — `Gateway` class → model mock
- `tests/test_canonical_lifecycle_e2e.py` — `gateway=object()` → `model=TestModel()`

### Task 5.5: Update agent-harness tests (5 files)
All define `StubGateway(LLMGateway)` or mock gateways:
- `tests/test_construction_regression.py` — `agent._gateway` → `agent._model`
- `tests/test_convergence_contracts.py` — `StubGateway.get_model()` → `TestModel`
- `tests/test_toolset_composition.py` — `RecordingGateway` → model mock
- `tests/test_production_services.py` — `class StubGateway(LLMGateway)` → model mock
- `tests/test_cli_lifecycle.py` — `class StubGateway(LLMGateway)` → model mock

### Task 5.6: Verify FallbackModel API (PREREQUISITE)
- **Action**: Run the verification script from design.md before writing tests
- **Block**: If `fallback_on` is NOT supported, redesign fallback approach before proceeding

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
