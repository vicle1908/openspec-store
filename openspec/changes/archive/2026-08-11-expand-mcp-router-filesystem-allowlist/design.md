# Design: Expand MCP Router Filesystem Allowlist

## Architecture

MCP Router enforces filesystem access via `allowedDirectories` — an array of absolute paths. All file tools (`read_file`, `write_file`, `create_directory`, `move_file`, `list_directory`, `edit_block`, `get_file_info`, `read_multiple_files`) validate paths against this list before execution. Operations outside allowed directories return `[DENIED]` or `[NOT_FOUND]`.

## Change

Use `mcp__mcp_router__set_config_value` to replace the `allowedDirectories` array atomically. The tool replaces the entire array — the new value MUST include all existing entries plus the new one.

**Critical:** `set_config_value` replaces arrays, does not append. Omitting the existing `/Users/androidteam/Developer` would break all current workspace file operations.

## Security Boundary

| Path | Rationale | Risk |
|------|-----------|------|
| `/Users/androidteam/Developer` | Existing workspace root (already allowed) | Low — workspace repos |
| `/Users/androidteam/.hermes` | Hermes config, skills, state, cron, plugins | Medium — contains `.env` with secrets |

**Mitigation:** Agent behavior rules prohibit reading `.env`, token files, or credential-bearing configuration. The allowlist grants technical access; behavioral rules prevent misuse.

## Rollback

Revert to `["/Users/androidteam/Developer"]` via the same `set_config_value` tool.

## Verification

1. `get_config` → confirm array contains both entries
2. `read_file("/Users/androidteam/.hermes/config.yaml")` → file is readable (non-secret config)
3. `list_directory("/Users/androidteam/.hermes/skills")` → directory is accessible
4. Do NOT read `.env` or credential files during verification
