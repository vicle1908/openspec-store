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

**Choice**: Module-level dict cache in `tdt_core.config_loader` with `reset_config_cache()`.

**Alternatives considered**:
- No caching (current behavior) — rejected: 19+ `load_settings()` calls per startup re-read YAML
- Singleton Settings object — rejected: would require refactoring all call sites

**Rationale**: Simple dict cache with explicit reset eliminates redundant I/O. Test isolation preserved.

### Decision 5: Model factory accepts config dict (no file I/O)

**Choice**: `_ai/models.py` functions accept `providers` and `model_config` dict parameters. Remove `_load_tdt_model_config()`, `_load_tdt_providers()`, `_load_tdt_env_value()`. The full call chain is refactored:
- `create_model(model, *, providers=None, model_config=None)` → passes to `_resolve_proxy_from_model_id()`
- `create_fallback_model(primary_id, fallback_ids, *, providers=None, model_config=None)` → passes to `_make_model()` per model
- `create_model_with_fallback(model, *, providers=None, model_config=None, fallback_ids=None)` → uses `fallback_ids` param instead of reading from config
- `_resolve_proxy_from_model_id(model_id, providers, model_config)` → uses passed `providers` dict
- `_resolve_provider_name(model_id, providers)` → uses passed `providers` dict

**Rationale**: Makes model factory a pure function. Caller already has loaded config.

### Decision 6: Clean break — no backward compatibility

**Choice**: Remove old config paths entirely. No deprecation warnings. Old config files (`repo-local config.yaml` model overrides, `$TDT_HOME/harness/config.yaml`) are simply not read.

**Alternatives considered**:
- Deprecation with warning — rejected: adds complexity for no benefit; operators can migrate in one step
- Parallel old+new paths during transition — rejected: defeats the purpose of simplification

**Rationale**: Cleaner codebase, no dead code paths, no maintenance burden of supporting two systems. Operators migrate by creating `~/.tdt/agents/{name}.yaml` files.

### Decision 7: ConfigMigrationError for repo-local model rejection

**Choice**: When `DocsSyncConfig.from_yaml()` encounters `runtime.model` in repo-local config, it raises `ConfigMigrationError` (already exists in `agent_docs_sync/config.py`). The error message includes the agent name and directs to `~/.tdt/agents/`.

**Rationale**: `ConfigMigrationError` already exists in the codebase for schema migration. Reusing it for model config migration is consistent. The error is raised at config load time, not at model creation time, giving clear feedback.

### Decision 8: `consumer:` → `runtime:` section rename

**Choice**: The existing `consumer:` section key in `ConsumerConfig.from_yaml()` is replaced by `runtime:`. The `consumer:` section is rejected with `ConfigMigrationError`.

**Rationale**: The `runtime:` key better describes what the section contains (runtime profile settings, not consumer identity). The rename is a breaking change but aligns with the clean-break approach.

### Decision 9: Env var prefix convention

**Choice**: Agent-specific env var prefixes follow `UPPERCASE_AGENT_NAME_` convention:
- `agent-core` → `AGENT_` (existing)
- `agent-docs-sync` → `DOCS_SYNC_` (existing)
- `agent-harness` → `HARNESS_` (existing)

**Rationale**: All three agents already use these prefixes. No change needed.

### Decision 10: `ConsumerRuntimeProfile.model` field preserved as SDK default

**Choice**: The `ConsumerRuntimeProfile.model` field retains its default value `"anthropic:Advance"`. It is NOT removed. Per-agent YAML writes to `model.primary` in the global/agent-specific config, and `build_agent()` resolves the actual model by checking `settings.model.primary` when `profile.model` equals the hardcoded default.

**Alternatives considered**:
- Remove `runtime.model` entirely — rejected: breaks `build_agent()` fallback path, `HarnessConfig.model` property, and `DocsSyncConfig.model` property
- Keep `runtime.model` as the authoritative source — rejected: defeats the purpose of centralized config

**Rationale**: The field stays for SDK backward compatibility. The resolution logic in `build_agent()` changes from:
```python
# BEFORE: profile.model is authoritative
model = create_model_with_fallback(profile.model)
```
to:
```python
# AFTER: profile.model is fallback, settings.model.primary is primary
effective_model = profile.model
if profile.model == "anthropic:Advance":  # default value
    effective_model = settings.model.primary  # use centralized config
model = create_model_with_fallback(effective_model, providers=..., model_config=...)
```

### Decision 11: API key resolution at call time (not in config dict)

**Choice**: The config dict returned by `load_agent_config()` contains `api_key_env` (the environment variable NAME), NOT the resolved API key value. The model factory resolves the actual key at call time using `_load_tdt_env_value()` — which is NOT removed, only renamed to `_resolve_api_key(env_var_name)` and kept as an internal helper.

**Rationale**: Prevents secrets from leaking into the config cache. The current security model (keys only in `.env` or env vars) is preserved. The `_load_tdt_env_value()` function is renamed to clarify its purpose but its implementation stays.

### Decision 12: `reset_agent_config_cache()` — distinct naming

**Choice**: Name the new cache reset function `reset_agent_config_cache()` to avoid collision with existing `tdt_core.config.reset_config_cache()` (which clears TOML cache). Update `tdt_core.env.reset_env_state()` to call both.

**Rationale**: Two different caches (TOML vs agent YAML) need independent reset functions. Naming collision would cause confusion.

### Decision 13: Merge semantics — deep merge for model, replace for runtime

**Choice**:
- `model.*` section: **deep merge** — agent YAML keys override matching global keys; missing keys inherit from global. Lists (e.g., `fallback`) are REPLACED, not appended.
- `runtime.*` section: **shallow replace** — each field in agent YAML replaces the corresponding global field; fields not in agent YAML inherit from global.
- `settings` field: NOT overridable via agent YAML (it's a full `Settings` object constructed separately).

**Example**:
```yaml
# Global: ~/.tdt/config.yaml
model:
  primary: anthropic:Advance
  fallback: [openai-chat:fable-5]
  thinking: medium
  temperature: 0.7

# Agent: ~/.tdt/agents/agent-docs-sync.yaml
model:
  primary: openai-chat:fable-5    # overrides
  thinking: high                   # overrides
  # fallback, temperature inherited from global

# Result:
# model.primary = openai-chat:fable-5
# model.fallback = [openai-chat:fable-5]  (inherited, NOT appended)
# model.thinking = high
# model.temperature = 0.7
```

### Decision 14: Edge cases in YAML loading

**Choice**:
- Empty YAML file (`yaml.safe_load("")` returns `None`): treat as `{}`, use global config only
- Malformed YAML (`yaml.YAMLError`): raise `ConfigError` with file path and parse error message
- Missing `~/.tdt/agents/` directory: return global config only (directory creation is NOT automatic)
- Non-dict YAML (list, scalar): raise `ConfigError` indicating agent config must be a mapping
- Unknown keys in agent YAML: silently ignored (not `extra="forbid"` — allows forward compatibility)
- Type coercion: rely on downstream Pydantic validation (no coercion in `load_agent_config()`)

## Risks / Trade-offs

**[Risk] Stale cache after config file change** → Mitigated by `reset_agent_config_cache()` and documented that cache is per-process. Operators must restart agent process after config changes (same as today).

**[Risk] Breaking existing setups** → Operators using repo-local `config.yaml` model overrides or `$TDT_HOME/harness/config.yaml` must migrate to `~/.tdt/agents/`. This is a one-time manual step.

**[Risk] Two Settings systems remain** → `TDTSettings` (tdt_core) and `Settings` (agent-core) are not unified in this change. Known tech debt tracked separately.

**[Risk] `ConfigMigrationError` reuse** → The error class already exists for schema migration. Using it for model config migration is consistent but callers must distinguish the two use cases by error message content.

**[Risk] `build_agent()` fallback logic** → The change from checking `profile.model` to checking `settings.model.primary` introduces a conditional default check. If the default value in `ConsumerRuntimeProfile` ever changes, the fallback logic must be updated. Mitigated by constant extraction: `DEFAULT_MODEL = "anthropic:Advance"`.

**[Risk] HARNESS_* env vars** → `load_agent_config()` only handles YAML merging. Agent-specific env var overrides (e.g., `HARNESS_MODEL`) must be applied AFTER `load_agent_config()` returns. Each consumer is responsible for its own env var layer. The env var precedence is: env > agent YAML > global YAML > code defaults.

**[Trade-off] Dict cache vs typed cache** → Cache stores raw merged dicts, not typed Settings objects. Simpler but downstream code still constructs Settings from the dict. Future optimization could cache Settings.

**[Trade-off] API key resolution at call time** → Keeping `_resolve_api_key()` means the model factory still does env resolution, but ONLY for API keys (not config). This is a smaller blast radius than passing resolved keys through the config dict.
