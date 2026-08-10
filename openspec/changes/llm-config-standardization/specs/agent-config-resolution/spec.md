## Purpose

Provides a standardized mechanism for TDT agent repos to load LLM configuration with per-agent overrides from `~/.tdt/agents/{name}.yaml`, using a single resolution chain that all agents share.

## ADDED Requirements

### Requirement: Agent-specific config files override global defaults

The system SHALL load agent-specific configuration from `~/.tdt/agents/{agent-name}.yaml` when it exists, and use it to override values from `~/.tdt/config.yaml`. Only the `model` and `runtime` sections SHALL be subject to per-agent override; all other sections (providers, observability, skills, etc.) SHALL come from global config only.

#### Scenario: Agent-specific model override applied
- **WHEN** `~/.tdt/agents/agent-docs-sync.yaml` contains `model: { primary: "openai-chat:fable-5" }`
- **AND** `~/.tdt/config.yaml` contains `model: { primary: "anthropic:Advance" }`
- **THEN** the resolved config for agent-docs-sync SHALL have `model.primary = "openai-chat:fable-5"`

#### Scenario: No agent-specific file falls back to global
- **WHEN** `~/.tdt/agents/agent-core.yaml` does not exist
- **AND** `~/.tdt/config.yaml` contains `model: { primary: "anthropic:Advance" }`
- **THEN** the resolved config for agent-core SHALL have `model.primary = "anthropic:Advance"`

#### Scenario: Partial agent-specific file merges with global
- **WHEN** `~/.tdt/agents/agent-harness.yaml` contains `model: { thinking: "high" }`
- **AND** `~/.tdt/config.yaml` contains `model: { primary: "anthropic:Advance", temperature: 0.7 }`
- **THEN** the resolved config SHALL have `model.thinking = "high"`, `model.primary = "anthropic:Advance"`, and `model.temperature = 0.7`

#### Scenario: Agent-harness resolves from agent-specific file
- **WHEN** `~/.tdt/agents/agent-harness.yaml` contains `model: { primary: "openai-chat:fable-5" }` and `runtime: { max_iterations: 15 }`
- **AND** `$TDT_HOME/harness/config.yaml` exists with different values
- **THEN** the resolved config for agent-harness SHALL use the `~/.tdt/agents/` values
- **AND** `$TDT_HOME/harness/config.yaml` SHALL NOT be read

### Requirement: Standardized resolution precedence

The system SHALL resolve agent configuration in this priority order (highest to lowest):

1. Runtime environment variables (e.g., `MODEL_PRIMARY`, `HARNESS_MODEL`, `DOCS_SYNC_MODEL`)
2. Agent-specific TDT config (`~/.tdt/agents/{agent-name}.yaml`)
3. Global TDT config (`~/.tdt/config.yaml`)
4. Code defaults

Agent-specific env var prefixes follow the convention: uppercase agent name with hyphens replaced by underscores, followed by an underscore. For example, `agent-docs-sync` uses `DOCS_SYNC_`, `agent-harness` uses `HARNESS_`, `agent-core` uses `AGENT_`.

#### Scenario: Env var overrides agent-specific YAML
- **WHEN** `MODEL_PRIMARY=openai-chat:fable-5` is set in the environment
- **AND** `~/.tdt/agents/agent-docs-sync.yaml` contains `model: { primary: "anthropic:Advance" }`
- **THEN** the resolved model SHALL be `"openai-chat:fable-5"`

#### Scenario: Agent-specific env var overrides agent-specific YAML
- **WHEN** `DOCS_SYNC_MODEL=openai-chat:fable-5` is set in the environment
- **AND** `~/.tdt/agents/agent-docs-sync.yaml` contains `model: { primary: "anthropic:Advance" }`
- **THEN** the resolved model SHALL be `"openai-chat:fable-5"`

#### Scenario: Agent-specific YAML overrides global
- **WHEN** `~/.tdt/agents/agent-harness.yaml` contains `model: { primary: "openai-chat:fable-5" }`
- **AND** `~/.tdt/config.yaml` contains `model: { primary: "anthropic:Advance" }`
- **AND** no relevant env vars are set
- **THEN** the resolved model SHALL be `"openai-chat:fable-5"`

### Requirement: Agents directory path resolution

The system SHALL provide a `tdt_agents_dir()` function in `tdt_core.paths` that returns the canonical `~/.tdt/agents/` directory path. The function SHALL validate the agent name component using existing `_validate_component()` rules.

#### Scenario: Agents directory resolves correctly
- **WHEN** `tdt_agents_dir()` is called
- **THEN** it SHALL return `tdt_root() / "agents"`

#### Scenario: Agent config path combines directory and name
- **WHEN** `tdt_config_path_for_agent("agent-docs-sync")` is called
- **THEN** it SHALL return `tdt_agents_dir() / "agent-docs-sync.yaml"`

### Requirement: Single config loading function

The system SHALL provide a single function `load_agent_config(agent_name)` in `tdt_core.config_loader` that returns a merged configuration dictionary. All agents SHALL use this function instead of independently reading `~/.tdt/config.yaml`.

#### Scenario: Function returns merged config
- **WHEN** `load_agent_config("agent-docs-sync")` is called
- **THEN** it SHALL return a dict containing the merged model and runtime sections from global and agent-specific configs

#### Scenario: Function is idempotent within a process
- **WHEN** `load_agent_config("agent-core")` is called twice in the same process
- **THEN** the second call SHALL return the cached result from the first call without re-reading files

#### Scenario: Unknown agent name returns global config only
- **WHEN** `load_agent_config("unknown-agent")` is called
- **AND** `~/.tdt/agents/unknown-agent.yaml` does not exist
- **THEN** it SHALL return the global config from `~/.tdt/config.yaml` without error

### Requirement: Config caching with test isolation

The system SHALL cache the merged configuration per process. A `reset_agent_config_cache()` function SHALL clear the cache for test isolation. This function SHALL be named distinctly from the existing `reset_config_cache()` in `tdt_core.config` to avoid naming collision.

#### Scenario: Cache is populated on first access
- **WHEN** `load_agent_config("agent-core")` is called for the first time
- **THEN** the config files SHALL be read from disk and the result cached

#### Scenario: Cache is cleared by reset function
- **WHEN** `reset_agent_config_cache()` is called
- **AND** `load_agent_config("agent-core")` is called again
- **THEN** the config files SHALL be re-read from disk

### Requirement: Secrets remain in .env only

Agent-specific YAML files MUST NOT contain secret values (API keys, tokens, database URLs). Secret-shaped keys in agent-specific YAML SHALL be rejected with a clear error message.

#### Scenario: Secret in agent YAML is rejected
- **WHEN** `~/.tdt/agents/agent-core.yaml` contains `model: { api_key: "sk-123" }`
- **THEN** the system SHALL raise a `ConfigError` indicating secrets must be in `.env`

### Requirement: Model factory receives config dict

The model factory (`_ai/models.py`) MUST NOT read config files directly. It SHALL receive provider and model configuration as dict parameters from the caller. The functions `_load_tdt_model_config()` and `_load_tdt_providers()` SHALL be removed. API key resolution remains as an internal helper (`_resolve_api_key()`) that resolves env var names to values at call time — keys are NOT stored in the config dict.

#### Scenario: Model factory uses passed config
- **WHEN** `create_model("openai-chat:fable-5", providers={...}, model_config={...})` is called
- **THEN** the function SHALL use the passed providers and model_config dicts for proxy resolution
- **AND** it SHALL NOT read `~/.tdt/config.yaml` or any other file
- **AND** API key resolution SHALL use `_resolve_api_key()` at call time (not from config dict)

#### Scenario: Model factory without config falls through to native provider
- **WHEN** `create_model("anthropic:claude-3-opus")` is called without providers or model_config
- **THEN** the function SHALL let pydantic-ai resolve the native provider

#### Scenario: Removed functions no longer exist
- **WHEN** the codebase is inspected after implementation
- **THEN** `_load_tdt_model_config` and `_load_tdt_providers` SHALL NOT exist in `_ai/models.py`

### Requirement: Consumers use load_agent_config for model resolution

All agent consumers (agent-core, agent-docs-sync, agent-harness) SHALL use `load_agent_config()` to resolve model configuration instead of calling `load_settings()` for model-related config. The `load_settings()` function remains available for non-model config sections (memory, tools, observability, skills).

#### Scenario: Agent-core build_agent uses load_agent_config
- **WHEN** `build_agent(profile)` is called in `sdk/agents.py`
- **THEN** it SHALL call `load_agent_config(profile.consumer_name)` to resolve providers and model_config
- **AND** pass the resolved config to `create_model()`

#### Scenario: Agent-docs-sync uses load_agent_config for model
- **WHEN** `DocsSyncConfig` is constructed
- **THEN** it SHALL call `load_agent_config("agent-docs-sync")` to resolve the model
- **AND** NOT read `~/.tdt/config.yaml` directly for model config
