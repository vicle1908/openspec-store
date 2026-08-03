## Why

Antigravity currently ignores the configured `mcp*` allow entry because it is not valid permission-resource syntax, leaving the intended MCP authorization partially ineffective and producing warnings on every run.

## What Changes

- Replace the invalid broad entry `mcp*` with the documented `mcp(*)` resource wildcard while retaining the existing tool-specific grants.
- Verify that Antigravity accepts the updated settings without an invalid-grant warning.
- Verify configured MCP discovery/tool access where the current CLI exposes a headless path.
- Record the separate Claude Code authentication blocker without changing credentials or starting an interactive login.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This is a user-level configuration correction with `skip_specs: true`.

## Impact

- **Modified surface:** `~/.gemini/antigravity-cli/settings.json` in the active user profile.
- **Behavior:** The existing intended broad MCP allow grant becomes syntactically valid.
- **Security:** This preserves the user's pre-existing broad authorization intent; it does not introduce a new permission category.
- **Unaffected:** Application repositories, credentials, MCP server definitions, and Claude authentication.

## Non-Goals

- Logging into Claude Code or Antigravity interactively.
- Rotating, printing, or changing credentials.
- Adding or removing MCP servers.
- Changing product capability specifications.
