# Tasks

## 1. Baseline Measurement & Preflight

- [x] 1.1 Record baseline `/System/Volumes/Data` capacity and verify that local APFS snapshots are not pinning blocks via `tmutil listlocalsnapshots /`

## 2. Tier 1 - Ephemeral Package Caches Reclamation

- [x] 2.1 Prune Homebrew bottle/cask caches via `brew cleanup --prune=all -s` and remove `$(brew --cache)`
- [x] 2.2 Clean npm global tarball cache via `npm cache clean --force` and verify `~/.npm/_cacache` reduction
- [x] 2.3 Prune unreferenced pnpm virtual store packages via `pnpm store prune`
- [x] 2.4 Prune unreferenced Python wheels and checkouts via `uv cache prune`
- [x] 2.5 Clear Go build cache via `go clean -cache`
- [x] 2.6 Measure intermediate APFS `/System/Volumes/Data` recovery post-Tier 1

## 3. Tier 2 - Container Runtime & Build Layer Pruning

- [x] 3.1 Prune Docker BuildKit cache layers via `docker builder prune -f`
- [x] 3.2 Prune unreferenced Docker images older than 7 days via `docker image prune -af --filter "until=168h"` while verifying running containers remain active
- [x] 3.3 Prune orphaned anonymous Docker volumes via `docker volume prune -f` while verifying named volumes (`omniroute-data`, `postgres-data`) are preserved
- [x] 3.4 Measure intermediate APFS `/System/Volumes/Data` recovery post-Tier 2

## 4. Tier 3 - Simulator & Diagnostic Housekeeping

- [x] 4.1 Delete unavailable or orphaned iOS simulator devices via `xcrun simctl delete unavailable`
- [x] 4.2 Purge system diagnostic crash logs older than 7 days from `~/Library/Logs/DiagnosticReports`
- [x] 4.3 Measure intermediate APFS `/System/Volumes/Data` recovery post-Tier 3

## 5. Verification & Toolchain Health Gates

- [x] 5.1 Confirm `/System/Volumes/Data` available capacity exceeds 30 GiB minimum threshold and calculate net reclaimed GiB
- [x] 5.2 Verify health of core developer toolchains (`node -v`, `brew --version`, `docker ps`, `git status`, `uv --version`, `go version`)
- [x] 5.3 Run `openspec validate --store openspec-store` to verify spec consistency
