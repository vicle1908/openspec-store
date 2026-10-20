# Spec Delta

## ADDED Requirements

### Requirement: Consumer CLI OmniRoute Registries and Prime Agent Allowlist SHALL Include Tiered Gemini 4 Argon Combo Models
Every active consumer CLI in the workstation provider registry (`omp`, `goose`, `pi`, `prime-agent`, `opencode`, `droid`, `kimi`, and `grok`) SHALL expose `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` under its active OmniRoute provider entry (`omniroute-responses`, `omniroute`, `omniroute-anthropic`, or `custom_omniroute`), superseding earlier two-model allowlist cardinality restrictions in `~/.prime/agent/models.json`.

#### Scenario: Prime Agent and Pi Coding Agent resolve Gemini 4 Argon models under omniroute-responses without cost fabrication or backup clutter
- **WHEN** `prime-agent model list gemini-4-argon` and `pi --list-models gemini-4-argon` are executed in a login shell with `OMNIROUTE_API_KEY` set
- **THEN** both CLIs list `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` under `omniroute-responses` with `contextWindow: 1000000`, `maxTokens: 65536`, explicit `thinkingLevelMap`, and `cost` omitted, while `~/.pi/agent/settings.json` and `~/.prime/agent/settings.json` remain unchanged and zero `.bak*` files exist inside `~/.prime/agent/`

#### Scenario: OpenCode, Kilo Code, Kimi Code, Factory Droid, and Grok Build expose Gemini 4 Argon models under active providers without altering defaults
- **WHEN** `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` are registered in `~/.config/opencode/opencode.json` (`provider.omniroute-responses.models`), `~/.config/kilo/kilo.jsonc` (`provider.omniroute-responses.models`), `~/.kimi-code/config.toml` (`[models."gemini-4-argon*"]` with explicit `model` and `provider = "omniroute-anthropic"`), `~/.factory/settings.json` (`customModels[]`), and `~/.grok/config.toml` (`[model.omniroute-gemini-4-argon*]`)
- **THEN** all pre-existing non-OmniRoute providers (`phanmemvip`, `shopapikey`, `cockpit`, `moonshot-ai`, `zai`), secondary `provider.omniroute` Chat-Completions fallbacks, inactive legacy `~/.kimi/config.toml`, and startup default models remain intact, and each CLI resolves all four `gemini-4-argon*` models on demand
