# coding-cli-provider-registry Spec Delta

## MODIFIED Requirements

### Requirement: Consumer CLI OmniRoute Registries and Prime Agent Allowlist SHALL Include Tiered Gemini 4 Argon Combo Models
Every active consumer CLI in the workstation provider registry (`omp`, `goose`, `pi`, `prime-agent`, `opencode`, `droid`, `kimi`, `grok`, and `cline`) SHALL expose the canonical OmniRoute combo set (`gemini-3.8-flash-high`, `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, `claude-opus-5.5`, `claude-sonnet-5.5`, `deepseek-v4.1-flash`, `kimi-k3.1-pro`, and `muse-spark-1.3`) under its active OmniRoute provider entry.

#### Scenario: Prime Agent and Pi Coding Agent resolve Gemini 4 Argon models under omniroute-responses without cost fabrication or backup clutter
- **WHEN** `prime-agent model list` and `pi --list-models` are executed in a login shell with `OMNIROUTE_API_KEY` set
- **THEN** both CLIs list `gemini-3.8-flash-high`, `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, `claude-opus-5.5`, `claude-sonnet-5.5`, `deepseek-v4.1-flash`, `kimi-k3.1-pro`, and `muse-spark-1.3` under `omniroute-responses` with `contextWindow: 1000000`, explicit `thinkingLevelMap`, `"headers": { "x-omniroute-no-memory": "true" }`, and `cost` omitted, while `~/.pi/agent/settings.json` and `~/.prime/agent/settings.json` remain unchanged and zero `.bak*` files exist inside `~/.prime/agent/`

#### Scenario: OpenCode, Kilo Code, Kimi Code, Factory Droid, and Grok Build expose Gemini 4 Argon models under active providers without altering defaults
- **WHEN** `~/.config/opencode/opencode.json` (`provider.omniroute-responses.models`), `~/.config/kilo/kilo.jsonc` (`provider.omniroute-responses.models`), `~/.kimi-code/config.toml` (`[models."<id>"]` with explicit `model` and `provider = "omniroute-anthropic"`), `~/.factory/settings.json` (`customModels[]`), `~/.grok/config.toml` (`[model.omniroute-*]`), and `~/.cline/data/settings/providers.json` (`providers.openai-compatible.settings`) are inspected
- **THEN** all pre-existing non-OmniRoute providers (`phanmemvip`, `shopapikey`, `cockpit`, `moonshot-ai`, `zai`), secondary `provider.omniroute` Chat-Completions fallbacks, and inactive legacy `~/.kimi/config.toml` remain intact, `kilo` and `cline` default to `gemini-3.8-flash-high`, and each CLI resolves all 10 OmniRoute combos on demand
