# Design: Canonical OpenCode Configuration

## Source Selection

The current effective result from `opencode debug config` is the compatibility target. It includes:

- default `cockpit/gpt-5.6-sol` and small model `cockpit/gpt-5.6-luna`;
- five custom agents: explore, oracle, librarian, frontend, and docwriter;
- shopapikey, cockpit, Google, and Z.ai providers;
- basedpyright LSP override;
- built-in formatters;
- workspace instructions;
- auto-compaction with pruning and a 4096-token reserve;
- watcher ignores for generated/dependency directories;
- mcp-router enabled and agentmemory disabled.

The canonical file will be generated from the user-owned configuration sources, not from plugin-injected runtime metadata such as `plugin_origins`, `mode`, `command`, or `username`.

## Backup and Consolidation

1. Create timestamped backups of `opencode.json` and `opencode.jsonc`.
2. Parse the JSONC source safely, preserving all provider, model, agent, plugin, permission, tool, instruction, LSP, formatter, compaction, watcher, and MCP settings.
3. Merge missing user-owned keys from the effective base JSON where needed.
4. Write a single valid JSON `opencode.json`.
5. Move the old JSONC file to a timestamped backup outside the active config names.

## Verification

- Canonical JSON parsed successfully with Node and Python.
- Only `opencode.json` remains under an active global config filename; timestamped JSON/JSONC backups are retained.
- Effective model is `cockpit/gpt-5.6-sol`; small model is `cockpit/gpt-5.6-luna`.
- Five custom agents and four configured provider IDs remain present.
- LSP, formatter, instructions, compaction, watcher, and MCP states match the compatibility target.
- Default model returned `DEFAULT_OK`.
- `shopapikey/fable-5` returned `FABLE_OK`.
- `cockpit/gpt-5.6-sol` returned `SOL_OK`.
- `cockpit/gpt-5.6-luna` returned `LUNA_OK`.
- Ruff 0.16.1 and Basedpyright 1.39.9 resolve from `/opt/homebrew/bin`.
