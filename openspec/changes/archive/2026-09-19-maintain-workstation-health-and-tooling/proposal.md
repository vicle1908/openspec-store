# Proposal: Maintain Workstation Health and Tooling

## Why

Developer workstations accumulate unmanaged software, stale package caches, and failing background daemons that degrade stability and consume critical disk space. This change establishes formal governance for periodic workstation health auditing, package manager updates, safe multi-tier disk reclamation, and LaunchAgent daemon remediation across the macOS developer environment.

## What Changes

- **Tooling & Package Updates**: Governs global runtime and package manager upgrades (`npm`, `bun`, `pnpm`, `uv`, Homebrew formulae and casks) with registry version matching and preflight integrity checks.
- **Unmanaged Application Migration**: Establishes standard migration of standalone applications (`Discord`, `Zalo`, `LarkSuite`, `InstantView`, `Hermes`, `Google Drive`) and standalone scripts (`gitlab-runner`, `fastlane`, `openspec`) into declarative Homebrew cask and formula management.
- **Tiered Storage Reclamation**: Formalizes safe disk reclamation separating Tier 1 (safe caches), Tier 2 (review-first build caches and older installers), and Tier 3 (strictly protected stateful assets like Docker raw disks, database volumes, cloud migration trees, and active virtualenvs).
- **Daemon & LaunchAgent Health**: Defines detection and repair procedures for failing or misconfigured user LaunchAgents, specifically resolving missing virtualenv binaries and binary symlink discrepancies.
- **Non-Goals**:
  - Enabling the macOS Application Firewall without prior network access review (avoids severing ARD, AnyViewer, or Cockpit remote sessions).
  - Mutating or forcibly rebasing diverged forks carrying local security patches (`prime-agent`) without explicit repository owner authorization.
  - Deleting or modifying the WHO-project iCloud tree containing unresolved worktrees and dataless files.

## Capabilities

### New Capabilities
- `workstation-tooling-maintenance`: Governs runtime updates, package manager audits, and LaunchAgent daemon health remediation for developer workstations.

### Modified Capabilities
- `workstation-storage-hygiene`: Extends storage hygiene with explicit multi-tier risk boundaries, review-first installer cleanup, and verified post-reclamation headroom tracking.

## Impact

- **Developer Environment**: Reclaims 32–36 GiB of local storage headroom (reducing utilization from 91% to 83%), clears crash-looping LaunchAgents, and ensures reproducible package management without breaking remote connectivity or active agent workloads.
