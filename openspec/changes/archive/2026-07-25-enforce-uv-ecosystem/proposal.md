## Why

The TDT ecosystem has 14 Python repos with inconsistent uv adoption:
- 1 repo missing uv.lock (agent-docs-sync)
- 4 repos missing .python-version
- 9 docs files with pip references instead of uv
- Only 2 of 14 repos have uv practices documented in AGENTS.md
- No standardized [tool.uv] config across repos

This inconsistency leads to:
- Developers using pip instead of uv (violating project standards)
- Different Python versions across repos
- Documentation that teaches outdated practices
- No enforced uv version pinning

## What Changes

- **Add uv.lock** to agent-docs-sync (the only repo missing it)
- **Add .python-version** to 4 repos (agent-docs-sync, code-daily-scan, tdt-observability, tdt-sheets)
- **Update AGENTS.md** in all Python repos with uv practices section
- **Fix pip references** in 9 docs files across tdt-meta and agent-docs-sync
- **Standardize [tool.uv] config** across all repos (consistent python-preference, required-version)
- **Add uv enforcement** to workspace root AGENTS.md

## Capabilities

### New Capabilities

- `uv-ecosystem-standardization`: Enforce uv practices across all TDT Python repos

### Modified Capabilities

None — this is a cross-repo standardization change.

## Impact

- **Files modified**: ~20 files across multiple repos
- **Repos affected**: agent-docs-sync, code-daily-scan, tdt-observability, tdt-sheets, tdt-meta
- **Risk**: LOW — documentation and config changes only, no code changes
