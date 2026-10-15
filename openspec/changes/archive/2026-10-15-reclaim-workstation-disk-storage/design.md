# Design: Reclaim Workstation Disk Storage

## Context

The workstation volume (`/System/Volumes/Data`) is at 94% capacity, with only 29 GiB available out of 460 GiB. Host diagnostics show 12.9 GB of swap in active use and high translation fault rates. 

Empirical probing revealed several large reclaimable targets:
- Homebrew bottle and download cache: 8.1 GiB (`~/Library/Caches/Homebrew`)
- NPM tarball chunk cache: 5.7 GiB (`~/.npm/_cacache`)
- Docker reclaimable resources: 13.5 GiB (8.0 GB images, 4.5 GB unreferenced volumes, 658 MB builder cache)
- uv wheel and source checkout cache: ~300 MiB
- Unavailable/orphaned iOS simulator runtime state
- Stale diagnostic reports and crash logs (`~/Library/Logs/DiagnosticReports/`)

## Goals / Non-Goals

**Goals:**
- Free between 25 GiB and 40+ GiB on `/System/Volumes/Data`, bringing free space above 60 GiB.
- Execute cleanup in 3 disciplined, prioritized tiers with verifiable checkpoints.
- Preserve all active repositories, persistent database volumes, active container images, and shell configurations.
- Eliminate swap thrashing and disk write throttling.

**Non-Goals:**
- Do not run unconstrained wildcards (`rm -rf`) across `~/Library/Caches` or `~/Library/Application Support`.
- Do not delete named Docker volumes or active workspace containers.
- Do not modify git repositories or delete untracked work in progress.
- Do not touch `~/.zshrc` or `~/.zshenv` (already hardened and verified).

## Decisions

### Decision 1: Tier 1 - Zero-Risk Ephemeral Caches
*Actions:*
1. `brew cleanup --prune=all -s` and remove `$(brew --cache)` (frees ~8.1 GiB).
2. `npm cache clean --force` (frees ~5.7 GiB).
3. `uv cache prune` (frees ~300 MiB).
*Rationale:* These are 100% ephemeral package download caches that auto-populate on demand.

### Decision 2: Tier 2 - Container Environment Pruning
*Actions:*
1. `docker builder prune -af` (frees ~658 MB of build cache).
2. `docker image prune -af --filter "until=168h"` (frees unreferenced images older than 7 days).
3. `docker volume prune -f` (safely removes anonymous orphaned volumes, keeping named volumes like `omniroute-data`).
4. `pnpm store prune` (frees unreferenced packages in global pnpm store).
*Rationale:* Reclaims up to 13.5 GiB of container sprawl without endangering running services.

### Decision 3: Tier 3 - Simulator & Diagnostic Housekeeping
*Actions:*
1. `xcrun simctl delete unavailable` (removes corrupted or missing simulator references).
2. Clear stale crash dumps older than 7 days in `~/Library/Logs/DiagnosticReports/`.
3. Check and purge any APFS local snapshots via `tmutil` if present.

## Risks / Trade-offs

- **[Risk]** Next `npm install` or `brew install` downloads from network instead of local cache.
  → *Mitigation:* One-time network fetch penalty is negligible compared to the system-wide danger of disk exhaustion.
- **[Risk]** Pruning unreferenced Docker images might prune an image needed offline.
  → *Mitigation:* We use `--filter "until=168h"` so recently used or pulled images are strictly preserved.

## Verification Plan

- Record baseline storage before Tier 1 (`df -h /System/Volumes/Data`).
- Check intermediate storage delta after each tier.
- Record final storage and calculate total GiB reclaimed.
- Confirm system stability: `zsh -i -c exit`, verify `git`, `node`, `brew`, `docker`.
- Validate OpenSpec change strictly.
