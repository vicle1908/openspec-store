# Proposal

## Why

The macOS host APFS Data volume has reached a critical 96% utilization threshold (only 20 GB available out of 461 GB), threatening APFS copy-on-write performance, SQLite WAL write operations, and container VM stability. A measured, tiered cleanup under OpenSpec governance is urgently required to reclaim 40–60+ GB of safe, regenerable CLI package caches, Docker builder layers, and obsolete local development build artifacts without risking active databases, persistent agent memory, or source code.

## What Changes

- **Tier 1 Safe Package Manager Cache Eviction**: Purge fully regenerable download caches and tarballs across Homebrew (`brew cleanup --prune=all`), npm (`npm cache clean --force` and `rm -rf ~/.npm/_npx/*`), pnpm (`pnpm store prune`), uv wheel archives (`uv cache clean`), Bun (`bun pm cache rm`), and Go compilation artifacts (`go clean -cache`), recovering ~21.5 GB.
- **Tier 2A Docker Native Resource Pruning**: Clear unreferenced Docker builder cache (`docker builder prune -a -f`) and dangling images older than 7 days (`docker image prune -a -f`), while strictly safeguarding active database containers (`omniroute`, `redis`, `shb-schedule-db-1`) and active mounted volumes (`omniroute_omniroute-data`, `shb-schedule_shb-scheduler-pgdata`, `685eacfa...`).
- **Tier 2A Obsolete Volume Decommissioning**: Explicitly inventory and decommission unattached ephemeral test volumes from prior milestones (`0b050242...`, `shb-audit-*`, `shb-verification-*`, `smoke_scheduler_*`, `tdt-local-full_*`), reclaiming ~4.7 GB.
- **Tier 2B Obsolete Build Residue & Stale Snapshot Purging**: Safely remove unmounted host build artifacts in `~/Omniroute/.build` (6.5 GB) and stale April 2026 test database dump `WHO-project/.../pre-p0-audit.dump` (2.9 GB), recovering ~9.4 GB.
- **Tier 2C Simulator Shared dyld Cache Purging**: Purge rebuildable iOS simulator shared dyld caches (`xcrun simctl runtime dyld_shared_cache remove --all`), recovering 12.0 GB.
- **Verification Gates**: Establish pre-execution and post-tier APFS volume availability verification via `df -h /System/Volumes/Data` to confirm the workstation returns above the healthy 50+ GiB headroom target.

## Capabilities

### Modified Capabilities

- `workstation-storage-hygiene`: Add concrete requirements and scenarios for staged multi-tier CLI cache eviction, Docker builder cache reclamation with strict named-volume preservation, and obsolete development backup archive purging.

## Impact

- **Affected Ownership Boundaries**:
  - Homebrew (`/opt/homebrew` and `~/Library/Caches/Homebrew`)
  - Node & npm (`~/.npm`, `~/.bun`)
  - Python toolchain (`~/.cache/uv`)
  - Go toolchain (`~/Library/Caches/go-build`, `~/go/pkg/mod`)
  - Docker Desktop daemon (`Docker.raw` sparse VM, builder cache, images, named volumes)
  - Workstation repositories (`~/Omniroute`, `~/Developer/vds/WHO-project`)
- **Non-Goals**:
  - No deletion or modification of `Docker.raw` sparse file directly on host macOS.
  - No blanket pruning of Docker volumes (`docker volume prune -a` is strictly forbidden).
  - No eviction of active containers or runtime databases (`omniroute-data`, `omniroute-redis-data`, `shb-scheduler-pgdata`).
  - No mutation or deletion of personal data (`~/Pictures/Photos Library.photoslibrary`), Google Drive streams (`Google/DriveFS`), or persistent agent memory (`~/.agentmemory`).
  - No deletion of active Git working tree files or unstaged code in `~/Developer`.
