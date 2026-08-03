## Context

Antigravity v1.1.10 parses permissions as resources such as `mcp(server/tool)` and `mcp(*)`. The active settings contain `mcp*`, and runtime logs repeatedly report `ignoring invalid allow entry "mcp*"`. Existing specific grants for two `mcp-router` tools are valid.

Claude Code is independently healthy but unauthenticated. Authentication requires user interaction or a credential and is outside this configuration repair.

## Goals / Non-Goals

**Goals:**

- Make the existing Antigravity MCP wildcard intent syntactically valid.
- Verify the correction from a fresh runtime log, not only JSON syntax.
- Preserve current model, telemetry, trusted-workspace, and specific MCP grants.
- Record credential/auth blockers without exposing secrets.

**Non-Goals:**

- Broadening beyond the existing intended wildcard authorization.
- Altering MCP server transport/configuration.
- Performing interactive OAuth.

## Decisions

### Decision: Replace, do not add, the wildcard

Replace `mcp*` with `mcp(*)` so the allow list has no duplicate invalid entry. Retain specific grants as documentation and defense against future broad-grant removal.

### Decision: Verify using a dedicated fresh log file

Run a bounded print-mode probe with `--log-file` pointing to a temporary file. Confirm settings initialize with `mcp(*)` and the invalid-entry warning is absent. This avoids confusing historical log matches with current behavior.

### Decision: Do not initiate Claude login

`claude auth login` opens a browser and requires user credentials/account choice. Record the blocker and leave authentication state unchanged.

## Risks / Trade-offs

- **Broad MCP access remains enabled** → This matches existing intent; specific least-privilege tightening requires a separate user decision.
- **Historical logs retain old warnings** → Verification uses a new dedicated log and does not rewrite history.
- **MCP tool invocation may depend on server availability** → Separate settings-parser success from server/tool reachability evidence.
