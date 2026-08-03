# Verification Evidence

Date: 2026-08-03

## Baseline

The active Antigravity settings contained:

```json
"allow": [
  "mcp*",
  "mcp(mcp-router/get_usage_stats)",
  "mcp(mcp-router/list_processes)"
]
```

Historical runtime logs repeatedly reported:

```text
ignoring invalid allow entry "mcp*": invalid grant string: "mcp*"
```

OpenSpec store doctor initially reported no issues and a clean Git repository.

## Configuration change

Changed only the invalid wildcard:

```diff
- "mcp*"
+ "mcp(*)"
```

The model, telemetry, trusted workspace, and specific MCP grants were preserved. `python3 -m json.tool` returned `SETTINGS_JSON_OK`.

## Fresh parser/runtime probe

Command shape:

```bash
agy --log-file /tmp/agy-mcp-permission-verify.log \
  --model gemini-3.6-flash-low --effort low \
  --print-timeout 45s --output-format json \
  --print 'Reply with exactly AGY_PERMISSION_OK. Do not call tools.'
```

Observed:

- Process exit: `0`
- Result status: `SUCCESS`
- Response: `AGY_PERMISSION_OK`
- Conversation ID: `da63deb3-1335-45b3-976e-ff79011dc659`
- Fresh settings initialization showed `Allow:[mcp(*) mcp(mcp-router/get_usage_stats) mcp(mcp-router/list_processes)]`.
- The dedicated fresh log contained no `invalid allow entry` warning.

## MCP tool probe

A global `mcp-router` server definition exists. Its transport configuration and credentials were not copied into this evidence.

Command shape:

```bash
agy --log-file /tmp/agy-mcp-tool-verify.log \
  --model gemini-3.6-flash-low --effort low \
  --print-timeout 90s --output-format stream-json \
  --dangerously-skip-permissions \
  --print 'Use the configured mcp-router get_usage_stats tool exactly once ...'
```

Observed:

- `call_mcp_tool` used server `mcp-router`, tool `get_usage_stats`, exactly once.
- Tool state: `DONE`.
- Tool duration: approximately 0.052 seconds.
- A valid usage-summary result was returned; detailed account/tool usage values are intentionally omitted here.
- Final response: `MCP_TOOL_OK`.
- Result status: `SUCCESS`.
- Conversation ID: `bbc2be8b-6fcf-4100-a53d-6aed140826e0`.
- The fresh tool-probe log contained no invalid-grant warning.

## Claude Code status

Commands:

```bash
claude auth status
claude doctor
```

Observed:

- Claude Code installation is healthy: `No installation issues found`.
- Authentication status remains `loggedIn: false`, `authMethod: none`.
- No login flow was initiated because it requires user account interaction and credentials.

## Security and scope

- No credential values were printed, modified, or committed.
- No MCP server definitions were changed.
- The repair preserves the existing intended broad MCP authorization rather than expanding it.
- Historical logs remain unchanged; verification relied on dedicated fresh logs.
