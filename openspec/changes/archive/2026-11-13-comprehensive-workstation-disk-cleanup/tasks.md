# Tasks

## 1. Pre-cleanup Baseline & Environment Verification

- [x] 1.1 Record initial filesystem capacity and allocation on `/System/Volumes/Data` via `df -h /System/Volumes/Data`.
- [x] 1.2 Verify running Docker containers and daemon health via `docker ps -a` to establish baseline state for active services (`omniroute`, `redis`, `shb-schedule`).
- [x] 1.3 Record initial Docker resource consumption via `docker system df -v` (build cache, images, containers, and volumes).

## 2. Tier 1 Safe Package Manager Cache Eviction

- [x] 2.1 Run `brew cleanup --prune=all` to purge cached Homebrew bottles, installer dmgs, and downloads from `~/Library/Caches/Homebrew`.
- [x] 2.2 Run `npm cache clean --force` to purge npm tarball caches, and run `rm -rf ~/.npm/_npx/*` to purge unreferenced binary downloads.
- [x] 2.3 Run `pnpm store prune` to delete unreferenced pnpm packages from `~/.pnpm-store`.
- [x] 2.4 Run `uv cache clean` to purge unreferenced python wheels, sdists, and build archives from `~/.cache/uv`.
- [x] 2.5 Run `bun pm cache rm` to remove transient package tarballs from `~/.bun/install/cache`.
- [x] 2.6 Run `go clean -cache` to clear Go build objects from `~/Library/Caches/go-build`.
- [x] 2.7 Verify Tier 1 recovery by measuring available space on `/System/Volumes/Data` via `df -h /System/Volumes/Data`.

## 3. Tier 2A Docker Native Prune & Obsolete Volume Decommissioning

- [x] 3.1 Run `docker builder prune -a -f` to purge unreferenced Docker build layers and cache records.
- [x] 3.2 Run `docker image prune -a -f` to purge unreferenced images while preserving running container images.
- [x] 3.3 Decommission audited historical unattached ephemeral test volumes individually: `0b050242...`, `shb-audit-kt0tlx3n_shb-scheduler-pgdata`, `shb-verification-qr6zlch6_shb-scheduler-pgdata`, and `smoke_scheduler_isolated_pgdata_proof`.
- [x] 3.4 Confirm active database volumes (`omniroute_omniroute-data`, `omniroute-redis-data`, `omniroute-qdrant-data`, `shb-schedule_shb-scheduler-pgdata`, and container mount `685eacfa...`) and running containers remain completely healthy.
- [x] 3.5 Verify Tier 2A recovery via `docker system df` and `df -h /System/Volumes/Data`.

## 4. Tier 2B Local Development Build Residue & Stale Snapshot Decommissioning

- [x] 4.1 Remove unmounted host build artifacts in `~/Omniroute/.build` (`rm -rf /Users/androidteam/Omniroute/.build`).
- [x] 4.2 Remove stale April 2026 database dump `pre-p0-audit.dump` from `/Users/androidteam/Developer/vds/WHO-project/vds-scripts/docker/backups/`.
- [x] 4.3 Verify Tier 2B recovery by measuring available space on `/System/Volumes/Data` via `df -h /System/Volumes/Data`.

## 5. Tier 2C Simulator Shared Cache Purging

- [x] 5.1 Run `xcrun simctl runtime dyld_shared_cache remove --all` to purge rebuildable iOS simulator shared dyld caches from `/Library/Developer/CoreSimulator/Caches/dyld`.
- [x] 5.2 Verify Tier 2C recovery by measuring available space on `/System/Volumes/Data` via `df -h /System/Volumes/Data`.

## 6. Final Capacity Verification & Evidence Reporting

- [x] 6.1 Re-measure final filesystem capacity and verify available storage on `/System/Volumes/Data` exceeds the 40+ GiB operational threshold.
- [x] 6.2 Verify operational health of local services: probe OmniRoute health endpoint (`curl -fsSL http://127.0.0.1:20128/api/health`) and SHB scheduler status (`curl -fsSL http://127.0.0.1:9110/scheduler/health` or `docker inspect`).
- [x] 6.3 Validate the change strictly with `openspec validate 2026-11-13-comprehensive-workstation-disk-cleanup --strict --store openspec-store`.
