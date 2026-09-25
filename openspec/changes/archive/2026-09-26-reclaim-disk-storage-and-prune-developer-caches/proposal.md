# Proposal: Reclaim Disk Storage and Prune Developer Caches

## Why

The local workstation primary APFS Data volume (`/System/Volumes/Data`) is under severe storage pressure at **91% utilization**, with only **43.7 GB free space** remaining out of 494.4 GB. 

An ecosystem storage audit identified significant rebuildable cache accumulation and historical unindexed backup artifacts that can be safely reclaimed without disrupting active development workflows or deleting stateful data:
1. **Homebrew Download Cache (~4.05 GB):** Accumulated bottles and source archives in `~/Library/Caches/Homebrew`.
2. **Node Package Caches (~5.84 GB):** Stale npm tarball cache in `~/.npm` (4.73 GB) and unreferenced pnpm store packages in `~/.pnpm-store` (1.11 GB).
3. **Python uv Cache (~596 MB):** Rebuildable package wheels in `~/.cache/uv`.
4. **Go Build Cache (~756 MB):** Rebuildable object and build cache in `~/go/pkg` and Go cache directories.
5. **Obsolete Development Backups (~2.74 GB):** Historical unindexed vector database backup directories in `~/Developer/mcp-servers/context-please` (`qdrant_storage.bak_20251113215427` at 2.4 GB and `qdrant_storage.bak_20251114083219` at 337 MB) from November 2025.
6. **Docker Build Cache (~34 MB) & Dangling Volumes (~847.6 MB):** Reclaimable local cache artifacts from previous builds.

Total immediate safe reclaim potential is estimated between **10 GB and 14 GB**.

## What Changes

- **Tier 1 (Safe Rebuildable Caches via Native Tools):**
  - Run `brew cleanup --prune=all -s` to remove all cached Homebrew installer bottles.
  - Run `npm cache clean --force` to flush cached tarballs in `~/.npm`.
  - Run `uv cache clean` to purge unreferenced wheels in `~/.cache/uv`.
  - Run `pnpm store prune` to unlink unreferenced packages in `~/.pnpm-store`.
  - Run `go clean -cache` to clear rebuildable Go compilation artifacts.

- **Tier 2 (Stale Development Backup Artifacts & Docker Pruning):**
  - Remove obsolete, non-active test backup directories from `~/Developer/mcp-servers/context-please/`:
    - `qdrant_storage.bak_20251113215427` (2.4 GB)
    - `qdrant_storage.bak_20251114083219` (337 MB)
  - Execute `docker builder prune -f` to reclaim orphaned Docker build cache.

- **Tier 3 (Protected Resources - Excluded):**
  - Active Docker images and running container volumes are strictly protected.
  - Active repositories in `~/Developer` and live databases (e.g. OmniRoute at `~/OmniRoute`) remain untouched.

## Capabilities

### Modified Capabilities
- `workstation-storage-hygiene`: Updated requirements for automated rebuildable cache pruning and stale project backup reclamation.

## Impact & Verification

- **Storage Reclaim:** Target recovery of **> 10 GB** of free space, bringing container availability from 43.7 GB to > 54 GB and dropping Data volume capacity below 89%.
- **Safety Gate:** Rebuildable caches are pruned exclusively via official vendor tooling (`brew`, `npm`, `uv`, `pnpm`, `go`, `docker`).
- **Audit Verification:** Measured APFS Data-volume capacity and free space before and after each execution tier.
