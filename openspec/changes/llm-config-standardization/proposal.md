## Why

The TDT agent ecosystem has three independent config loading paths for LLM model selection — agent-core reads `~/.tdt/config.yaml` via pydantic-settings AND raw YAML in `_ai/models.py`, agent-docs-sync calls `agent_core.sdk.load_settings()` then merges repo-local config, and agent-harness reads `$TDT_HOME/harness/config.yaml`. There is no per-agent config namespace: if agent-docs-sync needs a different model than agent-core, the only option is env vars or commenting/uncommenting fields in repo-local config.yaml. Two hardcoded `"anthropic:Advance"` strings in agent-docs-sync bypass the entire config system. Every `load_settings()` call (19+ sites in agent-core alone) re-reads YAML from disk with no caching. Two parallel `Settings` systems exist (`tdt_core.config_models.TDTSettings` and `agent_core.foundation.settings.Settings`) but only the latter is used by agents.

## What Changes

- Add `~/.tdt/agents/{agent-name}.yaml` as the standard per-agent config override location
- Add `load_agent_config(agent_name)` to `tdt_core.config_loader` with process-level caching — single function all agents call
- Standardize config resolution: env vars → agent-specific TDT YAML → global TDT YAML → code defaults
- **BREAKING**: Remove `_load_tdt_model_config()` and `_load_tdt_providers()` from `agent-core/_ai/models.py` — model factory receives config dict instead of reading files
- **BREAKING**: Remove hardcoded model defaults in `agent-docs-sync/agents/discovery.py` and `validation.py` — models must come from config chain
- **BREAKING**: Remove repo-local `config.yaml` model override support in agent-docs-sync — model config moves to `~/.tdt/agents/agent-docs-sync.yaml`
- **BREAKING**: Remove `$TDT_HOME/harness/config.yaml` loading in agent-harness — config moves to `~/.tdt/agents/agent-harness.yaml`
- Add config caching with `reset_agent_config_cache()` for test isolation
- Add streaming model tests and fallback chain tests
- Add config precedence and report semantics tests

## Capabilities

### New Capabilities
- `agent-config-resolution`: Per-agent LLM config loading from `~/.tdt/agents/{name}.yaml` with standardized merge, caching, and resolution chain across the TDT agent ecosystem

### Modified Capabilities
- `consumer-config-composition`: ConsumerRuntimeProfile now reflects merged agent-specific config; model factory no longer reads YAML directly

## Impact

- **tdt-core**: New `load_agent_config()` function in `config_loader.py`, new `tdt_agents_dir()` in `paths.py`, new `reset_agent_config_cache()` in config module
- **agent-core**: `_ai/models.py` model factory refactored — remove `_load_tdt_model_config()`, `_load_tdt_providers()`; accepts config dict from caller; `sdk/agents.py` passes resolved config
- **agent-docs-sync**: `agents/discovery.py` and `agents/validation.py` remove hardcoded model strings; `config.py` removes repo-local model override support; `config.yaml` runtime.model field removed
- **agent-harness**: `config.py` removes `$TDT_HOME/harness/config.yaml` loading; config moves to `~/.tdt/agents/agent-harness.yaml`
- **Breaking changes**: Agents without `~/.tdt/agents/{name}.yaml` will use global defaults only (same as today's fallback behavior, but repo-local overrides are removed)
