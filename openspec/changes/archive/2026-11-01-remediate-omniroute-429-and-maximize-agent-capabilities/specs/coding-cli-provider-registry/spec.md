# coding-cli-provider-registry Spec Delta

## MODIFIED Requirements

### Requirement: Consumer CLI OmniRoute Registries and Prime Agent Allowlist SHALL Include Tiered Gemini 4 Argon Combo Models
Every active consumer CLI in the workstation provider registry SHALL expose the canonical OmniRoute combo set with capability-maximized subagent roles, reasoning efforts, multimodal vision, and 800K context limits under its active OmniRoute provider entry.

#### Scenario: Prime Agent and Pi Coding Agent resolve Gemini 4 Argon models under omniroute-responses without cost fabrication or backup clutter
- **WHEN** `prime-agent model list` and `pi --list-models` are executed
- **THEN** `~/.pi/agent/settings.json` SHALL declare `modelThinkingLevels` for all 10 OmniRoute combos, `~/.prime/agent/settings.json` SHALL configure `providerBackupModel = "omniroute-responses/claude-sonnet-5.5"` and `callTimeoutMs = 300000` on `mcp-router`, and zero `.bak*` files exist inside `~/.prime/agent/`

#### Scenario: OpenCode, Kilo Code, Kimi Code, Factory Droid, and Grok Build expose Gemini 4 Argon models under active providers without altering defaults
- **WHEN** `~/.config/opencode/opencode.json`, `~/.config/kilo/kilo.jsonc`, `~/.kimi-code/config.toml`, `~/.factory/settings.json`, and `~/.grok/config.toml` are inspected
- **THEN** OpenCode SHALL configure `agent.oracle.model` to `omniroute-responses/claude-opus-5.5`, Kilo Code SHALL configure `agent.*.model` to OmniRoute combos, Kimi Code SHALL declare `capabilities = ["thinking", "image_in", "tool_use"]`, Grok SHALL configure `ui.fork_secondary_model` to `omniroute-claude-opus-5-5`, and Factory Droid SHALL declare `compactionTokenLimit = 800000`
