# Tasks: harden-grok-cli-mcp-credentials

All live mutation is approval-gated. Never print, log, or retain the token value; presence and length checks only.

## 1. Preparation

- [x] 1.1 Add the mcp-router token export to the `~/.zshenv` shared-agent-secrets block; verify `zsh -ic '[[ -n "$GROK_MCPR_TOKEN" ]]'` resolves true without printing the value
- [x] 1.2 Create the wrapper script (mode 700) that sources `~/.zshenv`, maps `GROK_MCPR_TOKEN` onto `MCPR_TOKEN`, and execs `npx -y @mcp_router/cli connect`; verify it contains no credential values
- [x] 1.3 Capture a mode-600 backup of `~/.grok/config.toml` with recorded sha256 and verify byte-identical restore (`cmp`)

## 2. Mutate and verify

- [x] 2.1 Repoint `[mcp_servers.mcp-router]` command at the wrapper and remove the literal `MCPR_TOKEN` from the env block; verify the file parses and `grok models` output is unchanged
- [x] 2.2 Re-run the provider-routing contract assertions (18/18 from `correct-grok-cli-provider-routing` §2) and confirm all pass — proving routing sections untouched
- [x] 2.3 Complete one real MCP round trip through the mcp-router server in a fresh grok session (server listed, one tool call succeeds) with the literal absent from config
- [x] 2.4 Re-run the credential-value scan: the token value ABSENT from `~/.grok/config.toml` and all OpenSpec artifacts

## 3. Delivery

- [x] 3.1 Run `openspec validate harden-grok-cli-mcp-credentials --strict --store openspec-store` and confirm it passes
- [x] 3.2 Record sanitized evidence (backup hash, assertion results, MCP round-trip outcome) in the change directory and commit after operator review
