# Proposal

## Why

The Pi coding agent setup drifted from the workspace's canonical Agent Skills ownership and still carried two third-party packages whose functionality Pi 1.0.0 now provides natively. Pi also retained a product-specific skill root (`~/.pi/agent/skills`) that duplicated the canonical shared surface, contradicting the workspace policy that standard-compatible agents discover shared skills through standard `.agents/skills` locations without product-specific copies.

## What Changes

- **Remove redundant third-party packages** (`pi-setup-custom-providers`, `pi-mcp-adapter`) in favor of Pi-native equivalents: custom providers via `~/.pi/agent/models.json`, and MCP via the built-in `mcp` extension.
- **Establish a single MCP implementation**: the built-in `mcp` extension is the sole MCP path; no plugin may co-register `/mcp`.
- **Eliminate the product-specific skill root**: delete `~/.pi/agent/skills` (47 redundant copies, a pure subset of `~/.agents/skills`).
- **Bridge workspace skills into user scope using the canonical link pattern**: `~/.agents/skills/<name>` SHALL resolve to the canonical workspace skill root rather than holding duplicated content.
- **Correct the placement of the 26 promoted skills**: they were copied into `~/.agents/skills`, but since each duplicates a workspace skill they must be standard user-level links per the existing convention.
- **Define the placement rule durably**: global (`~/.agents/skills`) for machine/service-level and vendor/library guidance; workspace (`Developer/.agents/skills`) for generator-owned skills.
- **Record upstream follow-ups**: Pi 1.0.0's fullscreen-by-default TUI mode decision, and the `graphify` skill referencing a non-existent `Task` tool.

## Capabilities

### New Capabilities

None. This change corrects implementation conformance to requirements that already exist.

### Modified Capabilities

- `workspace-openspec-skill-discovery`: Clarify that Pi is a covered standard-compatible agent, that `~/.agents/skills` entries bridging workspace skills MUST be links (never copied content), and add Pi-specific verification scenarios. Also record the placement rule distinguishing global machine/vendor guidance from generator-owned workspace skills.
- `agent-skill-distribution`: Record that package-managed product roots (for example `~/.pi/agent/skills`) MUST NOT hold copies of skills available through standard `.agents/skills` discovery.

## Impact

- **Pi configuration**: `~/.pi/agent/settings.json` (packages), `~/.pi/agent/models.json` (providers), `~/.pi/agent/mcp.json` (MCP server), `~/.pi/agent/skills` (removed).
- **Agent Skills surfaces**: `~/.agents/skills` (removed 47 copies; 26 promoted entries corrected to links), `~/Developer/.agents/skills` (unchanged canonical roots).
- **Removed dependencies**: `npm:pi-setup-custom-providers`, `npm:pi-mcp-adapter`.
- **Unaffected by decision**: project trust remains wide (`/Users/androidteam/Developer`), per explicit operator choice.
- **Evidence**: provider resolution via `pi --list-models`, MCP via `pi mcp list`, skill discovery via structural inventory, and Pi startup health with zero warnings.
