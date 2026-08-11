# Proposal: Expand MCP Router Filesystem Allowlist

## Why

MCP Router's `allowedDirectories` is locked to `["/Users/androidteam/Developer"]`. This blocks MCP file tools (`read_file`, `write_file`, `list_directory`, `edit_block`) from operating on any path outside the workspace root. When the agent needs to inspect Hermes config files, skills, or state under `~/.hermes/`, MCP tools fail silently or return `[DENIED]`.

**Root cause:** The allowlist was set during initial MCP Router setup and never expanded as agent workflows grew to require cross-directory file operations.

## What Changes

Add `/Users/androidteam/.hermes` to the `allowedDirectories` array in MCP Router's configuration via `set_config_value`.

**Current state:**
```json
{"allowedDirectories": ["/Users/androidteam/Developer"]}
```

**After change:**
```json
{"allowedDirectories": ["/Users/androidteam/Developer", "/Users/androidteam/.hermes"]}
```

**Non-goals:**
- Does NOT add `/Users/androidteam` (would expose entire home directory)
- Does NOT add `/` or `[]` (would grant full filesystem access)
- Does NOT add `/Users/androidteam/Library/Application Support/MCP Router` (separate scope, separate decision)
- Does NOT read `.env`, tokens, or credential-bearing files
