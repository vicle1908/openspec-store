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
- Unifying `TDTSettings` with `agent_core.foundation.settings.Settings` (separate concern)
- Config file watching or hot-reload
- Migration of non-LLM config sections (jira, sprint, sheets)

## Decisions

### Decision 1: Per-agent config in `~/.tdt/agents/` (not repo-local)

**Choice**: `~/.tdt/agents/{agent-name}.yaml` as the override location.

**Alternatives considered**:
- Repo-local `config.yaml` (current agent-docs-sync pattern) — rejected: config lives in different repos with different structures, hard to discover centrally
- XDG `$XDG_CONFIG_HOME/tdt/agents/` — rejected: ecosystem already uses `~/.tdt` consistently

**Rationale**: Centralizes config in `~/.tdt` where it already lives. Matches existing `~/.tdt/harness/` convention. Easy to discover.

### Decision 2: Merge only `model` and `runtime` sections

**Choice**: Per-agent YAML files override only `model.*` and `runtime.*` from global config.

**Rationale**: Keeps override surface small and predictable. Providers and credentials are shared infrastructure.

### Decision 3: Merge logic in `tdt_core.config_loader`

**Choice**: `load_agent_config(agent_name)` lives in `tdt_core.config_loader`.

**Rationale**: `tdt_core` is the foundation layer. All agents depend on it. Keeps agent-core as a consumer.

### Decision 4: Process-level caching with explicit reset

**Choice**: Module-level dict cache in `tdt_core.config_loader` with `reset_agent_config_cache()`.

**Alternatives considered**:
- No caching (current behavior) — rejected: 19+ `load_settings()` calls per startup re-read YAML
- Singleton Settings object — rejected: would require refactoring all call sites

**Rationale**: Simple dict cache with explicit reset eliminates redundant I/O. Test isolation preserved.

### Decision 5: Model factory accepts config dict (no file I/O)

**Choice**: `_ai/models.py` functions accept `providers` and `model_config` dict parameters. Remove `_load_tdt_model_config()`, `_load_tdt_providers()`. Keep `_load_tdt_env_value()` renamed as `_resolve_api_key()` for API key resolution at call time. The full call chain:
- `create_model(model, *, providers=None, model_config=None)`
- `create_fallback_model(primary_id, fallback_ids, *, providers=None, model_config=None)`
- `create_model_with_fallback(model, *, providers=None, model_config=None, fallback_ids=None)`
- `_resolve_proxy_from_model_id(model_id, providers, model_config)`
- `_resolve_provider_name(model_id, providers)`

**Rationale**: Makes model factory a pure function for config resolution. API key resolution stays as internal helper for security.

### Decision 6: Clean break — no backward compatibility

**Choice**: Remove old config paths entirely. No deprecation warnings. Old config files are simply not read.

**Rationale**: Cleaner codebase, no dead code paths. Operators migrate by creating `~/.tdt/agents/{name}.yaml` files.

### Decision 7: ConfigMigrationError for repo-local model rejection

**Choice**: When `DocsSyncConfig.from_yaml()` encounters `runtime.model` in repo-local config, it raises `ConfigMigrationError` (already exists in `agent_docs_sync/config.py`). The error message includes the agent name and directs to `~/.tdt/agents/`.

**Rationale**: Reuses existing error class. Error raised at config load time gives clear feedback.

### Decision 8: `consumer:` → `runtime:` section rename

**Choice**: The existing `consumer:` section key in `ConsumerConfig.from_yaml()` is replaced by `runtime:`. The `consumer:` section is rejected with `ConfigMigrationError`.

**Rationale**: Better describes section contents. Breaking change aligned with clean-break approach.

### Decision 9: Env var prefix convention

**Choice**: Agent-specific env var prefixes follow `UPPERCASE_AGENT_NAME_` convention:
- `agent-core` → `AGENT_` (existing)
- `agent-docs-sync` → `DOCS_SYNC_` (existing)
- `agent-harness` → `HARNESS_` (existing)

**Rationale**: All three agents already use these prefixes. No change needed.

### Decision 10: `ConsumerRuntimeProfile.model` field preserved as SDK default

**Choice**: The `ConsumerRuntimeProfile.model` field retains its default value `"anthropic:Advance"`. Per-agent YAML writes to `model.primary` in the global/agent-specific config, and `build_agent()` resolves the actual model by checking `settings.model.primary` when `profile.model` equals the hardcoded default.

**Rationale**: Preserves SDK backward compatibility. The field stays; the resolution logic changes.

### Decision 11: API key resolution at call time (not in config dict)

**Choice**: The config dict contains `api_key_env` (the env var NAME), NOT the resolved key. The model factory resolves at call time via `_resolve_api_key()`.

**Rationale**: Prevents secrets from leaking into config cache. Security model preserved.

### Decision 12: `reset_agent_config_cache()` — distinct naming

**Choice**: Named distinctly from existing `tdt_core.config.reset_config_cache()` to avoid collision. `reset_env_state()` updated to call both.

**Rationale**: Two different caches need independent reset functions.

### Decision 13: Merge semantics — deep merge for model, replace for runtime

**Choice**:
- `model.*` section: **deep merge** — agent YAML keys override matching global keys; lists (e.g., `fallback`) are REPLACED, not appended.
- `runtime.*` section: **shallow replace** — each field replaces the corresponding global field.
- `settings` field: NOT overridable via agent YAML.

### Decision 14: Edge cases in YAML loading

**Choice**:
- Empty YAML file: treat as `{}`, use global config only
- Malformed YAML: raise `ConfigError` with file path and parse error
- Missing `~/.tdt/agents/` directory: return global config only
- Non-dict YAML: raise `ConfigError` indicating agent config must be a mapping
- Unknown keys: silently ignored (forward compatibility)
- Type coercion: rely on downstream Pydantic validation

## Risks / Trade-offs

**[Risk] Stale cache after config file change** → Mitigated by `reset_agent_config_cache()`. Operators must restart agent process.

**[Risk] Breaking existing setups** → Operators using repo-local `config.yaml` model overrides or `$TDT_HOME/harness/config.yaml` must migrate to `~/.tdt/agents/`.

**[Risk] Two Settings systems remain** → `TDTSettings` and `Settings` not unified in this change. Known tech debt.

**[Risk] `build_agent()` fallback logic** → Conditional default check introduces coupling to default value. Mitigated by constant extraction: `DEFAULT_MODEL = "anthropic:Advance"`.

**[Risk] HARNESS_* env vars** → `load_agent_config()` only handles YAML merging. Agent-specific env vars applied AFTER return. Each consumer responsible for its own env var layer.

**[Trade-off] Dict cache vs typed cache** → Cache stores raw dicts. Simpler but downstream code constructs Settings from dict.

**[Trade-off] API key resolution at call time** → Keeps `_resolve_api_key()` as internal helper. Smaller blast radius than passing resolved keys through config dict.
