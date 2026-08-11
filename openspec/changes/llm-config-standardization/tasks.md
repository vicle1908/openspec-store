## Phase 1: tdt-core — Agent Config Resolution

- [x] 1.1 Add `tdt_agents_dir()` to `tdt_core/paths.py`
- [x] 1.2 Add `tdt_config_path_for_agent()` to `tdt_core/paths.py`
- [x] 1.3 Add `load_agent_config()` to `tdt_core/config_loader.py`
- [x] 1.4 Add `reset_agent_config_cache()` to `tdt_core/config_loader.py`
- [x] 1.5 Add secret rejection in agent-specific YAML
- [x] 1.6 Update `reset_env_state()` in `tdt_core/env.py`
- [x] 1.7 Write unit tests for `load_agent_config()`

## Phase 2: agent-core — Model Factory Refactor + Tests

### 2A: Refactor model factory
- [x] 2.1 Remove `_load_tdt_model_config()`, `_load_tdt_providers()`; rename `_load_tdt_env_value()` to `_resolve_api_key()`
- [x] 2.2 Refactor `_resolve_proxy_from_model_id()` and `_resolve_provider_name()` to accept providers dict
- [x] 2.3 Refactor `create_model()`, `create_fallback_model()`, `create_model_with_fallback()` with providers/model_config params
- [x] 2.4 Update `sdk/agents.py` `build_agent()` to use `load_agent_config()`
- [x] 2.5 Update `cli/utils.py` `_create_runtime_model()` to use `load_agent_config()`
- [x] 2.6 Update `agent_base/agent.py` `BaseAgent.__init__()` to use `load_agent_config()`

### 2B: Streaming model tests
- [x] 2.7-2.14 Add 8 streaming model tests

### 2C: Fallback chain tests
- [x] 2.15-2.19 Add 5 fallback chain tests

### 2D: Consumer integration tests
- [x] 2.20-2.22 Add consumer integration tests

### 2E: Documentation
- [x] 2.23-2.24 Document streaming and fallback chain

## Phase 3: agent-docs-sync — Config Alignment + Tests

### 3A: Remove hardcoded defaults
- [x] 3.1 Update `agents/discovery.py` — remove hardcoded model
- [x] 3.2 Update `agents/validation.py` — remove hardcoded model
- [x] 3.3 Update `config.py` `from_yaml()` — reject `runtime.model`
- [x] 3.4 Update `config.py` `from_yaml()` — reject legacy `consumer:` section
- [x] 3.5 Update `config.py` `_default_runtime_profile()` — use `load_agent_config()`
- [x] 3.6 Update `agents/generation.py` — pass providers/model_config
- [x] 3.7 Remove `runtime.model` from `config.yaml`
- [x] 3.8 Clean up dead code in `llm/model.py`

### 3B: Config precedence tests
- [x] 3.9-3.19 Add 11 config precedence tests

### 3C: Report semantics tests
- [x] 3.20-3.27 Add 8 report semantics tests

### 3D: Tests and cleanup
- [x] 3.28-3.30 Write tests, cleanup

## Phase 4: agent-harness — Remove Old Config Path

- [x] 4.1 Update `config.py` `HarnessConfig.load()` — use `load_agent_config("agent-harness")`
- [x] 4.2 Remove `_load_yaml_section()` helper
- [x] 4.3 Remove `$TDT_HOME/harness/config.yaml` reading code
- [x] 4.4 Create `~/.tdt/agents/agent-harness.yaml`
- [x] 4.5 Write tests

## Phase 5: Documentation and Validation

- [x] 5.1 Update `agent-core/docs/configuration.md`
- [x] 5.2 Update `agent-docs-sync/docs/configuration.md`
- [x] 5.3 Update `agent-harness/docs/example-config.yaml`
- [x] 5.4 Update `openspec/specs/consumer-config-composition/spec.md`
- [x] 5.5 Run `openspec validate`
- [x] 5.6 Run full test suite

## Verification

- [x] Run `pytest` across all repos
- [x] Run `ruff check` across all repos
- [x] Run `openspec validate`
- [x] Run real LLM test with both OpenAI and Anthropic protocols
