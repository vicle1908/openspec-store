# Proposal: Canonical OpenCode Configuration

## Why

OpenCode currently has both `~/.config/opencode/opencode.json` and `~/.config/opencode/opencode.jsonc`. Official configuration documentation defines a global `opencode.json` path and supports JSONC syntax, but maintaining two competing global files creates ambiguous ownership and makes future edits unsafe.

The effective runtime is currently correct because OpenCode merges both files, but the plain JSON file and JSONC file describe different defaults, agent definitions, compaction settings, watcher patterns, and MCP state.

## What Changes

- Preserve the current effective runtime configuration in one canonical `~/.config/opencode/opencode.json`.
- Back up both existing configuration files before consolidation.
- Move the JSONC source out of the active global config path as a timestamped backup.
- Verify the effective configuration remains unchanged for providers, agents, LSP, formatters, compaction, watcher ignores, instructions, and MCP enablement.
- Keep all credentials and provider endpoints intact; do not print secret values.

## Compatibility and Rollback

The change is local configuration only. Rollback restores the timestamped JSON and JSONC backups and removes the consolidated file if needed. Provider and model behavior should remain unchanged.

## References

- https://opencode.ai/docs/config/
- https://opencode.ai/docs/agents/
