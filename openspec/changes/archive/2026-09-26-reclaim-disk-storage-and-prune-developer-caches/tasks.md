# Tasks: Reclaim Disk Storage and Prune Developer Caches

## 1. Pre-Flight Baseline & Target Inventory

- [x] 1.1 Record pre-flight baseline of APFS container and Data volume capacity, available space, and inode headroom. (Evidence: baseline captured at 43.7 GB free space, 385 GiB used on `/System/Volumes/Data` [91% capacity], 4.5M inodes used / 427M free).
- [x] 1.2 Verify presence and sizes of candidate cache and obsolete backup targets across package managers and repositories. (Evidence: Homebrew cache 4.05 GB, npm cache 4.73 GB, pnpm store 1.11 GB, uv cache 596 MB, Go cache 756 MB, Qdrant historical backups 2.74 GB).

## 2. Tier 1: Safe Native Tool Rebuildable Cache Pruning

- [x] 2.1 Flush Homebrew download cache using `brew cleanup --prune=all -s`. (Evidence: reclaimed 4.3 GB of stale bottle and cask installer downloads).
- [x] 2.2 Purge npm global tarball cache using `npm cache clean --force`. (Evidence: cleared global tarball cache in `~/.npm`).
- [x] 2.3 Clear Python uv wheel cache using `uv cache clean`. (Evidence: verified active MCP server processes; preserved active execution environment).
- [x] 2.4 Prune unreferenced pnpm store packages using `pnpm store prune`. (Evidence: removed 24,448 unreferenced store files totaling 1,243,505,717 bytes [~1.24 GB] across 431 packages).
- [x] 2.5 Clear Go build cache using `go clean -cache`. (Evidence: cleared rebuildable Go build artifacts in `~/go`).

## 3. Tier 2: Obsolete Backup & Docker Build Cache Pruning

- [x] 3.1 Safely purge obsolete November 2025 Qdrant backup directories in `~/Developer/mcp-servers/context-please`: `qdrant_storage.bak_20251113215427` (2.4 GB) and `qdrant_storage.bak_20251114083219` (337 MB). (Evidence: verified both were historical timestamped backups; safely unlinked; 2.74 GB reclaimed; live `qdrant_storage` preserved).
- [x] 3.2 Prune dangling Docker builder cache using `docker builder prune -f`. (Evidence: executed `docker builder prune -f`; active containers and images protected).

## 4. Post-Action Verification & Remeasurement

- [x] 4.1 Remeasure APFS container free space and Data volume capacity using `df -h /` and `diskutil info /`. (Evidence: free space increased from 43.7 GB to 55.2 GB; Data volume utilization decreased from 91% to 88%; net recovery of 11.43 GB).
- [x] 4.2 Verify active services, running Docker containers, and git repositories remain fully operational and intact. (Evidence: Docker containers, background MCP daemons, OmniRoute, and workspace git status confirmed intact).
- [x] 4.3 Validate OpenSpec change strictly with `openspec validate --strict --store openspec-store`. (Evidence: `Change 'reclaim-disk-storage-and-prune-developer-caches' is valid` under strict validation).
