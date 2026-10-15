# Spec Delta: omniroute-agent-cli-routing

## MODIFIED Requirements

### Requirement: Gemini combo SHALL be configured as default across supported coding agents

Supported coding-agent CLIs and editors (`pi`, `omp`, `codex`, `opencode`, `grok`, `droid`, `prime-agent`, `goose`, `kimi-code`, `zed`, `continue`, and Claude Code OmniRoute profile) SHALL configure the live `gemini-3.8-flash-high` combo as their active default model via OmniRoute using the OpenAI Responses API (`/v1/responses` or `api: openai-responses` / `wire_api: responses`) where supported by the client, or via OmniRoute's OpenAI-compatible ingress / Anthropic Messages ingress for dialect-specific clients. Pre-existing providers SHALL remain preserved. Hermes Agent SHALL preserve its default MoA (Mixture of Agents) configuration with `omniroute:gemini-3.8-flash-high` as aggregator.

#### Scenario: Supported CLIs default to Gemini combo
- **WHEN** coding agents are invoked with default model selection
- **THEN** requests SHALL route through OmniRoute's `gemini-3.8-flash-high` combo
- **AND** clients supporting the Responses API SHALL use `/v1/responses`
- **AND** all existing alternative providers SHALL remain preserved
- **AND** credentials SHALL resolve via environment indirection (`OMNIROUTE_API_KEY`) with zero literal secrets committed

#### Scenario: All supported coding agents default to OmniRoute Gemini 3.8 Flash High
- **WHEN** any supported coding agent CLI (`pi`, `omp`, `codex`, `opencode`, `grok`, `droid`, `prime-agent`, `goose`, `kimi-code`), editor (`zed`), or tool (`continue`) is launched without an explicit model override
- **THEN** it SHALL resolve `gemini-3.8-flash-high` via OmniRoute as its default model
- **AND** pre-existing secondary providers and fallback chains SHALL remain preserved and accessible

#### Scenario: Hermes Agent default MoA is preserved
- **WHEN** Hermes Agent configuration is inspected or loaded
- **THEN** `model.provider` SHALL remain `moa`
- **AND** `model.default` SHALL remain `default`
- **AND** the primary aggregator model SHALL route to `omniroute:gemini-3.8-flash-high`

#### Scenario: Kimi Code CLI defaults to OmniRoute Gemini 3.8 Flash High
- **WHEN** Kimi Code CLI (`kimi`) is launched without an explicit model override
- **THEN** it SHALL resolve `default_model = "gemini-3.8-flash-high"` in `~/.kimi-code/config.toml`
- **AND** model `gemini-3.8-flash-high` SHALL route through provider `omniroute-anthropic` targeting `http://localhost:20128`
- **AND** the model definition SHALL declare `max_context_size = 1000000`, `capabilities = ["thinking", "tool_use"]`, and `default_effort = "high"`
- **AND** the configuration file SHALL maintain permission mode `0600`
