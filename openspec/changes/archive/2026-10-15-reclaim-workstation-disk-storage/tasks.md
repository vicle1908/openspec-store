# Tasks

## 1. Baseline Measurement

- [x] 1.1 Record initial baseline disk capacity and available GiB on `/System/Volumes/Data` via `df -h /System/Volumes/Data` (393 GiB used, 30 GiB available / 93% capacity).
- [x] 1.2 Check for APFS local snapshots via `tmutil listlocalsnapshots /` (verified 0 local snapshots).

## 2. Tier 1: Zero-Risk Ephemeral Caches

- [x] 2.1 Clean Homebrew cache and old downloaded bottles via `brew cleanup --prune=all -s` and remove `$(brew --cache)` (reclaimed 8.6 GB).
- [x] 2.2 Purge NPM tarball cache via `npm cache clean --force` (cleared 5.7 GB).
- [x] 2.3 Prune unreferenced uv wheels and build checkouts via `uv cache prune`.
- [x] 2.4 Measure intermediate storage recovery after Tier 1 (available space increased from 30 GiB to 44 GiB, +14 GiB delta).

## 3. Tier 2: Docker & Package Store Pruning

- [x] 3.1 Prune Docker builder cache via `docker builder prune -af` (reclaimed 970.9 MB).
- [x] 3.2 Prune unreferenced dangling Docker images older than 7 days via `docker image prune -af --filter "until=168h"` (reclaimed 5.487 GB).
- [x] 3.3 Prune orphaned anonymous Docker volumes via `docker volume prune -f` while preserving named volumes (removed 31 orphaned anonymous volumes).
- [x] 3.4 Prune unreferenced packages in pnpm global store via `pnpm store prune`.
- [x] 3.5 Measure intermediate storage recovery after Tier 2 (available space increased to 51 GiB).

## 4. Tier 3: Simulator & Diagnostic Housekeeping

- [x] 4.1 Delete unavailable and orphaned iOS simulator device references via `xcrun simctl delete unavailable`.
- [x] 4.2 Clean old crash dumps and diagnostic logs in `~/Library/Logs/DiagnosticReports/` older than 7 days.
- [x] 4.3 Measure intermediate storage recovery after Tier 3.

## 5. Post-Remediation Verification & OpenSpec Validation

- [x] 5.1 Record final disk capacity and calculate total GiB reclaimed on `/System/Volumes/Data` (51 GiB available / 88% capacity, 21.0 GiB net physical disk reclaimed).
- [x] 5.2 Verify core developer toolchains remain healthy (`git status`, `node v26.7.0`, `brew 7.0.9`, Docker services `omniroute` and `redis` healthy).
- [x] 5.3 Verify interactive zsh shell startup remains responsive (`time zsh -i -c exit` measured 0.16s).
- [x] 5.4 Validate OpenSpec change strictly via `openspec validate reclaim-workstation-disk-storage --strict --store openspec-store`.
