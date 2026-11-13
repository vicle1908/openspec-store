# Design

## Context

The workstation is a macOS Darwin 27.0.0 ARM64 machine with an APFS container holding `/dev/disk3s1s1` mounted on `/` and `/System/Volumes/Data`. Out of 461 GB total, 441 GB is allocated (96% full), leaving 20 GB free space.

Extensive pre-flight empirical audits revealed:
- 30 GB physical allocation in `~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw` (logical 704 GB sparse file).
- 18.1 GB Docker build cache (16.44 GB reclaimable).
- 5.8 GB Homebrew bottle/cask downloads in `~/Library/Caches/Homebrew`.
- 7.7 GB npm caches (`~/.npm/_npx` 5.1G, `~/.npm/_cacache` 2.6G).
- 5.2 GB uv package cache in `~/.cache/uv`.
- 1.2 GB Bun cache in `~/.bun/install/cache`.
- 6.5 GB unmounted Next.js host build in `~/Omniroute/.build`.
- 2.9 GB stale database dump in `vds/WHO-project/vds-scripts/docker/backups/pre-p0-audit.dump`.

See `proposal.md` for background and motivation.

## Goals / Non-Goals

**Goals:**
- Free at least 30–50 GB of disk space in a strictly ordered, staged execution flow.
- Maintain continuous availability of core local daemon services: OmniRoute (20128, 20129) and SHB Schedule scheduler/db (9110, 5432).
- Rely strictly on native package and daemon management CLIs (`brew`, `npm`, `uv`, `bun`, `go`, `docker`) rather than arbitrary file deletions.
- Re-measure APFS Data volume capacity after each tier to verify actual recovery.

**Non-Goals:**
- Direct manipulation, resizing, or host deletion of `Docker.raw`.
- Broad pruning of Docker volumes (`docker volume prune -a`).
- Modifying personal user data (Photos library), streaming caches (DriveFS), or persistent agent memories (`~/.agentmemory`).
- Modifying Chrome on-device AI weights.

## Decisions

### Decision 1: Staged Tiered Execution with Remeasurement Gates

We partition candidate operations into three sequential tiers executed strictly in order of increasing risk, with `df -h /System/Volumes/Data` checks between tiers:
- **Tier 1 (Safe, 100% Regenerable Package Caches)**:
  - `brew cleanup --prune=all`
  - `npm cache clean --force`
  - `rm -rf ~/.npm/_npx/*`
  - `pnpm store prune`
  - `uv cache clean`
  - `bun pm cache rm`
  - `go clean -cache`
  - Expected recovery: ~21.5 GB.
- **Tier 2A (Docker Daemon Native Prune with Volume Isolation)**:
  - `docker builder prune -a -f`
  - `docker image prune -a -f`
  - Explicit deletion of confirmed unattached ephemeral test volumes (`0b050242...`, `shb-audit-*`, `shb-verification-*`, `smoke_scheduler_*`).
  - Expected recovery: ~24.4 GB.
- **Tier 2B (Local Development Build Leftovers & Dumps)**:
  - Removal of `~/Omniroute/.build` (host Next.js build unused by Docker runtime).
  - Removal of stale snapshot `pre-p0-audit.dump` (April 2026).
  - Expected recovery: ~9.4 GB.
- **Tier 2C (Simulator Shared dyld Caches)**:
  - `xcrun simctl runtime dyld_shared_cache remove --all`
  - Expected recovery: ~12.0 GB.

*Rationale*: Tier 1 carries zero side-effect risk and requires no daemon state changes. Tier 2A targets the single largest reclaimable block inside the Docker VM. Tier 2B cleans verified orphaned files outside git tracking.

### Decision 2: Docker Named Volume Protection

*Decision*: We strictly prohibit running blanket volume pruning (`docker volume prune -a`). Only volume names explicitly verified as unattached historical test/audit artifacts will be deleted using individual `docker volume rm <name>` commands.

*Rationale*: OmniRoute (`omniroute_omniroute-data`, `omniroute-redis-data`) and SHB Schedule (`shb-schedule_shb-scheduler-pgdata`, plus its container-attached anonymous `/var/lib/postgresql` volume `685eacfa...`) store persistent state in Docker volumes. Host-side VirtioFS bind mounts are not used due to SQLite WAL corruption hazards; thus, mounted volumes are the sole persistence tier for local development daemons.

### Decision 3: Sparse File Trim Dynamics

*Decision*: Do not attempt to truncate or delete `Docker.raw` on the macOS host. Instead, invoke Docker builder and image pruning from within the Docker CLI.

*Rationale*: In Docker Desktop on macOS, `Docker.raw` is an APFS sparse file managed by LinuxKit and the Apple Virtualization Framework. The hypervisor automatically issues `fstrim`/discard calls back to macOS APFS when blocks are unallocated, recovering host space without risking VM corruption.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Accidental deletion of active Docker database volume | Maintain an explicit allowlist of protected volumes (`omniroute*`, `shb-schedule_shb-scheduler-pgdata`, and container mount `685eacfa...`). Use single-target `docker volume rm` only for audited unattached ephemeral test volumes. |
| Re-download latency on subsequent package builds | Package caches (uv, npm, brew, bun) are rebuilt automatically on demand during subsequent builds or installs. Storage headroom takes precedence when disk is at 96%. |
| Temporary load spike during Docker pruning | Docker builder prune and image prune are run with `-f` non-interactively while inspecting container health pre- and post-prune. |
