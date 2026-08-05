# Verification Evidence

Date: 2026-08-05

## Live inventory

- Pi CLI: `0.83.0`
- Default provider/model: `shoapikey` / `fable-5`
- Default thinking: `xhigh`
- Packages: `pi-subagents 0.40.0`, `pi-web-access 0.18.0`, `pi-intercom 0.9.2`, `pi-setup-custom-providers 1.0.1`, `pi-lens 3.8.74`, `pi-mcp-adapter 2.20.1`, `pi-gitnexus 0.6.4`
- Custom global extension: `agentmemory` (loaded, backend unreachable)
- Trust root: `/Users/androidteam/Developer` trusted globally
- MCP: one `mcp-router` server with `directTools: true`, yielding 77 direct tools

## File-mode and secret findings

- `~/.pi/agent/models.json`: mode `0600`, but contains literal inline provider secrets.
- `~/.pi/agent/mcp.json`: mode `0644`, contains literal `MCPR_TOKEN` in `env`.
- `~/.pi/web-search.json`: mode `0644`, contains inline API keys for Exa, Perplexity, and fable-5.
- `~/.pi/agent/auth.json`: mode `0600`, empty on this host.

## Direct MCP verification

### Wrong-name failure

Using the Hermes-style name `mcp__mcp_router__brave_web_search` in Pi did not work. Pi reported the tool unavailable.

### Actual generated name

Using the proxy tool and adapter cache confirmed the generated direct-tool name is:

- `mcp_router_brave_web_search`

Reason: adapter default `toolPrefix` is `server`, so server `mcp-router` becomes prefix `mcp_router` and original tool `brave_web_search` is formatted as `mcp_router_brave_web_search`.

### `--tools` allowlist verification

A print-mode run with:

```bash
pi -p --mode json --no-session --no-context-files --no-skills \
  --tools mcp_router_brave_web_search \
  "Call mcp_router_brave_web_search ..."
```

produced a successful tool call to `mcp_router_brave_web_search` and returned the requested success sentinel.

A second run with:

```bash
pi -p --mode json --no-session --no-context-files --no-skills \
  --tools read \
  "Try to call brave web search ..."
```

reported the MCP tool unavailable and returned the requested filtered-out sentinel.

**Conclusion:** direct MCP tools *are* filterable by Pi `--tools` / `--exclude-tools` when you use the generated Pi tool names.

## Proxy MCP verification

A run with only the `mcp` tool active successfully searched adapter metadata and reported the exact direct tool name `mcp_router_brave_web_search`.

**Conclusion:** proxy-mode MCP remains separately governed by whether the `mcp` tool is active and by adapter config.

## Subagent doctor probe

A bounded print-mode run using only the `subagent` tool returned useful doctor output:

- readiness healthy overall
- 9 executable builtin agents discovered
- 10 skills discovered
- spawn usage unlimited
- no configured session dir / current session file in the print context
- missing temp `chain-runs` directory warning

The process printed the diagnostics but did not exit before the outer host timeout, so print-mode `subagent doctor` should be treated as potentially sticky and bounded externally.

## Gateway FD diagnosis

Desktop Commander process inspection showed the Hermes gateway process (`python -m hermes_cli.main gateway run --replace`) holding ~300 file descriptors, including many repeated `state.db` / `state.db-wal` handles.

There was no evidence that Pi child processes were the primary cause of the `Errno 24` failures. The failures are attributable to the surrounding Hermes gateway runtime rather than Pi itself.

## Package-doc cross-checks

Installed package READMEs confirmed:

- `pi-subagents` supports builtin agents, chains, async runs, worktrees, direct MCP child selection, intercom bridge, and per-agent memory.
- `pi-web-access` supports multi-provider search, extraction, GitHub clone mode, PDFs, videos, curator workflows, and source-check artifacts.
- `pi-mcp-adapter` supports proxy/direct modes, approvals, output guards, `mcpScript`, MCP prompts, elicitation, UI resources, imports, and multiple config layers.
- `pi-lens` supports LSP diagnostics/navigation, AST tools, module reports, symbol search, formatting/autofix, and project intelligence.
- `pi-intercom` supports local brokered session messaging, ask/reply, attachments, and supervisor escalation.
- `pi-gitnexus` supports auto-augmentation and seven explicit graph tools.
- `pi-setup-custom-providers` supports provider/model discovery and testing.

## Grounded report

See `evaluation-report.md` in this change for the full analysis and recommendations.

## Sources
[1] https://pi.dev/docs/latest/usage — Pi Usage
[2] https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/settings.md — Pi Settings
[3] https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/security.md — Pi Security
[4] https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/packages.md — Pi Packages
[5] https://pi.dev/docs/latest/extensions — Pi Extensions
[6] https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md — Pi Skills
[7] https://pi.dev/docs/latest/sdk — Pi SDK
[8] https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md — Pi RPC
[9] https://pi.dev/news/releases — Pi Releases
[10] https://github.com/nicobailon/pi-mcp-adapter — pi-mcp-adapter
[11] https://github.com/nicobailon/pi-subagents — pi-subagents
[12] https://github.com/nicobailon/pi-web-access — pi-web-access
[13] https://github.com/apmantza/pi-lens — pi-lens
[14] https://github.com/tintinweb/pi-gitnexus — pi-gitnexus
[15] https://github.com/nicobailon/pi-intercom — pi-intercom
[17] https://rywalker.com/research/pi — Independent Pi Evaluation
