# Design: Reclaim Disk Storage and Prune Developer Caches

## Architecture Overview

This change applies a safe, multi-tiered reclamation strategy to relieve storage pressure on the primary macOS APFS Data volume (`/System/Volumes/Data`) without impacting running processes or active projects:

```
[ Workstation APFS Storage (43.7 GB Free / 91% Used) ]
                           │
                           ▼
  [ Phase 1: Pre-Flight Baseline & Target Confirmation ]
      - Confirm Data volume availability & inode headroom
      - Verify tool versions (`brew`, `npm`, `uv`, `pnpm`, `go`, `docker`)
      - Inspect targets and assert isolation
                           │
                           ▼
  [ Phase 2: Tier 1 - Native Tool Rebuildable Cache Flush ]
      - `brew cleanup --prune=all -s` (~4.05 GB reclaim)
      - `npm cache clean --force` (~4.73 GB reclaim)
      - `uv cache clean` (~596 MB reclaim)
      - `pnpm store prune` (~200-500 MB reclaim)
      - `go clean -cache` (~750 MB reclaim)
                           │
                           ▼
  [ Phase 3: Tier 2 - Obsolete Backup & Build Artifact Prune ]
      - Safely remove historical November 2025 Qdrant backups in `~/Developer/mcp-servers/context-please`:
        * `qdrant_storage.bak_20251113215427` (2.4 GB)
        * `qdrant_storage.bak_20251114083219` (337 MB)
      - Run `docker builder prune -f` (~34 MB reclaim)
                           │
                           ▼
  [ Phase 4: Tier 3 - Verification & Audit Remeasurement ]
      - Execute `df -h /` and `diskutil info /`
      - Calculate exact delta of reclaimed storage
      - Confirm active repositories, containers, and databases intact
```

## Safety Boundaries & Exclusions

| Target Category | Tool / Action | Safety Justification | Risk Level |
|---|---|---|---|
| Homebrew Bottles | `brew cleanup --prune=all -s` | Downloads are ephemeral; re-downloadable on demand | Tier 1 (Safe) |
| NPM Cache | `npm cache clean --force` | Tarball cache only; local `node_modules` untouched | Tier 1 (Safe) |
| UV Wheel Cache | `uv cache clean` | Local wheels only; `.venv` untouched | Tier 1 (Safe) |
| PNPM Store | `pnpm store prune` | Removes unreferenced package content only | Tier 1 (Safe) |
| Go Build Cache | `go clean -cache` | Clears compiled test/build artifacts; source untouched | Tier 1 (Safe) |
| Stale Qdrant Backups | `rm -rf context-please/*.bak_*` | Unreferenced snapshot backups from Nov 2025; live `qdrant_storage` untouched | Tier 2 (Safe / Stale Backup) |
| Docker Build Cache | `docker builder prune -f` | Clears intermediate build layers; active containers/images protected | Tier 2 (Safe) |
| Active Repositories | Excluded | Code, git branches, local edits strictly protected | Tier 3 (Protected) |
| Running Databases | Excluded | OmniRoute, local Postgres/Redis/Qdrant databases protected | Tier 3 (Protected) |

## Verification Criteria

1. **Tool-Native Operation:** All cache evictions must use the official CLI interface for each runtime.
2. **Path Guard:** File unlinking is strictly restricted to designated `.bak_*` patterns inside `~/Developer/mcp-servers/context-please`.
3. **Audited Recovery:** Free space must be remeasured using APFS filesystem counters before and after each tier.
