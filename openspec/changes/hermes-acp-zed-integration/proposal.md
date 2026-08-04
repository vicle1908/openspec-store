# Proposal: Hermes ACP + Zed Integration

## Why

Zed 1.13.2 is installed and configured with multiple ACP External Agents (fable-5, codex-acp, claude-acp, etc.). Hermes Agent v0.20.0 has ACP support installed and verified (`hermes acp --check` passes). Adding Hermes as a Zed External Agent gives the team a local-first, provider-agnostic AI coding agent with persistent memory, skills, and multi-platform gateway — running inside Zed's Agent Panel alongside existing agents.

## What Changes

Add `hermes-agent` as a custom External Agent in Zed's `~/.config/zed/settings.json` under `agent_servers`. This is a config-only change — no code modifications, no spec deltas.

### Configuration

**File:** `~/.config/zed/settings.json`

Add to the existing `agent_servers` block:

```json
"hermes-agent": {
  "type": "custom",
  "command": "hermes",
  "args": ["acp"]
}
```

### What Hermes Exposes in ACP Mode

Hermes runs with a curated `hermes-acp` toolset:

| Tool | Purpose |
|------|---------|
| `read_file` | Read files in the project |
| `write_file` | Write/create files |
| `patch` | Targeted find-and-replace edits |
| `search_files` | Search by filename or content |
| `terminal` | Run shell commands |
| `process` | Manage background processes |

Intentionally excluded: messaging delivery, cronjob management (not relevant for editor context).

### How It Works

1. Zed spawns `hermes acp` as a subprocess
2. Communication over stdio via ACP JSON-RPC
3. Hermes uses its own provider config (`~/.hermes/.env` + `~/.hermes/config.yaml`)
4. File tools bind to the editor's working directory
5. Terminal commands route back to Zed for approval (allow_once/allow_session/allow_always/deny)
6. Hermes starts its own MCP servers from its config (separate from Zed's mcp-router)

## Capabilities

### Modified Capabilities

- None (this is a config-only change with no spec delta)

### New Capabilities

- None (`skip_specs: true` — tooling/config only)

## Impact

- **Low risk** — adds a single config entry to an existing block
- **Reversible** — remove the entry to disconnect Hermes from Zed
- **No code changes** — only Zed settings modification
- **Credentials** — Hermes uses its own existing credentials (shopapikey/fable-5)
- **MCP** — Hermes starts its own MCP servers; Zed's mcp-router remains separate unless forwarded via ACP

## Compatibility

- Zed 1.13.2 supports `type: "custom"` agent servers (confirmed in Zed docs)
- Hermes v0.20.0 ACP adapter is installed and verified
- No breaking changes to existing Zed agent configuration
