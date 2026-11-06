# Proposal: Reclaim Workstation Disk Storage

## Why

The macOS primary APFS Data volume (`/System/Volumes/Data`) is under critical storage pressure at **95% utilization**, with only **21.9 GiB free space** remaining out of 460 GiB, falling below the mandatory **30 GiB minimum readiness threshold** defined in `workstation-storage-hygiene`. Immediate, safety-gated execution of multi-tiered storage reclamation is necessary to restore safe operating headroom without disrupting running containers or active repositories.

## What Changes

- **Tier 1 (Zero-Risk Ephemeral Package Caches):**
  - Run `brew cleanup --prune=all -s` and clean Homebrew cache directory (`~/Library/Caches/Homebrew`, ~10.0 GiB).
  - Run `npm cache clean --force` to clear global npm tarball cache (`~/.npm/_cacache`, ~6.1 GiB).
  - Run `pnpm store prune` to delete unreferenced pnpm packages (`~/Library/pnpm`, ~6.1 GiB).
  - Run `uv cache prune` to purge unreferenced Python wheels (`~/.cache/uv`, ~5.2 GiB).
  - Run `go clean -cache` to clear Go compiler and build cache (`~/Library/Caches/go-build`, ~3.8 GiB).
  - Run `git repack` and `prune-packed` on `~/.agentmemory/snapshots` if loose objects accumulate.

- **Tier 2 (Container Runtime & Build Cache Pruning):**
  - Execute `docker builder prune -f` to purge unreferenced BuildKit build cache (~4.2 GiB).
  - Execute `docker image prune -af --filter "until=168h"` to remove unreferenced images older than 7 days (~6.8 GiB).
  - Execute `docker volume prune -f` to remove orphaned anonymous volumes (~4.4 GiB).
  - Enforce strict preservation invariants for running containers (`omniroute`, `shb-schedule-db-1`, etc.) and named volumes (`omniroute-data`, `postgres-data`).

- **Tier 3 (Simulator & Diagnostic Housekeeping):**
  - Run `xcrun simctl delete unavailable` to purge unreferenced simulator devices.
  - Purge stale diagnostic crash reports older than 7 days from `~/Library/Logs/DiagnosticReports`.
  - Clean stale Xcode DerivedData if present.

- **Safety & Verification:**
  - Record APFS `/System/Volumes/Data` capacity and availability before and after each execution tier.
  - Verify core toolchain health (`node`, `brew`, `docker`, `git`) post-reclamation.

## Capabilities

### Modified Capabilities

- `workstation-storage-hygiene`: Adds normative procedures for multi-tiered automated execution (Tier 1 package caches, Tier 2 Docker builder/volume pruning with named-volume preservation, and Tier 3 simulator/diagnostic housekeeping) with mandatory before/after APFS capacity verification.

## Impact

- Restores >30 GiB of available storage on `/System/Volumes/Data`, bringing total free space above 50–70 GiB.
- No impact on active running containers or named application volumes.
- All operations use official vendor tool commands rather than unguided recursive filesystem deletions.
