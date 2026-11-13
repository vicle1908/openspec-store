# Execution & Verification Evidence

## Change
`2026-11-13-comprehensive-workstation-disk-cleanup`

## Execution Summary
- **Baseline Date**: 2026-11-13
- **Initial APFS Data Storage**: 461 GB total, 440 GB used, 22 GB available (96% critical utilization).
- **Final APFS Data Storage**: 461 GB total, 383 GB used, 79 GB available (83% healthy operational headroom).
- **Net Reclaimed**: **+57 GB**.

## Detailed Tier Evidence

### Tier 1: Safe Package Manager Cache Eviction
- `brew cleanup --prune=all`: Removed cached bottle archives and installer downloads, reclaiming **5.8 GB**.
- `npm cache clean --force` & `rm -rf ~/.npm/_npx/*`: Flushed `.npm` tarball cache and one-off CLI binary trees from 7.7 GB down to 85 MB (**~7.6 GB reclaimed**).
- `pnpm store prune`: Pruned unreferenced package virtual store metadata.
- `uv cache clean --force`: Purged 191,351 unreferenced wheel and sdist files from `~/.cache/uv`, shrinking it from 5.2 GB down to 99 MB (**5.1 GiB reclaimed**).
- `bun pm cache rm`: Purged `bun install` cache (**~1.2 GB reclaimed**).
- `go clean -cache`: Cleared Go compilation build objects.
- **Subtotal Reclaimed Tier 1**: ~20.3 GB (Available storage reached 40 GB / 92% use).

### Tier 2A: Docker Native Prune & Volume Safety
- `docker builder prune -a -f`: Purged all unreferenced build layers, recovering **18.1 GB** (Build cache reduced from 18.1 GB to 0B).
- `docker image prune -a -f`: Purged 12 dangling and untagged image layers, recovering **3.311 GB**.
- Explicit decommissioning of audited historical unattached test volumes:
  - `0b0502420445b5a62246253f0b2ef8f653197bb20041af3bf1852d72f8b4f451`
  - `shb-audit-kt0tlx3n_shb-scheduler-pgdata`
  - `shb-verification-qr6zlch6_shb-scheduler-pgdata`
  - `smoke_scheduler_isolated_pgdata_proof`
- Protected volumes verified present and healthy:
  - `omniroute_omniroute-data`
  - `omniroute-redis-data`
  - `omniroute-qdrant-data`
  - `shb-schedule_shb-scheduler-pgdata`
  - `685eacfa...` (active PostgreSQL 18 container mount)
- **Subtotal Reclaimed Tier 2A**: ~21.4 GB (Available storage reached 51 GB / 90% use).

### Tier 2B: Local Build Residue & Stale Snapshot Decommissioning
- `rm -rf /Users/androidteam/Omniroute/.build`: Removed unmounted host Next.js build cache, recovering **6.5 GB**.
- `rm -f /Users/androidteam/Developer/vds/WHO-project/vds-scripts/docker/backups/pre-p0-audit.dump`: Removed stale April 2026 database snapshot, recovering **2.9 GB**.
- **Subtotal Reclaimed Tier 2B**: ~9.4 GB (Available storage reached 68 GB / 86% use).

### Tier 2C: iOS Simulator Shared dyld Cache Purging
- `xcrun simctl runtime dyld_shared_cache remove --all`: Purged rebuildable shared dyld caches from `/Library/Developer/CoreSimulator/Caches/dyld` across iOS 18.0, iOS 26.0, and iOS 26.1, recovering **12.0 GB** (Caches directory reduced from 12 GB to 0B).
- **Subtotal Reclaimed Tier 2C**: ~12.0 GB (Available storage reached 79 GB / 83% use).

## Daemon & Service Health Verification
- **OmniRoute API**: `http://127.0.0.1:20128/api/health` returned `HTTP/1.1 200 OK` (`{"status":"ok"}`).
- **SHB Scheduler**: `http://127.0.0.1:9110/scheduler/health` returned `HTTP/1.1 200 OK` (`{"status":"healthy","app":"shb-schedule","is_leader":true,"backend":"postgres"}`).
- **Container Health**: All 4 background containers (`omniroute`, `omniroute-redis`, `shb-schedule-scheduler-1`, `shb-schedule-db-1`) continuously healthy with zero downtime.

## OpenSpec Invariants
- `openspec validate 2026-11-13-comprehensive-workstation-disk-cleanup --strict --store openspec-store` strictly valid.
- All 23 tasks completed and verified with empirical outputs.
