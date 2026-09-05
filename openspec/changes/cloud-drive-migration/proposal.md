# Proposal: Cloud Drive Migration

## Summary

Migrate all code projects from iCloud Drive and Google Drive to `~/Developer`, delete duplicates and build artifacts, and establish a clean separation: `~/Developer` for all code, cloud drives for documentation only.

## Problem

Development projects are scattered across iCloud Drive and Google Drive, creating several risks:

1. **iCloud corrupts git state** — iCloud's sync daemon can modify `.git/` files, corrupting repositories. Two code projects (`project/vds/` at 6.7G and `project/microservices/` at 604M) are currently in iCloud.
2. **Google Drive duplicates** — `~/My Drive/TDT (1)/` (2.9G) is a stale duplicate of `~/My Drive/tdt/`. The `tdt/` directory (6.9G) contains rclone bisync mirrors of all workspace repos, which are already in `~/Developer`.
3. **Build artifacts in iCloud** — Android build caches (`compileDebugKotlin/`, `compileKotlin/`, `ksp/`) totaling 1.4M are in iCloud.
4. **Desktop/Documents migration stubs** — Empty (0B) stubs from a previous migration clutter Desktop and Documents.

## Proposed Solution

### Phase 1: iCloud Migration

- Move `~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/` → `~/Developer/vds`
- Move `~/Library/Mobile Documents/com~apple~CloudDocs/project/microservices/` → `~/Developer/microservices`
- Delete iCloud build artifacts: `compileDebugKotlin/`, `compileKotlin/`, `ksp/`, `sparse/`, `inventory/`, `com 2/`, `camunda*`, `airbridge/`, `tmz/`

### Phase 2: Google Drive Cleanup

- Delete `~/My Drive/TDT (1)/` (2.9G duplicate)
- Delete `~/My Drive/VinID/` (2.3G — user confirmed delete, no migration)
- Delete code repos from `~/My Drive/tdt/` (6.3G) — keep documentation repos (600M)
- Delete `go-microservices-cleanup-20260817.bundle` from `~/Developer/` (1.4G)

### Phase 3: Desktop/Documents Cleanup

- Delete empty migration stubs from Desktop and Documents
- Delete `tdt-python-source-package` from Desktop (132K)

## Success Criteria

1. All code projects are in `~/Developer/` only
2. iCloud has zero code projects (documentation only)
3. Google Drive has zero code repo mirrors (documentation only)
4. All empty migration stubs are removed from Desktop/Documents
5. `~/Developer/` gains ~9.6G (vds + microservices) while cloud drives lose ~20G

## Risks

1. **iCloud mv may be slow** — Moving 6.7G from iCloud to local disk. Mitigation: `mv` on same APFS volume is fast (directory entry update, not data copy).
2. **Google Drive sync may propagate deletions** — Deleting from `~/My Drive/` deletes from cloud. Mitigation: This is intentional — user wants code removed from cloud.
3. **rclone bisync may see deletions** — Next bisync run will detect removed code repos. Mitigation: User can update rclone config to exclude code repos, or stop bisync entirely.
