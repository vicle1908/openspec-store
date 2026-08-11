## Context

The TDT agent ecosystem has three repos (agent-core, agent-docs-sync, agent-harness) that each independently load LLM configuration. See proposal.md for the problem statement. The existing `tdt_core.paths.tdt_root()` already resolves `~/.tdt`, and `tdt_core.config_loader` has secret classification and `${VAR}` reference validation — these are the natural home for the new resolution logic.

Key constraint: providers (giaoduc, shopapikey, cockpit) and credentials (`~/.tdt/.env`) are shared infrastructure and MUST remain global. Only model choice and behavior tuning (thinking, temperature) are per-agent concerns.

## Goals / Non-Goals

**Goals:**
- Single `load_agent_config(agent_name)` function all agents call
- `~/.tdt/agents/{name}.yaml` as standard per-agent override location
- Process-level config caching with test-reset capability
- Model factory (`_ai/models.py`) receives config dict instead of reading YAML
- Remove hardcoded model strings in agent-docs-sync
- Remove repo-local `config.yaml` model override support
- Remove `$TDT_HOME/harness/config.yaml` loading in agent-harness
- Migrate consumers from `load_settings()` for model config to `load_agent_config()`
- Add streaming model tests and fallback chain tests
- Add config precedence and report semantics tests

**Non-Goals:**
- Per-agent provider overrides (providers stay global)
- Per-agent credential isolation (all agents share `~/.tdt/.env`)
- Unifying `TDTSettings` with `agent_core.foundation.settings.Settings`
- Config file watching or hot-reload
- Migration of non-LLM config sections

## Decisions

### Decision 1: Per-agent config in `~/.tdt/agents/`
`~/.tdt/agents/{agent-name}.yaml` as the override location. Centralizes config in `~/.tdt` where it already lives.

### Decision 2: Merge only `model` and `runtime` sections
Per-agent YAML files override only `model.*` and `runtime.*` from global config. Providers and credentials are shared infrastructure.

### Decision 3: Merge logic in `tdt_core.config_loader`
`load_agent_config(agent_name)` lives in `tdt_core.config_loader`. Foundation layer, all agents depend on it.

### Decision 4: Process-level caching with explicit reset
Module-level dict cache with `reset_agent_config_cache()`. Named distinctly from existing `reset_config_cache()`.

### Decision 5: Model factory accepts config dict (no file I/O)
Remove `_load_tdt_model_config()`, `_load_tdt_providers()`. Keep `_resolve_api_key()` for API key resolution at call time. Full call chain refactored.

### Decision 6: Clean break — no backward compatibility
Remove old config paths entirely. No deprecation warnings. Operators migrate by creating `~/.tdt/agents/{name}.yaml` files.

### Decision 7: ConfigMigrationError for repo-local model rejection
Reuse existing `ConfigMigrationError` when `DocsSyncConfig.from_yaml()` encounters `runtime.model`.

### Decision 8: `consumer:` → `runtime:` section rename
The `consumer:` section key is replaced by `runtime:`. Breaking change aligned with clean-break approach.

### Decision 9: Env var prefix convention
`UPPERCASE_AGENT_NAME_` convention. All three agents already use these prefixes.

### Decision 10: `ConsumerRuntimeProfile.model` preserved as SDK default
Field retains default `"anthropic:Advance"`. `build_agent()` checks `settings.model.primary` when default.

### Decision 11: API key resolution at call time
Config dict contains `api_key_env` (env var NAME), not resolved key. Factory resolves at call time.

### Decision 12: `reset_agent_config_cache()` — distinct naming
Named distinctly from existing `reset_config_cache()`. `reset_env_state()` calls both.

### Decision 13: Merge semantics
`model.*`: deep merge (lists replace, not append). `runtime.*`: shallow replace. `settings`: not overridable.

### Decision 14: Edge cases
Empty YAML → `{}`, malformed → ConfigError, missing directory → global only, non-dict → ConfigError, unknown keys → ignored.

## Risks / Trade-offs

**[Risk] Stale cache** → `reset_agent_config_cache()`. Operators restart process.
**[Risk] Breaking existing setups** → One-time migration to `~/.tdt/agents/`.
**[Risk] Two Settings systems remain** → Known tech debt, separate change.
**[Trade-off] Dict cache vs typed cache** → Simpler, future optimization possible.
