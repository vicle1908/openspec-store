# Tasks: llm-config-standardization

Consolidated from: `standardize-agent-llm-config-loading`, `agent-core-model-resolution-hardening`, `agent-docs-sync-config-and-report-hardening`

## Phase 1: tdt-core — Agent Config Resolution (foundation)

- [x] 1.1 Add `tdt_agents_dir() -> Path` helper to `tdt_core/paths.py` — returns `tdt_root() / "agents"`, with `_validate_component` for agent name; add to `__all__`
- [x] 1.2 Add `tdt_config_path_for_agent(agent_name: str) -> Path` helper to `tdt_core/paths.py` — returns `tdt_agents_dir() / f"{agent_name}.yaml"`
- [x] 1.3 Add `load_agent_config(agent_name: str, *, config_path: str | Path | None = None) -> dict` to `tdt_core/config_loader.py` — reads `~/.tdt/config.yaml` as global base, deep-merges `model.*` section from `~/.tdt/agents/{agent_name}.yaml` (or the explicit `config_path`, when provided; lists replace, not append), shallow-overrides `runtime.*` fields; handles empty YAML (`None` → `{}`), malformed YAML (raise `ConfigError`), missing directory (return global), non-dict YAML (raise `ConfigError`)
- [x] 1.4 Add `reset_agent_config_cache()` to `tdt_core/config_loader.py` — clears `_agent_config_cache`; named distinctly from existing `tdt_core.config.reset_config_cache()` to avoid collision
- [x] 1.5 Add secret rejection in agent-specific YAML — use existing `classify_secret_key()` to reject secret-shaped keys with clear error; exempt `max_tokens`, `max_output_tokens`, `api_key_header_name`; validate `api_key_env` under `providers.<name>` as env var name
- [x] 1.6 Update `tdt_core/env.py` `reset_env_state()` — add call to `reset_agent_config_cache()` alongside existing `reset_config_cache()`
- [x] 1.7 Write unit tests for `load_agent_config()` — test: global-only fallback, agent override merge (deep for model, shallow for runtime), partial override, list replacement (not append), secret rejection, cache hit/miss, `reset_agent_config_cache()` effectiveness, empty YAML file, malformed YAML, missing agents directory, non-dict YAML, unknown keys (rejected), distinct values for two agents, explicit config_path override

## Phase 2: agent-core — Model Factory Refactor + Tests

### 2A: Refactor model factory to accept config params

- [x] [historical] 2.1 Remove `_load_tdt_model_config()`, `_load_tdt_providers()` from `_ai/models.py`; rename `_load_tdt_env_value()` to `_resolve_api_key(env_var_name: str) -> str` (kept as internal helper for API key resolution at call time); remove now-unused `from tdt_core.paths import tdt_root` import if no longer needed
- [x] [historical] 2.2 Refactor `_resolve_proxy_from_model_id(model_id, providers: dict, model_config: dict)` to accept providers and model_config params — remove internal `_load_tdt_providers()` call; also refactor `_resolve_provider_name(model_id, providers: dict)` to accept providers dict (called from within `_resolve_proxy_from_model_id`)
- [x] [historical] 2.3 Refactor `create_model()`, `create_fallback_model()`, and `create_model_with_fallback()` to accept optional `providers: dict | None`, `model_config: dict | None`, and (for `create_model_with_fallback`) `fallback_ids: list[str] | None` params; remove internal `_load_tdt_model_config()` call in `create_model_with_fallback()` that reads fallback list — use caller-provided `fallback_ids` instead
- [x] [historical] 2.4 Update `sdk/agents.py` `build_agent()` — call `load_agent_config(profile.consumer_name)` to resolve providers/model_config; extract `providers` and `model` sections from returned dict; change model resolution to: use `settings.model.primary` when `profile.model` equals the default `"anthropic:Advance"`, otherwise use `profile.model`; pass `providers`, `model_config`, `fallback_ids` to `create_model_with_fallback()`
- [x] [historical] 2.5 Update `cli/utils.py` `_create_runtime_model()` — call `load_agent_config(settings.agent.name)` to resolve providers/model_config; extract sections and pass to `create_fallback_model()`/`create_model()`; determine agent_name from `settings.agent.name`
- [x] [historical] 2.6 Update `agent_base/agent.py` `BaseAgent.__init__()` — when constructing model from string, pass providers/model_config from `load_agent_config()` to `create_model()`

### 2B: Streaming model tests (from agent-core-model-resolution-hardening)

- [x] [historical] 2.7 Add test: stream aggregates text output into ModelResponse
- [x] [historical] 2.8 Add test: stream handles empty/null completion output
- [x] [historical] 2.9 Add test: stream preserves tool calls
- [x] [historical] 2.10 Add test: stream propagates usage metadata
- [x] [historical] 2.11 Add test: stream propagates finish reason
- [x] [historical] 2.12 Add test: stream handles malformed/non-ResponseCompletedEvent items
- [x] [historical] 2.13 Add test: stream propagates upstream exception
- [x] [historical] 2.14 Add test: request() delegates to request_stream() + get()

### 2C: Fallback chain tests (from agent-core-model-resolution-hardening)

- [x] [historical] 2.15 Add test: no fallback config returns single model
- [x] [historical] 2.16 Add test: single fallback returns FallbackModel
- [x] [historical] 2.17 Add test: multiple fallbacks returns FallbackModel
- [x] [historical] 2.18 Add test: explicit Model instance bypasses fallback construction
- [x] [historical] 2.19 Add test: empty fallback list returns single model

### 2D: Consumer integration tests

- [x] [historical] 2.20 Add test: build_agent() uses create_model_with_fallback()
- [x] [historical] 2.21 Add regression test: existing string-model behavior with no fallback
- [x] [historical] 2.22 Write unit tests — verify model factory accepts config dict, verify `build_agent()` uses `load_agent_config()` and falls through to `settings.model.primary`, verify no direct YAML reads remain in `_ai/models.py`, rewrite existing tests in `tests/ai/test_models.py` that monkeypatch removed functions

### 2E: Documentation

- [x] [historical] 2.23 Document streaming compatibility boundary in _StreamingResponsesModel docstring
- [x] [historical] 2.24 Document fallback chain precedence in create_model_with_fallback() docstring

## Phase 3: agent-docs-sync — Config Alignment + Tests

### 3A: Remove hardcoded defaults and repo-local model override

- [x] [historical] 3.1 Update `agents/discovery.py` `discovery_runtime_profile()` — remove hardcoded `model="anthropic:Advance"`, accept model parameter resolved from config chain
- [x] [historical] 3.2 Update `agents/validation.py` `validation_runtime_profile()` — remove hardcoded `model="anthropic:Advance"`, accept model parameter resolved from config chain
- [x] [historical] 3.3 Update `config.py` `from_yaml()` — reject `runtime.model` field in repo-local config.yaml with `ConfigMigrationError` directing to `~/.tdt/agents/agent-docs-sync.yaml`
- [x] [historical] 3.4 Update `config.py` `from_yaml()` — reject legacy `consumer:` section with `ConfigMigrationError` indicating migration to `runtime:` section
- [x] [historical] 3.5 Update `config.py` `_default_runtime_profile()` — use `load_agent_config("agent-docs-sync")` to resolve model from per-agent config
- [x] [historical] 3.6 Update `agents/generation.py` `_resolve_model_with_fallback()` — pass `providers` and `model_config` from `load_agent_config()` to `create_fallback_model()` and `create_model()` (these functions now require config dict params)
- [x] [historical] 3.7 Remove `runtime.model` from `config.yaml` repo file — model config is now exclusively in `~/.tdt/agents/agent-docs-sync.yaml`
- [x] [historical] 3.8 Clean up dead code in `llm/model.py` — remove hardcoded default model string

### 3B: Config precedence tests (from agent-docs-sync-config-and-report-hardening)

- [x] [historical] 3.9 Add test: env var overrides repo config
- [x] [historical] 3.10 Add test: repo config overrides TDT global
- [x] [historical] 3.11 Add test: TDT global overrides code default
- [x] [historical] 3.12 Add test: code default used when all absent
- [x] [historical] 3.13 Add test: alternate TDT_HOME respected
- [x] [historical] 3.14 Add test: missing global config graceful fallback
- [x] [historical] 3.15 Add test: malformed YAML raises error
- [x] [historical] 3.16 Add test: env var int coercion (MAX_ITERATIONS)
- [x] [historical] 3.17 Add test: env var float coercion (TIMEOUT_SECONDS)
- [x] [historical] 3.18 Add test: invalid env var type raises ValueError
- [x] [historical] 3.19 Add test: with_overrides creates immutable copy

### 3C: Report semantics tests (from agent-docs-sync-config-and-report-hardening)

- [x] [historical] 3.20 Add test: generation failure + gaps results in exit 1
- [x] [historical] 3.21 Add test: generation timeout results in exit 1
- [x] [historical] 3.22 Add test: generation max_iterations results in exit 1
- [x] [historical] 3.23 Add test: structured provider error results in exit 1
- [x] [historical] 3.24 Add test: generation_completed=False results in exit 1
- [x] [historical] 3.25 Add test: execution failure results in exit 2
- [x] [historical] 3.26 Add test: compliant run results in exit 0
- [x] [historical] 3.27 Add test: generation failure masks compliance

### 3D: Tests and cleanup

- [x] [historical] 3.28 Write tests — verify discovery/validation agents inherit model from config, verify repo-local model override raises error, verify agent-specific YAML works, verify legacy `consumer:` section raises error, update existing tests in `tests/test_config_contract.py`
- [x] [historical] 3.29 Inspect .scratch/e2e_test.py for valid tests, move or remove
- [x] [historical] 3.30 Remove doc-sync/SKILL.md placeholder stub

## Phase 4: agent-harness — Remove Old Config Path

- [x] [historical] 4.1 Update `config.py` `HarnessConfig.load()` — call `load_agent_config("agent-harness")` for YAML config; preserve `_load_env_overrides()` logic to apply HARNESS_* env var overrides AFTER `load_agent_config()` returns (env vars must still win)
- [x] [historical] 4.2 Remove `_load_yaml_section()` helper — no longer needed for harness-specific config loading
- [x] [historical] 4.3 Remove `$TDT_HOME/harness/config.yaml` default path assignment and `if config_path.exists()` block in `HarnessConfig.load()` — config is now exclusively in `~/.tdt/agents/agent-harness.yaml`
- [x] [historical] 4.4 Create `~/.tdt/agents/agent-harness.yaml` from existing harness config values (model, max_iterations, timeout_seconds) — manual migration step
- [x] [historical] 4.5 Write tests — verify harness config resolves from new location, verify HARNESS_* env vars still override, verify old location is ignored, update existing tests in `tests/test_config.py` to redirect YAML fixtures from `$TDT_HOME/harness/config.yaml` to `~/.tdt/agents/agent-harness.yaml`

## Phase 5: Documentation and Validation

- [x] [historical] 5.1 Update `agent-core/docs/configuration.md` — document `~/.tdt/agents/{name}.yaml` pattern, resolution precedence, `load_agent_config()` API, `reset_agent_config_cache()`, and removed old code paths
- [x] [historical] 5.2 Update `agent-docs-sync/docs/configuration.md` — document migration from repo-local config.yaml to `~/.tdt/agents/`, `consumer:` → `runtime:` rename, model config rejection
- [x] [historical] 5.3 Update `agent-harness/docs/example-config.yaml` — replace with `~/.tdt/agents/agent-harness.yaml` example
- [x] [historical] 5.4 Update `openspec/specs/consumer-config-composition/spec.md` — apply the delta changes to the main spec (consumer: → runtime:, model rejection)

## Verification

- [x] [historical] Run `uv run pytest tests/ -q` across all three repos — all tests pass
- [x] [historical] Run `uv run ruff check src/ tests/` — clean
- [x] [historical] Run `uv run mypy src/ --strict` — clean
- [x] [historical] Run `openspec validate` on the change — confirm all artifacts pass validation
- [x] [historical] Run live LLM test on agent-core with `docs-sync sync --full` — confirm generation works end-to-end


---

> **Historical record:** This change was archived with 68 incomplete task(s) (7/75 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
