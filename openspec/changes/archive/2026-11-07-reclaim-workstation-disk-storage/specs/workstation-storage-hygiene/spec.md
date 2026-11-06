## ADDED Requirements

### Requirement: Staged multi-tier package cache reclamation

The workstation storage reclamation workflow SHALL execute rebuildable cache eviction using only native vendor commands across Homebrew, npm, pnpm, Python uv, and Go to reclaim disk capacity without modifying active source code or repositories.

#### Scenario: Native package manager caches are pruned
- **WHEN** the operator executes Tier 1 package cache reclamation
- **THEN** the system SHALL run `brew cleanup --prune=all -s` and purge cached bottle archives
- **AND** the system SHALL run `npm cache clean --force` to flush global npm tarball caches
- **AND** the system SHALL run `pnpm store prune` to delete unreferenced pnpm packages
- **AND** the system SHALL run `uv cache prune` to purge unreferenced python wheels
- **AND** the system SHALL run `go clean -cache` to clear rebuildable Go compilation artifacts.

### Requirement: Container runtime pruning with named volume protection

The storage reclamation workflow SHALL prune dangling Docker build cache, unreferenced images older than 7 days, and orphaned anonymous volumes while strictly preserving all active running containers and named database or application volumes.

#### Scenario: Docker builder cache and unreferenced layers are pruned
- **WHEN** Docker daemon is running and reports reclaimable builder cache and unreferenced images
- **THEN** the system SHALL execute `docker builder prune -f`
- **AND** the system SHALL execute `docker image prune -af --filter "until=168h"`
- **AND** the system SHALL execute `docker volume prune -f` to purge anonymous volumes only
- **AND** active containers and named volumes including `omniroute-data` and `postgres-data` SHALL remain untouched.

### Requirement: Simulator and diagnostic housekeeping

The storage reclamation workflow SHALL delete unavailable iOS simulator devices and purge system diagnostic crash reports older than 7 days to eliminate orphaned system runtime accumulation.

#### Scenario: Stale simulators and crash logs are purged
- **WHEN** the operator executes Tier 3 housekeeping
- **THEN** the system SHALL run `xcrun simctl delete unavailable`
- **AND** the system SHALL remove diagnostic reports older than 7 days from `~/Library/Logs/DiagnosticReports`.

### Requirement: APFS Data volume capacity verification

The storage reclamation workflow SHALL measure and record `/System/Volumes/Data` capacity and availability before execution and after each tier, confirming that available storage exceeds the mandatory 30 GiB minimum threshold.

#### Scenario: Final availability exceeds minimum threshold
- **WHEN** all approved cleanup tiers complete
- **THEN** the system SHALL verify available space on `/System/Volumes/Data` via `df -h`
- **AND** the system SHALL verify that available capacity is greater than 30 GiB
- **AND** the system SHALL calculate and report the net reclaimed GiB.
