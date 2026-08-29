## Why

The grok CLI configuration at `~/.grok/config.toml` embeds the mcp-router MCP server token (`MCPR_TOKEN`) as a literal value inside `[mcp_servers.mcp-router.env]` — the only remaining literal credential in the file after provider credentials were migrated to environment indirection. The `correct-grok-cli-provider-routing` verification flagged it as a pre-existing item (evidence §3) for this separate hardening change.

## What Changes

- Move the mcp-router token from `~/.grok/config.toml` into the `~/.zshenv` shared-agent-secrets block.
- Replace the literal with indirection: grok's MCP `env` table accepts literal values only (no `env_key` interpolation for MCP servers), so the `mcp_servers.mcp-router` entry is repointed at a mode-700 wrapper script that sources `~/.zshenv` and execs `npx -y @mcp_router/cli connect`; the env block drops the literal entirely.
- Capture a mode-600 backup with recorded hash before mutation and verify a real MCP round trip after.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None.

Config/tooling-only hardening — `skip_specs: true`.

## Impact

- `~/.grok/config.toml` — `[mcp_servers.mcp-router]` block only; provider/model routing sections remain byte-identical
- `~/.zshenv` — one export added to the shared-agent-secrets block
- `~/.grok/` — new wrapper script (mode 700), no credential stored in it
- MCP connectivity for future grok sessions; zero effect on provider routing or defaults
