# omniroute-agent-cli-routing Specification Delta

## ADDED Requirements

### Requirement: Qwen Code CLI SHALL route default inference through OmniRoute and multiplex MCP via mcp-router

Qwen Code (`qwen` v0.25.2+) SHALL configure `~/.qwen/settings.json` (`$version: 4`, mode `0600`) with a `modelProviders.openai` array entry targeting `http://localhost:20128/v1` via `OMNIROUTE_API_KEY`, `security.auth.selectedType: "openai"`, `model.name: "gemini-3.8-flash-high"`, and a single `mcpServers.mcp-router` stdio bridge while preserving existing Orca lifecycle hooks.

#### Scenario: Qwen Code resolves OmniRoute default model and mcp-router
- **WHEN** `~/.qwen/settings.json` is loaded by Qwen Code CLI (`v0.25.2+`)
- **THEN** `modelProviders.openai` SHALL be a `ModelConfig[]` array containing `id: "gemini-3.8-flash-high"`, `baseUrl: "http://localhost:20128/v1"`, and `envKey: "OMNIROUTE_API_KEY"`
- **AND** `security.auth.selectedType` SHALL equal `"openai"` and `model.name` SHALL equal `"gemini-3.8-flash-high"`
- **AND** `mcpServers.mcp-router` SHALL connect via `command: "npx"`, `args: ["-y", "@mcp_router/cli@latest", "connect"]`, `trust: true`
- **AND** `~/.qwen/settings.json` SHALL have permission mode `0600` while retaining all 12 existing Orca lifecycle hook arrays

### Requirement: Credential-bearing MCP and provider backup files SHALL enforce mode 0600 across all agent surfaces

All MCP configuration files and provider backup files carrying `MCPR_TOKEN` or provider credentials across Copilot, Gemini/Antigravity, Kimi, and Goose SHALL be restricted to permission mode `0600` under named operator approval, audited with symlink-following `stat -L`, and OpenCode SHALL omit duplicate standalone `mcp.agentmemory` entries already multiplexed by `mcp-router`.

#### Scenario: Mode 0644 MCP config and backup files are tightened to 0600 and verified with symlink-following stat -L
- **WHEN** filesystem permissions are audited via `stat -L -f '%Mp%Lp %N'` across `~/.copilot/mcp-config.json`, `~/.gemini/config/mcp_config.json`, `~/.gemini/antigravity/mcp_config.json`, `~/.kimi/mcp.json`, and `~/.config/goose/custom_providers/*.bak*`
- **THEN** every resolved file target (including symlinked `~/.gemini/antigravity/mcp_config.json`) SHALL report permission mode `0600` with byte-identical content verified before and after mode tightening
- **AND** `~/.config/opencode/opencode.json` SHALL route `agentmemory` exclusively through `mcp.mcp-router` without a duplicate `mcp.agentmemory` process

### Requirement: Secondary CLI model selectors and upstream capability flags SHALL align with canonical OmniRoute routes

Kimi Code, Grok, Pi, Block Goose, and Claude Code configurations SHALL align their secondary model selectors with canonical `sh/gpt-5.6-sol` routes, remove decommissioned `ollamacloud/*` and `dlg/*` entries, and enable verified upstream capabilities (`supports_vision: true` in Goose, `minimumVersion` and retry watchdog in Claude Code).

#### Scenario: Kimi Code, Grok, Pi, Goose, and Claude Code reflect canonical selectors and upstream flags
- **WHEN** `~/.kimi-code/config.toml`, `~/.grok/config.toml`, `~/.pi/agent/models.json`, `~/.config/goose/custom_providers/custom_omniroute.json`, and `~/.claude/settings.json` are inspected
- **THEN** `[models.or-gpt-5-6-sol]` in `~/.kimi-code/config.toml` and `[model.omniroute-sol]` in `~/.grok/config.toml` SHALL specify `model = "sh/gpt-5.6-sol"`
- **AND** decommissioned `ollamacloud/*` entries in `~/.pi/agent/` and `dlg/kimi-k2.6` in `~/.kimi/config.toml` SHALL be removed
- **AND** `custom_omniroute.json` in Goose SHALL declare `"supports_vision": true` on `gemini-3.8-flash-high`
- **AND** `~/.claude/settings.json` SHALL configure top-level `"minimumVersion": "2.1.302"` and `env.CLAUDE_CODE_RETRY_WATCHDOG_MAX_USAGE_LIMIT_WAIT_MS: "300000"`

### Requirement: Container lifecycle helpers SHALL preserve OmniRoute Gate 4b SSE compatibility patches

Workstation container lifecycle scripts (`~/Developer/scripts/docker-service.sh` and `~/Developer/scripts/omniroute-watchdog.sh`) SHALL pass `--profile base` when managing `~/Omniroute` and invoke `~/Omniroute/scripts/ensure-muse-wire-compat.sh` whenever the `omniroute` container is started or recreated so the Gate 4b `muse-wire-compat` SSE keepalive and `/v1/muse-code/models` normalization remains applied.

#### Scenario: Container recreate via docker-service or watchdog preserves Muse wire compatibility
- **WHEN** `docker-service.sh up` or `omniroute-watchdog.sh` starts or recreates the `omniroute` container with `--profile base`
- **THEN** `~/Omniroute/scripts/ensure-muse-wire-compat.sh` SHALL verify that `response:{id:null,status:"in_progress"}` is absent from `/app/.build/next/server/chunks/*.js` and `/v1/muse-code/models` returns HTTP 200
