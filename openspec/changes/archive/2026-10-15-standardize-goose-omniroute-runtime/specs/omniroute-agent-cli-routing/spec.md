# omniroute-agent-cli-routing Delta Specification

## ADDED Requirements

### Requirement: Goose CLI workstation runtime SHALL enforce 1M context limit and auto-compaction

The Goose CLI configuration in `~/.config/goose/config.yaml` SHALL specify the full 1,048,576 token context window for both execution and planning, enforce auto-compaction thresholds that trigger before context exhaustion, configure high thinking effort, and enable reasoning block rendering per official Goose specification (`docs/guides/sessions/smart-context-management.md` and `docs/guides/environment-variables.md`).

#### Scenario: Goose loads full 1M context window configuration
- **WHEN** `~/.config/goose/config.yaml` is parsed by Goose CLI
- **THEN** `GOOSE_CONTEXT_LIMIT` and `GOOSE_PLANNER_CONTEXT_LIMIT` SHALL both equal `1048576`
- **AND** `GOOSE_MAX_TOKENS` SHALL equal `65536`
- **AND** `GOOSE_THINKING_EFFORT` and `GEMINI3_THINKING_LEVEL` SHALL be set to `high`
- **AND** `GOOSE_CLI_SHOW_THINKING` SHALL equal `1` to render thinking blocks
- **AND** `GOOSE_TOOL_CALL_CUTOFF` SHALL equal `10`

#### Scenario: Auto-compaction thresholds reserve generation headroom
- **WHEN** a Goose session accumulates context exceeding the 80% threshold (`GOOSE_AUTO_COMPACT_THRESHOLD: 0.8`) of the 1,048,576 token limit (~838,860 tokens)
- **THEN** Goose auto-compaction SHALL trigger under `GOOSE_CONTEXT_STRATEGY: summarize`
- **AND** earlier conversation turns SHALL be condensed into a summary with recent tool outputs trimmed to `GOOSE_TOOL_CALL_CUTOFF: 10`, restoring working context headroom for continued execution

### Requirement: Goose provider declarations SHALL point to OmniRoute loopback without legacy port residue

The custom OmniRoute provider definition in `~/.config/goose/custom_providers/custom_omniroute.json` SHALL specify canonical local loopback routing to OmniRoute (`docs/getting-started/providers.md`), reflect the true 1M context capacity for `gemini-3.8-flash-high` under Tier 1 model configuration precedence, and omit decommissioned model routes. Configuration files SHALL NOT point default fallback URLs to legacy tool ports.

#### Scenario: Custom provider routes to canonical OmniRoute loopback
- **WHEN** `~/.config/goose/custom_providers/custom_omniroute.json` is inspected
- **THEN** `base_url` SHALL be `http://localhost:20128/v1`
- **AND** model `gemini-3.8-flash-high` SHALL declare `context_limit: 1048576`
- **AND** `timeout_seconds` SHALL equal `600`
- **AND** decommissioned model identifiers (`ollamacloud/*`, `sh/*`) SHALL be absent

#### Scenario: Legacy port residue eliminated from default configuration
- **WHEN** `~/.config/goose/config.yaml` is inspected
- **THEN** `OPENAI_BASE_URL` and `OPENAI_HOST` SHALL point to `http://localhost:20128/v1` or be cleared
- **AND** port `51006` SHALL NOT appear anywhere in `config.yaml`
- **AND** `OPENAI_BASE_PATH` SHALL NOT equal `v1/response` and SHALL point to `chat/completions` or be cleared

### Requirement: Goose configuration files and directories SHALL adhere to strict permission boundaries

Configuration directories and files holding Goose runtime and provider settings SHALL be restricted to user-only read/write access.

#### Scenario: Restrictive filesystem permissions enforced
- **WHEN** filesystem permissions for Goose configuration are audited
- **THEN** `~/.config/goose` and `~/.config/goose/custom_providers` SHALL be mode `0700`
- **AND** `~/.config/goose/config.yaml` and all JSON files in `~/.config/goose/custom_providers/` SHALL be mode `0600`

### Requirement: Goose MCP tool surface SHALL remain multiplexed via mcp-router stdio bridge

Goose CLI tool integrations SHALL remain unified under the `@mcp_router/cli` stdio bridge without creating redundant point-to-point server declarations.

#### Scenario: Single multiplexed MCP router extension verified
- **WHEN** active extensions in `~/.config/goose/config.yaml` are enumerated
- **THEN** `mcp-router` SHALL be enabled with `cmd: npx`, `args: ["-y", "@mcp_router/cli@latest", "connect"]`, and `env_keys: ["MCPR_TOKEN"]`
- **AND** no duplicate individual stdio entries for `gitnexus`, `graphify`, or `agentmemory` SHALL be declared
