## Why

The MCP Router (Desktop Commander) configuration has suboptimal defaults that cause friction during development workflows. Specifically: mismatched shell default, and line limits that force excessive re-reads and chunking for a workspace with 160+ sessions and 3900+ tool calls.

## What Changes

- Change `defaultShell` from `/bin/sh` to `zsh` to match the system default shell
- Increase `fileReadLineLimit` from 500 to 1000 to reduce re-reads for large files
- Increase `fileWriteLineLimit` from 50 to 100 to reduce chunking overhead during bulk writes

## Capabilities

### New Capabilities

_(none — this is a configuration tuning change, no new behavioral capabilities)_

### Modified Capabilities

_(none — no spec-level behavior changes; this is pure configuration optimization)_

> **Note:** This change has no spec-level behavior changes. Setting `skip_specs: true` in `.openspec.yaml`.

## Impact

- **Configuration:** `set_config_value` calls to update `defaultShell`, `fileReadLineLimit`, `fileWriteLineLimit`
- **Affected files:** Desktop Commander MCP server config (runtime state, not persisted in repo)
- **Risk:** Low — these are tuning changes with immediate feedback; reversibility is trivial
- **Verification:** Confirm `get_config` reflects updated values after apply
