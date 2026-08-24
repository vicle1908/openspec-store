## Why

The workspace currently has no CLI-based alternative to Claude Code for AI-assisted development. Adding Cline CLI provides a complementary tool with native multi-provider support — all 3 workspace providers (cockpit, giaoduc, shopapikey) work directly with Cline's built-in providers, requiring no adapters, bridges, or protocol translation. Cline's OpenAI provider uses the Responses API natively (`provider.responses(modelId)` in `sdk/packages/llms/src/providers/vendors/openai.ts`), connecting directly to cockpit-cliproxy. Cline's Anthropic provider supports custom base URLs via `config.baseUrl` (passed to `@ai-sdk/anthropic` SDK), enabling direct connections to shopapikey and giaoduc proxies.

## What Changes

- Install Cline CLI v3.0.57 globally via npm
- Configure 3 provider connections using Cline's native providers:
  - **cockpit** → `openai-native` provider, base URL `http://localhost:51006/v1`, Responses API
  - **shopapikey** → `openai-native` provider, base URL `https://api.phanmemvip.shop/v1`, Responses API
  - **giaoduc** → `openai-compatible` provider, base URL `https://api.giaoduc.online/v1`, Chat Completions
- Register mcp-router as the sole MCP server in `~/.cline/mcp.json` (same `MCPR_TOKEN` as Claude Code)
- Add 3 shell launcher functions to `~/.zshrc`: `cline_shopapikey()`, `cline_giaoduc()`, `cline_cockpit()`
- Each launcher writes `providers.json` with the correct config before invoking Cline

## Non-Goals

- No adapter or bridge for any provider (all work natively)
- No agentmemory MCP registration (mcp-router only per user request)
- No VS Code or JetBrains extension (CLI only)
- No project-level `.cline/` config in individual repos (global config only)
- No Docker dependency for any provider

## Validated Findings (from real CLI calls)

| Provider | Cline Provider | Protocol | Streaming | Tool Calls | Status |
|----------|---------------|----------|-----------|------------|--------|
| cockpit | `openai-native` | Responses API | ✅ | ✅ | ✅ Stable |
| giaoduc | `anthropic` | Messages API | ✅ | ✅ | ✅ Stable |
| shopapikey | `anthropic` | Messages API | ✅ | ✅ | ⚠️ Intermittent 503 |

**Key discoveries:**
1. Cline's Anthropic provider DOES support custom base URLs — `cline auth` CLI rejects it, but `providers.json` injection works because the SDK reads `config.baseUrl`
2. Base URL MUST include `/v1` suffix (Anthropic SDK appends `/messages` to the base URL)
3. All 3 providers support streaming and tool calls via their native protocol
4. shopapikey's `/v1/messages` backend is intermittently unavailable (503 gateway_empty_response) — this is a backend capacity issue, not a Cline configuration issue

## Capabilities

### New Capabilities

- `cline-cli-setup`: Installation, provider configuration, MCP setup, and shell launchers for Cline CLI

### Modified Capabilities

(none — tooling/infrastructure change, no spec-level behavior changes)

## Impact

- **Shell profile**: `~/.zshrc` gets 3 new launcher functions
- **Config directory**: `~/.cline/` with `data/settings/providers.json`, `mcp.json`
- **MCP**: mcp-router registered in Cline's MCP config (same token as Claude Code)
- **Dependencies**: Node.js 20+ (already present), npm (already present)
- **Runtime**: No new daemons; cockpit-cliproxy must be running for cockpit provider

## Ownership Boundaries

- **Shell profile (`~/.zshrc`)**: User-owned, modified by implementation
- **Cline config (`~/.cline/`)**: User-owned, created/modified by implementation
- **MCP config (`~/.cline/mcp.json`)**: User-owned, created by implementation
- **API keys (`~/.hermes/.env`)**: Read-only reference — no modification
- **Existing Claude Code config (`~/.claude/`)**: Read-only reference — no modification
- **cockpit-cliproxy**: External dependency — must be running, not modified
