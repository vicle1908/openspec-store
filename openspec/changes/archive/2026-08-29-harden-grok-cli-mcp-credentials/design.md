## Context

`~/.grok/config.toml` routes provider credentials through `env_key` indirection (verified by `correct-grok-cli-provider-routing`), but the MCP server block still carries a literal `MCPR_TOKEN` for the mcp-router server. grok's README documents MCP server env as `env = { VAR = "value" }` — literal values only, with no `env_key` or `${VAR}` interpolation for MCP servers (unlike model providers). The token therefore cannot be indirected through the same mechanism used for providers.

## Goals / Non-Goals

**Goals:**

- Remove the literal mcp-router token from `~/.grok/config.toml` so the file contains no credential values.
- Keep MCP connectivity context-independent (works regardless of how grok was launched).
- Leave provider/model routing sections byte-identical.

**Non-Goals:**

- No changes to provider routing, defaults, or any artifact of `correct-grok-cli-provider-routing`.
- No changes to other CLIs' mcp-router tokens (each owns its config).
- No upstream grok feature work (MCP env_key interpolation would be an upstream request).

## Decisions

1. **Wrapper script over pure env inheritance.** Adding the token to `~/.zshenv` alone would only work when grok is launched from a shell that sources it; GUI/cron launches would break the MCP server. A mode-700 wrapper (`source ~/.zshenv; export MCPR_TOKEN="$GROK_MCPR_TOKEN"; exec npx -y @mcp_router/cli connect`) is context-independent: the shared-secrets block exports `GROK_MCPR_TOKEN`, and the wrapper maps it onto `MCPR_TOKEN`, the variable the mcp-router CLI reads. Alternative rejected: relying on inherited environment (context-dependent).
2. **Token lives in the `~/.zshenv` shared-agent-secrets block**, consistent with the workspace credential convention (mode 600, single source of truth, presence-checked without printing values).
3. **Backup before mutation** with mode 600 and recorded hash, mirroring the provider-routing change's backup discipline; restore verified byte-identical.
4. **Regression gate:** the provider-routing contract assertions (18/18) must re-pass after the MCP block edit, proving the routing sections were untouched.

## Risks / Trade-offs

- [MCP breakage if the wrapper or zshenv var is wrong] → backup + immediate MCP round-trip verification; rollback restores the original block atomically.
- [Wrapper sources the full zshenv] → the npx child sees all shared secrets; acceptable (same exposure as any zsh-launched child), and the wrapper contains no credential values itself.
- [Env broadening vs literal] → the literal was visible to anyone reading the config; the wrapper moves it to a mode-600 file, strictly reducing exposure.

## Migration Plan

1. Capture backup of `~/.grok/config.toml` (mode 600, sha256, `cmp` verified).
2. Add the token export to `~/.zshenv` (presence-checked, never printed).
3. Create the wrapper (mode 700), repoint the mcp_servers command, drop the literal.
4. Verify: config parses, `grok models` unchanged, provider contract assertions re-pass, one real MCP round trip completes, credential scan shows the token value absent from `~/.grok/config.toml`.
5. Rollback: restore the backup byte-identically.
