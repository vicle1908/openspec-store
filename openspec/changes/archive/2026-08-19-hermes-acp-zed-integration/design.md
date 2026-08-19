# Design: Hermes ACP + Zed Integration

## Context

Zed 1.15.0 on macOS with existing ACP External Agents (kimi, codex-acp, claude-acp, gemini, github-copilot-cli, goose, amp-acp, opencode, factory-droid, github-copilot). Hermes Agent v0.20.3 with ACP adapter installed. The team wants Hermes available as an External Agent in Zed's Agent Panel.

## Approach

### Configuration Target

**File:** `~/.config/zed/settings.json`

The existing `agent_servers` block contains 10 entries (all `"type": "registry"`). We add one custom entry:

```json
"agent_servers": {
  "kimi": { "type": "registry" },
  "codex-acp": { "type": "registry" },
  ...existing entries...
  "hermes-agent": {
    "default_mode": "accept_edits",
    "type": "custom",
    "command": "hermes",
    "args": ["acp"]
  }
}
```

### Why `type: "custom"` (not `"registry"`)

The ACP Registry is for agents published to the registry. Hermes is a local installation, so `"type": "custom"` is correct. This matches Zed's documentation for self-hosted/local agents.

### Hermes ACP Server Behavior

When Zed spawns `hermes acp`:

1. **Initialization**: Hermes resolves provider config from `~/.hermes/config.yaml` and credentials from `~/.hermes/.env`
2. **Tool Registration**: Registers the `hermes-acp` toolset (read_file, write_file, patch, search_files, terminal, process)
3. **MCP**: Starts globally configured MCP servers from Hermes config unless `HERMES_ACP_SKIP_CONFIGURED_MCP=1` is set by the host
4. **Session Management**: Each Zed thread maps to a Hermes ACP session with isolated context
5. **Working Directory**: Binds editor's cwd to the session so file tools operate on the project
6. **Approvals**: Terminal commands request approval through Zed's approval UI

### Approval Scenarios

| Command | Expected Behavior |
|---------|-------------------|
| `git status` | Allow always (idempotent, safe) |
| `ls -la` | Allow for session (read-only) |
| `uv run pytest` | Allow once initially, promote to session after verification |
| `rm -rf /tmp/scratch` | Allow once (destructive) |
| `curl ... \| sh` | Deny (untrusted source) |

## Verification

### Pre-implementation

- [x] `hermes acp --check` passes
- [x] `hermes-acp` launcher exists
- [x] `agent-client-protocol` v0.9.0 installed in venv
- [x] Zed 1.15.0 installed
- [x] `~/.hermes/.env` exists with provider credentials

### Post-implementation

- [ ] Zed recognizes Hermes in Agent Panel
- [ ] Hermes starts when a new thread is created
- [ ] File tools operate on the project directory
- [ ] Terminal commands route through Zed approval
- [ ] Hermes MCP servers start (or skip if configured)
