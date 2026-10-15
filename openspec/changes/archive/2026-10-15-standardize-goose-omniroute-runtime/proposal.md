# Proposal: Standardize Goose CLI Workstation Runtime with OmniRoute

## Why

Goose CLI on this workstation routes through OmniRoute using `gemini-3.8-flash-high`, but its configuration exhibits operational drift in context window sizing, missing auto-compaction rules, legacy Cockpit port bindings, and permissive file modes. Bringing Goose into strict alignment with ecosystem standards and the established Notion/OpenSpec contracts prevents context truncation during heavy agent tasks and hardens workstation configuration security.

## What Changes

- **Context Window Alignment**: Update `GOOSE_CONTEXT_LIMIT` and `GOOSE_PLANNER_CONTEXT_LIMIT` from `1000000` to `1048576` ($2^{20}$ true 1M token window) to fully leverage OmniRoute Gemini 3.8 Flash combo capacity.
- **Auto-Compaction & Token Headroom**: Add `GOOSE_MAX_TOKENS: 65536`, `GOOSE_AUTO_COMPACT_THRESHOLD: 0.8` (triggers at ~838k tokens), `GOOSE_CONTEXT_STRATEGY: summarize`, and `GOOSE_TOOL_CALL_CUTOFF: 10` in `~/.config/goose/config.yaml`.
- **Reasoning Effort Normalization**: Configure `GOOSE_THINKING_EFFORT: high` and `GEMINI3_THINKING_LEVEL: high` to align with the Antigravity provider's supported effort tiers.
- **Endpoint Sanitation**: Reconcile legacy Cockpit port `51006` references (`OPENAI_BASE_URL`, `OPENAI_HOST`, `OPENAI_BASE_PATH`) to point to the canonical local OmniRoute gateway (`http://localhost:20128/v1`) and standard path `chat/completions` (eliminating Cockpit's 404-inducing `v1/response`).
- **Custom Provider Catalog Hygiene**: Update `~/.config/goose/custom_providers/custom_omniroute.json` to specify `context_limit: 1048576` and `timeout_seconds: 600` for `gemini-3.8-flash-high`, and prune decommissioned model references (`ollamacloud/*`, `sh/*`).
- **Configuration Security Hardening**: Lock `~/.config/goose` and `custom_providers` directories to mode `0700` and configuration files (`config.yaml`, `custom_omniroute.json`) to mode `0600`.
- **MCP Integration Verification**: Confirm that `mcp-router` remains the sole stdio multiplexer extension in Goose, providing unified access to GitNexus, Graphify, AgentMemory, and search tools without redundant point-to-point stdio declarations.

## Non-Goals

- Modifying the underlying MCP multiplexer (`mcp-router` via `@mcp_router/cli@latest connect`) or adding separate individual stdio MCP servers in Goose.
- Changing the default model away from `gemini-3.8-flash-high` or switching the active provider from `custom_omniroute`.
- Changing other workstation coding agent configurations (`omp`, `codex`, `pi`, `prime-agent`, `opencode`, `droid`, `grok`, `kimi-code`).
- Altering Docker host port bindings or OmniRoute container configurations.

## Ownership Boundaries

- **Local Workstation Configuration**: `~/.config/goose/config.yaml` and `~/.config/goose/custom_providers/custom_omniroute.json`.
- **OpenSpec Governance**: Managed under store `openspec-store` in capability `omniroute-agent-cli-routing`.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `omniroute-agent-cli-routing`: Update requirements and scenarios for Goose CLI runtime configuration standards, including context sizing, compaction thresholds, port hygiene, and file security hardening.
