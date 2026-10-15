# Proposal: Reclaim Workstation Disk Storage

## Why

The workstation storage on `/System/Volumes/Data` is at critical capacity (393 GiB used out of 460 GiB, 94% utilization, leaving only 29 GiB free). With 12.9 GB of swap actively committed, this low disk headroom triggers APFS file allocation delays, virtual memory translation faults (>100M faults), and UI freezes across developer tools including Terminal.app, iTerm2, and IDEs.

## What Changes

Execute a disciplined 3-tier storage reclamation plan:
- **Tier 1 (Safe Ephemeral Caches):** Clean Homebrew bottle archives (`brew cleanup --prune=all -s`, `rm -rf $(brew --cache)` saving ~8.1 GiB), NPM cache (`npm cache clean --force` saving ~5.7 GiB), and uv cache (`uv cache prune` saving ~300 MiB).
- **Tier 2 (Docker Container Environment Pruning):** Reclaim unused Docker resources (`docker builder prune -af`, `docker image prune -af --filter "until=168h"`, and `docker volume prune -f` for unreferenced anonymous volumes, preserving named persistent volumes).
- **Tier 3 (Simulator & Deep Developer Artifacts):** Remove unavailable/orphaned iOS simulator devices (`xcrun simctl delete unavailable`), prune the pnpm global store (`pnpm store prune`), and clear stale user logs and crash dumps.

## Capabilities

### New Capabilities
None (`skip_specs: true`). Operational environment maintenance.

### Modified Capabilities
None.

## Impact

- Restores 25–40+ GiB of free disk space on `/System/Volumes/Data`.
- Lowers volume capacity from 94% toward <85%.
- Relieves macOS Mach VM swap paging bottleneck and prevents disk allocation stalls.
- Zero disruption to active development repositories or persistent database volumes.
