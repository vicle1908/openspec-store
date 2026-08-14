## 1. tdt-core: Agent Config Resolution

- [x] [historical] 1.1 Add `tdt_agents_dir() -> Path` helper to `tdt_core/paths.py` — returns `tdt_root() / "agents"`, with `_validate_component` for agent name; add to `__all__`
- [x] [historical] 1.2 Add `tdt_config_path_for_agent(agent_name: str) -> Path` helper to `tdt_core/paths.py` — returns `tdt_agents_dir() / f"{agent_name}.yaml"`
- [x] [historical] 1.3 Add `load_agent_config(agent_name: str) -> dict` to `tdt_core/config_loader.py` — reads `~/.tdt/config.yaml` as global base, deep-merges `model.*` section from `~/.tdt/agents/{agent_name}.yaml` (lists replace, not append), shallow-overrides `runtime.*` fields; handles empty YAML (`None` → `{}`), malformed YAML (raise `ConfigError`), missing directory (return global), non-dict YAML (raise `ConfigError`)
- [x] [historical] 1.4 Add `reset_agent_config_cache()` to `tdt_core/config_loader.py` — clears `_agent_config_cache`; named distinctly from existing `tdt_core.config.reset_config_cache()` to avoid collision
- [x] [historical] 1.5 Add secret rejection in agent-specific YAML — use existing `classify_secret_key()` to reject secret-shaped keys with clear error
- [x] [historical] 1.6 Update `tdt_core/env.py` `reset_env_state()` — add call to `reset_agent_config_cache()` alongside existing `reset_config_cache()`
- [x] [historical] 1.7 Write unit tests for `load_agent_config()` — test: global-only fallback, agent override merge (deep for model, shallow for runtime), partial override, list replacement (not append), secret rejection, cache hit/miss, `reset_agent_config_cache()` effectiveness, empty YAML file, malformed YAML, missing agents directory, non-dict YAML, unknown keys (ignored)

## 2. agent-core: Model Factory Refactor

- [x] [historical] 2.1 Remove `_load_tdt_model_config()`, `_load_tdt_providers()` from `_ai/models.py`; rename `_load_tdt_env_value()` to `_resolve_api_key(env_var_name: str) -> str` (kept as internal helper for API key resolution at call time); remove now-unused `from tdt_core.paths import tdt_root` import if no longer needed
- [x] [historical] 2.2 Refactor `_resolve_proxy_from_model_id(model_id, providers: dict, model_config: dict)` to accept providers and model_config params — remove internal `_load_tdt_providers()` call; also refactor `_resolve_provider_name(model_id, providers: dict)` to accept providers dict (called from within `_resolve_proxy_from_model_id`)
- [x] [historical] 2.3 Refactor `create_model()`, `create_fallback_model()`, and `create_model_with_fallback()` to accept optional `providers: dict | None`, `model_config: dict | None`, and (for `create_model_with_fallback`) `fallback_ids: list[str] | None` params; remove internal `_load_tdt_model_config()` call in `create_model_with_fallback()` that reads fallback list — use caller-provided `fallback_ids` instead
- [x] [historical] 2.4 Update `sdk/agents.py` `build_agent()` — call `load_agent_config(profile.consumer_name)` to resolve providers/model_config; extract `providers` and `model` sections from returned dict; change model resolution to: use `settings.model.primary` when `profile.model` equals the default `"anthropic:Advance"`, otherwise use `profile.model`; pass `providers`, `model_config`, `fallback_ids` to `create_model_with_fallback()`
- [x] [historical] 2.5 Update `cli/utils.py` `_create_runtime_model()` — call `load_agent_config(settings.agent.name)` to resolve providers/model_config; extract sections and pass to `create_fallback_model()`/`create_model()`; determine agent_name from `settings.agent.name`
- [x] [historical] 2.6 Update `agent_base/agent.py` `BaseAgent.__init__()` — when constructing model from string, pass providers/model_config from `load_agent_config()` to `create_model()`
- [x] [historical] 2.7 Write unit tests — verify model factory accepts config dict, verify `build_agent()` uses `load_agent_config()` and falls through to `settings.model.primary`, verify no direct YAML reads remain in `_ai/models.py`, rewrite existing tests in `tests/ai/test_models.py` that monkeypatch removed functions

## 3. agent-docs-sync: Remove Hardcoded Defaults and Repo-Local Model Override

- [x] [historical] 3.1 Update `agents/discovery.py` `discovery_runtime_profile()` — remove hardcoded `model="anthropic:Advance"`, accept model parameter resolved from config chain
- [x] [historical] 3.2 Update `agents/validation.py` `validation_runtime_profile()` — remove hardcoded `model="anthropic:Advance"`, accept model parameter resolved from config chain
- [x] [historical] 3.3 Update `config.py` `from_yaml()` — reject `runtime.model` field in repo-local config.yaml with `ConfigMigrationError` directing to `~/.tdt/agents/agent-docs-sync.yaml`
- [x] [historical] 3.4 Update `config.py` `from_yaml()` — reject legacy `consumer:` section with `ConfigMigrationError` indicating migration to `runtime:` section
- [x] [historical] 3.5 Update `config.py` `_default_runtime_profile()` — use `load_agent_config("agent-docs-sync")` to resolve model from per-agent config
- [x] [historical] 3.6 Update `agents/generation.py` `_resolve_model_with_fallback()` — pass `providers` and `model_config` from `load_agent_config()` to `create_fallback_model()` and `create_model()` (these functions now require config dict params)
- [x] [historical] 3.7 Remove `runtime.model` from `config.yaml` repo file — model config is now exclusively in `~/.tdt/agents/agent-docs-sync.yaml`
- [x] [historical] 3.8 Clean up dead code in `llm/model.py` — remove hardcoded default model string
- [x] [historical] 3.9 Write tests — verify discovery/validation agents inherit model from config, verify repo-local model override raises error, verify agent-specific YAML works, verify legacy `consumer:` section raises error, update existing tests in `tests/test_config_contract.py`

## 4. agent-harness: Remove Old Config Path

- [x] [historical] 4.1 Update `config.py` `HarnessConfig.load()` — call `load_agent_config("agent-harness")` for YAML config; preserve `_load_env_overrides()` logic to apply HARNESS_* env var overrides AFTER `load_agent_config()` returns (env vars must still win)
- [x] [historical] 4.2 Remove `_load_yaml_section()` helper — no longer needed for harness-specific config loading
- [x] [historical] 4.3 Remove `$TDT_HOME/harness/config.yaml` default path assignment and `if config_path.exists()` block in `HarnessConfig.load()` — config is now exclusively in `~/.tdt/agents/agent-harness.yaml`
- [x] [historical] 4.4 Create `~/.tdt/agents/agent-harness.yaml` from existing harness config values (model, max_iterations, timeout_seconds) — manual migration step
- [x] [historical] 4.5 Write tests — verify harness config resolves from new location, verify HARNESS_* env vars still override, verify old location is ignored, update existing tests in `tests/test_config.py` to redirect YAML fixtures from `$TDT_HOME/harness/config.yaml` to `~/.tdt/agents/agent-harness.yaml`

## 5. Documentation and Validation

- [x] [historical] 5.1 Update `agent-core/docs/configuration.md` — document `~/.tdt/agents/{name}.yaml` pattern, resolution precedence, `load_agent_config()` API, `reset_agent_config_cache()`, and removed old code paths
- [x] [historical] 5.2 Update `agent-docs-sync/docs/configuration.md` — document migration from repo-local config.yaml to `~/.tdt/agents/`, `consumer:` → `runtime:` rename, model config rejection
- [x] [historical] 5.3 Update `agent-harness/docs/example-config.yaml` — replace with `~/.tdt/agents/agent-harness.yaml` example
- [x] [historical] 5.4 Update `openspec/specs/consumer-config-composition/spec.md` — apply the delta changes to the main spec (consumer: → runtime:, model rejection)
- [x] [historical] 5.5 Run `openspec validate` on the change — confirm all artifacts pass validation
- [x] [historical] 5.6 Run full test suite across all three repos — confirm no regressions


---

> **Historical record:** This change was archived with 34 incomplete task(s) (0/34 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
